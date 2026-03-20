from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
import yaml

from registry.api import models, schemas
from registry.api.database import get_db
from registry.api.routers.auth import get_current_user

router = APIRouter(prefix="/skills", tags=["skills"])


# ── LIST ──────────────────────────────────────────────────────────────────────

@router.get("/", response_model=schemas.SkillListResponse)
def list_skills(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """List all skills with pagination."""
    total = db.query(func.count(models.Skill.id)).scalar()
    skip = (page - 1) * limit
    skills = db.query(models.Skill).offset(skip).limit(limit).all()
    return schemas.SkillListResponse(
        skills=skills,
        total_count=total,
        page=page,
        limit=limit,
    )


# ── SEARCH ────────────────────────────────────────────────────────────────────

@router.get("/search", response_model=schemas.SkillListResponse)
def search_skills(
    q: Optional[str] = Query(None, description="Search by name or description"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    type: Optional[str] = Query(None, description="Filter by execution type (prompt, tool_call, code, chain)"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search skills by name, description, tag, or execution type."""
    query = db.query(models.Skill)

    if q:
        query = query.filter(
            or_(
                models.Skill.name.ilike(f"%{q}%"),
                models.Skill.description.ilike(f"%{q}%"),
                models.Skill.id.ilike(f"%{q}%"),
            )
        )

    # SQLite tag filtering: tags are stored as JSON arrays, e.g. '["nlp", "text"]'
    # SQLite doesn't support native JSON array queries, so we filter in Python
    # after the query. This is fine for MVP with a small dataset.
    if tag:
        query = query.filter(models.Skill.tags.isnot(None))

    if type:
        valid_types = ["prompt", "tool_call", "code", "chain"]
        if type.lower() not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid type. Must be one of: {', '.join(valid_types)}")
        query = query.filter(models.Skill.exec_type == type.lower())

    if tag:
        # Fetch all matching results first to apply Python post-filter
        results = query.all()
        tag_lower = tag.lower()
        results = [
            s for s in results
            if s.tags and any(t.lower() == tag_lower for t in (s.tags if isinstance(s.tags, list) else []))
        ]
        total = len(results)
        
        # Slicing for pagination
        skip = (page - 1) * limit
        results = results[skip:skip + limit]
    else:
        total = query.count()
        skip = (page - 1) * limit
        results = query.offset(skip).limit(limit).all()

    return schemas.SkillListResponse(
        skills=results,
        total_count=total,
        page=page,
        limit=limit,
    )


# ── PUBLISH ───────────────────────────────────────────────────────────────────

@router.post("/", response_model=schemas.SkillDetail, status_code=201)
def publish_skill(
    skill: schemas.SkillCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Publish a new skill to the registry (requires authentication)."""
    # Override author with authenticated user
    author = current_user

    # Check if this exact version already exists (immutable versions)
    existing = db.query(models.Skill).filter_by(
        author=author,
        id=skill.id,
        version=skill.version,
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Skill '{author}/{skill.id}@{skill.version}' already exists. Published versions are immutable."
        )

    try:
        parsed_yaml = yaml.safe_load(skill.yaml_content)
    except yaml.YAMLError:
        raise HTTPException(status_code=422, detail="Invalid YAML content")

    if not isinstance(parsed_yaml, dict) or "skill" not in parsed_yaml:
        raise HTTPException(status_code=422, detail="Invalid skill.yaml: missing top-level 'skill' key")

    db_skill = models.Skill(
        id=skill.id,
        name=skill.name,
        description=skill.description,
        version=skill.version,
        yaml_content=skill.yaml_content,
        tags=skill.tags,
        exec_type=skill.exec_type,
        benchmarks=skill.benchmarks,
        author=author,
    )
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill


# ── GET LATEST ────────────────────────────────────────────────────────────────

def _semver_key(version_str: str):
    """Parse a semver string into a tuple for sorting."""
    try:
        parts = version_str.split(".")
        return tuple(int(p) for p in parts[:3])
    except (ValueError, AttributeError):
        return (0, 0, 0)


@router.get("/{author}/{skill_id}", response_model=schemas.SkillDetail)
def get_skill_latest(author: str, skill_id: str, db: Session = Depends(get_db)):
    """Get the latest version of a skill by author and ID."""
    skills = db.query(models.Skill).filter_by(author=author, id=skill_id).all()
    if not skills:
        raise HTTPException(status_code=404, detail=f"Skill '{author}/{skill_id}' not found")

    # Sort by semver (descending) and return the latest
    latest = sorted(skills, key=lambda s: _semver_key(s.version), reverse=True)[0]
    return latest


# ── GET SPECIFIC VERSION ──────────────────────────────────────────────────────

@router.get("/{author}/{skill_id}/{version}", response_model=schemas.SkillDetail)
def get_skill_version(
    author: str,
    skill_id: str,
    version: str,
    db: Session = Depends(get_db)
):
    """Get a specific version of a skill."""
    skill = db.query(models.Skill).filter_by(
        author=author,
        id=skill_id,
        version=version,
    ).first()

    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{author}/{skill_id}@{version}' not found")
    return skill


# ── DELETE (YANK) ─────────────────────────────────────────────────────────────

@router.delete("/{author}/{skill_id}/{version}", response_model=schemas.MessageResponse)
def delete_skill_version(
    author: str,
    skill_id: str,
    version: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Yank (delete) a specific version of a skill. Author only."""
    if current_user != author:
        raise HTTPException(status_code=403, detail="You can only delete your own skills")

    skill = db.query(models.Skill).filter_by(
        author=author,
        id=skill_id,
        version=version,
    ).first()

    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{author}/{skill_id}@{version}' not found")

    db.delete(skill)
    db.commit()
    return schemas.MessageResponse(message=f"Skill '{author}/{skill_id}@{version}' has been yanked")

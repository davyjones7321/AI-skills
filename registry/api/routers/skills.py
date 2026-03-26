from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Any, Dict, List, Optional
import json
import yaml

from registry.api import models, schemas
from registry.api.database import get_db
from registry.api.routers.auth import get_current_user

router = APIRouter(prefix="/skills", tags=["skills"])


def _build_skill_detail(skill: models.Skill) -> schemas.SkillDetail:
    """Build a detail payload with structured fields parsed from yaml_content."""
    tags: List[str] = []
    if isinstance(skill.tags, str):
        try:
            loaded_tags = json.loads(skill.tags)
            if isinstance(loaded_tags, list):
                tags = loaded_tags
        except Exception:
            tags = []
    elif isinstance(skill.tags, list):
        tags = skill.tags

    benchmarks: Dict[str, Any] = {}
    if isinstance(skill.benchmarks, str):
        try:
            loaded_benchmarks = json.loads(skill.benchmarks)
            if isinstance(loaded_benchmarks, dict):
                benchmarks = loaded_benchmarks
        except Exception:
            benchmarks = {}
    elif isinstance(skill.benchmarks, dict):
        benchmarks = skill.benchmarks

    try:
        parsed_yaml = yaml.safe_load(skill.yaml_content)
    except Exception:
        parsed_yaml = {}

    parsed: Dict[str, Any] = {}
    if isinstance(parsed_yaml, dict):
        skill_block = parsed_yaml.get("skill", parsed_yaml)
        if isinstance(skill_block, dict):
            parsed = skill_block

    return schemas.SkillDetail(
        id=skill.id,
        author=skill.author,
        version=skill.version,
        name=skill.name,
        description=skill.description,
        tags=tags,
        exec_type=skill.exec_type,
        benchmarks=benchmarks,
        downloads=skill.downloads,
        published_at=skill.published_at,
        reviewed=skill.reviewed,
        yaml_content=skill.yaml_content,
        inputs=parsed.get("inputs", []) if isinstance(parsed.get("inputs", []), list) else [],
        outputs=parsed.get("outputs", []) if isinstance(parsed.get("outputs", []), list) else [],
        execution=parsed.get("execution", {}) if isinstance(parsed.get("execution", {}), dict) else {},
        compatible_with=parsed.get("compatible_with", []) if isinstance(parsed.get("compatible_with", []), list) else [],
    )


def _sort_skills(skills: List[models.Skill], sort: str) -> List[models.Skill]:
    if sort == "most_downloaded":
        return sorted(skills, key=lambda skill: skill.downloads or 0, reverse=True)
    if sort == "lowest_latency":
        def latency_key(skill: models.Skill) -> float:
            benchmarks = skill.benchmarks if isinstance(skill.benchmarks, dict) else {}
            latency = benchmarks.get("avg_latency_ms")
            if isinstance(latency, (int, float)):
                return float(latency)
            return float("inf")

        return sorted(skills, key=lambda skill: (latency_key(skill), -(skill.downloads or 0)))
    # Default newest
    return sorted(skills, key=lambda skill: skill.published_at or 0, reverse=True)


def _paginate(skills: List[models.Skill], page: int, limit: int) -> List[models.Skill]:
    skip = (page - 1) * limit
    return skills[skip: skip + limit]


# ── LIST ──────────────────────────────────────────────────────────────────────

@router.get("/", response_model=schemas.SkillListResponse)
def list_skills(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort: str = Query("newest", description="Sort order: newest | most_downloaded | lowest_latency"),
    db: Session = Depends(get_db)
):
    """List all skills with pagination."""
    valid_sorts = {"newest", "most_downloaded", "lowest_latency"}
    if sort not in valid_sorts:
        raise HTTPException(status_code=400, detail=f"Invalid sort. Must be one of: {', '.join(sorted(valid_sorts))}")

    all_skills = db.query(models.Skill).all()
    sorted_skills = _sort_skills(all_skills, sort)
    total = len(sorted_skills)
    skills = _paginate(sorted_skills, page, limit)
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
    sort: str = Query("newest", description="Sort order: newest | most_downloaded | lowest_latency"),
    db: Session = Depends(get_db)
):
    """Search skills by name, description, tag, or execution type."""
    valid_sorts = {"newest", "most_downloaded", "lowest_latency"}
    if sort not in valid_sorts:
        raise HTTPException(status_code=400, detail=f"Invalid sort. Must be one of: {', '.join(sorted(valid_sorts))}")

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

    results = query.all()

    if tag:
        tag_lower = tag.lower()
        results = [
            s for s in results
            if s.tags and any(t.lower() == tag_lower for t in (s.tags if isinstance(s.tags, list) else []))
        ]

    sorted_results = _sort_skills(results, sort)
    total = len(sorted_results)
    paged_results = _paginate(sorted_results, page, limit)

    return schemas.SkillListResponse(
        skills=paged_results,
        total_count=total,
        page=page,
        limit=limit,
    )


@router.get("/tags", response_model=schemas.TagListResponse)
def list_tags(db: Session = Depends(get_db)):
    """Return a deduplicated list of all tags in published skills."""
    query = db.query(models.Skill)
    if hasattr(models.Skill, "published"):
        query = query.filter(getattr(models.Skill, "published") == True)  # noqa: E712

    all_tags: List[str] = []
    for skill in query.all():
        raw_tags = skill.tags
        try:
            tags = json.loads(raw_tags) if isinstance(raw_tags, str) else raw_tags
        except Exception:
            tags = []

        if isinstance(tags, list):
            all_tags.extend(tag for tag in tags if isinstance(tag, str) and tag.strip())

    unique_tags = sorted(set(tag.strip() for tag in all_tags if tag.strip()), key=str.lower)
    return schemas.TagListResponse(tags=unique_tags)


# ── PUBLISH ───────────────────────────────────────────────────────────────────

@router.post("/", response_model=schemas.SkillDetail, status_code=201)
def publish_skill(
    skill: schemas.SkillCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Publish a new skill to the registry (requires authentication)."""
    # Override author with authenticated user
    author = current_user.username

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
    return _build_skill_detail(db_skill)


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
    return _build_skill_detail(latest)


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
    return _build_skill_detail(skill)


# ── DELETE (YANK) ─────────────────────────────────────────────────────────────

@router.delete("/{author}/{skill_id}/{version}", response_model=schemas.MessageResponse)
def delete_skill_version(
    author: str,
    skill_id: str,
    version: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Yank (delete) a specific version of a skill. Author only."""
    if current_user.username != author:
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

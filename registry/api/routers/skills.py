from fastapi import APIRouter, Depends, HTTPException, Query, Request
from starlette.datastructures import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Any, Dict, List, Optional, Tuple
import json
import yaml

from registry.api import models, schemas
from registry.api.categories import VALID_CATEGORY_SET
from registry.api.database import get_db
from registry.api.routers.auth import get_current_user
from registry.api.utils import make_json_safe

router = APIRouter(prefix="/skills", tags=["skills"])
VALID_EXEC_TYPES = {"prompt", "tool_call", "code", "chain"}


def _raise_validation_error(message: str) -> None:
    raise HTTPException(status_code=422, detail=message)


def _read_string_field(data: Dict[str, Any], key: str, *, required: bool = True) -> str:
    value = data.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    if required:
        _raise_validation_error(f"Invalid skill.yaml: missing required field 'skill.{key}'")
    return ""


def _validate_tags(value: Any) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        _raise_validation_error("Invalid skill.yaml: 'skill.tags' must be a list of strings")
    return [item.strip() for item in value]


def _validate_io_rows(value: Any, *, field_name: str, require_required_flag: bool) -> List[Dict[str, Any]]:
    if not isinstance(value, list) or not value:
        _raise_validation_error(f"Invalid skill.yaml: 'skill.{field_name}' must contain at least one entry")

    normalized_rows: List[Dict[str, Any]] = []
    for index, row in enumerate(value, start=1):
        if not isinstance(row, dict):
            _raise_validation_error(f"Invalid skill.yaml: 'skill.{field_name}[{index}]' must be an object")

        name = row.get("name")
        io_type = row.get("type")
        if not isinstance(name, str) or not name.strip():
            _raise_validation_error(f"Invalid skill.yaml: 'skill.{field_name}[{index}].name' is required")
        if not isinstance(io_type, str) or not io_type.strip():
            _raise_validation_error(f"Invalid skill.yaml: 'skill.{field_name}[{index}].type' is required")
        if require_required_flag and "required" in row and not isinstance(row.get("required"), bool):
            _raise_validation_error(f"Invalid skill.yaml: 'skill.{field_name}[{index}].required' must be a boolean")

        normalized_row = dict(row)
        normalized_row["name"] = name.strip()
        normalized_row["type"] = io_type.strip()
        normalized_rows.append(normalized_row)

    return normalized_rows


def _validate_execution(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        _raise_validation_error("Invalid skill.yaml: 'skill.execution' must be an object")

    execution_type = value.get("type")
    if not isinstance(execution_type, str) or execution_type not in VALID_EXEC_TYPES:
        _raise_validation_error("Invalid skill.yaml: 'skill.execution.type' must be one of prompt, tool_call, code, chain")

    if execution_type == "prompt":
        prompt_template = value.get("prompt_template")
        if not isinstance(prompt_template, str) or not prompt_template.strip():
            _raise_validation_error("Invalid skill.yaml: prompt skills require 'skill.execution.prompt_template'")
    elif execution_type == "tool_call":
        endpoint = value.get("endpoint")
        if not isinstance(endpoint, str) or not endpoint.strip():
            _raise_validation_error("Invalid skill.yaml: tool_call skills require 'skill.execution.endpoint'")
    elif execution_type == "code":
        source = value.get("source", value.get("code"))
        if not isinstance(source, str) or not source.strip():
            _raise_validation_error("Invalid skill.yaml: code skills require 'skill.execution.source'")
    elif execution_type == "chain":
        steps = value.get("steps")
        if not isinstance(steps, list) or not steps:
            _raise_validation_error("Invalid skill.yaml: chain skills require at least one 'skill.execution.steps' entry")

    return dict(value)


def _extract_skill_from_yaml(raw_yaml: str, author: str) -> Tuple[schemas.SkillCreate, str]:
    try:
        parsed_yaml = yaml.safe_load(raw_yaml)
    except yaml.YAMLError as exc:
        _raise_validation_error(f"Invalid YAML content: {exc}")

    if not isinstance(parsed_yaml, dict) or "skill" not in parsed_yaml:
        _raise_validation_error("Invalid skill.yaml: missing top-level 'skill' key")

    skill_block = parsed_yaml.get("skill")
    if not isinstance(skill_block, dict):
        _raise_validation_error("Invalid skill.yaml: 'skill' must be an object")

    skill_id = _read_string_field(skill_block, "id")
    version = _read_string_field(skill_block, "version")
    name = _read_string_field(skill_block, "name")
    description = _read_string_field(skill_block, "description")
    tags = _validate_tags(skill_block.get("tags"))
    inputs = _validate_io_rows(skill_block.get("inputs"), field_name="inputs", require_required_flag=True)
    outputs = _validate_io_rows(skill_block.get("outputs"), field_name="outputs", require_required_flag=False)
    execution = _validate_execution(skill_block.get("execution"))

    category = skill_block.get("category")
    if category is not None:
        if not isinstance(category, str) or category not in VALID_CATEGORY_SET:
            _raise_validation_error("Invalid skill.yaml: 'skill.category' must be one of the supported categories")
        category = category.strip()

    normalized_skill_block = dict(skill_block)
    normalized_skill_block["id"] = skill_id
    normalized_skill_block["version"] = version
    normalized_skill_block["name"] = name
    normalized_skill_block["description"] = description
    normalized_skill_block["author"] = author
    normalized_skill_block["tags"] = tags
    normalized_skill_block["inputs"] = inputs
    normalized_skill_block["outputs"] = outputs
    normalized_skill_block["execution"] = execution
    if category is not None:
        normalized_skill_block["category"] = category

    normalized_yaml = yaml.safe_dump(
        {"skill": normalized_skill_block},
        sort_keys=False,
        allow_unicode=False,
    )

    benchmarks = normalized_skill_block.get("benchmarks")
    if benchmarks is not None and not isinstance(benchmarks, dict):
        _raise_validation_error("Invalid skill.yaml: 'skill.benchmarks' must be an object when provided")

    return (
        schemas.SkillCreate(
            id=skill_id,
            author=author,
            version=version,
            name=name,
            description=description,
            tags=tags,
            exec_type=execution["type"],
            category=category,
            benchmarks=benchmarks if isinstance(benchmarks, dict) else None,
            yaml_content=normalized_yaml,
        ),
        normalized_yaml,
    )


async def _parse_publish_request(request: Request, author: str) -> schemas.SkillCreate:
    content_type = request.headers.get("content-type", "").lower()

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        upload = form.get("file")
        if not isinstance(upload, UploadFile):
            _raise_validation_error("Missing file upload. Send a multipart form with a 'file' field containing skill.yaml")

        try:
            raw_bytes = await upload.read()
            raw_yaml = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            _raise_validation_error(f"Invalid YAML file encoding: {exc}")

        if not raw_yaml.strip():
            _raise_validation_error("Uploaded skill.yaml file is empty")

        skill, _ = _extract_skill_from_yaml(raw_yaml, author)
        return skill

    try:
        payload = await request.json()
    except Exception as exc:
        _raise_validation_error(f"Unable to parse request body: {exc}")

    if not isinstance(payload, dict):
        _raise_validation_error("Invalid JSON payload")

    try:
        json_payload = schemas.SkillCreate.model_validate(payload)
    except Exception as exc:
        _raise_validation_error(str(exc))

    skill, _ = _extract_skill_from_yaml(json_payload.yaml_content, author)
    return skill


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
        category=skill.category,
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
    category: Optional[str] = Query(None, description="Filter by category"),
    sort: str = Query("newest", description="Sort order: newest | most_downloaded | lowest_latency"),
    db: Session = Depends(get_db)
):
    """List all skills with pagination."""
    valid_sorts = {"newest", "most_downloaded", "lowest_latency"}
    if sort not in valid_sorts:
        raise HTTPException(status_code=400, detail=f"Invalid sort. Must be one of: {', '.join(sorted(valid_sorts))}")

    query = db.query(models.Skill)
    if category:
        if category not in VALID_CATEGORY_SET:
            raise HTTPException(status_code=400, detail="Invalid category")
        query = query.filter(models.Skill.category == category)

    all_skills = query.all()
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
    category: Optional[str] = Query(None, description="Filter by category"),
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

    if category:
        if category not in VALID_CATEGORY_SET:
            raise HTTPException(status_code=400, detail="Invalid category")
        query = query.filter(models.Skill.category == category)

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
async def publish_skill(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Publish a new skill to the registry (requires authentication)."""
    author = current_user.username
    skill = await _parse_publish_request(request, author)

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

    db_skill = models.Skill(
        id=skill.id,
        name=skill.name,
        description=skill.description,
        version=skill.version,
        yaml_content=skill.yaml_content,
        tags=skill.tags,
        exec_type=skill.exec_type,
        category=skill.category,
        benchmarks=make_json_safe(skill.benchmarks) if skill.benchmarks else None,
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

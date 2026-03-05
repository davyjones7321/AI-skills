from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from registry.api import models, schemas
from registry.api.database import get_db

router = APIRouter(prefix="/skills", tags=["skills"])

@router.get("/", response_model=List[schemas.Skill])
def list_skills(
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    skills = db.query(models.Skill).offset(skip).limit(limit).all()
    return skills

@router.get("/search", response_model=List[schemas.Skill])
def search_skills(
    q: Optional[str] = None, 
    tag: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(models.Skill)
    if q:
        query = query.filter(
            or_(
                models.Skill.name.contains(q),
                models.Skill.description.contains(q)
            )
        )
    # Tag filtering implementation would need proper JSON filtering logic
    # For SQLite, simplistic check (ideally Postgres @> operator)
    if tag:
        # This is a naive implementation for SQLite prototype
        # In a real Postgres implementation, use: models.Skill.tags.contains([tag])
        pass
        
    return query.limit(50).all()

@router.post("/", response_model=schemas.Skill)
def publish_skill(skill: schemas.SkillCreate, db: Session = Depends(get_db)):
    # Check if exists
    existing = db.query(models.Skill).filter_by(
        author="unknown", # TODO: Get from auth
        id=skill.id,
        version=skill.version
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Skill version already exists")

    db_skill = models.Skill(
        **skill.model_dump(),
        author="unknown", # TODO: Get from auth
    )
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

@router.get("/{author}/{skill_id}", response_model=schemas.SkillDetail)
def get_skill_latest(author: str, skill_id: str, db: Session = Depends(get_db)):
    # Naive 'latest' implementation: sort by version desc? 
    # Semver sorting in SQL is hard. 
    # For prototype, just getting the one with matching ID? 
    # Actually, the Key is (author, id, version). 
    # This endpoint implies finding the latest version.
    
    # Simple approach: Get all versions, sort in python, return latest
    skills = db.query(models.Skill).filter_by(author=author, id=skill_id).all()
    if not skills:
        raise HTTPException(status_code=404, detail="Skill not found")
        
    # TODO: Implement proper semver sorting. For now, just return the last created.
    latest = sorted(skills, key=lambda s: s.published_at, reverse=True)[0]
    return latest

@router.get("/{author}/{skill_id}/{version}", response_model=schemas.SkillDetail)
def get_skill_version(
    author: str, 
    skill_id: str, 
    version: str, 
    db: Session = Depends(get_db)
):
    skill = db.query(models.Skill).filter_by(
        author=author, 
        id=skill_id, 
        version=version
    ).first()
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill version not found")
    return skill

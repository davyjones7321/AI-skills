"""
Seed script — Populates the registry database with all example skills.

Usage:
    python -m registry.api.seed
    
    # Or from project root:
    python registry/api/seed.py

This script is idempotent — it skips skills that already exist.
"""

import sys
import os
from pathlib import Path

# Add project root to path so we can import registry modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import yaml
from datetime import date, datetime
from registry.api.database import SessionLocal, engine, Base
from registry.api import models


def _make_json_safe(obj):
    """Recursively convert date/datetime objects to ISO strings for JSON serialization."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_make_json_safe(item) for item in obj]
    return obj


def seed_database():
    """Read all example skills and insert them into the database."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    examples_dir = project_root / "examples"
    
    if not examples_dir.exists():
        print(f"[ERROR] Examples directory not found: {examples_dir}")
        sys.exit(1)
    
    skills_added = 0
    skills_skipped = 0
    
    # Find all skill.yaml files in examples/
    skill_dirs = sorted(examples_dir.iterdir())
    
    for skill_dir in skill_dirs:
        skill_file = skill_dir / "skill.yaml"
        if not skill_file.exists():
            continue
        
        # Read and parse the YAML
        with open(skill_file, encoding="utf-8") as f:
            raw_content = f.read()
        
        try:
            data = yaml.safe_load(raw_content)
        except yaml.YAMLError as e:
            print(f"  [SKIP] {skill_dir.name}: YAML parse error — {e}")
            skills_skipped += 1
            continue
        
        skill = data.get("skill", {})
        skill_id = skill.get("id", skill_dir.name)
        version = skill.get("version", "1.0.0")
        author = skill.get("author", "ai-skills-team")
        
        # Check if already exists
        existing = db.query(models.Skill).filter_by(
            author=author,
            id=skill_id,
            version=version,
        ).first()
        
        if existing:
            print(f"  [SKIP] {author}/{skill_id}@{version} — already exists")
            skills_skipped += 1
            continue
        
        # Extract fields
        execution = skill.get("execution", {})
        benchmarks = skill.get("benchmarks", {})
        
        db_skill = models.Skill(
            id=skill_id,
            author=author,
            version=version,
            name=skill.get("name", skill_id),
            description=skill.get("description", "").strip(),
            yaml_content=raw_content,
            tags=skill.get("tags", []),
            exec_type=execution.get("type", "prompt"),
            benchmarks=_make_json_safe(benchmarks) if benchmarks else {},
            downloads=0,
            reviewed=True,  # Example skills are pre-reviewed
        )
        
        db.add(db_skill)
        db.commit()
        print(f"  [ADD]  {author}/{skill_id}@{version} ({execution.get('type', '?')})")
        skills_added += 1
    
    db.close()
    
    print(f"\n{'=' * 40}")
    print(f"  Seed complete: {skills_added} added, {skills_skipped} skipped")
    print(f"{'=' * 40}")
    
    return skills_added, skills_skipped


if __name__ == "__main__":
    print("\n  ai-skills Registry — Seeding database\n")
    seed_database()

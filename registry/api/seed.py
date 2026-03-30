"""
Seed script — Populates the registry database with all example skills.

Usage:
    python -m registry.api.seed
    
    # Or from project root:
    python registry/api/seed.py

This script is idempotent — it skips skills that already exist.
"""

import sys
from pathlib import Path

# Add project root to path so we can import registry modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import yaml
from datetime import date, datetime
from registry.api.database import SessionLocal, engine, Base, run_migrations
from registry.api import models
from registry.api.categories import VALID_CATEGORIES


SKILL_CATEGORIES = {
    "summarize-document": "Content & Writing",
    "extract-invoice": "Data Processing",
    "classify-sentiment": "Content & Writing",
    "translate-text": "Content & Writing",
    "extract-email-data": "Content & Writing",
    "generate-commit-message": "Code Review",
    "code-review": "Code Review",
    "detect-language": "Utilities",
    "generate-sql": "Database",
    "summarize-to-tweet": "Content & Writing",
    "web-search": "APIs & Integrations",
    "spell-check": "APIs & Integrations",
    "weather-lookup": "APIs & Integrations",
    "word-frequency": "Data Processing",
    "markdown-to-html": "Utilities",
    "json-to-csv": "Data Processing",
    "calculate-reading-time": "Utilities",
    "translate-and-summarize": "Content & Writing",
    "review-and-fix-code": "Code Review",
}


from registry.api.utils import make_json_safe


def seed_database():
    """Read all example skills and insert them into the database."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    run_migrations()
    
    db = SessionLocal()
    examples_dir = project_root / "examples"
    
    if not examples_dir.exists():
        print(f"[ERROR] Examples directory not found: {examples_dir}")
        sys.exit(1)
    
    skills_added = 0
    skills_skipped = 0

    missing_categories = sorted(set(SKILL_CATEGORIES.values()) - set(VALID_CATEGORIES))
    if missing_categories:
        raise ValueError(f"Seed category map contains invalid values: {missing_categories}")
    
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
        category = SKILL_CATEGORIES.get(skill_id)
        
        # Check if already exists
        existing = db.query(models.Skill).filter_by(
            author=author,
            id=skill_id,
            version=version,
        ).first()
        
        if existing:
            if existing.category != category:
                existing.category = category
                db.add(existing)
                db.commit()
                print(f"  [UPDATE] {author}/{skill_id}@{version} category → {category}")
            else:
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
            category=category,
            benchmarks=make_json_safe(benchmarks) if benchmarks else {},
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

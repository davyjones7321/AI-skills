from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SkillBase(BaseModel):
    name: str
    description: str
    tags: List[str] = []
    exec_type: str
    benchmarks: Optional[Dict[str, Any]] = None

class SkillCreate(SkillBase):
    id: str
    version: str
    yaml_content: str

class Skill(SkillBase):
    id: str
    author: str
    version: str
    downloads: int
    published_at: datetime
    reviewed: bool

    model_config = ConfigDict(from_attributes=True)

class SkillDetail(Skill):
    yaml_content: str

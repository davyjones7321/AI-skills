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
    author: str
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
    inputs: List[Dict[str, Any]] = []
    outputs: List[Dict[str, Any]] = []
    execution: Dict[str, Any] = {}
    compatible_with: List[str] = []


class SkillListResponse(BaseModel):
    skills: List[Skill]
    total_count: int
    page: int
    limit: int


class TagListResponse(BaseModel):
    tags: List[str]


class MessageResponse(BaseModel):
    message: str


class AuthUserResponse(BaseModel):
    github_id: str
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None


class LogoutResponse(BaseModel):
    ok: bool

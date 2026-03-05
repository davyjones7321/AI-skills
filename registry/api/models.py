from sqlalchemy import Column, String, Text, Integer, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from registry.api.database import Base

class Skill(Base):
    __tablename__ = "skills"

    id = Column(String, primary_key=True, index=True)
    author = Column(String, primary_key=True, index=True)
    version = Column(String, primary_key=True, index=True)
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    yaml_content = Column(Text, nullable=False)
    
    tags = Column(JSON, default=[])
    exec_type = Column(String, nullable=False)
    benchmarks = Column(JSON, default={})
    
    downloads = Column(Integer, default=0)
    reviewed = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True), server_default=func.now())

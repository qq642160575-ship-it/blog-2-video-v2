from sqlalchemy import Column, String, Integer, Text, DateTime, func
from app.core.db import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(32), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    source_type = Column(String(16), nullable=False)  # text / markdown
    content = Column(Text, nullable=False)
    char_count = Column(Integer, nullable=False)
    language = Column(String(16), default="zh-CN")
    status = Column(String(16), default="draft")  # draft / generated / failed
    latest_job_id = Column(String(32), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

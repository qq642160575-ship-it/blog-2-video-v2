"""input: 依赖 SQLAlchemy Base 和项目字段设计。
output: 向外提供 Project 数据模型。
pos: 位于模型层，负责持久化项目主体。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

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

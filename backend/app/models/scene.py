"""input: 依赖 SQLAlchemy Base 和分镜字段设计。
output: 向外提供 Scene 数据模型。
pos: 位于模型层，负责持久化当前分镜。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, func
from app.core.db import Base


class Scene(Base):
    __tablename__ = "scenes"

    id = Column(String(32), primary_key=True, index=True)
    project_id = Column(String(32), nullable=False, index=True)
    current_version = Column(Integer, default=1)
    scene_order = Column(Integer, nullable=False)
    template_type = Column(String(32), nullable=False)
    goal = Column(Text, nullable=True)
    voiceover = Column(Text, nullable=False)
    screen_text = Column(JSON, nullable=False)  # Array of strings
    duration_sec = Column(Integer, nullable=False)
    pace = Column(String(16), nullable=True)
    transition = Column(String(16), nullable=True)
    visual_params = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

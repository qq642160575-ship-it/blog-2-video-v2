"""input: 依赖 SQLAlchemy Base 和版本字段设计。
output: 向外提供 SceneVersion 数据模型。
pos: 位于模型层，负责持久化分镜历史版本。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, func
from app.core.db import Base


class SceneVersion(Base):
    __tablename__ = "scene_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scene_id = Column(String(32), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    project_id = Column(String(32), nullable=False, index=True)
    template_type = Column(String(32), nullable=False)
    goal = Column(Text, nullable=True)
    voiceover = Column(Text, nullable=False)
    screen_text = Column(JSON, nullable=False)
    duration_sec = Column(Integer, nullable=False)
    pace = Column(String(16), nullable=True)
    transition = Column(String(16), nullable=True)
    visual_params = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

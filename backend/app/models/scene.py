"""input: 依赖 SQLAlchemy Base 和分镜字段设计（含 v3 叙事质量字段）。
output: 向外提供 Scene 数据模型。
pos: 位于模型层，负责持久化当前分镜。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON, func
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

    # v3: 叙事质量字段（对应 migration b1c2d3e4f5a6）
    scene_role = Column(String(20), nullable=False, default='body')       # hook | body | close
    narrative_stage = Column(String(20), nullable=False, default='build') # opening | build | payoff | close
    emotion_level = Column(Integer, nullable=False, default=3)            # 1-5
    hook_type = Column(String(20), nullable=True)                         # question | reveal | contrast
    quality_score = Column(Float, nullable=True)                          # 0.0-1.0

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

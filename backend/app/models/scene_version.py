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

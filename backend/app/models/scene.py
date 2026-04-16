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

"""input: 依赖 SQLAlchemy Base 和素材字段设计。
output: 向外提供 Asset 数据模型。
pos: 位于模型层，负责持久化素材记录。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

"""
Asset model - Tracks all generated files (audio, subtitle, video)
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.core.db import Base


class Asset(Base):
    """Asset model for tracking generated files"""
    __tablename__ = "assets"

    id = Column(String, primary_key=True)  # asset_xxx
    project_id = Column(String, nullable=False, index=True)
    job_id = Column(String, nullable=False, index=True)

    # Asset type: audio, subtitle, video, scene_json, image
    asset_type = Column(String, nullable=False, index=True)

    # File information
    file_path = Column(String, nullable=False)  # Relative or absolute path
    file_url = Column(String, nullable=True)  # Public URL if uploaded to storage
    file_size = Column(Integer, nullable=True)  # Size in bytes
    mime_type = Column(String, nullable=True)  # e.g., audio/mpeg, video/mp4

    # Metadata (JSON string)
    meta_data = Column(Text, nullable=True)  # Additional metadata as JSON

    # Status
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Asset {self.id} type={self.asset_type} project={self.project_id}>"

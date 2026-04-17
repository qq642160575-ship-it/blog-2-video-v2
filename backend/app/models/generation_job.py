"""input: 依赖 SQLAlchemy Base 和任务字段设计。
output: 向外提供 GenerationJob 数据模型。
pos: 位于模型层，负责持久化任务状态。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from sqlalchemy import Column, String, Integer, Text, DateTime, Numeric, func
from app.core.db import Base


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(String(32), primary_key=True, index=True)
    project_id = Column(String(32), nullable=False, index=True)
    job_type = Column(String(16), nullable=False)  # generate / rerender
    status = Column(String(16), default="queued", index=True)  # queued / running / waiting_retry / failed / completed / cancelled
    stage = Column(String(32), nullable=True, index=True)  # article_parse / scene_generate / ...
    progress = Column(Numeric(4, 2), default=0.0)  # 0 to 1
    attempt = Column(Integer, default=1)
    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    result_video_url = Column(Text, nullable=True)
    result_subtitle_url = Column(Text, nullable=True)
    result_scene_json_url = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

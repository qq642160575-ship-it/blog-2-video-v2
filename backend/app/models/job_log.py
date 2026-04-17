"""
Job Log Model - Records detailed logs for each job stage
"""
from sqlalchemy import Column, String, Text, DateTime, Float, Integer
from sqlalchemy.sql import func
from app.core.db import Base


class JobLog(Base):
    """Job execution logs"""
    __tablename__ = "job_logs"

    id = Column(String, primary_key=True)  # log_xxx
    job_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    stage = Column(String, nullable=False)  # article_parse, scene_generate, etc.
    level = Column(String, nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)  # JSON string for additional data
    duration_ms = Column(Integer, nullable=True)  # Stage duration in milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<JobLog {self.id} job={self.job_id} stage={self.stage} level={self.level}>"

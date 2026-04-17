"""input: 依赖 SQLAlchemy Base 和 AI 日志字段设计。
output: 向外提供 AILog 数据模型。
pos: 位于模型层，负责持久化 AI 调用记录。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

"""
AI Log model for storing AI interactions in database
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, Float
from sqlalchemy.sql import func
from app.core.db import Base


class AILog(Base):
    """AI interaction logs"""
    __tablename__ = "ai_logs"

    id = Column(String, primary_key=True)
    job_id = Column(String, index=True, nullable=True)
    project_id = Column(String, index=True, nullable=True)

    # AI interaction details
    operation = Column(String, nullable=False)  # e.g., "scene_generation", "article_parsing"
    model = Column(String, nullable=False)  # e.g., "gpt-4", "claude-3"

    # Input/Output
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)

    # Metadata
    tokens_input = Column(Integer, nullable=True)
    tokens_output = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    # Status
    status = Column(String, default="success")  # success, error
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<AILog {self.id} - {self.operation}>"

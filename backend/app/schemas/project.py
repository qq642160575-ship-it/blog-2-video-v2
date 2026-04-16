from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    source_type: str = Field(..., pattern="^(text|markdown)$")
    content: str = Field(..., min_length=1)


class ProjectResponse(BaseModel):
    id: str
    title: str
    source_type: str
    char_count: int
    status: str
    latest_job_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArticleStats(BaseModel):
    char_count: int
    estimated_reading_sec: int

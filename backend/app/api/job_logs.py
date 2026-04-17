"""input: 依赖 FastAPI、数据库会话和 JobLogService。
output: 向外提供任务日志查询 HTTP 接口。
pos: 位于 API 层，负责任务日志查询。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

"""
Job Logs API - Endpoints for retrieving job execution logs
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.db import get_db
from app.services.job_log_service import JobLogService
from app.models.job_log import JobLog

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobLogResponse(BaseModel):
    id: str
    job_id: str
    project_id: str
    stage: str
    level: str
    message: str
    details: Optional[str]
    duration_ms: Optional[int]
    created_at: str

    class Config:
        from_attributes = True


@router.get("/{job_id}/logs", response_model=List[JobLogResponse])
def get_job_logs(
    job_id: str,
    level: Optional[str] = Query(None, description="Filter by log level (INFO, WARNING, ERROR)"),
    db: Session = Depends(get_db)
):
    """Get all logs for a specific job"""
    log_service = JobLogService(db)
    logs = log_service.get_job_logs(job_id, level=level)

    return [
        JobLogResponse(
            id=log.id,
            job_id=log.job_id,
            project_id=log.project_id,
            stage=log.stage,
            level=log.level,
            message=log.message,
            details=log.details,
            duration_ms=log.duration_ms,
            created_at=log.created_at.isoformat() if log.created_at else None
        )
        for log in logs
    ]


@router.get("/{job_id}/logs/errors", response_model=List[JobLogResponse])
def get_job_errors(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Get only error logs for a specific job"""
    log_service = JobLogService(db)
    logs = log_service.get_job_logs(job_id, level="ERROR")

    return [
        JobLogResponse(
            id=log.id,
            job_id=log.job_id,
            project_id=log.project_id,
            stage=log.stage,
            level=log.level,
            message=log.message,
            details=log.details,
            duration_ms=log.duration_ms,
            created_at=log.created_at.isoformat() if log.created_at else None
        )
        for log in logs
    ]

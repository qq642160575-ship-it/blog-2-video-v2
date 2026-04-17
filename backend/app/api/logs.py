"""input: 依赖 FastAPI、数据库会话和 AILog 模型。
output: 向外提供 AI 日志查询与统计接口。
pos: 位于 API 层，负责 AI 日志可观测性。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

"""
API endpoints for viewing logs
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.db import get_db
from app.models.ai_log import AILog
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/logs", tags=["logs"])


class AILogResponse(BaseModel):
    id: str
    job_id: Optional[str]
    project_id: Optional[str]
    operation: str
    model: str
    prompt: str
    response: str
    tokens_input: Optional[int]
    tokens_output: Optional[int]
    cost: Optional[float]
    duration_ms: Optional[int]
    status: str
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/ai", response_model=List[AILogResponse])
def get_ai_logs(
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    operation: Optional[str] = Query(None, description="Filter by operation type"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of logs"),
    db: Session = Depends(get_db)
):
    """
    Get AI interaction logs

    Args:
        job_id: Filter by job ID
        project_id: Filter by project ID
        operation: Filter by operation (e.g., 'article_parsing', 'scene_generation')
        limit: Maximum number of logs to return
        db: Database session

    Returns:
        List of AI logs
    """
    query = db.query(AILog)

    if job_id:
        query = query.filter(AILog.job_id == job_id)
    if project_id:
        query = query.filter(AILog.project_id == project_id)
    if operation:
        query = query.filter(AILog.operation == operation)

    logs = query.order_by(AILog.created_at.desc()).limit(limit).all()

    return logs


@router.get("/ai/{log_id}", response_model=AILogResponse)
def get_ai_log(log_id: str, db: Session = Depends(get_db)):
    """
    Get a specific AI log by ID

    Args:
        log_id: AI log ID
        db: Database session

    Returns:
        AI log details
    """
    log = db.query(AILog).filter(AILog.id == log_id).first()

    if not log:
        raise HTTPException(status_code=404, detail="AI log not found")

    return log


@router.get("/ai/stats/summary")
def get_ai_stats(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_db)
):
    """
    Get AI usage statistics

    Args:
        project_id: Optional project ID filter
        db: Database session

    Returns:
        Statistics summary
    """
    from sqlalchemy import func

    query = db.query(
        func.count(AILog.id).label("total_calls"),
        func.sum(AILog.tokens_input).label("total_input_tokens"),
        func.sum(AILog.tokens_output).label("total_output_tokens"),
        func.sum(AILog.cost).label("total_cost"),
        func.avg(AILog.duration_ms).label("avg_duration_ms")
    )

    if project_id:
        query = query.filter(AILog.project_id == project_id)

    stats = query.first()

    return {
        "total_calls": stats.total_calls or 0,
        "total_input_tokens": stats.total_input_tokens or 0,
        "total_output_tokens": stats.total_output_tokens or 0,
        "total_cost": float(stats.total_cost or 0),
        "avg_duration_ms": float(stats.avg_duration_ms or 0)
    }

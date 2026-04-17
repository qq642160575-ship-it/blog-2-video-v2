"""input: 依赖数据库会话、JobLog 模型和日志配置。
output: 向外提供任务阶段日志写入与查询能力。
pos: 位于 service 层，负责任务日志中枢。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

"""
Job Log Service - Manages job execution logs
"""
import json
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.job_log import JobLog
from app.core.logging_config import get_logger


class JobLogService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger("worker")

    def log_info(
        self,
        job_id: str,
        project_id: str,
        stage: str,
        message: str,
        details: Optional[dict] = None,
        duration_ms: Optional[int] = None
    ) -> JobLog:
        """Log an info message"""
        return self._create_log(
            job_id=job_id,
            project_id=project_id,
            stage=stage,
            level="INFO",
            message=message,
            details=details,
            duration_ms=duration_ms
        )

    def log_warning(
        self,
        job_id: str,
        project_id: str,
        stage: str,
        message: str,
        details: Optional[dict] = None
    ) -> JobLog:
        """Log a warning message"""
        return self._create_log(
            job_id=job_id,
            project_id=project_id,
            stage=stage,
            level="WARNING",
            message=message,
            details=details
        )

    def log_error(
        self,
        job_id: str,
        project_id: str,
        stage: str,
        message: str,
        details: Optional[dict] = None,
        error_code: Optional[str] = None
    ) -> JobLog:
        """Log an error message"""
        if details is None:
            details = {}
        if error_code:
            details["error_code"] = error_code

        return self._create_log(
            job_id=job_id,
            project_id=project_id,
            stage=stage,
            level="ERROR",
            message=message,
            details=details
        )

    def _create_log(
        self,
        job_id: str,
        project_id: str,
        stage: str,
        level: str,
        message: str,
        details: Optional[dict] = None,
        duration_ms: Optional[int] = None
    ) -> JobLog:
        """Create a log entry"""
        log_id = f"log_{uuid.uuid4().hex[:12]}"
        details_json = json.dumps(details, ensure_ascii=False) if details else None

        log = JobLog(
            id=log_id,
            job_id=job_id,
            project_id=project_id,
            stage=stage,
            level=level,
            message=message,
            details=details_json,
            duration_ms=duration_ms
        )

        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        self.logger.log(
            self._to_logging_level(level),
            f"[job_id={job_id}] [project_id={project_id}] [stage={stage}] {message}"
            + (f" | details={details_json}" if details_json else "")
            + (f" | duration_ms={duration_ms}" if duration_ms is not None else "")
        )

        return log

    def _to_logging_level(self, level: str) -> int:
        mapping = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50,
        }
        return mapping.get(level.upper(), 20)

    def get_job_logs(
        self,
        job_id: str,
        level: Optional[str] = None
    ) -> List[JobLog]:
        """Get all logs for a job"""
        query = self.db.query(JobLog).filter(JobLog.job_id == job_id)

        if level:
            query = query.filter(JobLog.level == level)

        return query.order_by(JobLog.created_at).all()

    def get_project_logs(
        self,
        project_id: str,
        level: Optional[str] = None,
        limit: int = 100
    ) -> List[JobLog]:
        """Get logs for a project"""
        query = self.db.query(JobLog).filter(JobLog.project_id == project_id)

        if level:
            query = query.filter(JobLog.level == level)

        return query.order_by(JobLog.created_at.desc()).limit(limit).all()

    def get_stage_logs(
        self,
        job_id: str,
        stage: str
    ) -> List[JobLog]:
        """Get logs for a specific stage"""
        return (
            self.db.query(JobLog)
            .filter(JobLog.job_id == job_id, JobLog.stage == stage)
            .order_by(JobLog.created_at)
            .all()
        )

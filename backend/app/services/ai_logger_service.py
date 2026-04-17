"""input: 依赖数据库会话、AILog 模型和日志配置。
output: 向外提供 AI 调用日志写入与查询服务。
pos: 位于 service 层，负责 AI 可观测性。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

"""
AI Logger Service - Logs AI interactions to both file and database
"""
import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.core.logging_config import get_logger
from app.models.ai_log import AILog


class AILoggerService:
    """Service for logging AI interactions"""

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.logger = get_logger("ai")

    def log_ai_call(
        self,
        operation: str,
        model: str,
        prompt: str,
        response: str,
        job_id: Optional[str] = None,
        project_id: Optional[str] = None,
        tokens_input: Optional[int] = None,
        tokens_output: Optional[int] = None,
        cost: Optional[float] = None,
        duration_ms: Optional[int] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> str:
        """
        Log an AI interaction to both file and database

        Args:
            operation: Type of operation (e.g., "scene_generation")
            model: AI model used
            prompt: Input prompt
            response: AI response
            job_id: Associated job ID
            project_id: Associated project ID
            tokens_input: Input token count
            tokens_output: Output token count
            cost: API call cost
            duration_ms: Duration in milliseconds
            status: Status (success/error)
            error_message: Error message if failed

        Returns:
            Log ID
        """
        log_id = f"ailog_{uuid.uuid4().hex[:12]}"
        safe_response = response or ""

        self.logger.info(
            f"AI Call [{log_id}] - Operation: {operation}, Model: {model}, "
            f"Job: {job_id}, Project: {project_id}, Status: {status}, "
            f"Duration: {duration_ms}ms"
        )
        self.logger.info(f"Prompt [{log_id}]: {prompt}")
        self.logger.info(f"Response [{log_id}]: {safe_response}")

        if error_message:
            self.logger.error(f"Error [{log_id}]: {error_message}")

        db = self.db or SessionLocal()
        should_close = self.db is None

        try:
            ai_log = AILog(
                id=log_id,
                job_id=job_id,
                project_id=project_id,
                operation=operation,
                model=model,
                prompt=prompt,
                response=safe_response,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                cost=cost,
                duration_ms=duration_ms,
                status=status,
                error_message=error_message
            )
            db.add(ai_log)
            db.commit()
        except Exception as e:
            self.logger.error(f"Failed to save AI log to database: {str(e)}")
            db.rollback()
        finally:
            if should_close:
                db.close()

        return log_id

    def log_llm_call(
        self,
        operation: str,
        messages: list,
        response_text: str,
        model: str = "unknown",
        job_id: Optional[str] = None,
        project_id: Optional[str] = None,
        usage: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None
    ) -> str:
        """
        Convenience method for logging LLM calls

        Args:
            operation: Operation name
            messages: List of message dicts
            response_text: Response text
            model: Model name
            job_id: Job ID
            project_id: Project ID
            usage: Usage dict with token counts
            duration_ms: Duration in milliseconds

        Returns:
            Log ID
        """
        # Format prompt from messages
        prompt = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')[:500]}"
            for msg in messages
        ])

        # Extract token counts from usage
        tokens_input = None
        tokens_output = None
        if usage:
            tokens_input = usage.get("prompt_tokens") or usage.get("input_tokens")
            tokens_output = usage.get("completion_tokens") or usage.get("output_tokens")

        return self.log_ai_call(
            operation=operation,
            model=model,
            prompt=prompt,
            response=response_text,
            job_id=job_id,
            project_id=project_id,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            duration_ms=duration_ms
        )

    def get_ai_logs(
        self,
        job_id: Optional[str] = None,
        project_id: Optional[str] = None,
        operation: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        Retrieve AI logs from database

        Args:
            job_id: Filter by job ID
            project_id: Filter by project ID
            operation: Filter by operation
            limit: Max number of logs to return

        Returns:
            List of AILog objects
        """
        if not self.db:
            return []

        query = self.db.query(AILog)

        if job_id:
            query = query.filter(AILog.job_id == job_id)
        if project_id:
            query = query.filter(AILog.project_id == project_id)
        if operation:
            query = query.filter(AILog.operation == operation)

        return query.order_by(AILog.created_at.desc()).limit(limit).all()


def create_ai_logger(db: Session = None) -> AILoggerService:
    """Factory function to create AI logger"""
    return AILoggerService(db)

"""input: 依赖任务模型、项目模型、队列与缓存能力。
output: 向外提供任务创建、状态推进和结果更新能力。
pos: 位于 service 层，负责任务生命周期编排。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.generation_job import GenerationJob
from app.services.task_queue import TaskQueue
from app.services.concurrency_manager import ConcurrencyManager
from app.services.cache_service import CacheService, CacheKeys, CacheInvalidator
from app.core.errors import ErrorCode
from app.core.logging_config import get_logger
from typing import Optional

logger = get_logger("worker")


class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.task_queue = TaskQueue()
        self.concurrency_manager = ConcurrencyManager()
        self.cache = CacheService()
        self.cache_invalidator = CacheInvalidator()

    def create_generation_job(self, project_id: str, job_type: str = "generate") -> GenerationJob:
        """Create a new generation job and push to queue"""
        logger.info(f"Creating generation job for project {project_id}, type: {job_type}")

        # Check if project already has a running job
        if self.concurrency_manager.is_project_locked(project_id):
            existing_job_id = self.concurrency_manager.get_project_lock_owner(project_id)
            logger.warning(f"Project {project_id} already has running job: {existing_job_id}")
            raise ValueError(
                f"Project {project_id} already has a running job: {existing_job_id}. "
                f"Error code: {ErrorCode.JOB_ALREADY_RUNNING}"
            )

        # Generate job ID
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        logger.debug(f"Generated job ID: {job_id}")

        # Acquire project lock
        if not self.concurrency_manager.acquire_project_lock(project_id, job_id):
            logger.error(f"Failed to acquire lock for project {project_id}")
            raise ValueError(
                f"Failed to acquire lock for project {project_id}. "
                f"Error code: {ErrorCode.JOB_ALREADY_RUNNING}"
            )

        try:
            # Create job record
            job = GenerationJob(
                id=job_id,
                project_id=project_id,
                job_type=job_type,
                status="queued",
                stage=None,
                progress=0.0
            )

            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
            logger.info(f"Job {job_id} created and committed to database")

            # Push to queue
            self.task_queue.push_generation_task(job_id, project_id, job_type)
            logger.info(f"Job {job_id} pushed to task queue")

            return job
        except Exception as e:
            logger.error(f"Failed to create job for project {project_id}: {str(e)}")
            # Release lock if job creation failed
            self.concurrency_manager.release_project_lock(project_id, job_id)
            raise e

    def get_job(self, job_id: str) -> Optional[GenerationJob]:
        """Get job by ID"""
        # Try cache first for job status
        cache_key = CacheKeys.job_status(job_id)
        cached_status = self.cache.get(cache_key)

        if cached_status:
            # For status queries, we can return cached data
            # But for full job data, always query DB to ensure freshness
            pass

        return self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()

    def cancel_job(self, job_id: str) -> GenerationJob:
        """Cancel a running or queued job"""
        logger.info(f"Cancelling job {job_id}")
        job = self.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            raise ValueError(f"Job {job_id} not found")

        if job.status in ["completed", "failed", "cancelled"]:
            logger.warning(f"Job {job_id} is already {job.status}, cannot cancel")
            raise ValueError(f"Job {job_id} is already {job.status}")

        # Update job status
        job.status = "cancelled"
        job.finished_at = datetime.utcnow()
        job.error_message = "Job cancelled by user"

        self.db.commit()
        self.db.refresh(job)
        logger.info(f"Job {job_id} cancelled successfully")

        # Invalidate cache
        self.cache_invalidator.invalidate_job(job_id, job.project_id)

        # Release project lock
        self.concurrency_manager.release_project_lock(job.project_id, job_id)
        logger.debug(f"Released project lock for {job.project_id}")

        # Release render slot if it was acquired
        self.concurrency_manager.release_render_slot(job_id)

        return job

    def update_job_status(
        self,
        job_id: str,
        status: str,
        stage: Optional[str] = None,
        progress: Optional[float] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> GenerationJob:
        """Update job status"""
        logger.info(f"Updating job {job_id} status to {status}, stage: {stage}, progress: {progress}")
        job = self.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            raise ValueError(f"Job {job_id} not found")

        job.status = status
        if stage is not None:
            job.stage = stage
        if progress is not None:
            job.progress = progress
        if error_code is not None:
            job.error_code = error_code
            logger.error(f"Job {job_id} error: {error_code} - {error_message}")
        if error_message is not None:
            job.error_message = error_message

        if status == "running" and not job.started_at:
            job.started_at = datetime.utcnow()
            logger.info(f"Job {job_id} started at {job.started_at}")
        elif status in ["completed", "failed", "cancelled"]:
            job.finished_at = datetime.utcnow()
            logger.info(f"Job {job_id} finished with status {status} at {job.finished_at}")
            # Release project lock when job finishes
            self.concurrency_manager.release_project_lock(job.project_id, job_id)
            # Release render slot if it was acquired
            self.concurrency_manager.release_render_slot(job_id)
            # Invalidate cache when job finishes
            self.cache_invalidator.invalidate_job(job_id, job.project_id)
            self.cache_invalidator.invalidate_project(job.project_id)

        self.db.commit()
        self.db.refresh(job)

        # Update job status cache
        self.cache.set(CacheKeys.job_status(job_id), {
            "status": job.status,
            "stage": job.stage,
            "progress": float(job.progress) if job.progress else 0.0
        }, ttl=self.cache.SHORT_TTL)

        return job

    def update_job_result(
        self,
        job_id: str,
        video_url: Optional[str] = None,
        subtitle_url: Optional[str] = None,
        scene_json_url: Optional[str] = None
    ) -> GenerationJob:
        """Update job result URLs"""
        logger.info(f"Updating job {job_id} results - video: {video_url}, subtitle: {subtitle_url}, scene_json: {scene_json_url}")
        job = self.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            raise ValueError(f"Job {job_id} not found")

        if video_url:
            job.result_video_url = video_url
        if subtitle_url:
            job.result_subtitle_url = subtitle_url
        if scene_json_url:
            job.result_scene_json_url = scene_json_url

        self.db.commit()
        self.db.refresh(job)
        logger.debug(f"Job {job_id} results updated successfully")
        return job

    def get_all_jobs(self, skip: int = 0, limit: int = 100) -> list[GenerationJob]:
        """Get all jobs with pagination"""
        return self.db.query(GenerationJob).order_by(GenerationJob.created_at.desc()).offset(skip).limit(limit).all()

    def get_stats(self) -> dict:
        """Get job statistics"""
        from sqlalchemy import func

        total_jobs = self.db.query(func.count(GenerationJob.id)).scalar()
        running_jobs = self.db.query(func.count(GenerationJob.id)).filter(GenerationJob.status == "running").scalar()
        completed_jobs = self.db.query(func.count(GenerationJob.id)).filter(GenerationJob.status == "completed").scalar()
        failed_jobs = self.db.query(func.count(GenerationJob.id)).filter(GenerationJob.status == "failed").scalar()

        stats = {
            "total_jobs": total_jobs or 0,
            "running_jobs": running_jobs or 0,
            "completed_jobs": completed_jobs or 0,
            "failed_jobs": failed_jobs or 0
        }
        logger.debug(f"Job stats: {stats}")
        return stats

    def get_concurrency_stats(self) -> dict:
        """Get concurrency statistics"""
        stats = {
            "max_concurrent_renders": self.concurrency_manager.max_concurrent_renders,
            "current_concurrent_renders": self.concurrency_manager.get_concurrent_render_count(),
            "running_render_jobs": self.concurrency_manager.get_running_renders(),
            "available_slots": self.concurrency_manager.max_concurrent_renders -
                             self.concurrency_manager.get_concurrent_render_count()
        }
        logger.debug(f"Concurrency stats: {stats}")
        return stats

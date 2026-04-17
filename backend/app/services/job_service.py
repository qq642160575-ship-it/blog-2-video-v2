import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.generation_job import GenerationJob
from app.services.task_queue import TaskQueue
from app.services.concurrency_manager import ConcurrencyManager
from app.services.cache_service import CacheService, CacheKeys, CacheInvalidator
from app.core.errors import ErrorCode
from typing import Optional


class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.task_queue = TaskQueue()
        self.concurrency_manager = ConcurrencyManager()
        self.cache = CacheService()
        self.cache_invalidator = CacheInvalidator()

    def create_generation_job(self, project_id: str, job_type: str = "generate") -> GenerationJob:
        """Create a new generation job and push to queue"""

        # Check if project already has a running job
        if self.concurrency_manager.is_project_locked(project_id):
            existing_job_id = self.concurrency_manager.get_project_lock_owner(project_id)
            raise ValueError(
                f"Project {project_id} already has a running job: {existing_job_id}. "
                f"Error code: {ErrorCode.JOB_ALREADY_RUNNING}"
            )

        # Generate job ID
        job_id = f"job_{uuid.uuid4().hex[:8]}"

        # Acquire project lock
        if not self.concurrency_manager.acquire_project_lock(project_id, job_id):
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

            # Push to queue
            self.task_queue.push_generation_task(job_id, project_id, job_type)

            return job
        except Exception as e:
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
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        if job.status in ["completed", "failed", "cancelled"]:
            raise ValueError(f"Job {job_id} is already {job.status}")

        # Update job status
        job.status = "cancelled"
        job.finished_at = datetime.utcnow()
        job.error_message = "Job cancelled by user"

        self.db.commit()
        self.db.refresh(job)

        # Invalidate cache
        self.cache_invalidator.invalidate_job(job_id, job.project_id)

        # Release project lock
        self.concurrency_manager.release_project_lock(job.project_id, job_id)

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
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = status
        if stage is not None:
            job.stage = stage
        if progress is not None:
            job.progress = progress
        if error_code is not None:
            job.error_code = error_code
        if error_message is not None:
            job.error_message = error_message

        if status == "running" and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status in ["completed", "failed", "cancelled"]:
            job.finished_at = datetime.utcnow()
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
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        if video_url:
            job.result_video_url = video_url
        if subtitle_url:
            job.result_subtitle_url = subtitle_url
        if scene_json_url:
            job.result_scene_json_url = scene_json_url

        self.db.commit()
        self.db.refresh(job)
        return job

    def get_concurrency_stats(self) -> dict:
        """Get concurrency statistics"""
        return {
            "max_concurrent_renders": self.concurrency_manager.max_concurrent_renders,
            "current_concurrent_renders": self.concurrency_manager.get_concurrent_render_count(),
            "running_render_jobs": self.concurrency_manager.get_running_renders(),
            "available_slots": self.concurrency_manager.max_concurrent_renders -
                             self.concurrency_manager.get_concurrent_render_count()
        }

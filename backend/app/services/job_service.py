import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.generation_job import GenerationJob
from app.services.task_queue import TaskQueue
from typing import Optional


class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.task_queue = TaskQueue()

    def create_generation_job(self, project_id: str, job_type: str = "generate") -> GenerationJob:
        """Create a new generation job and push to queue"""
        # Generate job ID
        job_id = f"job_{uuid.uuid4().hex[:8]}"

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

    def get_job(self, job_id: str) -> Optional[GenerationJob]:
        """Get job by ID"""
        return self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()

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

        self.db.commit()
        self.db.refresh(job)
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

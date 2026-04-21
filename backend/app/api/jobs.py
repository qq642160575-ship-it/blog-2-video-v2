"""input: 依赖 FastAPI、数据库会话和 job/project 服务。
output: 向外提供任务创建、状态查询和控制接口。
pos: 位于 API 层，负责任务生命周期接口。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.job_service import JobService
from app.services.project_service import ProjectService
from typing import Optional
from pydantic import BaseModel

router = APIRouter(tags=["jobs"])


class JobStatusUpdate(BaseModel):
    status: str
    stage: Optional[str] = None
    progress: Optional[float] = None
    result_data: Optional[dict] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


@router.get("/jobs")
def get_all_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all jobs with pagination
    """
    try:
        job_service = JobService(db)
        jobs = job_service.get_all_jobs(skip=skip, limit=limit)

        return [
            {
                "id": job.id,
                "project_id": job.project_id,
                "job_type": job.job_type,
                "status": job.status,
                "stage": job.stage,
                "progress": float(job.progress) if job.progress else 0.0,
                "created_at": job.created_at.isoformat(),
                "updated_at": job.updated_at.isoformat() if job.updated_at else None,
                "error_code": job.error_code,
                "error_message": job.error_message
            }
            for job in jobs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/projects/{project_id}/jobs/generate")
def create_generation_job(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Create a generation job for a project
    """
    try:
        # Verify project exists
        project_service = ProjectService(db)
        project = project_service.get_project(project_id)

        # Create job
        job_service = JobService(db)
        job = job_service.create_generation_job(project_id, job_type="generate")

        # Update project's latest_job_id
        project.latest_job_id = job.id
        db.commit()

        return {
            "job_id": job.id,
            "status": job.status
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/projects/{project_id}/jobs/rerender")
def create_rerender_job(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Create a rerender job for a project
    """
    try:
        # Verify project exists
        project_service = ProjectService(db)
        project = project_service.get_project(project_id)

        # Create job
        job_service = JobService(db)
        job = job_service.create_generation_job(project_id, job_type="rerender")

        # Update project's latest_job_id
        project.latest_job_id = job.id
        db.commit()

        return {
            "job_id": job.id,
            "status": job.status
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/jobs/{job_id}")
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get job status by ID
    """
    try:
        job_service = JobService(db)
        job = job_service.get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        return {
            "job_id": job.id,
            "status": job.status,
            "stage": job.stage,
            "progress": float(job.progress) if job.progress else 0.0,
            "error": {
                "code": job.error_code,
                "message": job.error_message
            } if job.error_code else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.patch("/jobs/{job_id}/status")
def update_job_status(
    job_id: str,
    update: JobStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update job status (used by workers)
    """
    try:
        job_service = JobService(db)

        # Update job status
        job_service.update_job_status(
            job_id=job_id,
            status=update.status,
            stage=update.stage,
            progress=update.progress,
            error_code=update.error_code,
            error_message=update.error_message
        )

        # Update result data if provided
        if update.result_data:
            video_url = update.result_data.get("video_url")
            subtitle_url = update.result_data.get("subtitle_url")
            scene_json_url = update.result_data.get("scene_json_url")
            job_service.update_job_result(
                job_id=job_id,
                video_url=video_url,
                subtitle_url=subtitle_url,
                scene_json_url=scene_json_url
            )

        # Update project status if job is completed
        if update.status == "completed":
            job = job_service.get_job(job_id)
            project_service = ProjectService(db)
            project = project_service.get_project(job.project_id)
            project.status = "completed"
            db.commit()

        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/jobs/{job_id}/cancel")
def cancel_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Cancel a running or queued job
    """
    try:
        job_service = JobService(db)
        job = job_service.cancel_job(job_id)

        return {
            "job_id": job.id,
            "status": job.status,
            "message": "Job cancelled successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/concurrency/stats")
def get_concurrency_stats(
    db: Session = Depends(get_db)
):
    """
    Get concurrency statistics
    """
    try:
        job_service = JobService(db)
        stats = job_service.get_concurrency_stats()

        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

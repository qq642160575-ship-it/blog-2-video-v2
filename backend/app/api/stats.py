"""input: 依赖 FastAPI、数据库会话和 ProjectService、JobService。
output: 向外提供统计数据接口。
pos: 位于 API 层，负责统计数据接口。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.project_service import ProjectService
from app.services.job_service import JobService

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview")
def get_overview_stats(db: Session = Depends(get_db)):
    """
    Get overview statistics for admin dashboard
    """
    try:
        project_service = ProjectService(db)
        job_service = JobService(db)

        # Get project stats
        project_stats = project_service.get_stats()

        # Get job stats
        job_stats = job_service.get_stats()

        # Combine stats
        overview_stats = {
            "totalProjects": project_stats["total_projects"],
            "totalJobs": job_stats["total_jobs"],
            "runningJobs": job_stats["running_jobs"],
            "completedJobs": job_stats["completed_jobs"],
            "failedJobs": job_stats["failed_jobs"]
        }

        return overview_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

"""input: 依赖 FastAPI、数据库会话和 ProjectService。
output: 向外提供项目创建、查询与结果接口。
pos: 位于 API 层，负责项目入口接口。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ArticleStats
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list)
def get_all_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all projects with pagination
    """
    try:
        service = ProjectService(db)
        projects = service.get_all_projects(skip=skip, limit=limit)

        return [
            {
                "id": project.id,
                "title": project.title,
                "status": project.status,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat() if project.updated_at else None,
                "article_content": project.article_content[:100] + "..." if project.article_content and len(project.article_content) > 100 else project.article_content
            }
            for project in projects
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=dict)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new project
    """
    try:
        service = ProjectService(db)
        project, stats = service.create_project(project_data)

        return {
            "project_id": project.id,
            "status": project.status,
            "article_stats": {
                "char_count": stats.char_count,
                "estimated_reading_sec": stats.estimated_reading_sec
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get project by ID
    """
    try:
        service = ProjectService(db)
        project = service.get_project(project_id)
        return project
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{project_id}/result")
def get_project_result(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get project result (video URL)
    """
    try:
        service = ProjectService(db)
        project = service.get_project(project_id)
        
        if not project.latest_job_id:
            raise HTTPException(status_code=404, detail="No job found for this project")
        
        # Get latest job
        from app.services.job_service import JobService
        job_service = JobService(db)
        job = job_service.get_job(project.latest_job_id)
        
        if job.status != "completed":
            return {
                "project_id": project_id,
                "status": job.status,
                "stage": job.stage,
                "progress": float(job.progress) if job.progress else 0.0,
                "video_url": None
            }
        
        # Extract video URL from result fields
        video_url = job.result_video_url

        return {
            "project_id": project_id,
            "status": job.status,
            "video_url": video_url
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

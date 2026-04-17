"""input: 依赖 FastAPI、数据库会话和 asset 相关服务。
output: 向外提供素材相关 HTTP 接口。
pos: 位于 API 层，负责素材接口编排。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.asset_service import AssetService
from typing import Optional
from pydantic import BaseModel

router = APIRouter(tags=["assets"])


class AssetCreate(BaseModel):
    project_id: str
    job_id: str
    asset_type: str
    file_path: str
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    metadata: Optional[dict] = None


class AssetUpdate(BaseModel):
    file_url: Optional[str] = None


@router.post("/assets")
def create_asset(
    asset_data: AssetCreate,
    db: Session = Depends(get_db)
):
    """Create a new asset record"""
    try:
        asset_service = AssetService(db)
        asset = asset_service.create_asset(
            project_id=asset_data.project_id,
            job_id=asset_data.job_id,
            asset_type=asset_data.asset_type,
            file_path=asset_data.file_path,
            file_url=asset_data.file_url,
            file_size=asset_data.file_size,
            mime_type=asset_data.mime_type,
            metadata=asset_data.metadata
        )

        return {
            "asset_id": asset.id,
            "asset_type": asset.asset_type,
            "file_path": asset.file_path,
            "file_url": asset.file_url,
            "file_size": asset.file_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/assets/{asset_id}")
def get_asset(
    asset_id: str,
    db: Session = Depends(get_db)
):
    """Get asset by ID"""
    try:
        asset_service = AssetService(db)
        asset = asset_service.get_asset(asset_id)

        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")

        return {
            "asset_id": asset.id,
            "project_id": asset.project_id,
            "job_id": asset.job_id,
            "asset_type": asset.asset_type,
            "file_path": asset.file_path,
            "file_url": asset.file_url,
            "file_size": asset.file_size,
            "mime_type": asset.mime_type,
            "metadata": asset.meta_data,
            "is_deleted": asset.is_deleted,
            "created_at": asset.created_at.isoformat() if asset.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/projects/{project_id}/assets")
def get_project_assets(
    project_id: str,
    asset_type: Optional[str] = Query(None),
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get all assets for a project"""
    try:
        asset_service = AssetService(db)
        assets = asset_service.get_project_assets(
            project_id=project_id,
            asset_type=asset_type,
            include_deleted=include_deleted
        )

        return {
            "project_id": project_id,
            "total": len(assets),
            "assets": [
                {
                    "asset_id": asset.id,
                    "job_id": asset.job_id,
                    "asset_type": asset.asset_type,
                    "file_path": asset.file_path,
                    "file_url": asset.file_url,
                    "file_size": asset.file_size,
                    "mime_type": asset.mime_type,
                    "is_deleted": asset.is_deleted,
                    "created_at": asset.created_at.isoformat() if asset.created_at else None
                }
                for asset in assets
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/jobs/{job_id}/assets")
def get_job_assets(
    job_id: str,
    asset_type: Optional[str] = Query(None),
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get all assets for a job"""
    try:
        asset_service = AssetService(db)
        assets = asset_service.get_job_assets(
            job_id=job_id,
            asset_type=asset_type,
            include_deleted=include_deleted
        )

        return {
            "job_id": job_id,
            "total": len(assets),
            "assets": [
                {
                    "asset_id": asset.id,
                    "project_id": asset.project_id,
                    "asset_type": asset.asset_type,
                    "file_path": asset.file_path,
                    "file_url": asset.file_url,
                    "file_size": asset.file_size,
                    "mime_type": asset.mime_type,
                    "is_deleted": asset.is_deleted,
                    "created_at": asset.created_at.isoformat() if asset.created_at else None
                }
                for asset in assets
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/assets/{asset_id}")
def update_asset(
    asset_id: str,
    update_data: AssetUpdate,
    db: Session = Depends(get_db)
):
    """Update asset information"""
    try:
        asset_service = AssetService(db)

        if update_data.file_url:
            asset = asset_service.update_asset_url(asset_id, update_data.file_url)
        else:
            asset = asset_service.get_asset(asset_id)

        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")

        return {
            "asset_id": asset.id,
            "file_url": asset.file_url,
            "message": "Asset updated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/assets/{asset_id}")
def delete_asset(
    asset_id: str,
    hard_delete: bool = Query(False),
    delete_file: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Delete an asset (soft delete by default)"""
    try:
        asset_service = AssetService(db)

        if hard_delete:
            success = asset_service.hard_delete_asset(asset_id, delete_file=delete_file)
            if not success:
                raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
            return {"message": "Asset deleted permanently"}
        else:
            asset = asset_service.soft_delete_asset(asset_id)
            return {
                "asset_id": asset.id,
                "is_deleted": asset.is_deleted,
                "message": "Asset soft deleted successfully"
            }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/jobs/{job_id}/assets")
def cleanup_job_assets(
    job_id: str,
    delete_files: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Clean up all assets for a job"""
    try:
        asset_service = AssetService(db)
        count = asset_service.cleanup_job_assets(job_id, delete_files=delete_files)

        return {
            "job_id": job_id,
            "deleted_count": count,
            "message": f"Cleaned up {count} assets"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/projects/{project_id}/assets")
def cleanup_project_assets(
    project_id: str,
    delete_files: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Clean up all assets for a project"""
    try:
        asset_service = AssetService(db)
        count = asset_service.cleanup_project_assets(project_id, delete_files=delete_files)

        return {
            "project_id": project_id,
            "deleted_count": count,
            "message": f"Cleaned up {count} assets"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/assets/storage/stats")
def get_storage_stats(db: Session = Depends(get_db)):
    """Get storage statistics"""
    try:
        asset_service = AssetService(db)
        stats = asset_service.get_storage_stats()

        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

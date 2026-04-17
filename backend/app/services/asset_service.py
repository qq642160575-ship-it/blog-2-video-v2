"""
Asset Service - Manages asset lifecycle and storage
"""
import uuid
import os
import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.asset import Asset
from app.services.cache_service import CacheService, CacheKeys, CacheInvalidator


class AssetService:
    """Service for managing assets"""

    def __init__(self, db: Session):
        self.db = db
        self.cache = CacheService()
        self.cache_invalidator = CacheInvalidator()

    def create_asset(
        self,
        project_id: str,
        job_id: str,
        asset_type: str,
        file_path: str,
        file_url: Optional[str] = None,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Asset:
        """Create a new asset record"""
        asset_id = f"asset_{uuid.uuid4().hex[:8]}"

        # Calculate file size if not provided
        if file_size is None and os.path.exists(file_path):
            file_size = os.path.getsize(file_path)

        # Serialize metadata to JSON
        metadata_json = json.dumps(metadata) if metadata else None

        asset = Asset(
            id=asset_id,
            project_id=project_id,
            job_id=job_id,
            asset_type=asset_type,
            file_path=file_path,
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type,
            meta_data=metadata_json
        )

        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)

        # Invalidate asset cache
        self.cache_invalidator.invalidate_assets(project_id=project_id, job_id=job_id)

        return asset

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """Get asset by ID"""
        return self.db.query(Asset).filter(
            Asset.id == asset_id,
            Asset.is_deleted == False
        ).first()

    def get_project_assets(
        self,
        project_id: str,
        asset_type: Optional[str] = None,
        include_deleted: bool = False
    ) -> List[Asset]:
        """Get all assets for a project"""
        query = self.db.query(Asset).filter(Asset.project_id == project_id)

        if asset_type:
            query = query.filter(Asset.asset_type == asset_type)

        if not include_deleted:
            query = query.filter(Asset.is_deleted == False)

        return query.order_by(Asset.created_at.desc()).all()

    def get_job_assets(
        self,
        job_id: str,
        asset_type: Optional[str] = None,
        include_deleted: bool = False
    ) -> List[Asset]:
        """Get all assets for a job"""
        query = self.db.query(Asset).filter(Asset.job_id == job_id)

        if asset_type:
            query = query.filter(Asset.asset_type == asset_type)

        if not include_deleted:
            query = query.filter(Asset.is_deleted == False)

        return query.order_by(Asset.created_at.desc()).all()

    def update_asset_url(self, asset_id: str, file_url: str) -> Asset:
        """Update asset URL (after uploading to storage)"""
        asset = self.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        asset.file_url = file_url
        self.db.commit()
        self.db.refresh(asset)

        return asset

    def soft_delete_asset(self, asset_id: str) -> Asset:
        """Soft delete an asset"""
        asset = self.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        asset.is_deleted = True
        asset.deleted_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(asset)

        return asset

    def hard_delete_asset(self, asset_id: str, delete_file: bool = False) -> bool:
        """Hard delete an asset and optionally delete the file"""
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return False

        # Delete physical file if requested
        if delete_file and asset.file_path and os.path.exists(asset.file_path):
            try:
                os.remove(asset.file_path)
            except Exception as e:
                print(f"Failed to delete file {asset.file_path}: {e}")

        # Delete database record
        self.db.delete(asset)
        self.db.commit()

        return True

    def cleanup_job_assets(self, job_id: str, delete_files: bool = False) -> int:
        """Clean up all assets for a job"""
        assets = self.db.query(Asset).filter(Asset.job_id == job_id).all()
        count = 0

        for asset in assets:
            if delete_files and asset.file_path and os.path.exists(asset.file_path):
                try:
                    os.remove(asset.file_path)
                    count += 1
                except Exception as e:
                    print(f"Failed to delete file {asset.file_path}: {e}")

            self.db.delete(asset)

        self.db.commit()
        return count

    def cleanup_project_assets(self, project_id: str, delete_files: bool = False) -> int:
        """Clean up all assets for a project"""
        assets = self.db.query(Asset).filter(Asset.project_id == project_id).all()
        count = 0

        for asset in assets:
            if delete_files and asset.file_path and os.path.exists(asset.file_path):
                try:
                    os.remove(asset.file_path)
                    count += 1
                except Exception as e:
                    print(f"Failed to delete file {asset.file_path}: {e}")

            self.db.delete(asset)

        self.db.commit()
        return count

    def get_storage_stats(self) -> dict:
        """Get storage statistics"""
        # Try cache first
        cache_key = CacheKeys.storage_stats()
        cached_stats = self.cache.get(cache_key)

        if cached_stats:
            return cached_stats

        # Calculate stats from database
        total_assets = self.db.query(Asset).filter(Asset.is_deleted == False).count()
        total_size = self.db.query(func.sum(Asset.file_size)).filter(
            Asset.is_deleted == False
        ).scalar() or 0

        # Get counts by type
        asset_types = self.db.query(
            Asset.asset_type,
            func.count(Asset.id).label('count'),
            func.sum(Asset.file_size).label('size')
        ).filter(
            Asset.is_deleted == False
        ).group_by(Asset.asset_type).all()

        type_stats = {
            asset_type: {
                'count': count,
                'size': size or 0
            }
            for asset_type, count, size in asset_types
        }

        stats = {
            'total_assets': total_assets,
            'total_size': total_size,
            'by_type': type_stats
        }

        # Cache for 5 minutes
        self.cache.set(cache_key, stats, ttl=self.cache.DEFAULT_TTL)

        return stats

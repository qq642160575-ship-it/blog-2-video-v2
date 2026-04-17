"""
File Cleanup Utility - Manages cleanup of temporary and old files
"""
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.asset import Asset
from app.models.generation_job import GenerationJob


class FileCleanupService:
    """Service for cleaning up old and temporary files"""

    def __init__(self, db: Session):
        self.db = db

    def cleanup_failed_job_files(self, job_id: str) -> Dict[str, int]:
        """Clean up files from a failed job"""
        assets = self.db.query(Asset).filter(
            Asset.job_id == job_id,
            Asset.is_deleted == False
        ).all()

        deleted_count = 0
        deleted_size = 0

        for asset in assets:
            if asset.file_path and os.path.exists(asset.file_path):
                try:
                    file_size = os.path.getsize(asset.file_path)
                    os.remove(asset.file_path)
                    deleted_count += 1
                    deleted_size += file_size
                except Exception as e:
                    print(f"Failed to delete file {asset.file_path}: {e}")

            # Mark asset as deleted
            asset.is_deleted = True
            asset.deleted_at = datetime.utcnow()

        self.db.commit()

        return {
            "deleted_count": deleted_count,
            "deleted_size": deleted_size
        }

    def cleanup_old_jobs(self, days: int = 30, keep_completed: bool = True) -> Dict[str, int]:
        """Clean up files from old jobs"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Query old jobs
        query = self.db.query(GenerationJob).filter(
            GenerationJob.created_at < cutoff_date
        )

        if keep_completed:
            # Only clean up failed/cancelled jobs
            query = query.filter(
                GenerationJob.status.in_(["failed", "cancelled"])
            )

        old_jobs = query.all()

        total_deleted = 0
        total_size = 0

        for job in old_jobs:
            result = self.cleanup_failed_job_files(job.id)
            total_deleted += result["deleted_count"]
            total_size += result["deleted_size"]

        return {
            "jobs_cleaned": len(old_jobs),
            "files_deleted": total_deleted,
            "bytes_freed": total_size
        }

    def cleanup_orphaned_files(self, storage_dir: str) -> Dict[str, int]:
        """Clean up files that don't have corresponding asset records"""
        if not os.path.exists(storage_dir):
            return {"deleted_count": 0, "deleted_size": 0}

        deleted_count = 0
        deleted_size = 0

        # Get all file paths from assets
        asset_paths = set()
        assets = self.db.query(Asset).filter(Asset.is_deleted == False).all()
        for asset in assets:
            if asset.file_path:
                asset_paths.add(os.path.abspath(asset.file_path))

        # Walk through storage directory
        for root, dirs, files in os.walk(storage_dir):
            for file in files:
                file_path = os.path.abspath(os.path.join(root, file))

                # Skip if file is in asset records
                if file_path in asset_paths:
                    continue

                # Delete orphaned file
                try:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    deleted_count += 1
                    deleted_size += file_size
                    print(f"Deleted orphaned file: {file_path}")
                except Exception as e:
                    print(f"Failed to delete orphaned file {file_path}: {e}")

        return {
            "deleted_count": deleted_count,
            "deleted_size": deleted_size
        }

    def get_cleanup_candidates(self, days: int = 30) -> List[Dict]:
        """Get list of jobs that are candidates for cleanup"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        jobs = self.db.query(GenerationJob).filter(
            GenerationJob.created_at < cutoff_date,
            GenerationJob.status.in_(["failed", "cancelled"])
        ).all()

        candidates = []
        for job in jobs:
            # Count assets
            asset_count = self.db.query(Asset).filter(
                Asset.job_id == job.id,
                Asset.is_deleted == False
            ).count()

            # Calculate total size
            total_size = self.db.query(func.sum(Asset.file_size)).filter(
                Asset.job_id == job.id,
                Asset.is_deleted == False
            ).scalar() or 0

            candidates.append({
                "job_id": job.id,
                "project_id": job.project_id,
                "status": job.status,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "asset_count": asset_count,
                "total_size": total_size
            })

        return candidates

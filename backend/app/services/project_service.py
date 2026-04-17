"""input: 依赖项目仓储、缓存服务和项目 schema。
output: 向外提供项目创建与查询能力。
pos: 位于 service 层，负责项目核心业务。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

import uuid
from sqlalchemy.orm import Session
from app.models.project import Project
from app.repositories.project_repo import ProjectRepository
from app.schemas.project import ProjectCreate, ArticleStats
from app.services.cache_service import CacheService, CacheKeys, CacheInvalidator


class ProjectService:
    def __init__(self, db: Session):
        self.repo = ProjectRepository(db)
        self.cache = CacheService()
        self.cache_invalidator = CacheInvalidator()

    def create_project(self, project_data: ProjectCreate) -> tuple[Project, ArticleStats]:
        # Generate project ID
        project_id = f"proj_{uuid.uuid4().hex[:8]}"

        # Calculate character count
        char_count = len(project_data.content)

        # Validate content length
        if char_count < 500:
            raise ValueError("内容不足，建议补充论点（至少500字）")
        if char_count > 3000:
            raise ValueError("内容超限，建议缩短至3000字以内")

        # Create project
        project = Project(
            id=project_id,
            title=project_data.title,
            source_type=project_data.source_type,
            content=project_data.content,
            char_count=char_count,
            status="draft"
        )

        project = self.repo.create(project)

        # Cache the project
        self.cache.set(CacheKeys.project(project_id), {
            "id": project.id,
            "title": project.title,
            "status": project.status,
            "char_count": project.char_count,
            "source_type": project.source_type
        }, ttl=self.cache.LONG_TTL)

        # Invalidate project list cache
        self.cache.delete_pattern("projects:list:*")

        # Calculate stats
        estimated_reading_sec = int(char_count / 3)  # Rough estimate: 3 chars per second
        stats = ArticleStats(
            char_count=char_count,
            estimated_reading_sec=estimated_reading_sec
        )

        return project, stats

    def get_project(self, project_id: str) -> Project:
        # Try to get from cache first
        cache_key = CacheKeys.project(project_id)
        cached_data = self.cache.get(cache_key)

        if cached_data:
            # Don't reconstruct from cache, just use it as a hint
            # Always fetch from DB to ensure we have complete data
            pass

        # Get from database
        project = self.repo.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Cache the project data (for quick lookups)
        self.cache.set(cache_key, {
            "id": project.id,
            "title": project.title,
            "status": project.status,
            "char_count": project.char_count,
            "source_type": project.source_type,
            "latest_job_id": project.latest_job_id
        }, ttl=self.cache.LONG_TTL)

        return project

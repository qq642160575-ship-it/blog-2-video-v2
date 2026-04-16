import uuid
from sqlalchemy.orm import Session
from app.models.project import Project
from app.repositories.project_repo import ProjectRepository
from app.schemas.project import ProjectCreate, ArticleStats


class ProjectService:
    def __init__(self, db: Session):
        self.repo = ProjectRepository(db)

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

        # Calculate stats
        estimated_reading_sec = int(char_count / 3)  # Rough estimate: 3 chars per second
        stats = ArticleStats(
            char_count=char_count,
            estimated_reading_sec=estimated_reading_sec
        )

        return project, stats

    def get_project(self, project_id: str) -> Project:
        project = self.repo.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        return project

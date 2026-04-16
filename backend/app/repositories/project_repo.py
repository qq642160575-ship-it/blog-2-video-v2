from sqlalchemy.orm import Session
from app.models.project import Project
from typing import Optional


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_by_id(self, project_id: str) -> Optional[Project]:
        return self.db.query(Project).filter(Project.id == project_id).first()

    def update(self, project: Project) -> Project:
        self.db.commit()
        self.db.refresh(project)
        return project

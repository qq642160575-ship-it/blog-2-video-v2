"""input: 依赖数据库会话和 Project 模型。
output: 向外提供项目仓储读写接口。
pos: 位于仓储层，负责项目持久化封装。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

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

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Project]:
        """Get all projects with pagination, ordered by creation time (newest first)"""
        return self.db.query(Project)\
            .order_by(Project.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    def update(self, project: Project) -> Project:
        self.db.commit()
        self.db.refresh(project)
        return project

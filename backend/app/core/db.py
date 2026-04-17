"""input: 依赖数据库连接串和 SQLAlchemy。
output: 向外提供 engine、SessionLocal、Base 和 get_db。
pos: 位于基础设施层，负责数据库接入。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

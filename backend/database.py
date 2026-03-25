from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testcase.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{db_path.replace(chr(92), '/')}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from models.schema import Problem, TestCase, TagCategory, TestCaseTag, KnowledgeComponent, KCAssignment
    Base.metadata.create_all(bind=engine)

from typing import Generator, Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from core.config import config


engine = create_engine(
    config.database_url,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)


# Dependency
def get_db() -> Generator[Session, Any, Any]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

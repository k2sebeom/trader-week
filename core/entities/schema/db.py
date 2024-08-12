from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import config


engine = create_engine(
    config.database_url, connect_args={
        'check_same_thread': False,
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,                            
)

Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)

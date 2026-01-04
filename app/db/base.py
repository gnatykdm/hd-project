from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, Engine
from app.core.config import settings

engine: Engine = create_engine(
    settings.db_url,
    pool_pre_ping=True, 
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

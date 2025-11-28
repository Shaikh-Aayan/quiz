import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./questions.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
metadata = MetaData()

# Create all tables on startup
def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create tables: {e}")

# Call on import
init_db()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


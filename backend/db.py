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
        # Run migrations to add new columns
        run_migrations()
    except Exception as e:
        print(f"Warning: Could not create tables: {e}")

def run_migrations():
    """Run database migrations"""
    try:
        from sqlalchemy import inspect, text
        
        inspector = inspect(engine)
        if 'questions' not in inspector.get_table_names():
            return  # Table doesn't exist yet
        
        columns = {col['name'] for col in inspector.get_columns('questions')}
        
        with engine.connect() as conn:
            # Add image_data if missing
            if 'image_data' not in columns:
                if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
                    conn.execute(text("ALTER TABLE questions ADD COLUMN image_data BYTEA DEFAULT NULL"))
                else:
                    conn.execute(text("ALTER TABLE questions ADD COLUMN image_data BLOB DEFAULT NULL"))
                conn.commit()
                print("✅ Added image_data column")
            
            # Add image_type if missing
            if 'image_type' not in columns:
                conn.execute(text("ALTER TABLE questions ADD COLUMN image_type VARCHAR(50) DEFAULT NULL"))
                conn.commit()
                print("✅ Added image_type column")
    except Exception as e:
        print(f"Migration note: {e}")  # Don't fail if columns already exist

# Call on import
init_db()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


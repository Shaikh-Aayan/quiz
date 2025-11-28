#!/usr/bin/env python3
"""
Database migration script to add image columns to questions table
"""

import os
import sqlite3
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./questions.db")

def migrate_sqlite():
    """Migrate SQLite database"""
    db_path = DATABASE_URL.replace("sqlite:///", "")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(questions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'image_data' not in columns:
            logger.info("Adding image_data column...")
            cursor.execute("ALTER TABLE questions ADD COLUMN image_data BLOB")
        
        if 'image_type' not in columns:
            logger.info("Adding image_type column...")
            cursor.execute("ALTER TABLE questions ADD COLUMN image_type VARCHAR(50)")
        
        conn.commit()
        conn.close()
        logger.info("✅ SQLite migration completed")
        
    except Exception as e:
        logger.error(f"❌ SQLite migration failed: {str(e)}")

def migrate_postgresql():
    """Migrate PostgreSQL database"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if columns exist
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='questions'
            """))
            columns = [row[0] for row in result]
            
            if 'image_data' not in columns:
                logger.info("Adding image_data column...")
                conn.execute(text("ALTER TABLE questions ADD COLUMN image_data BYTEA"))
                conn.commit()
            
            if 'image_type' not in columns:
                logger.info("Adding image_type column...")
                conn.execute(text("ALTER TABLE questions ADD COLUMN image_type VARCHAR(50)"))
                conn.commit()
        
        logger.info("✅ PostgreSQL migration completed")
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL migration failed: {str(e)}")

if __name__ == "__main__":
    if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
        migrate_postgresql()
    else:
        migrate_sqlite()

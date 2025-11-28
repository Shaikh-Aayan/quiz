#!/usr/bin/env python3
"""
Run database migration to add image columns
"""

import os
import sqlite3
from sqlalchemy import create_engine, text, inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./questions.db")

def migrate_add_image_columns():
    """Add image columns to existing questions table"""
    
    if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
        migrate_postgresql()
    else:
        migrate_sqlite()

def migrate_sqlite():
    """Migrate SQLite database"""
    db_path = DATABASE_URL.replace("sqlite:///", "")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(questions)")
        columns = {col[1] for col in cursor.fetchall()}
        
        logger.info(f"Existing columns: {columns}")
        
        # Add image_data if missing
        if 'image_data' not in columns:
            logger.info("Adding image_data column...")
            cursor.execute("ALTER TABLE questions ADD COLUMN image_data BLOB DEFAULT NULL")
            conn.commit()
            logger.info("✅ Added image_data column")
        
        # Add image_type if missing
        if 'image_type' not in columns:
            logger.info("Adding image_type column...")
            cursor.execute("ALTER TABLE questions ADD COLUMN image_type VARCHAR(50) DEFAULT NULL")
            conn.commit()
            logger.info("✅ Added image_type column")
        
        conn.close()
        logger.info("✅ SQLite migration completed successfully")
        
    except Exception as e:
        logger.error(f"❌ SQLite migration failed: {str(e)}")
        raise

def migrate_postgresql():
    """Migrate PostgreSQL database"""
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        columns = {col['name'] for col in inspector.get_columns('questions')}
        logger.info(f"Existing columns: {columns}")
        
        with engine.connect() as conn:
            # Add image_data if missing
            if 'image_data' not in columns:
                logger.info("Adding image_data column...")
                conn.execute(text("ALTER TABLE questions ADD COLUMN image_data BYTEA DEFAULT NULL"))
                conn.commit()
                logger.info("✅ Added image_data column")
            
            # Add image_type if missing
            if 'image_type' not in columns:
                logger.info("Adding image_type column...")
                conn.execute(text("ALTER TABLE questions ADD COLUMN image_type VARCHAR(50) DEFAULT NULL"))
                conn.commit()
                logger.info("✅ Added image_type column")
        
        logger.info("✅ PostgreSQL migration completed successfully")
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info(f"Starting migration for: {DATABASE_URL}")
    migrate_add_image_columns()
    logger.info("✅ All migrations completed!")

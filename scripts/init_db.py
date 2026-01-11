#!/usr/bin/env python3
"""
Database initialization script.

Creates database tables and runs any initial setup.
Run this before starting the application for the first time.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.database import init_db
from app.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


async def main():
    """Initialize the database."""
    logger.info("Starting database initialization")
    logger.info("Database URL", url=settings.database_url)

    try:
        await init_db()
        logger.info("✅ Database tables created successfully!")

        # Print database location
        if settings.database_url.startswith("sqlite"):
            db_path = settings.database_url.replace("sqlite:///", "")
            logger.info("Database file location", path=db_path)

        return 0

    except Exception as e:
        logger.error("Failed to initialize database", error=str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

"""
Database configuration and session management.
Uses SQLAlchemy 2.0 with async support.
"""
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# For SQLite in POC, we need to handle sync vs async carefully
# SQLite doesn't support true async, but we use aiosqlite for compatibility
def get_database_url() -> str:
    """Get the appropriate database URL based on the database type."""
    url = settings.database_url

    # For SQLite, convert to async URL if needed
    if url.startswith("sqlite:///"):
        # Use aiosqlite for async operations
        return url.replace("sqlite:///", "sqlite+aiosqlite:///")

    return url


# Create async engine
engine = create_async_engine(
    get_database_url(),
    echo=settings.debug,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# For migrations and initial setup, we also need a sync engine
sync_engine = create_engine(
    settings.database_url,
    echo=settings.debug,
)

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get database session.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def init_db_sync() -> None:
    """Initialize database tables synchronously (for scripts)."""
    Base.metadata.create_all(bind=sync_engine)

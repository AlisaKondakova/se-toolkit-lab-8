"""Database connection management - no pooling for immediate failure detection."""

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.settings import settings


def get_database_url() -> str:
    return (
        f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )


# Disable connection pooling entirely - create new connection for each request
engine = create_async_engine(
    get_database_url(),
    pool_size=0,  # No pool
    max_overflow=0,  # No overflow connections
    pool_pre_ping=True,  # Verify connection before use
    pool_recycle=1,  # Recycle after 1 second
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    """
    Create a fresh database session for each request.
    This ensures we detect postgres failures immediately.
    """
    # Create new session without pooling
    session = AsyncSession(engine, expire_on_commit=False)
    try:
        # Test connection FIRST - this will raise if postgres is down
        await session.execute(text("SELECT 1"))
        yield session
    finally:
        # Always close the session after use
        await session.close()

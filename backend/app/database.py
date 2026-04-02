"""Database connection management - no pooling for immediate failure detection."""

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.settings import settings


def get_database_url() -> str:
    return (
        f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )


# Use NullPool - create new connection for EVERY request
engine: AsyncEngine = create_async_engine(
    get_database_url(),
    poolclass=NullPool,  # No pooling at all
    pool_pre_ping=True,  # Verify connection before each use
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    """
    Create a fresh database session for each request.
    This ensures we detect postgres failures immediately.
    """
    session = AsyncSession(engine, expire_on_commit=False)
    try:
        # Test connection FIRST - this will raise if postgres is down
        await session.execute(text("SELECT 1"))
        yield session
    finally:
        await session.close()

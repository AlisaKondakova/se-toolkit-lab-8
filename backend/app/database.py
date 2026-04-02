"""Database connection management."""

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.settings import settings


def get_database_url() -> str:
    return (
        f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )


engine = create_async_engine(get_database_url(), pool_pre_ping=True)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(engine) as session:
        # Verify database connection before yielding session
        try:
            await session.execute(text("SELECT 1"))
        except Exception as exc:
            # Re-raise to trigger exception handler in routes
            raise exc
        yield session

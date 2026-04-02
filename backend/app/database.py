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


engine = create_async_engine(get_database_url())


async def get_session() -> AsyncGenerator[AsyncSession]:
    # Create a new connection for each request to detect failures immediately
    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Test connection before yielding - this will raise if postgres is down
        await session.execute(text("SELECT 1"))
        yield session

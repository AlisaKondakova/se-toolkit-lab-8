#!/usr/bin/env python
"""Create database tables."""

import asyncio
from sqlmodel import SQLModel
from app.database import get_database_url
from app.models import interaction, item, learner  # noqa: F401
from sqlalchemy.ext.asyncio import create_async_engine


async def main():
    url = get_database_url()
    print(f"Connecting to {url}")
    engine = create_async_engine(url)
    
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("Tables created successfully!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

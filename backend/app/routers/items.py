"""Router for item endpoints — reference implementation."""

import logging

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.db.items import create_item, read_item, read_items, update_item
from app.models.item import ItemCreate, ItemRecord, ItemUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=list[ItemRecord])
async def get_items(session: AsyncSession = Depends(get_session)):
    """Get all items."""
    try:
        return await read_items(session)
    except asyncpg.PostgresConnectionError as exc:
        # Database connection error - return 500
        logger.error(f"Database connection failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {str(exc)}",
        ) from exc
    except SQLAlchemyError as exc:
        # Database error - return 500
        logger.error(f"Database error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(exc)}",
        ) from exc
    except Exception as exc:
        # Any other error - return 500
        logger.exception("Failed to fetch items: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching items: {str(exc)}",
        ) from exc


@router.get("/{item_id}", response_model=ItemRecord)
async def get_item(item_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific item by its id."""
    try:
        item = await read_item(session, item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )
        return item
    except asyncpg.PostgresConnectionError as exc:
        logger.error(f"Database connection failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {str(exc)}",
        ) from exc
    except SQLAlchemyError as exc:
        logger.error(f"Database error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(exc)}",
        ) from exc


@router.post("/", response_model=ItemRecord, status_code=201)
async def post_item(body: ItemCreate, session: AsyncSession = Depends(get_session)):
    """Create a new item."""
    try:
        return await create_item(
            session,
            type=body.type,
            parent_id=body.parent_id,
            title=body.title,
            description=body.description,
        )
    except asyncpg.PostgresConnectionError as exc:
        logger.error(f"Database connection failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {str(exc)}",
        ) from exc
    except SQLAlchemyError as exc:
        logger.error(f"Database error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(exc)}",
        ) from exc


@router.put("/{item_id}", response_model=ItemRecord)
async def put_item(
    item_id: int, body: ItemUpdate, session: AsyncSession = Depends(get_session)
):
    """Update an existing item."""
    try:
        item = await update_item(
            session, item_id=item_id, title=body.title, description=body.description
        )
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )
        return item
    except asyncpg.PostgresConnectionError as exc:
        logger.error(f"Database connection failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {str(exc)}",
        ) from exc
    except SQLAlchemyError as exc:
        logger.error(f"Database error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(exc)}",
        ) from exc

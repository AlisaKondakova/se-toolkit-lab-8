"""Health check router."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session

router = APIRouter()


@router.get("/health/db")
async def check_database(session: AsyncSession = Depends(get_session)):
    """Check database connection."""
    try:
        await session.exec("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "unhealthy", "database": str(exc)},
        )

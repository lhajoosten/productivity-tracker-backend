from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from productivity_tracker.core.settings import settings
from productivity_tracker.database import get_db

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    app_name: str
    version: str
    timestamp: datetime
    database: str


class DetailedHealthResponse(HealthResponse):
    """Detailed health check response with database info."""

    database_version: str | None = None


@router.get("/health", response_model=HealthResponse, operation_id="healthCheck")
def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.utcnow(),
        "database": "not_checked",
    }


@router.get(
    "/health/detailed",
    response_model=DetailedHealthResponse,
    operation_id="detailedHealthCheck",
)
def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with database connection test."""
    database_status = "disconnected"
    database_version = None

    try:
        # Test database connection
        result = db.execute(text("SELECT version()"))
        database_version = result.scalar()
        database_status = "connected"
    except Exception as e:
        database_status = f"error: {str(e)}"

    return {
        "status": "healthy" if database_status == "connected" else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.utcnow(),
        "database": database_status,
        "database_version": database_version,
    }

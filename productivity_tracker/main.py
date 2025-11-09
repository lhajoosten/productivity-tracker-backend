from fastapi import FastAPI

from productivity_tracker.api.setup import setup_versioned_routers
from productivity_tracker.core.database import Base, engine
from productivity_tracker.core.logging_config import get_logger, setup_logging
from productivity_tracker.core.redis_client import redis_client
from productivity_tracker.core.settings import settings
from productivity_tracker.core.setup import setup_exception_handling, setup_middleware
from productivity_tracker.versioning.version import __version__

setup_logging(
    console_only=settings.is_development or settings.is_testing,
    enable_file_logging=settings.is_production or settings.ENVIRONMENT.lower() == "staging",
)
logger = get_logger(__name__)

app = FastAPI(
    title="Productivity Tracker API",
    description="Professional productivity tracking application",
    version=__version__,
)

setup_exception_handling(app)
setup_middleware(app)
setup_versioned_routers(app)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    from productivity_tracker.core.database import SessionLocal
    from productivity_tracker.database.entities.version import Version

    logger.info(f"Starting {settings.APP_NAME} v{__version__}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    db = SessionLocal()
    try:
        active_version = db.query(Version).filter(Version.status == "active").first()
        if active_version:
            # Keep docs at root - FastAPI serves them there by default
            pass
    finally:
        db.close()

    if redis_client.is_connected:
        logger.info("Redis connected and ready for session management")
    else:
        logger.warning("Redis not connected - session management disabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info(f"Shutting down {settings.APP_NAME}")
    redis_client.close()

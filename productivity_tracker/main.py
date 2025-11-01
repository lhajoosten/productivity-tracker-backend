from fastapi import FastAPI

from productivity_tracker.api.setup import setup_versioned_routers
from productivity_tracker.core.database import Base, engine
from productivity_tracker.core.logging_config import get_logger, setup_logging
from productivity_tracker.core.settings import settings
from productivity_tracker.core.setup import setup_exception_handling, setup_middleware
from productivity_tracker.versioning.version import __version__
from productivity_tracker.versioning.versioning import CURRENT_VERSION

# Setup logging based on environment
# Development/Testing: Console only
# Staging/Production: Console + File logging
setup_logging(
    console_only=settings.is_development or settings.is_testing,
    enable_file_logging=settings.is_production or settings.ENVIRONMENT.lower() == "staging",
)
logger = get_logger(__name__)

app = FastAPI(
    title="Productivity Tracker API",
    description="Professional productivity tracking application",
    version=__version__,
    docs_url=f"{CURRENT_VERSION.api_prefix}/docs",
    redoc_url=f"{CURRENT_VERSION.api_prefix}/redoc",
    openapi_url=f"{CURRENT_VERSION.api_prefix}/openapi.json",
)

# Setup exception handling
setup_exception_handling(app)

# Setup middleware
setup_middleware(app)

# Setup routers
setup_versioned_routers(app)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Starting {settings.APP_NAME} v{__version__}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info(f"Shutting down {settings.APP_NAME}")

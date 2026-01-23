"""
Main FastAPI application.

Production-quality WhatsApp bot for UIC generation using Twilio.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.webhook import router as webhook_router
from app.config import settings
from app.database import init_db
from app.logging_config import configure_logging, get_logger

# Configure logging first
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "Starting application",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment
    )

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-quality WhatsApp bot for UIC validation and generation",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware (for development/testing)
if settings.debug:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(webhook_router)

# Mount static files for QR codes (if feature enabled)
if settings.enable_qr_code:
    from pathlib import Path
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Static files mounted for QR codes", directory="static")


@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "operational",
        "docs": "/docs" if settings.debug else "disabled in production"
    }


@app.get("/health")
async def health():
    """Health check endpoint for load balancers."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


def run() -> None:
    """Start the application with uvicorn."""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    # Run with: python -m app.main
    run()

"""
FastAPI application setup.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import logging

from app.config import get_settings
from app.api.router import api_router, health_router, webhook_router
from app.core.exceptions import ZelavoBaseException

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="Zelavo Kids Backend",
    description="AI-powered personalized children's storybook platform",
    version="1.0.0",
    docs_url="/docs" if get_settings().app_debug else None,
    redoc_url="/redoc" if get_settings().app_debug else None,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "https://zelavokids.com",  # Production frontend
        "https://*.zelavokids.com",  # Subdomains
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(ZelavoBaseException)
async def zelavo_exception_handler(request: Request, exc: ZelavoBaseException):
    """Handle custom Zelavo exceptions."""
    logger.error(
        "Zelavo exception occurred",
        exception=exc.__class__.__name__,
        code=exc.code,
        message=exc.message,
        details=exc.details,
        path=str(request.url)
    )

    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(
        "Unexpected exception occurred",
        exception=exc.__class__.__name__,
        message=str(exc),
        path=str(request.url)
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again."
            }
        }
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    settings = get_settings()
    logger.info(
        "Starting Zelavo Kids Backend",
        version="1.0.0",
        environment=settings.app_env,
        debug=settings.app_debug
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down Zelavo Kids Backend")


# Include routers
app.include_router(health_router)  # Health check at root level
app.include_router(api_router, prefix="/api")  # API endpoints
app.include_router(webhook_router, prefix="/webhooks")  # Webhooks


@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "service": "Zelavo Kids Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs" if get_settings().app_debug else "disabled"
    }


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app_debug,
        log_level="info"
    )
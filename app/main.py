"""
FastAPI application setup.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import structlog
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.api.router import api_router, health_router, webhook_router
from app.routers import proxy
from app.core.exceptions import ZelavoBaseException
from app.core.rate_limiter import limiter

# Configure logging handlers based on environment
# Render has read-only filesystem, so only use console logging there
if os.getenv("RENDER"):
    # Production on Render: stdout only (Render captures logs automatically)
    log_handlers = [logging.StreamHandler()]
else:
    # Local development: console + file logging
    LOGS_DIR = Path(__file__).parent.parent / "logs"
    LOGS_DIR.mkdir(exist_ok=True)
    log_handlers = [
        logging.StreamHandler(),
        RotatingFileHandler(
            LOGS_DIR / "app.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
    ]

# Configure Python's standard logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=log_handlers
)

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

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration - Allow Shopify domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins for Shopify App Proxy
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite default dev server
        "http://0.0.0.0:3000",    # Vite with host 0.0.0.0
        "https://zelavokids.com",  # Production frontend
        "https://*.zelavokids.com",  # Subdomains
        "https://*.myshopify.com",  # Shopify stores
        "https://admin.shopify.com",  # Shopify Admin
        "https://cdn.shopify.com",  # Shopify CDN
    ],
    allow_credentials=True,
    allow_methods=["*"],
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
app.include_router(api_router, prefix="/proxy/api")  # Shopify App Proxy mirror
app.include_router(webhook_router, prefix="/webhooks")  # Webhooks
app.include_router(proxy.router)  # Shopify App Proxy frontend serving (MUST BE LAST - has catch-all)

# Mount static assets for React frontend (CSS/JS)
# Path: magictales_backend/../Magictales/dist/assets (i.e. sibling Magictales folder)
_frontend_assets_path = Path(__file__).parent.parent.parent / "Magictales" / "dist" / "assets"
if _frontend_assets_path.exists():
    app.mount("/proxy/assets", StaticFiles(directory=str(_frontend_assets_path)), name="proxy-assets")
    logger.info("Mounted frontend assets", path=str(_frontend_assets_path))
else:
    logger.warning("Frontend assets not found", path=str(_frontend_assets_path))



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
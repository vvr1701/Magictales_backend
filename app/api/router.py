"""
Main API router that combines all endpoints.
"""

from fastapi import APIRouter

from app.api.endpoints import upload, preview, status, download, health, development, my_creations
from app.api.webhooks import shopify
from app.config import get_settings

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, tags=["health"])  # Health check also under /api/
api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(preview.router, tags=["preview"])  # No prefix - routes already have /preview
api_router.include_router(status.router, tags=["status"])
api_router.include_router(download.router, tags=["download"])
api_router.include_router(development.router, tags=["development"])
api_router.include_router(my_creations.router, tags=["my-creations"])

# Test endpoints for local Shopify flow testing
# ONLY included when TESTING_MODE_ENABLED=true (never in production)
settings = get_settings()
if settings.testing_mode_enabled:
    from app.api.endpoints import test_shopify
    api_router.include_router(test_shopify.router, tags=["test"])

# Health check (no prefix)
health_router = APIRouter()
health_router.include_router(health.router, tags=["health"])

# Webhook router
webhook_router = APIRouter()
webhook_router.include_router(shopify.router, prefix="/shopify", tags=["webhooks"])
"""
Main API router that combines all endpoints.
"""

from fastapi import APIRouter

from app.api.endpoints import upload, preview, status, download, health, development, test_shopify
from app.api.webhooks import shopify

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, tags=["health"])  # Health check also under /api/
api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(preview.router, tags=["preview"])  # No prefix - routes already have /preview
api_router.include_router(status.router, tags=["status"])
api_router.include_router(download.router, tags=["download"])
api_router.include_router(development.router, tags=["development"])

# Test endpoints for local Shopify flow testing (only enabled when TESTING_MODE_ENABLED=true)
api_router.include_router(test_shopify.router, tags=["test"])

# Health check (no prefix)
health_router = APIRouter()
health_router.include_router(health.router, tags=["health"])

# Webhook router
webhook_router = APIRouter()
webhook_router.include_router(shopify.router, prefix="/shopify", tags=["webhooks"])
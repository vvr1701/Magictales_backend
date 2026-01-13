"""
Shopify App Proxy router.

Handles requests proxied from Shopify at /apps/zelavo/* -> /proxy/*
Serves the React SPA for frontend routes, with HMAC signature verification.

Traffic Flow:
    Shopify (/apps/zelavo/preview) 
    -> App Proxy adds ?signature=...&shop=...&timestamp=...
    -> Backend (/proxy/preview)
    -> Verify signature
    -> Serve React index.html
"""

import os
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
import structlog

from app.config import get_settings
from app.services.shopify_auth import verify_proxy_signature

logger = structlog.get_logger()

# Prefix matches your Shopify App Proxy setting
router = APIRouter(prefix="/proxy", tags=["proxy"])

# Path to your React Build folder (relative to backend root)
# Backend is at: magictales_backend/
# Frontend dist is at: Magictales/dist/
FRONTEND_DIST = Path(__file__).parent.parent.parent.parent / "Magictales" / "dist"


@router.get("/preview")
@router.get("/preview/{path:path}")
async def serve_preview_app(request: Request, path: str = ""):
    """
    Serve React app for /proxy/preview/* routes.
    
    1. Verifies Shopify Signature (in production)
    2. Serves index.html so React Router can handle routing
    """
    settings = get_settings()
    
    # Verify signature - skip in debug mode if no signature present
    is_valid = await verify_proxy_signature(request)
    if not is_valid and not settings.app_debug:
        logger.warning("Unauthorized App Proxy request", path=path)
        raise HTTPException(status_code=401, detail="Unauthorized Shopify Request")
    
    # Serve React app
    return await _serve_index_html()


@router.get("/")
async def serve_proxy_root(request: Request):
    """
    Serve React app for /proxy/ root.
    """
    settings = get_settings()
    
    is_valid = await verify_proxy_signature(request)
    if not is_valid and not settings.app_debug:
        raise HTTPException(status_code=401, detail="Unauthorized Shopify Request")
    
    return await _serve_index_html()


@router.get("/{path:path}")
async def serve_catch_all(request: Request, path: str):
    """
    Catch-all route for any other /proxy/* paths.
    
    This allows React Router to handle all client-side routes.
    """
    settings = get_settings()
    
    # Skip API paths - they should be handled by api_router
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Skip asset paths - they should be handled by StaticFiles mount
    if path.startswith("assets/"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    is_valid = await verify_proxy_signature(request)
    if not is_valid and not settings.app_debug:
        raise HTTPException(status_code=401, detail="Unauthorized Shopify Request")
    
    return await _serve_index_html()


async def _serve_index_html():
    """Helper to serve the React index.html file."""
    index_file = FRONTEND_DIST / "index.html"
    
    if not index_file.exists():
        logger.error("Frontend build not found", path=str(index_file))
        return HTMLResponse(
            content="""
            <html>
            <head><title>Backend Ready</title></head>
            <body style="font-family: sans-serif; padding: 40px;">
                <h1>Backend Ready, Frontend Not Found</h1>
                <p>The React build directory was not found at:</p>
                <code style="background: #f0f0f0; padding: 10px; display: block; margin: 20px 0;">
                    {path}
                </code>
                <p>Please run <code>npm run build</code> in the frontend directory.</p>
            </body>
            </html>
            """.format(path=str(index_file)),
            status_code=500
        )
    
    logger.debug("Serving React SPA", index_path=str(index_file))
    return FileResponse(index_file, media_type="text/html")

"""
Health check endpoint with database verification.
"""

from fastapi import APIRouter
from datetime import datetime
import structlog

from app.models.database import get_db

logger = structlog.get_logger()
router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint with database verification.

    Returns:
        - status: "healthy" if all systems operational, "degraded" if DB issues
        - database: "connected" or "disconnected"
        - timestamp: Current UTC timestamp
    """
    db_status = "disconnected"

    try:
        db = get_db()
        # Simple query to verify database connection
        result = db.table("previews").select("preview_id").limit(1).execute()
        if result.error:
            db_status = "error"
        else:
            db_status = "connected"
    except Exception as e:
        logger.warning("Health check database connection failed", error=str(e))
        db_status = "disconnected"

    overall_status = "healthy" if db_status == "connected" else "degraded"

    return {
        "status": overall_status,
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "zelavo-kids-backend"
    }

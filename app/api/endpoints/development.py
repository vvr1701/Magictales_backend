"""
Development endpoints for testing - bypasses payment verification.
WARNING: These endpoints should only be used in development/testing environments.
"""

import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import structlog

from app.models.database import get_db
from app.models.enums import OrderStatus, PreviewStatus
from app.background.tasks import generate_pdf
from app.config import get_settings

logger = structlog.get_logger()
router = APIRouter()


class DevPdfGenerationRequest(BaseModel):
    """Request model for development PDF generation."""
    preview_id: str
    customer_email: str = "test@example.com"
    customer_name: str = "Test Customer"


class DevPdfGenerationResponse(BaseModel):
    """Response model for development PDF generation."""
    success: bool
    order_id: str
    preview_id: str
    message: str


@router.post("/dev/generate-pdf", response_model=DevPdfGenerationResponse)
async def dev_generate_pdf(
    request: DevPdfGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Development endpoint to generate PDF without payment verification.

    This endpoint:
    1. Validates that the preview exists and is ready
    2. Creates an order record with status 'PAID' (bypassing Shopify)
    3. Triggers PDF generation background task
    4. Returns order_id for tracking

    WARNING: This bypasses all payment verification and should only be used for testing.
    """
    try:
        settings = get_settings()

        # Log security warning for non-development environments
        if settings.app_env not in ["development", "testing", "local"]:
            logger.warning(
                "Development PDF generation endpoint called in production environment",
                environment=settings.app_env,
                preview_id=request.preview_id
            )
            raise HTTPException(
                status_code=403,
                detail="Development endpoints are disabled in production"
            )

        logger.info(
            "Development PDF generation requested",
            preview_id=request.preview_id,
            customer_email=request.customer_email
        )

        db = get_db()

        # 1. Validate preview exists and is ready
        preview_response = db.table("previews").select("*").eq("preview_id", request.preview_id).execute()

        if not preview_response.data:
            logger.warning("Preview not found", preview_id=request.preview_id)
            raise HTTPException(status_code=404, detail="Preview not found")

        preview = preview_response.data[0]

        # Check preview status
        if preview["status"] != PreviewStatus.ACTIVE.value:
            logger.warning(
                "Preview not ready for PDF generation",
                preview_id=request.preview_id,
                status=preview["status"]
            )
            raise HTTPException(
                status_code=400,
                detail=f"Preview is not ready. Current status: {preview['status']}"
            )

        # Check if preview has expired
        expiry_date = datetime.fromisoformat(preview["expires_at"].replace("Z", "+00:00"))
        if datetime.utcnow().replace(tzinfo=expiry_date.tzinfo) > expiry_date:
            logger.warning("Preview has expired", preview_id=request.preview_id)
            raise HTTPException(status_code=400, detail="Preview has expired")

        # 2. Check if order already exists for this preview (allow retry for failed orders)
        existing_order_response = db.table("orders").select("*").eq("preview_id", request.preview_id).execute()

        if existing_order_response.data:
            existing_order = existing_order_response.data[0]
            logger.info(
                "Order already exists for preview",
                preview_id=request.preview_id,
                order_id=existing_order["order_id"],
                status=existing_order["status"]
            )
            
            # If order failed, allow retry by resetting status and re-triggering PDF generation
            if existing_order["status"] == OrderStatus.FAILED.value:
                logger.info("Retrying failed order", order_id=existing_order["order_id"])
                
                # Reset order status to PAID for retry
                db.table("orders").update({
                    "status": OrderStatus.PAID.value,
                    "error_message": None,
                    "last_error": None,
                    "retry_count": existing_order.get("retry_count", 0) + 1
                }).eq("order_id", existing_order["order_id"]).execute()
                
                # Trigger PDF generation again
                background_tasks.add_task(
                    generate_pdf,
                    order_id=existing_order["order_id"],
                    preview_id=request.preview_id
                )
                
                return DevPdfGenerationResponse(
                    success=True,
                    order_id=existing_order["order_id"],
                    preview_id=request.preview_id,
                    message=f"Retrying PDF generation for failed order (attempt #{existing_order.get('retry_count', 0) + 1})"
                )
            
            # For non-failed orders, return existing order info
            return DevPdfGenerationResponse(
                success=True,
                order_id=existing_order["order_id"],
                preview_id=request.preview_id,
                message=f"Order already exists with status: {existing_order['status']}"
            )

        # 3. Generate order ID and create order record
        order_id = f"DEV-{uuid.uuid4().hex[:16].upper()}"

        order_data = {
            "order_id": order_id,
            "preview_id": request.preview_id,
            "customer_email": request.customer_email,
            "customer_name": request.customer_name,
            "total_amount": 0.00,  # Free for development
            "currency": "USD",
            "status": OrderStatus.PAID.value,  # Skip payment verification
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),  # 30 days for downloads
            "payment_method": "DEV_BYPASS",
            "is_development_order": True  # Flag to identify dev orders
        }

        # Insert order record
        order_response = db.table("orders").insert(order_data).execute()

        if not order_response.data:
            logger.error("Failed to create order record", order_id=order_id)
            raise HTTPException(status_code=500, detail="Failed to create order")

        logger.info(
            "Development order created",
            order_id=order_id,
            preview_id=request.preview_id,
            status=OrderStatus.PAID.value
        )

        # 4. Trigger PDF generation background task
        background_tasks.add_task(
            generate_pdf,
            order_id=order_id,
            preview_id=request.preview_id
        )

        logger.info(
            "PDF generation task queued",
            order_id=order_id,
            preview_id=request.preview_id
        )

        return DevPdfGenerationResponse(
            success=True,
            order_id=order_id,
            preview_id=request.preview_id,
            message="PDF generation started. Use order_id to track progress."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Development PDF generation failed",
            preview_id=request.preview_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/dev/order-status/{order_id}")
async def dev_get_order_status(order_id: str):
    """
    Development endpoint to check order status.

    Returns the current status of an order including PDF generation progress.
    """
    try:
        db = get_db()

        # Get order details
        order_response = db.table("orders").select("*").eq("order_id", order_id).execute()

        if not order_response.data:
            raise HTTPException(status_code=404, detail="Order not found")

        order = order_response.data[0]

        # Get preview details
        preview_response = db.table("previews").select("*").eq("preview_id", order["preview_id"]).execute()
        preview = preview_response.data[0] if preview_response.data else None

        return {
            "success": True,
            "order": {
                "order_id": order["order_id"],
                "preview_id": order["preview_id"],
                "status": order["status"],
                "created_at": order["created_at"],
                "customer_email": order["customer_email"],
                "is_development_order": order.get("is_development_order", False)
            },
            "preview": {
                "status": preview["status"] if preview else "unknown",
                "expires_at": preview["expires_at"] if preview else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get order status", order_id=order_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/dev/info")
async def dev_info():
    """
    Development endpoint info and available operations.
    """
    settings = get_settings()

    return {
        "service": "Magictales Development Endpoints",
        "environment": settings.app_env,
        "warning": "These endpoints bypass payment verification and should only be used for testing",
        "available_endpoints": [
            {
                "endpoint": "POST /api/dev/generate-pdf",
                "description": "Generate PDF without payment (requires preview_id)",
                "required_fields": ["preview_id"],
                "optional_fields": ["customer_email", "customer_name"]
            },
            {
                "endpoint": "GET /api/dev/order-status/{order_id}",
                "description": "Check order and PDF generation status"
            },
            {
                "endpoint": "GET /api/dev/info",
                "description": "This info endpoint"
            }
        ],
        "complete_testing_flow": [
            "1. Upload photo: POST /api/upload-photo",
            "2. Create preview: POST /api/preview",
            "3. Wait for preview completion: GET /api/preview-status/{job_id}",
            "4. [DEV] Generate PDF: POST /api/dev/generate-pdf",
            "5. Check PDF status: GET /api/dev/order-status/{order_id}",
            "6. Download PDF: GET /api/download/{order_id}"
        ]
    }
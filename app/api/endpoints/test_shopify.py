"""
Test endpoints for Shopify integration local testing.

These endpoints simulate Shopify's cart and payment flow for local development.
They should NOT be exposed in production (controlled via TESTING_MODE_ENABLED setting).

Usage:
1. Start backend: uvicorn app.main:app --reload
2. Start frontend: npm run dev
3. Open: http://localhost:3000?shopify_test=true
4. The frontend will use these test endpoints instead of real Shopify
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import structlog

from app.models.database import get_db
from app.models.enums import PreviewStatus, OrderStatus, JobStatus, JobType
from app.background.tasks import generate_pdf_from_order
from app.config import get_settings

logger = structlog.get_logger()
router = APIRouter(prefix="/test", tags=["test"])


class TestCartAddRequest(BaseModel):
    preview_id: str
    variant_id: Optional[str] = "test-variant"


class TestCartAddResponse(BaseModel):
    success: bool
    order_id: str
    message: str


class TestPaymentRequest(BaseModel):
    preview_id: str
    order_id: Optional[str] = None


class TestPaymentResponse(BaseModel):
    success: bool
    order_id: str
    preview_id: str
    status: str
    message: str


@router.post("/cart/add", response_model=TestCartAddResponse)
async def test_cart_add(request: TestCartAddRequest):
    """
    Simulate adding item to Shopify cart.

    This creates a pending order record that will be "paid" when
    test_simulate_payment is called.
    """
    settings = get_settings()

    if not settings.testing_mode_enabled:
        raise HTTPException(
            status_code=403,
            detail="Test endpoints are disabled. Set TESTING_MODE_ENABLED=true"
        )

    try:
        logger.info("Test cart add", preview_id=request.preview_id)

        db = get_db()

        # Verify preview exists
        preview_response = db.table("previews").select("*").eq("preview_id", request.preview_id).execute()
        if not preview_response.data:
            raise HTTPException(status_code=404, detail="Preview not found")

        preview = preview_response.data[0]

        # Generate test order ID
        order_id = f"test-order-{uuid.uuid4().hex[:8]}"

        logger.info("Test cart item added", order_id=order_id, preview_id=request.preview_id)

        return TestCartAddResponse(
            success=True,
            order_id=order_id,
            message=f"Item added to test cart. Preview: {preview['child_name']}'s story"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Test cart add failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate-payment", response_model=TestPaymentResponse)
async def test_simulate_payment(
    request: TestPaymentRequest,
    background_tasks: BackgroundTasks
):
    """
    Simulate Shopify payment webhook.

    This does what the real webhook handler does:
    1. Creates an order record
    2. Updates preview status to PURCHASED
    3. Triggers PDF generation background task
    """
    settings = get_settings()

    if not settings.testing_mode_enabled:
        raise HTTPException(
            status_code=403,
            detail="Test endpoints are disabled. Set TESTING_MODE_ENABLED=true"
        )

    try:
        logger.info("Test payment simulation", preview_id=request.preview_id)

        db = get_db()

        # Verify preview exists and is ready
        preview_response = db.table("previews").select("*").eq("preview_id", request.preview_id).execute()
        if not preview_response.data:
            raise HTTPException(status_code=404, detail="Preview not found")

        preview = preview_response.data[0]

        # Check preview status - should be completed (ACTIVE) or generating
        if preview["status"] not in [PreviewStatus.ACTIVE.value, PreviewStatus.GENERATING.value, "completed"]:
            logger.warning(
                "Preview not ready for payment",
                preview_id=request.preview_id,
                status=preview["status"]
            )
            # Allow anyway for testing
            pass

        # Generate order ID if not provided
        order_id = request.order_id or f"test-order-{uuid.uuid4().hex[:8]}"
        order_number = int(datetime.utcnow().timestamp())

        # Check if order already exists (idempotency)
        existing_order = db.table("orders").select("*").eq("order_id", order_id).execute()
        if existing_order.data:
            logger.info("Order already exists", order_id=order_id)
            return TestPaymentResponse(
                success=True,
                order_id=order_id,
                preview_id=request.preview_id,
                status="already_processed",
                message="Order was already processed"
            )

        # Create order record
        # Note: .get() default only works if key is missing, not if value is None
        order_data = {
            "order_id": order_id,
            "order_number": order_number,
            "preview_id": request.preview_id,
            "customer_email": preview.get("customer_email") or "test@example.com",
            "customer_name": preview.get("child_name") or "Test Customer",
            "status": OrderStatus.PAID.value,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }

        db.table("orders").insert(order_data).execute()
        logger.info("Test order created", order_id=order_id)

        # Update preview status to PURCHASED
        db.table("previews").update({
            "status": PreviewStatus.PURCHASED.value
        }).eq("preview_id", request.preview_id).execute()

        # Create PDF generation job
        job_id = str(uuid.uuid4())
        job_data = {
            "job_id": job_id,
            "job_type": JobType.PDF_CREATION.value,
            "reference_id": order_id,
            "status": JobStatus.QUEUED.value,
            "progress": 0,
            "queued_at": datetime.utcnow().isoformat(),
            "current_step": "Starting PDF generation..."
        }
        db.table("generation_jobs").insert(job_data).execute()

        # Trigger PDF generation in background
        # Note: generate_pdf_from_order expects (order_id, preview_id, child_name)
        background_tasks.add_task(
            generate_pdf_from_order,
            order_id=order_id,
            preview_id=request.preview_id,
            child_name=preview["child_name"]
        )

        logger.info(
            "Test payment complete, PDF generation started",
            order_id=order_id,
            preview_id=request.preview_id,
            job_id=job_id
        )

        return TestPaymentResponse(
            success=True,
            order_id=order_id,
            preview_id=request.preview_id,
            status="paid",
            message="Payment simulated successfully. PDF generation started."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Test payment simulation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/order/{order_id}")
async def test_get_order(order_id: str):
    """
    Get test order details for debugging.
    """
    settings = get_settings()

    if not settings.testing_mode_enabled:
        raise HTTPException(
            status_code=403,
            detail="Test endpoints are disabled"
        )

    try:
        db = get_db()
        order_response = db.table("orders").select("*").eq("order_id", order_id).execute()

        if not order_response.data:
            raise HTTPException(status_code=404, detail="Order not found")

        order = order_response.data[0]

        # Get associated preview
        preview_response = db.table("previews").select("*").eq("preview_id", order["preview_id"]).execute()
        preview = preview_response.data[0] if preview_response.data else None

        # Get PDF job status
        job_response = db.table("generation_jobs").select("*").eq("reference_id", order_id).execute()
        job = job_response.data[0] if job_response.data else None

        return {
            "order": order,
            "preview": preview,
            "pdf_job": job
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

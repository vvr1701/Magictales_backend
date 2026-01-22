"""
Shopify webhook handlers.
"""

import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
import structlog

from app.config import get_settings
from app.models.database import get_db
from app.models.enums import OrderStatus, PreviewStatus
from app.core.security import verify_shopify_webhook, verify_shop_domain
from app.background.tasks import generate_pdf

logger = structlog.get_logger()
router = APIRouter()


@router.post("/order-paid")
async def handle_order_paid(request: Request, background_tasks: BackgroundTasks):
    """
    Handle Shopify orders/paid webhook.

    Flow:
    1. Verify HMAC signature
    2. Verify shop domain
    3. Check idempotency (order not already processed)
    4. Extract preview_id from line item properties
    5. Create order record
    6. Queue PDF generation
    7. Return 200 immediately
    """

    settings = get_settings()

    try:
        logger.info("Received Shopify order-paid webhook")

        # Step 1: Verify HMAC signature and get verified body
        verified_body = await verify_shopify_webhook(request, settings.shopify_webhook_secret)

        # Step 2: Verify shop domain
        verify_shop_domain(request, settings.shopify_shop_domain)

        # Parse the verified body (no need to read again - prevents race condition)
        webhook_data = json.loads(verified_body.decode('utf-8'))

        # Extract order information
        order_id = str(webhook_data.get("id"))
        order_number = webhook_data.get("order_number")
        customer_email = webhook_data.get("customer", {}).get("email")
        customer_name = f"{webhook_data.get('customer', {}).get('first_name', '')} {webhook_data.get('customer', {}).get('last_name', '')}".strip()

        if not customer_email:
            logger.error("No customer email in webhook", order_id=order_id)
            # Still return 200 to acknowledge webhook
            return {"success": True, "message": "Webhook received but missing customer email"}

        # Step 3: Check idempotency
        db = get_db()
        existing_order = db.table("orders").select("*").eq("order_id", order_id).execute()

        if existing_order.data:
            logger.info("Order already processed", order_id=order_id)
            return {"success": True, "message": "Order already processed"}

        # Step 4: Extract preview_id from line item properties
        # Note: Frontend sends '_preview_id' (underscore prefix hides from customer)
        # We check for both 'preview_id' and '_preview_id' for compatibility
        preview_id = None
        line_items = webhook_data.get("line_items", [])

        for item in line_items:
            properties = item.get("properties", [])
            for prop in properties:
                prop_name = prop.get("name", "")
                # Check for both '_preview_id' (hidden) and 'preview_id' (visible)
                if prop_name in ("_preview_id", "preview_id"):
                    preview_id = prop.get("value")
                    logger.info("Found preview_id in line item",
                               property_name=prop_name,
                               preview_id=preview_id)
                    break
            if preview_id:
                break

        if not preview_id:
            logger.error("No preview_id found in line items", order_id=order_id)
            # Still return 200 to acknowledge webhook
            return {"success": True, "message": "Webhook received but no preview_id found"}

        # Verify preview exists
        preview_response = db.table("previews").select("*").eq("preview_id", preview_id).execute()

        if not preview_response.data:
            logger.error("Preview not found", preview_id=preview_id, order_id=order_id)
            # TODO: Trigger refund via Shopify API - customer paid for non-existent preview
            return {"success": True, "message": "Preview not found", "action_required": "refund"}

        preview = preview_response.data[0]

        # Check if preview has expired
        expires_at = datetime.fromisoformat(preview["expires_at"].replace('Z', '+00:00'))
        preview_expired = expires_at < datetime.utcnow().replace(tzinfo=expires_at.tzinfo)

        if preview_expired:
            # GRACE PERIOD: If expired within last 24 hours, extend and continue
            # This handles cases where user started checkout just before expiry
            hours_since_expiry = (datetime.utcnow().replace(tzinfo=expires_at.tzinfo) - expires_at).total_seconds() / 3600

            if hours_since_expiry <= 24:
                # Extend preview by 7 days from now (grace period)
                new_expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()
                db.table("previews").update({
                    "expires_at": new_expires_at
                }).eq("preview_id", preview_id).execute()

                logger.warning(
                    "Extended expired preview (grace period)",
                    preview_id=preview_id,
                    order_id=order_id,
                    hours_since_expiry=round(hours_since_expiry, 2),
                    new_expires_at=new_expires_at
                )
            else:
                # Expired too long ago - log for manual review/refund
                logger.error(
                    "Preview expired beyond grace period - requires manual refund",
                    preview_id=preview_id,
                    order_id=order_id,
                    hours_since_expiry=round(hours_since_expiry, 2),
                    customer_email=customer_email
                )
                # Still create order record for tracking, but mark as needing attention
                order_data = {
                    "order_id": order_id,
                    "order_number": str(order_number) if order_number else None,
                    "preview_id": preview_id,
                    "customer_email": customer_email,
                    "customer_name": customer_name or None,
                    "status": OrderStatus.FAILED.value,
                    "error_message": f"Preview expired {round(hours_since_expiry, 1)} hours ago. Manual refund required.",
                    "retry_count": 0,
                    "created_at": datetime.utcnow().isoformat(),
                    "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
                }
                db.table("orders").insert(order_data).execute()

                return {
                    "success": True,
                    "message": "Preview expired - order marked for refund",
                    "action_required": "manual_refund",
                    "customer_email": customer_email
                }

        # Extract shipping address
        shipping_address = None
        if webhook_data.get("shipping_address"):
            shipping_address = {
                "first_name": webhook_data["shipping_address"].get("first_name"),
                "last_name": webhook_data["shipping_address"].get("last_name"),
                "address1": webhook_data["shipping_address"].get("address1"),
                "address2": webhook_data["shipping_address"].get("address2"),
                "city": webhook_data["shipping_address"].get("city"),
                "province": webhook_data["shipping_address"].get("province"),
                "country": webhook_data["shipping_address"].get("country"),
                "zip": webhook_data["shipping_address"].get("zip"),
            }

        # Step 5: Create order record
        order_data = {
            "order_id": order_id,
            "order_number": str(order_number) if order_number else None,
            "preview_id": preview_id,
            "customer_email": customer_email,
            "customer_name": customer_name or None,
            "status": OrderStatus.PAID.value,
            "shipping_address": shipping_address,
            "error_message": None,
            "retry_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow().replace(tzinfo=None) +
                          timedelta(days=30)).isoformat()
        }

        order_response = db.table("orders").insert(order_data).execute()

        if not order_response.data:
            logger.error("Failed to create order record", order_id=order_id)
            raise HTTPException(status_code=500, detail="Failed to create order")

        # CRITICAL: Update preview status to PURCHASED so frontend detects payment
        # This is what the frontend polls for after checkout_success=true
        db.table("previews").update({
            "status": PreviewStatus.PURCHASED.value,
            "generation_phase": "generating_full"
        }).eq("preview_id", preview_id).execute()
        
        logger.info("Preview status updated to PURCHASED", preview_id=preview_id)

        # Step 6: Queue PDF generation (remaining pages + PDF)
        # Get child_name from preview data (stored when preview was created)
        child_name_from_preview = preview.get("child_name", "Child")
        
        background_tasks.add_task(
            generate_pdf,
            order_id=order_id,
            preview_id=preview_id,
            child_name=child_name_from_preview  # CRITICAL: Required by generate_pdf
        )

        logger.info(
            "Order processed successfully",
            order_id=order_id,
            preview_id=preview_id,
            customer_email=customer_email
        )

        # Step 7: Return 200 immediately
        return {"success": True, "message": "Webhook received and processed"}

    except HTTPException:
        # Re-raise HTTP exceptions (HMAC/domain verification failures)
        raise

    except Exception as e:
        # Log detailed error for manual investigation/retry
        # Extract what we can from local variables for debugging
        error_context = {
            "error": str(e),
            "error_type": type(e).__name__,
        }
        
        # Try to get context from local variables if they exist
        try:
            error_context["order_id"] = order_id if 'order_id' in dir() else "unknown"
            error_context["preview_id"] = preview_id if 'preview_id' in dir() else "unknown"
            error_context["customer_email"] = customer_email if 'customer_email' in dir() else "unknown"
        except:
            pass
        
        logger.error(
            "WEBHOOK FAILED - REQUIRES MANUAL INVESTIGATION",
            **error_context
        )
        
        # Return 500 to trigger Shopify retry for transient errors
        # Shopify will retry up to 19 times over 48 hours
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


@router.post("/order-cancelled")
async def handle_order_cancelled(request: Request):
    """
    Handle Shopify orders/cancelled webhook.

    Optional: Handle order cancellations and refunds.
    """
    settings = get_settings()

    try:
        # Verify webhook and get verified body
        verified_body = await verify_shopify_webhook(request, settings.shopify_webhook_secret)
        verify_shop_domain(request, settings.shopify_shop_domain)

        # Parse verified body
        webhook_data = json.loads(verified_body.decode('utf-8'))

        order_id = str(webhook_data.get("id"))
        logger.info("Order cancelled", order_id=order_id)

        # Update order status if exists
        db = get_db()
        db.table("orders").update({
            "status": OrderStatus.REFUNDED.value
        }).eq("order_id", order_id).execute()

        return {"success": True, "message": "Order cancellation processed"}

    except Exception as e:
        logger.error("Failed to process cancellation webhook", error=str(e))
        return {"success": True, "message": "Webhook received"}


@router.post("/test")
async def test_webhook(request: Request):
    """
    Test webhook endpoint for development.
    Does not verify HMAC.
    """
    try:
        body = await request.body()
        if body:
            webhook_data = json.loads(body.decode('utf-8'))
            logger.info("Test webhook received", data=webhook_data)
        else:
            logger.info("Test webhook received with no body")

        return {"success": True, "message": "Test webhook received"}

    except Exception as e:
        logger.error("Test webhook error", error=str(e))
        return {"success": True, "message": "Test webhook error"}


@router.post("/test-order-paid")
async def test_order_paid(request: Request, background_tasks: BackgroundTasks):
    """
    TEST ENDPOINT: Simulate order-paid webhook without HMAC verification.
    
    For local development only! Does not verify HMAC or shop domain.
    
    Usage:
    POST /webhooks/shopify/test-order-paid
    {
        "preview_id": "your-preview-id",
        "customer_email": "test@example.com"
    }
    """
    try:
        body = await request.body()
        webhook_data = json.loads(body.decode('utf-8'))
        
        preview_id = webhook_data.get("preview_id")
        customer_email = webhook_data.get("customer_email", "test@example.com")
        order_id = webhook_data.get("order_id", f"test_{datetime.utcnow().timestamp()}")
        
        if not preview_id:
            raise HTTPException(status_code=400, detail="preview_id is required")
        
        logger.info(
            "TEST order-paid webhook received",
            preview_id=preview_id,
            order_id=order_id
        )
        
        # Verify preview exists
        db = get_db()
        preview_response = db.table("previews").select("*").eq("preview_id", preview_id).execute()
        
        if not preview_response.data:
            raise HTTPException(status_code=404, detail=f"Preview not found: {preview_id}")
        
        preview = preview_response.data[0]
        
        # Create order record
        order_data = {
            "order_id": str(order_id),
            "order_number": "TEST-001",
            "preview_id": preview_id,
            "customer_email": customer_email,
            "customer_name": "Test User",
            "status": OrderStatus.PAID.value,
            "shipping_address": None,
            "error_message": None,
            "retry_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        
        # Check if order already exists
        existing = db.table("orders").select("*").eq("order_id", str(order_id)).execute()
        if existing.data:
            logger.info("Order already exists, skipping creation", order_id=order_id)
        else:
            db.table("orders").insert(order_data).execute()
        
        # Queue PDF generation - must pass child_name
        child_name_from_preview = preview.get("child_name", "Child")
        background_tasks.add_task(
            generate_pdf,
            order_id=str(order_id),
            preview_id=preview_id,
            child_name=child_name_from_preview
        )
        
        logger.info(
            "TEST order processed - PDF generation queued",
            order_id=order_id,
            preview_id=preview_id
        )
        
        return {
            "success": True,
            "message": "Test order created and PDF generation started",
            "order_id": str(order_id),
            "preview_id": preview_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Test order-paid failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
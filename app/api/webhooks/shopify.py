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

        # Step 1: Verify HMAC signature
        await verify_shopify_webhook(request, settings.shopify_webhook_secret)

        # Step 2: Verify shop domain
        verify_shop_domain(request, settings.shopify_shop_domain)

        # Get the raw body again for parsing
        body = await request.body()
        webhook_data = json.loads(body.decode('utf-8'))

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
        preview_id = None
        line_items = webhook_data.get("line_items", [])

        for item in line_items:
            properties = item.get("properties", [])
            for prop in properties:
                if prop.get("name") == "preview_id":
                    preview_id = prop.get("value")
                    break
            if preview_id:
                break

        if not preview_id:
            logger.error("No preview_id found in line items", order_id=order_id)
            # Still return 200 to acknowledge webhook
            return {"success": True, "message": "Webhook received but no preview_id found"}

        # Verify preview exists and is not expired
        preview_response = db.table("previews").select("*").eq("preview_id", preview_id).execute()

        if not preview_response.data:
            logger.error("Preview not found", preview_id=preview_id, order_id=order_id)
            return {"success": True, "message": "Preview not found"}

        preview = preview_response.data[0]

        # Check if preview has expired
        expires_at = datetime.fromisoformat(preview["expires_at"].replace('Z', '+00:00'))
        if expires_at < datetime.utcnow().replace(tzinfo=expires_at.tzinfo):
            logger.error("Preview has expired", preview_id=preview_id, order_id=order_id)
            return {"success": True, "message": "Preview has expired"}

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

        # Step 6: Queue PDF generation
        background_tasks.add_task(
            generate_pdf,
            order_id=order_id,
            preview_id=preview_id
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
        logger.error("Failed to process webhook", error=str(e))
        # Always return 200 for webhooks to prevent retries
        # Log the error for investigation
        return {"success": True, "message": f"Webhook received but processing failed: {str(e)}"}


@router.post("/order-cancelled")
async def handle_order_cancelled(request: Request):
    """
    Handle Shopify orders/cancelled webhook.

    Optional: Handle order cancellations and refunds.
    """
    settings = get_settings()

    try:
        # Verify webhook
        await verify_shopify_webhook(request, settings.shopify_webhook_secret)
        verify_shop_domain(request, settings.shopify_shop_domain)

        # Get webhook data
        body = await request.body()
        webhook_data = json.loads(body.decode('utf-8'))

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
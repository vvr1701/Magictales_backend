"""
Security utilities for webhook verification and signed URLs.
"""

import hmac
import hashlib
import base64
from fastapi import Request, HTTPException
import structlog

logger = structlog.get_logger()


async def verify_shopify_webhook(request: Request, secret: str) -> bool:
    """
    Verify Shopify webhook HMAC signature.

    CRITICAL: Must read raw body before any parsing.
    """
    try:
        # Get signature from header
        shopify_hmac = request.headers.get("X-Shopify-Hmac-Sha256")
        if not shopify_hmac:
            logger.warning("Missing HMAC signature in webhook")
            raise HTTPException(status_code=401, detail="Missing HMAC signature")

        # Get raw body
        body = await request.body()

        # Compute expected signature
        computed_hmac = base64.b64encode(
            hmac.new(
                secret.encode("utf-8"),
                body,
                hashlib.sha256
            ).digest()
        ).decode("utf-8")

        # Compare signatures
        if not hmac.compare_digest(computed_hmac, shopify_hmac):
            logger.warning("Invalid HMAC signature in webhook")
            raise HTTPException(status_code=401, detail="Invalid HMAC signature")

        logger.info("Webhook HMAC signature verified")
        return True

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Webhook verification failed", error=str(e))
        raise HTTPException(status_code=500, detail="Webhook verification failed")


def verify_shop_domain(request: Request, expected_domain: str) -> bool:
    """Verify webhook came from expected shop."""
    shop_domain = request.headers.get("X-Shopify-Shop-Domain")
    if shop_domain != expected_domain:
        logger.warning("Invalid shop domain", received=shop_domain, expected=expected_domain)
        raise HTTPException(status_code=401, detail="Invalid shop domain")
    return True
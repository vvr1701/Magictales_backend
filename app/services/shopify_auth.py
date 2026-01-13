"""
Shopify App Proxy signature verification.

Shopify signs all App Proxy requests with HMAC-SHA256.
The signature is passed as a 'signature' query parameter.

This is DIFFERENT from webhook verification which uses headers.
"""

import hmac
import hashlib
from fastapi import Request
import structlog

from app.config import get_settings

logger = structlog.get_logger()


async def verify_proxy_signature(request: Request) -> bool:
    """
    Verify that the request coming to /proxy endpoints is truly from Shopify.
    
    Algorithm:
    1. Get all query parameters
    2. Pop the signature (we don't hash the signature itself)
    3. Sort parameters alphabetically by key
    4. Concatenate as "key1=value1key2=value2" (NO separators)
    5. Compute HMAC-SHA256 with API secret
    6. Compare with provided signature
    
    Returns True if valid, False otherwise.
    """
    settings = get_settings()
    
    # 1. Get all query parameters
    query_params = dict(request.query_params)
    
    # 2. Pop the signature (we don't hash the signature itself)
    signature = query_params.pop("signature", None)
    if not signature:
        logger.debug("No signature in request, skipping verification")
        return False

    # 3. Sort parameters alphabetically and create the string
    # Format: "key1=value1key2=value2" (No separator for Proxy HMAC)
    sorted_params = "".join(f"{k}={query_params[k]}" for k in sorted(query_params))

    # 4. Calculate HMAC-SHA256
    computed_hmac = hmac.new(
        settings.shopify_api_secret.encode('utf-8'),
        sorted_params.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # 5. Compare (timing-safe)
    is_valid = hmac.compare_digest(computed_hmac, signature)
    
    if is_valid:
        logger.debug("Shopify App Proxy signature verified successfully")
    else:
        logger.warning(
            "Invalid App Proxy signature",
            computed=computed_hmac[:10] + "...",
            received=signature[:10] + "..."
        )
    
    return is_valid

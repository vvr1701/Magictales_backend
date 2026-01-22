"""
Rate limiter configuration for API endpoints.

Uses slowapi for request rate limiting to prevent abuse.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize rate limiter with IP-based key function
# Default limit: 200 requests per minute (can be overridden per endpoint)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
    # Use memory storage (for single-instance deployments)
    # For multi-instance, configure Redis: storage_uri="redis://localhost:6379"
)

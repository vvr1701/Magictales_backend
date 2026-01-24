"""
My Creations API endpoint.

Allows users to fetch their previously generated story previews.
Works for both logged-in Shopify customers and guest sessions.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import structlog

from app.models.database import get_db

logger = structlog.get_logger()
router = APIRouter()


# ==================
# Response Models
# ==================

class CreationItem(BaseModel):
    preview_id: str
    child_name: str
    theme: str
    cover_url: Optional[str] = None
    status: str
    payment_status: str  # "unpaid" or "paid"
    created_at: str
    expires_at: str
    days_remaining: int
    job_id: Optional[str] = None  # For in-progress generation


class MyCreationsResponse(BaseModel):
    creations: List[CreationItem]
    total: int
    can_create_more: bool  # False if guest has hit 3-story limit


class LinkSessionRequest(BaseModel):
    session_id: str


class LinkSessionResponse(BaseModel):
    linked_count: int
    message: str


# ==================
# Helper Functions
# ==================

def extract_session_and_customer(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract session_id and customer_id from request headers."""
    session_id = request.headers.get("X-Session-Id")
    customer_id = request.headers.get("X-Shopify-Customer-Id")
    
    # Clean null-like values
    if session_id in (None, "", "null", "undefined"):
        session_id = None
    if customer_id in (None, "", "null", "undefined"):
        customer_id = None
    
    return session_id, customer_id


def calculate_days_remaining(expires_at_str: str) -> int:
    """Calculate days remaining until expiration."""
    try:
        from datetime import timezone
        expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        delta = expires_at - now
        return max(0, delta.days)
    except Exception:
        return 0


# ==================
# API Endpoints
# ==================

@router.get("/my-creations", response_model=MyCreationsResponse)
async def get_my_creations(request: Request):
    """
    Fetch all non-expired previews for the current user.
    
    - If logged in (X-Shopify-Customer-Id): fetch by customer_id
    - If guest (X-Session-Id): fetch by session_id
    - Results are sorted by created_at DESC
    - Expired previews are automatically filtered out
    """
    try:
        session_id, customer_id = extract_session_and_customer(request)
        
        if not session_id and not customer_id:
            # No identification - return empty
            return MyCreationsResponse(creations=[], total=0, can_create_more=True)
        
        db = get_db()
        now = datetime.utcnow()
        
        # Build query - fetch previews and filter non-expired in Python
        # For logged-in users, fetch by customer_id
        # For guests, fetch by session_id
        if customer_id:
            # Logged-in user: fetch by customer_id
            result = db.table("previews").select("*").eq(
                "customer_id", customer_id
            ).order("created_at", desc=True).limit(50).execute()
        else:
            # Guest: fetch by session_id
            result = db.table("previews").select("*").eq(
                "session_id", session_id
            ).order("created_at", desc=True).limit(50).execute()
        
        # Filter out expired previews in Python
        all_previews = result.data or []
        previews = []
        for p in all_previews:
            try:
                expires_at = datetime.fromisoformat(p["expires_at"].replace("Z", "+00:00")).replace(tzinfo=None)
                if expires_at > now:
                    previews.append(p)
            except (ValueError, KeyError):
                pass
        
        # Check if each preview has been paid for
        preview_ids = [p["preview_id"] for p in previews]
        paid_previews = set()
        
        if preview_ids:
            orders = db.table("orders").select("preview_id").in_("preview_id", preview_ids).execute()
            paid_previews = {o["preview_id"] for o in (orders.data or [])}
        
        # Get job_ids for any in-progress generations
        job_map = {}
        if preview_ids:
            jobs = db.table("generation_jobs").select(
                "job_id,reference_id,status"
            ).in_("reference_id", preview_ids).execute()
            for job in (jobs.data or []):
                job_map[job["reference_id"]] = job["job_id"]
        
        # Build response
        creations = []
        for p in previews:
            # Get cover URL from cover_url or preview_images
            cover_url = p.get("cover_url")
            if not cover_url and p.get("preview_images"):
                images = p.get("preview_images", [])
                if images:
                    # First image might be cover (page 0) or first page
                    cover_url = images[0] if isinstance(images[0], str) else images[0].get("url")
            
            creations.append(CreationItem(
                preview_id=p["preview_id"],
                child_name=p["child_name"],
                theme=p["theme"],
                cover_url=cover_url,
                status=p["status"],
                payment_status="paid" if p["preview_id"] in paid_previews else "unpaid",
                created_at=p["created_at"],
                expires_at=p["expires_at"],
                days_remaining=calculate_days_remaining(p["expires_at"]),
                job_id=job_map.get(p["preview_id"])
            ))
        
        # Determine if user can create more (guests limited to 3)
        can_create_more = True
        if not customer_id and session_id:
            # Guest user - check limit
            can_create_more = len(creations) < 3
        
        logger.info(
            "Fetched my creations",
            customer_id=customer_id,
            session_id=session_id[:20] if session_id else None,
            count=len(creations)
        )
        
        return MyCreationsResponse(
            creations=creations,
            total=len(creations),
            can_create_more=can_create_more
        )
    except Exception as e:
        logger.error(
            "Error fetching my creations",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=f"Failed to fetch creations: {str(e)}")


@router.post("/link-session", response_model=LinkSessionResponse)
async def link_session_to_customer(request: Request):
    """
    Link guest session previews to a Shopify customer account.
    
    Called after login to migrate guest creations to the user's account.
    - Reads X-Session-Id and X-Shopify-Customer-Id from headers
    - Updates all previews with matching session_id to have customer_id
    """
    session_id, customer_id = extract_session_and_customer(request)
    
    if not customer_id:
        raise HTTPException(status_code=400, detail="Customer ID required (not logged in)")
    
    if not session_id:
        # No session to link
        return LinkSessionResponse(linked_count=0, message="No session to link")
    
    db = get_db()
    
    # Update all previews with this session_id to have the customer_id
    # Only update if customer_id is currently null
    result = db.table("previews").update({
        "customer_id": customer_id
    }).eq("session_id", session_id).is_("customer_id", None).execute()
    
    linked_count = len(result.data) if result.data else 0
    
    logger.info(
        "Linked session to customer",
        session_id=session_id[:20] if session_id else None,
        customer_id=customer_id,
        linked_count=linked_count
    )
    
    return LinkSessionResponse(
        linked_count=linked_count,
        message=f"Linked {linked_count} creation(s) to your account"
    )


@router.get("/my-creations/count")
async def get_creation_count(request: Request):
    """
    Get the count of non-expired creations for the current session.
    Used to check guest limit before creating new preview.
    """
    session_id, customer_id = extract_session_and_customer(request)
    
    if customer_id:
        # Logged-in users have no limit
        return {"count": 0, "limit": None, "can_create": True}
    
    if not session_id:
        return {"count": 0, "limit": 3, "can_create": True}
    
    db = get_db()
    now = datetime.utcnow()
    
    # Fetch all previews for this session and count non-expired in Python
    result = db.table("previews").select("preview_id, expires_at").eq(
        "session_id", session_id
    ).execute()
    
    # Count non-expired in Python
    count = 0
    if result.data:
        for row in result.data:
            try:
                expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00")).replace(tzinfo=None)
                if expires_at > now:
                    count += 1
            except (ValueError, KeyError):
                pass
    
    can_create = count < 3
    
    return {
        "count": count,
        "limit": 3,
        "can_create": can_create
    }

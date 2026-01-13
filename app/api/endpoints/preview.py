"""
Preview creation and retrieval endpoints.

Shopify Integration:
- Frontend passes X-Shopify-Customer-Id and X-Shopify-Customer-Email headers
- These headers are extracted from Liquid data attributes injected by Shopify
- Customer ID is stored with preview for order linking
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
import structlog

from app.models.schemas import (
    PreviewCreateRequest,
    JobStartResponse,
    PreviewResponse,
    PageData,
    ErrorResponse
)
from app.models.database import get_db
from app.models.enums import PreviewStatus, JobStatus, JobType, BookStyle
from app.background.tasks import generate_full_preview
from app.config import get_settings

logger = structlog.get_logger()
router = APIRouter()


def extract_shopify_customer_context(request: Request) -> tuple[Optional[str], Optional[str]]:
    """
    Extract Shopify customer ID and email from request headers.

    These headers are added by the frontend when running in Shopify:
    - X-Shopify-Customer-Id: The Shopify customer ID
    - X-Shopify-Customer-Email: The customer's email

    Returns:
        tuple: (customer_id, customer_email) - either can be None if not present
    """
    customer_id = request.headers.get("X-Shopify-Customer-Id")
    customer_email = request.headers.get("X-Shopify-Customer-Email")

    # Clean up null-like values
    if customer_id in (None, "", "null", "undefined"):
        customer_id = None
    if customer_email in (None, "", "null", "undefined"):
        customer_email = None

    return customer_id, customer_email


@router.post("/preview", response_model=JobStartResponse)
async def create_preview(
    preview_request: PreviewCreateRequest,
    background_tasks: BackgroundTasks,
    request: Request
):
    """
    Create a new preview generation job.

    This endpoint:
    1. Extracts Shopify customer context from headers (if present)
    2. Creates preview and job records in database
    3. Starts background task to generate ALL 10 pages + 5 watermarked previews
    4. Returns job_id for status polling

    The background task generates all images upfront.

    Shopify Integration:
    - X-Shopify-Customer-Id header is stored as customer_id
    - X-Shopify-Customer-Email header is stored as customer_email
    - These are used to link previews to Shopify customers for order matching
    """

    try:
        # Extract Shopify customer context from headers
        shopify_customer_id, shopify_customer_email = extract_shopify_customer_context(request)

        logger.info(
            "Creating preview",
            child_name=preview_request.child_name,
            theme=preview_request.theme,
            shopify_customer_id=shopify_customer_id
        )

        settings = get_settings()
        db = get_db()

        # Generate IDs
        preview_id = str(uuid.uuid4())
        job_id = str(uuid.uuid4())

        # Determine customer email: prefer Shopify header, fallback to request body
        customer_email = shopify_customer_email or preview_request.customer_email

        # Create preview record with Shopify customer info
        preview_data = {
            "preview_id": preview_id,
            "session_id": preview_request.session_id,
            "customer_id": shopify_customer_id,  # Shopify customer ID from header
            "customer_email": customer_email,
            "child_name": preview_request.child_name,
            "child_age": preview_request.child_age,
            "child_gender": preview_request.child_gender,
            "theme": preview_request.theme.value,
            "style": preview_request.style.value,
            "photo_url": preview_request.photo_url,
            "photo_validated": True,
            "status": PreviewStatus.GENERATING.value,
            "hires_images": [],
            "preview_images": [],
            "story_pages": [],
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }

        preview_response = db.table("previews").insert(preview_data).execute()
        if not preview_response.data:
            raise Exception("Failed to create preview record")

        # Create job record
        job_data = {
            "job_id": job_id,
            "job_type": JobType.PREVIEW_GENERATION.value,
            "reference_id": preview_id,
            "status": JobStatus.QUEUED.value,
            "progress": 0,
            "queued_at": datetime.utcnow().isoformat(),
            "attempts": 0,
            "max_attempts": 3
        }

        job_response = db.table("generation_jobs").insert(job_data).execute()
        if not job_response.data:
            raise Exception("Failed to create job record")

        # Start background generation task using NanoBanana pipeline
        # All themes now use the NanoBanana pipeline (storygift approach)
        theme_value = preview_request.theme.value

        background_tasks.add_task(
            generate_full_preview,
            job_id=job_id,
            preview_id=preview_id,
            photo_url=preview_request.photo_url,
            child_name=preview_request.child_name,
            child_age=preview_request.child_age,
            child_gender=preview_request.child_gender,
            theme=theme_value,
            style=preview_request.style.value  # Pass art style to background task
        )

        logger.info("Preview generation job started", job_id=job_id, preview_id=preview_id, style=preview_request.style.value)

        return JobStartResponse(
            job_id=job_id,
            preview_id=preview_id,
            status=JobStatus.QUEUED,
            estimated_time_seconds=180,  # ~3 minutes
            message="Your personalized storybook is being generated..."
        )

    except Exception as e:
        logger.error("Failed to create preview", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to start preview generation. Please try again."
        )


@router.post("/preview/{job_id}/retry", response_model=JobStartResponse)
async def retry_preview_generation(
    job_id: str,
    background_tasks: BackgroundTasks
):
    """
    Retry a failed preview generation job.

    This endpoint:
    1. Checks if the job exists and has failed
    2. Verifies retry attempts haven't exceeded max
    3. Creates a new job with the same preview data
    4. Starts background task to resume generation

    The retry uses existing preview/photo data.
    """

    try:
        logger.info("Retrying failed job", job_id=job_id)

        db = get_db()

        # Get the failed job
        job_response = db.table("generation_jobs").select("*").eq("job_id", job_id).execute()

        if not job_response.data:
            raise HTTPException(status_code=404, detail="Job not found")

        old_job = job_response.data[0]

        # Verify it's a failed job
        if old_job["status"] != JobStatus.FAILED.value:
            raise HTTPException(
                status_code=400,
                detail="Only failed jobs can be retried"
            )

        # Check retry attempts
        if old_job["attempts"] >= old_job["max_attempts"]:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum retry attempts ({old_job['max_attempts']}) exceeded. Please create a new story."
            )

        preview_id = old_job["reference_id"]

        # Get preview data
        preview_response = db.table("previews").select("*").eq("preview_id", preview_id).execute()

        if not preview_response.data:
            raise HTTPException(status_code=404, detail="Preview data not found")

        preview = preview_response.data[0]

        # Create new job record for retry
        new_job_id = str(uuid.uuid4())
        new_job_data = {
            "job_id": new_job_id,
            "job_type": JobType.PREVIEW_GENERATION.value,
            "reference_id": preview_id,
            "status": JobStatus.QUEUED.value,
            "progress": 0,
            "queued_at": datetime.utcnow().isoformat(),
            "attempts": old_job["attempts"] + 1,  # Increment attempt count
            "max_attempts": old_job["max_attempts"],
            "current_step": "Retrying generation..."
        }

        db.table("generation_jobs").insert(new_job_data).execute()

        # Update preview status back to GENERATING
        db.table("previews").update({
            "status": PreviewStatus.GENERATING.value
        }).eq("preview_id", preview_id).execute()

        # Start background generation task
        background_tasks.add_task(
            generate_full_preview,
            job_id=new_job_id,
            preview_id=preview_id,
            photo_url=preview["photo_url"],
            child_name=preview["child_name"],
            child_age=preview["child_age"],
            child_gender=preview["child_gender"],
            theme=preview["theme"],
            style=preview.get("style", "photorealistic")
        )

        logger.info("Preview retry job started", 
                   old_job_id=job_id, 
                   new_job_id=new_job_id, 
                   preview_id=preview_id,
                   attempt=old_job["attempts"] + 1)

        return JobStartResponse(
            job_id=new_job_id,
            preview_id=preview_id,
            status=JobStatus.QUEUED,
            estimated_time_seconds=180,
            message=f"Retrying generation (attempt {old_job['attempts'] + 1} of {old_job['max_attempts']})..."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retry preview", job_id=job_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retry generation. Please try again."
        )

@router.get("/preview/{preview_id}", response_model=PreviewResponse)
async def get_preview(preview_id: str):
    """
    Get preview data for display.

    Returns preview pages (watermarked) and locked pages info.
    Only available after generation is complete.
    
    generation_phase values:
    - 'preview': Only first 5 pages generated (pre-payment)
    - 'generating_full': Remaining 5 pages being generated (post-payment)
    - 'complete': All 10 pages and PDF ready
    """

    try:
        logger.info("Getting preview", preview_id=preview_id)

        db = get_db()

        # Get preview record
        preview_response = db.table("previews").select("*").eq("preview_id", preview_id).execute()

        if not preview_response.data:
            raise HTTPException(status_code=404, detail="Preview not found")

        preview = preview_response.data[0]

        # Check if preview has expired
        expires_at = datetime.fromisoformat(preview["expires_at"].replace('Z', '+00:00'))
        if expires_at < datetime.utcnow().replace(tzinfo=expires_at.tzinfo):
            raise HTTPException(status_code=410, detail="Preview has expired")

        # Check if preview is ready - allow GENERATING status to return partial data
        if preview["status"] == PreviewStatus.FAILED.value:
            raise HTTPException(status_code=500, detail="Preview generation failed")
        
        # For GENERATING status, we'll return partial data (whatever is available)
        is_generating = preview["status"] == PreviewStatus.GENERATING.value
        
        # Get generation phase
        generation_phase = preview.get("generation_phase", "preview")
        is_purchased = preview["status"] == PreviewStatus.PURCHASED.value

        # Prepare preview pages
        preview_pages = []
        
        # Get cover URL if available
        cover_url = preview.get("cover_url")
        
        # Add cover as page 0 (first page) if available
        if cover_url:
            preview_pages.append(PageData(
                page_number=0,
                image_url=cover_url,
                story_text="",  # Cover has no story text - text is overlaid
                is_watermarked=not is_purchased,
                is_locked=False,
                is_cover=True  # Flag this as cover page
            ))
        
        # For paid users with complete generation: show ALL 10 hi-res pages
        if is_purchased and generation_phase == 'complete' and preview.get("hires_images"):
            for img_data in preview["hires_images"]:
                story_page = next(
                    (sp for sp in preview["story_pages"] if sp["page"] == img_data["page"]),
                    None
                )
                preview_pages.append(PageData(
                    page_number=img_data["page"],
                    image_url=img_data["url"],  # Hi-res, no watermark
                    story_text=story_page["text"] if story_page else "",
                    is_watermarked=False,  # No watermark for paid users
                    is_locked=False
                ))
        else:
            # For unpaid or in-progress: show first 5 watermarked
            if preview.get("preview_images"):
                for img_data in preview["preview_images"]:
                    story_page = next(
                        (sp for sp in preview["story_pages"] if sp["page"] == img_data["page"]),
                        None
                    )
                    preview_pages.append(PageData(
                        page_number=img_data["page"],
                        image_url=img_data["url"],
                        story_text=story_page["text"] if story_page else "",
                        is_watermarked=not is_purchased,  # No watermark if purchased
                        is_locked=False
                    ))

        # Prepare locked pages (pages 6-10)
        # Only show for unpaid users in preview phase
        locked_pages = []
        
        if not is_purchased and generation_phase == 'preview':
            # Get theme template for teaser text
            from app.stories.themes import get_theme
            theme_template = get_theme(preview["theme"])
            
            # Show pages 6-10 as locked with teaser text from template
            for page_num in range(6, 11):
                page_idx = page_num - 1  # 0-indexed
                if page_idx < len(theme_template.pages):
                    teaser_text = theme_template.pages[page_idx].story_text
                    # Replace {name} and truncate for teaser
                    teaser_text = teaser_text.replace('{name}', preview["child_name"])
                    teaser_preview = teaser_text[:80] + "..." if len(teaser_text) > 80 else teaser_text
                else:
                    teaser_preview = "More adventure awaits..."
                
                locked_pages.append(PageData(
                    page_number=page_num,
                    image_url="",  # No image for locked pages
                    story_text=teaser_preview,  # Teaser text to create FOMO
                    is_watermarked=False,
                    is_locked=True
                ))
        # Note: For paid users with complete phase, locked_pages stays empty (all pages in preview_pages)

        # Calculate days remaining
        days_remaining = max(0, (expires_at - datetime.utcnow().replace(tzinfo=expires_at.tzinfo)).days)

        # Get theme title
        from app.stories.themes import get_theme
        theme_template = get_theme(preview["theme"])
        story_title = theme_template.get_title(preview["child_name"])

        # Build checkout URL (for Shopify)
        settings = get_settings()
        checkout_url = f"https://{settings.shopify_shop_domain}/cart/add?id=PRODUCT_VARIANT_ID&properties[preview_id]={preview_id}"

        return PreviewResponse(
            preview_id=preview_id,
            status=PreviewStatus(preview["status"]),
            generation_phase=generation_phase,  # NEW: Include generation phase
            story_title=story_title,
            child_name=preview["child_name"],
            theme=preview["theme"],
            style=preview.get("style", "photorealistic"),
            cover_url=cover_url,  # Dedicated cover image URL
            preview_pages=preview_pages,
            locked_pages=locked_pages,
            total_pages=11,  # 1 cover + 10 story pages
            preview_pages_count=len(preview_pages),
            locked_pages_count=len(locked_pages),
            expires_at=expires_at,
            days_remaining=days_remaining,
            pdf_url=preview.get("pdf_url"),  # PDF URL (only after payment + generation)
            purchase={
                "price": 2999,  # $29.99 in cents
                "currency": "USD",
                "price_formatted": "$29.99",
                "checkout_url": checkout_url
            }
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error("Failed to get preview", preview_id=preview_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve preview. Please try again."
        )


# ============================================
# TEST ENDPOINT - Trigger remaining page generation
# ============================================
@router.post("/test/trigger-completion/{preview_id}")
async def test_trigger_completion(preview_id: str, background_tasks: BackgroundTasks):
    """
    TEST ONLY: Triggers the remaining page generation for a preview.
    This simulates what happens after Shopify webhook confirms payment.
    
    Usage: POST /api/preview/test/trigger-completion/{preview_id}
    """
    from app.background.tasks import generate_remaining_pages
    from app.models.enums import OrderStatus
    from datetime import datetime, timedelta
    
    logger.info("TEST: Triggering remaining page generation", preview_id=preview_id)
    
    db = get_db()
    
    # Verify preview exists
    result = db.table("previews").select("*").eq("preview_id", preview_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Preview not found")
    
    preview = result.data[0]
    
    # Create a test order_id
    order_id = f"test-order-{preview_id[:8]}"
    
    # Check if order already exists
    existing_order = db.table("orders").select("*").eq("order_id", order_id).execute()
    
    if not existing_order.data:
        # Create order record (required for download endpoint)
        # Schema matches actual Shopify webhook order creation
        db.table("orders").insert({
            "order_id": order_id,
            "order_number": "TEST-001",  # Matches actual schema
            "preview_id": preview_id,
            "customer_email": "test@example.com",
            "status": OrderStatus.PAID.value,  # Use PAID like Shopify webhook
            "error_message": None,
            "retry_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }).execute()
        logger.info("TEST: Created order record", order_id=order_id)
    
    # Update preview status to simulate payment
    db.table("previews").update({
        "status": PreviewStatus.PURCHASED.value,
        "generation_phase": "generating_full"
    }).eq("preview_id", preview_id).execute()
    
    # Get child_name from preview (required by generate_remaining_pages)
    child_name = preview.get("child_name", "Child")
    
    # Queue the remaining page generation
    background_tasks.add_task(
        generate_remaining_pages,
        order_id=order_id,
        preview_id=preview_id,
        child_name=child_name  # CRITICAL: This was missing!
    )
    
    return {
        "status": "triggered",
        "message": f"Remaining page generation started for preview {preview_id}",
        "order_id": order_id,
        "child_name": child_name,
        "note": "Order record created. Download endpoint will work after generation completes."
    }
"""
Preview creation and retrieval endpoints.
"""

import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import structlog

from app.models.schemas import (
    PreviewCreateRequest,
    JobStartResponse,
    PreviewResponse,
    PageData,
    ErrorResponse
)
from app.models.database import get_db
from app.models.enums import PreviewStatus, JobStatus, JobType
from app.background.tasks import generate_full_preview
from app.config import get_settings

logger = structlog.get_logger()
router = APIRouter()


@router.post("/preview", response_model=JobStartResponse)
async def create_preview(
    request: PreviewCreateRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new preview generation job.

    This endpoint:
    1. Creates preview and job records in database
    2. Starts background task to generate ALL 10 pages + 5 watermarked previews
    3. Returns job_id for status polling

    The background task generates all images upfront.
    """

    try:
        logger.info("Creating preview", child_name=request.child_name, theme=request.theme)

        settings = get_settings()
        db = get_db()

        # Generate IDs
        preview_id = str(uuid.uuid4())
        job_id = str(uuid.uuid4())

        # Create preview record
        preview_data = {
            "preview_id": preview_id,
            "session_id": request.session_id,
            "customer_email": request.customer_email,
            "child_name": request.child_name,
            "child_age": request.child_age,
            "child_gender": request.child_gender,
            "theme": request.theme.value,
            "style": request.style.value,
            "photo_url": request.photo_url,
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

        # Start background generation task
        background_tasks.add_task(
            generate_full_preview,
            job_id=job_id,
            preview_id=preview_id,
            photo_url=request.photo_url,
            child_name=request.child_name,
            child_age=request.child_age,
            child_gender=request.child_gender,
            theme=request.theme.value,
            style=request.style.value
        )

        logger.info("Preview generation job started", job_id=job_id, preview_id=preview_id)

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


@router.get("/preview/{preview_id}", response_model=PreviewResponse)
async def get_preview(preview_id: str):
    """
    Get preview data for display.

    Returns preview pages (watermarked) and locked pages info.
    Only available after generation is complete.
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

        # Check if preview is ready
        if preview["status"] not in [PreviewStatus.ACTIVE.value, PreviewStatus.PURCHASED.value]:
            if preview["status"] == PreviewStatus.GENERATING.value:
                raise HTTPException(status_code=202, detail="Preview is still being generated")
            elif preview["status"] == PreviewStatus.FAILED.value:
                raise HTTPException(status_code=500, detail="Preview generation failed")
            else:
                raise HTTPException(status_code=400, detail=f"Preview status: {preview['status']}")

        # Prepare preview pages (first 5, watermarked)
        preview_pages = []
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
                    is_watermarked=True,
                    is_locked=False
                ))

        # Prepare locked pages (remaining 5)
        locked_pages = []
        if preview.get("story_pages"):
            for story_data in preview["story_pages"][5:]:  # Pages 6-10
                locked_pages.append(PageData(
                    page_number=story_data["page"],
                    image_url="",  # No image for locked pages
                    story_text=story_data["text"][:100] + "...",  # Teaser text
                    is_watermarked=False,
                    is_locked=True
                ))

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
            story_title=story_title,
            child_name=preview["child_name"],
            theme=preview["theme"],
            style=preview["style"],
            preview_pages=preview_pages,
            locked_pages=locked_pages,
            total_pages=10,
            preview_pages_count=len(preview_pages),
            locked_pages_count=len(locked_pages),
            expires_at=expires_at,
            days_remaining=days_remaining,
            purchase={
                "price": 499,
                "currency": "INR",
                "price_formatted": "₹499",
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
"""
FastAPI background tasks for image generation and PDF creation.
Uses NanoBanana pipeline for all generation.
"""

import structlog

# Import StoryGift task functions (uses NanoBanana pipeline)
from app.background.storygift_tasks import (
    generate_storygift_preview,
    generate_storygift_pdf_from_order,
    generate_remaining_pages_and_pdf  # NEW: Post-payment completion
)

# Import utilities
from app.background.utils import (
    update_job_progress,
    update_job_status,
    update_preview_status,
    create_watermarked_preview
)

# Re-export for backward compatibility
__all__ = [
    'update_job_progress',
    'update_job_status',
    'update_preview_status',
    'create_watermarked_preview',
    'generate_full_preview',
    'generate_pdf_from_order',
    'generate_pdf',
    'generate_remaining_pages_and_pdf'  # NEW
]

logger = structlog.get_logger()


async def generate_full_preview(
    job_id: str,
    preview_id: str,
    photo_url: str,
    child_name: str,
    child_age: int,
    child_gender: str,
    theme: str,
    style: str = "photorealistic"  # NEW: art style parameter with backward-compatible default
):
    """
    Generate story preview using appropriate pipeline based on style.

    Supports all themes with configurable page generation.
    Testing mode: 5 pages, Production mode: 10 pages
    
    Args:
        style: "photorealistic" (default) or "cartoon_3d"
    """
    logger.info("Preview generation started", theme=theme, style=style, preview_id=preview_id)

    await generate_storygift_preview(
        job_id=job_id,
        preview_id=preview_id,
        photo_url=photo_url,
        child_name=child_name,
        child_age=child_age,
        child_gender=child_gender,
        theme=theme,
        style=style  # Pass style through
    )


async def generate_pdf_from_order(
    order_id: str,
    preview_id: str,
    child_name: str
):
    """
    Generate final PDF after payment.
    """
    return await generate_storygift_pdf_from_order(
        order_id=order_id,
        preview_id=preview_id,
        child_name=child_name
    )


# Legacy alias for backward compatibility
generate_pdf = generate_pdf_from_order

# Alias for test endpoint  
generate_remaining_pages = generate_remaining_pages_and_pdf
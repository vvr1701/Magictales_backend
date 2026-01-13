"""
Shared background task utilities.

This module contains helper functions used by multiple task modules
to avoid circular imports.
"""

from datetime import datetime
from typing import Optional
import structlog

from app.config import get_settings
from app.models.database import get_db
from app.models.enums import PreviewStatus, OrderStatus, JobStatus
from app.services.storage import StorageService
from app.core.exceptions import StorageError

logger = structlog.get_logger()


async def update_job_progress(job_id: str, progress: int, current_step: str = None):
    """Update job progress in database."""
    try:
        db = get_db()
        update_data = {
            "progress": progress
        }
        if current_step:
            update_data["current_step"] = current_step

        db.table("generation_jobs").update(update_data).eq("job_id", job_id).execute()
    except Exception as e:
        logger.error("Failed to update job progress", job_id=job_id, error=str(e))


async def update_job_status(
    job_id: str,
    status: JobStatus,
    progress: int = None,
    error: str = None,
    result_data: dict = None
):
    """Update job status in database."""
    try:
        db = get_db()
        update_data = {
            "status": status.value
        }

        if progress is not None:
            update_data["progress"] = progress

        if status == JobStatus.PROCESSING and "started_at" not in update_data:
            update_data["started_at"] = datetime.utcnow().isoformat()

        if status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            update_data["completed_at"] = datetime.utcnow().isoformat()

        if error:
            update_data["error_message"] = error

        if result_data:
            update_data["result_data"] = result_data

        db.table("generation_jobs").update(update_data).eq("job_id", job_id).execute()
    except Exception as e:
        logger.error("Failed to update job status", job_id=job_id, error=str(e))


async def update_preview_status(preview_id: str, status: PreviewStatus, **kwargs):
    """Update preview status and other fields."""
    try:
        db = get_db()
        update_data = {
            "status": status.value,
            **kwargs
        }

        # Debug logging
        logger.info(
            "Updating preview in database",
            preview_id=preview_id,
            status=status.value,
            update_keys=list(kwargs.keys()),
            hires_images_count=len(kwargs.get('hires_images', [])) if isinstance(kwargs.get('hires_images'), list) else 'not_list',
            preview_images_count=len(kwargs.get('preview_images', [])) if isinstance(kwargs.get('preview_images'), list) else 'not_list',
            story_pages_count=len(kwargs.get('story_pages', [])) if isinstance(kwargs.get('story_pages'), list) else 'not_list'
        )

        result = db.table("previews").update(update_data).eq("preview_id", preview_id).execute()

        # Debug: Log the result
        logger.info(
            "Database update result",
            preview_id=preview_id,
            result_data_count=len(result.data) if result.data else 0
        )
    except Exception as e:
        logger.error("Failed to update preview status", preview_id=preview_id, error=str(e), traceback=str(e))


async def update_preview_pages_incrementally(
    preview_id: str,
    hires_images: list,
    preview_images: list,
    story_pages: list
):
    """
    Update preview pages incrementally as they are generated.
    This allows the frontend to show pages one by one as they complete.
    """
    try:
        db = get_db()
        update_data = {
            "hires_images": hires_images,
            "preview_images": preview_images,
            "story_pages": story_pages
        }

        db.table("previews").update(update_data).eq("preview_id", preview_id).execute()
        
        logger.debug(
            "Incremental preview update",
            preview_id=preview_id,
            pages_count=len(story_pages)
        )
    except Exception as e:
        logger.error("Failed to update preview pages incrementally", preview_id=preview_id, error=str(e))


async def create_watermarked_preview(
    source_url: str,
    output_path: str,
    watermark_text: str = "PREVIEW - zelavokids.com",
    resize_width: int = 800
) -> str:
    """Create watermarked preview image."""
    from PIL import Image, ImageDraw, ImageFont
    import httpx
    from io import BytesIO

    if not source_url:
        raise ValueError("source_url cannot be None or empty")

    try:
        # Download original image
        async with httpx.AsyncClient() as client:
            response = await client.get(source_url)
            response.raise_for_status()
            image_bytes = response.content

        # Open image
        img = Image.open(BytesIO(image_bytes))

        # Resize to low-res (maintain aspect ratio)
        aspect_ratio = img.height / img.width
        new_height = int(resize_width * aspect_ratio)
        img = img.resize((resize_width, new_height), Image.Resampling.LANCZOS)

        # Create watermark overlay
        watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)

        # Load font
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()

        # Calculate text size and position
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Draw diagonal watermarks
        for y in range(-img.height, img.height * 2, 150):
            for x in range(-img.width, img.width * 2, 300):
                # Create rotated text
                txt_img = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
                txt_draw = ImageDraw.Draw(txt_img)
                txt_draw.text((10, 10), watermark_text, font=font, fill=(255, 255, 255, 80))
                txt_img = txt_img.rotate(45, expand=True)

                # Paste onto watermark layer
                watermark.paste(txt_img, (x, y), txt_img)

        # Combine original with watermark
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, watermark)
        img = img.convert('RGB')

        # Save to bytes
        output_buffer = BytesIO()
        img.save(output_buffer, format='JPEG', quality=80)
        output_buffer.seek(0)

        # Upload to storage
        storage = StorageService()
        preview_url = await storage.upload_image(
            output_buffer.getvalue(),
            output_path,
            "image/jpeg"
        )

        return preview_url

    except Exception as e:
        logger.error("Failed to create watermarked preview", error=str(e))
        raise StorageError(f"Failed to create watermarked preview: {str(e)}")

"""
FastAPI background tasks for image generation and PDF creation.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
import structlog
from uuid import UUID
import base64

from app.config import get_settings
from app.models.database import get_db
from app.models.enums import PreviewStatus, OrderStatus, JobStatus
from app.services.storage import StorageService
from app.services.pdf_generator import PDFGeneratorService
from app.stories.themes import get_theme
from app.ai.pipelines.artistic import ArtisticPipeline
from app.ai.pipelines.realistic import RealisticPipeline
from app.core.exceptions import ImageGenerationError, StorageError

logger = structlog.get_logger()


async def update_job_progress(job_id: str, progress: int, current_step: str = None):
    """Update job progress in database."""
    try:
        db = get_db()
        update_data = {
            "progress": progress,
            "updated_at": datetime.utcnow().isoformat()
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
            "status": status.value,
            "updated_at": datetime.utcnow().isoformat()
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
            "updated_at": datetime.utcnow().isoformat(),
            **kwargs
        }
        db.table("previews").update(update_data).eq("preview_id", preview_id).execute()
    except Exception as e:
        logger.error("Failed to update preview status", preview_id=preview_id, error=str(e))


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


async def generate_full_preview(
    job_id: str,
    preview_id: str,
    photo_url: str,
    child_name: str,
    child_age: int,
    child_gender: str,
    theme: str,
    style: str
):
    """
    Generate ALL 10 high-res pages + 5 watermarked previews.

    This is the main generation task that runs when user submits form.
    All 10 images are generated immediately and stored.
    """
    try:
        logger.info("Starting full preview generation", preview_id=preview_id, style=style)

        await update_job_status(job_id, JobStatus.PROCESSING, progress=0)
        await update_job_progress(job_id, 0, "Starting generation...")

        # Get story template
        template = get_theme(theme)
        settings = get_settings()

        # Select pipeline
        if style == "artistic":
            pipeline = ArtisticPipeline()
        else:
            pipeline = RealisticPipeline()

        hires_images = []
        story_pages = []

        # ============================================
        # PHASE 1: Generate all 10 HIGH-RES pages
        # ============================================
        logger.info("Phase 1: Generating 10 high-res pages")

        for page_num in range(1, 11):
            progress = int((page_num / 10) * 80)  # 0% to 80%
            await update_job_progress(
                job_id,
                progress,
                f"Generating page {page_num} of 10..."
            )

            # Build prompt for this page
            prompt_data = template.get_page_prompt(
                page_num, style, child_name, child_age, child_gender
            )

            # Generate high-res image
            output_path = f"final/{preview_id}/page_{page_num:02d}.jpg"

            result = await pipeline.generate_page(
                prompt=prompt_data["prompt"],
                negative_prompt=prompt_data["negative_prompt"],
                child_photo_url=photo_url,
                output_path=output_path,
                seed=settings.default_seed
            )

            if not result.success:
                error_msg = f"Failed to generate page {page_num}: {result.error_message}"
                logger.error(error_msg)
                await update_job_status(job_id, JobStatus.FAILED, error=error_msg)
                await update_preview_status(preview_id, PreviewStatus.FAILED)
                return

            hires_images.append({
                "page": page_num,
                "url": result.image_url
            })

            # Get story text
            story_text = template.get_story_text(page_num, child_name)
            story_pages.append({
                "page": page_num,
                "text": story_text
            })

            logger.info(f"Generated page {page_num}", url=result.image_url)

        # ============================================
        # PHASE 2: Create 5 watermarked previews
        # ============================================
        logger.info("Phase 2: Creating 5 watermarked previews")
        await update_job_progress(job_id, 85, "Creating preview images...")

        preview_images = []

        for page_num in range(1, 6):  # Only first 5 pages
            hires_url = hires_images[page_num - 1]["url"]
            preview_path = f"previews/{preview_id}/page_{page_num:02d}_preview.jpg"

            preview_url = await create_watermarked_preview(
                source_url=hires_url,
                output_path=preview_path,
                watermark_text="PREVIEW - zelavokids.com",
                resize_width=800  # Low resolution
            )

            preview_images.append({
                "page": page_num,
                "url": preview_url,
                "text": story_pages[page_num - 1]["text"]
            })

        # ============================================
        # PHASE 3: Update database
        # ============================================
        await update_job_progress(job_id, 95, "Saving your storybook...")

        # Update preview record
        await update_preview_status(
            preview_id,
            PreviewStatus.ACTIVE,
            hires_images=hires_images,
            preview_images=preview_images,
            story_pages=story_pages,
            expires_at=(datetime.utcnow() + timedelta(days=7)).isoformat()
        )

        await update_job_status(job_id, JobStatus.COMPLETED, progress=100)

        logger.info("Preview generation completed successfully", preview_id=preview_id)

    except Exception as e:
        error_msg = f"Generation failed for {preview_id}: {str(e)}"
        logger.error(error_msg)
        await update_job_status(job_id, JobStatus.FAILED, error=error_msg)
        await update_preview_status(preview_id, PreviewStatus.FAILED)


async def generate_pdf(order_id: str, preview_id: str):
    """
    Generate PDF from existing high-res images.

    Called after payment is confirmed via webhook.
    Images already exist in /final/{preview_id}/
    """
    try:
        logger.info("Starting PDF generation", order_id=order_id, preview_id=preview_id)

        db = get_db()

        # Update order status
        db.table("orders").update({
            "status": OrderStatus.GENERATING_PDF.value,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("order_id", order_id).execute()

        # Get preview data
        preview_response = db.table("previews").select("*").eq("preview_id", preview_id).execute()

        if not preview_response.data:
            raise Exception(f"Preview not found: {preview_id}")

        preview = preview_response.data[0]

        # Prepare pages for PDF generation
        pages = []
        for img_data in preview["hires_images"]:
            story_page = next(
                (sp for sp in preview["story_pages"] if sp["page"] == img_data["page"]),
                None
            )

            pages.append({
                "page_number": img_data["page"],
                "image_url": img_data["url"],
                "story_text": story_page["text"] if story_page else ""
            })

        # Sort pages by page number
        pages.sort(key=lambda x: x["page_number"])

        # Generate PDF
        pdf_generator = PDFGeneratorService()
        pdf_bytes = await pdf_generator.generate_storybook_pdf(
            pages=pages,
            title=f"{preview['child_name']}'s First Day of Magic",
            child_name=preview["child_name"],
            theme=preview["theme"]
        )

        # Upload PDF
        storage = StorageService()
        pdf_path = f"final/{preview_id}/book.pdf"
        pdf_url = await storage.upload_pdf(pdf_bytes, pdf_path)

        # Update order
        db.table("orders").update({
            "status": OrderStatus.COMPLETED.value,
            "pdf_url": pdf_url,
            "pdf_generated_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("order_id", order_id).execute()

        # Update preview
        await update_preview_status(preview_id, PreviewStatus.PURCHASED)

        # Extend preview expiry to 30 days for downloads
        db.table("previews").update({
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }).eq("preview_id", preview_id).execute()

        # Cleanup preview images (watermarked no longer needed)
        try:
            await storage.delete_folder(f"previews/{preview_id}/")
        except Exception as e:
            logger.warning("Failed to cleanup preview folder", error=str(e))

        logger.info("PDF generation completed successfully", order_id=order_id)

    except Exception as e:
        error_msg = f"PDF generation failed for order {order_id}: {str(e)}"
        logger.error(error_msg)

        # Update order status
        try:
            db = get_db()
            db.table("orders").update({
                "status": OrderStatus.FAILED.value,
                "error_message": error_msg,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("order_id", order_id).execute()
        except Exception as db_error:
            logger.error("Failed to update order status", error=str(db_error))


async def cleanup_expired_previews():
    """
    Cleanup expired preview files.
    Called manually or via scheduled endpoint.
    """
    try:
        db = get_db()
        storage = StorageService()

        # Get expired previews
        expired_response = db.table("previews").select("preview_id").eq("status", "expired").execute()

        cleaned_count = 0

        for preview in expired_response.data:
            preview_id = preview["preview_id"]

            try:
                # Delete all files from R2
                await storage.delete_folder(f"final/{preview_id}/")
                await storage.delete_folder(f"previews/{preview_id}/")
                await storage.delete_folder(f"uploads/{preview_id}/")

                cleaned_count += 1
                logger.info("Cleaned up expired preview", preview_id=preview_id)

            except Exception as e:
                logger.error("Failed to cleanup preview", preview_id=preview_id, error=str(e))

        logger.info("Cleanup completed", cleaned_count=cleaned_count)
        return cleaned_count

    except Exception as e:
        logger.error("Cleanup failed", error=str(e))
        return 0
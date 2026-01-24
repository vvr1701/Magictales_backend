"""
StoryGift-style background tasks for image generation and PDF creation.

Updated to use:
- NanoBanana pipeline with VLM face analysis
- Configurable page generation (5 testing / 10 production)
- StoryGift magic castle theme
- Superior PDF generation
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
import structlog
from uuid import UUID

from app.config import get_settings
from app.models.database import get_db
from app.models.enums import PreviewStatus, OrderStatus, JobStatus
from app.services.storage import StorageService
from app.services.storygift_pdf_generator import StoryGiftPDFGeneratorService
from app.services.email_service import get_email_service
from app.stories.themes import get_theme
from app.ai.factory import get_pipeline_for_style
from app.core.exceptions import ImageGenerationError, StorageError
from app.core.sanitization import sanitize_child_name, sanitize_for_prompt

# Import helper functions from utils (not tasks) to avoid circular import
from app.background.utils import (
    update_job_progress,
    update_job_status,
    update_preview_status,
    create_watermarked_preview,
    update_preview_pages_incrementally
)

logger = structlog.get_logger()

# Story-themed progress messages for each generation phase
PROGRESS_MESSAGES = {
    "face_analysis": [
        "Discovering your hero's magical features... ✨",
        "Reading the sparkle in their eyes... 👀",
        "Learning what makes them special... 🌟",
    ],
    "cover": [
        "Designing your magical book cover... 📚",
        "Painting the entrance to adventure... 🎨",
        "Creating the perfect first impression... ✨",
    ],
    "page_1": [
        "Opening the enchanted storybook... 📖",
        "Your hero is waking up to adventure! 🌅",
        "Chapter 1 is brewing with magic... ☕",
    ],
    "page_2": [
        "The adventure begins! 🚀",
        "Magic sparkles fill the air... ✨",
        "New discoveries await around every corner... 🔮",
    ],
    "page_3": [
        "Meeting wonderful new friends! 🤝",
        "The story grows more exciting... 🎭",
        "Courage is building in your hero's heart... 💪",
    ],
    "page_4": [
        "Plot twist incoming! 🎢",
        "The adventure reaches new heights... 🏔️",
        "Magic swirls all around... 🌀",
    ],
    "page_5": [
        "Creating a magical moment! 🌈",
        "Almost at the grand finale... 🎆",
        "Wrapping up this chapter beautifully... 🎁",
    ],
    "finalizing": [
        "Sprinkling final fairy dust... ✨",
        "Putting the finishing touches... 🖌️",
        "Your magical story is almost ready! 🎉",
    ],
}

def get_progress_message(phase: str, page_num: int = None) -> str:
    """Get a themed progress message for the current generation phase."""
    import random

    if page_num is not None:
        # Use page-specific message if available
        page_key = f"page_{page_num}"
        if page_key in PROGRESS_MESSAGES:
            return random.choice(PROGRESS_MESSAGES[page_key])

    # Fall back to phase-based message
    if phase in PROGRESS_MESSAGES:
        return random.choice(PROGRESS_MESSAGES[phase])

    # Default fallback
    return "Creating magic... ✨"


async def generate_storygift_preview(
    job_id: str,
    preview_id: str,
    photo_url: str,
    child_name: str,
    child_age: int,
    child_gender: str,
    theme: str,
    style: str = "photorealistic"  # NEW: art style with backward-compatible default
):
    """
    Generate StoryGift-style preview with configurable page count.

    Uses NanoBanana pipeline with VLM face analysis.
    Supports testing mode (5 pages) vs production mode (10 pages).
    """
    try:
        # PREVIEW MODE: Always generate 5 pages first (remaining 5 after payment)
        preview_pages = 5
        total_pages = 10  # Total pages in full book

        # Sanitize child name to prevent prompt injection
        safe_child_name = sanitize_child_name(child_name)

        logger.info(
            "Starting StoryGift preview generation (5-page preview mode)",
            preview_id=preview_id,
            child_name=safe_child_name,
            original_name_length=len(child_name),
            theme=theme,
            style=style,
            preview_pages=preview_pages,
            total_pages=total_pages
        )

        await update_job_status(job_id, JobStatus.PROCESSING, progress=0)
        await update_job_progress(job_id, 0, "Preparing your magical adventure... 🎭")

        # Get StoryGift theme
        try:
            template = get_theme(theme)
            logger.info("StoryGift template loaded", theme=theme, page_count=len(template.pages))
        except Exception as e:
            logger.error("Failed to load StoryGift theme", theme=theme, error=str(e))
            raise

        # Initialize appropriate pipeline based on style
        try:
            pipeline = get_pipeline_for_style(style)
            logger.info(f"Pipeline initialized for style: {style}", style=style)
        except Exception as e:
            logger.error(f"Failed to initialize pipeline for style {style}", error=str(e))
            raise

        # Prepare story pages for generation (ONLY first 5 for preview)
        pages_to_generate = template.pages[:preview_pages]
        logger.info(f"Generating {len(pages_to_generate)} preview pages (full book has {len(template.pages)} pages)")

        # ============================================
        # PHASE 1: VLM Face Analysis (5% progress)
        # ============================================
        await update_job_progress(job_id, 5, get_progress_message("face_analysis"))

        try:
            analyzed_features = await pipeline.analyze_face(photo_url)
            logger.info("Face analysis completed", features_length=len(analyzed_features))
            
            # Store analyzed_features for consistency when generating remaining pages
            db = get_db()
            db.table("previews").update({
                "analyzed_features": analyzed_features
            }).eq("preview_id", preview_id).execute()
            logger.info("Stored analyzed_features for future generation consistency")
            
        except Exception as e:
            logger.error("Face analysis failed", error=str(e))
            analyzed_features = "a cute child"  # Fallback

        # ============================================
        # PHASE 1.5: Generate Cover Image (10% progress)
        # ============================================
        await update_job_progress(job_id, 10, get_progress_message("cover"))

        cover_url = None
        try:
            # Get cover prompt from template (using sanitized name and matching style)
            # This ensures cover and pages use consistent artistic styling
            cover_prompt = template.get_cover_prompt(safe_child_name, style=style)
            logger.info(
                "Generating cover image with face-preserving pipeline",
                preview_id=preview_id,
                style=style,
                prompt_length=len(cover_prompt),
                prompt_preview=cover_prompt[:200]  # First 200 chars for debugging
            )

            # Generate cover using same face analysis pipeline for consistency
            # Cover uses 1:1 aspect ratio to perfectly fit PDF page (10x10 inches)
            cover_result = await pipeline.generate_with_face_analysis(
                prompt=cover_prompt,
                face_url=photo_url,
                child_name=safe_child_name,
                analyzed_features=analyzed_features,
                aspect_ratio="1:1"  # Cover is square for PDF, story pages use 5:4
            )

            logger.info(
                "Cover generation result",
                preview_id=preview_id,
                success=cover_result.success,
                has_image_url=bool(cover_result.image_url),
                error_message=cover_result.error_message if hasattr(cover_result, 'error_message') else None
            )

            if cover_result.success and cover_result.image_url:
                # Store cover in cloud storage
                cover_storage_path = f"final/{preview_id}/cover.jpg"
                logger.info("Uploading cover to storage", path=cover_storage_path)

                cover_url = await StorageService().download_and_upload(
                    cover_result.image_url, cover_storage_path
                )

                logger.info("Cover uploaded to storage", cover_url=cover_url)

                # Update database with cover URL
                update_result = db.table("previews").update({
                    "cover_url": cover_url
                }).eq("preview_id", preview_id).execute()

                logger.info(
                    "Cover URL saved to database",
                    preview_id=preview_id,
                    cover_url=cover_url,
                    db_update_success=bool(update_result.data)
                )
            else:
                logger.warning(
                    "Cover generation failed, will use first page as cover",
                    preview_id=preview_id,
                    success=cover_result.success,
                    error=getattr(cover_result, 'error_message', 'Unknown error')
                )

        except Exception as e:
            logger.error(
                "Cover generation error (non-fatal)",
                preview_id=preview_id,
                error=str(e),
                error_type=type(e).__name__
            )
            import traceback
            logger.error("Cover generation traceback", traceback=traceback.format_exc())
            # Continue without cover - will fall back to using first page

        # ============================================
        # PHASE 2: Generate story pages (15% to 90%)
        # ============================================
        hires_images = []
        story_pages = []

        for i, page_template in enumerate(pages_to_generate):
            page_num = i + 1

            try:
                # Calculate progress (15% to 90% for story page generation)
                progress = 15 + int((i / len(pages_to_generate)) * 75)
                await update_job_progress(
                    job_id,
                    progress,
                    get_progress_message(f"page_{page_num}", page_num)
                )

                # Get prompt for this page (use realistic_prompt for NanoBanana)
                prompt = page_template.realistic_prompt or page_template.artistic_prompt or ""

                if not prompt:
                    logger.warning(f"No prompt found for page {page_num}, skipping")
                    continue

                # Generate image with NanoBanana
                logger.info(f"Generating page {page_num} with NanoBanana")

                result = await pipeline.generate_with_face_analysis(
                    prompt=prompt,
                    face_url=photo_url,
                    child_name=safe_child_name,
                    analyzed_features=analyzed_features
                )

                if result.success and result.image_url:
                    # Store in cloud storage
                    storage_path = f"final/{preview_id}/page_{page_num:02d}.jpg"
                    stored_url = await StorageService().download_and_upload(
                        result.image_url, storage_path
                    )

                    # Store in format expected by preview.py
                    hires_images.append({"page": page_num, "url": stored_url})

                    # Prepare page data (use both 'text' and 'story_text' for compatibility)
                    # Use sanitize_for_prompt to safely insert name into story text
                    story_text_value = sanitize_for_prompt(page_template.story_text, safe_child_name)
                    story_pages.append({
                        'page': page_num,
                        'image_url': stored_url,
                        'text': story_text_value,  # For preview.py
                        'story_text': story_text_value,  # For PDF generator
                        'dialogue': [],  # StoryGift handles dialogue in HTML template
                        'realistic_prompt': prompt
                    })

                    logger.info(f"Page {page_num} generated successfully")

                    # PROGRESSIVE LOADING: Update database after each page so frontend can show it
                    # Create watermarked preview for this page immediately
                    if page_num <= 5:  # Only first 5 pages get previews
                        try:
                            preview_path = f"final/{preview_id}/preview_{page_num:02d}.jpg"
                            watermarked_url = await create_watermarked_preview(
                                source_url=stored_url,
                                output_path=preview_path,
                                watermark_text="PREVIEW - zelavokids.com",
                                resize_width=800
                            )

                            # Store preview URL in story_pages for tracking
                            story_pages[-1]["preview_url"] = watermarked_url

                        except Exception as preview_err:
                            logger.error(f"Failed to create preview for page {page_num}: {preview_err}")
                            # Don't wipe previous pages - just skip this page's preview
                            # Frontend will show the high-res version instead

                    # Build preview_images list from story_pages that have preview_url
                    current_preview_images = [
                        {"page": sp["page"], "url": sp["preview_url"]}
                        for sp in story_pages
                        if sp.get("preview_url")
                    ]

                    # Update database incrementally so frontend can show this page
                    await update_preview_pages_incrementally(
                        preview_id=preview_id,
                        hires_images=hires_images,
                        preview_images=current_preview_images,
                        story_pages=story_pages
                    )
                else:
                    logger.error(f"Page {page_num} generation failed: {result.error_message}")

            except Exception as e:
                logger.error(f"Error generating page {page_num}", error=str(e))
                continue

        # ============================================
        # PHASE 3: Finalize Preview (95% to 100%)
        # ============================================
        await update_job_progress(job_id, 95, get_progress_message("finalizing"))

        # Build final preview_images from story_pages
        preview_images = [
            {"page": sp["page"], "url": sp["preview_url"]}
            for sp in story_pages
            if sp.get("preview_url")
        ]

        # Debug logging before database update
        logger.info(
            "About to update database with generation results",
            preview_id=preview_id,
            hires_images_count=len(hires_images),
            preview_images_count=len(preview_images),
            story_pages_count=len(story_pages),
            hires_images_sample=hires_images[0] if hires_images else None,
            preview_images_sample=preview_images[0] if preview_images else None,
            story_pages_sample=story_pages[0] if story_pages else None
        )

        # Check if generation was actually successful
        if not hires_images or not story_pages:
            error_msg = f"Generation failed: No images or story pages generated"
            logger.error(error_msg, preview_id=preview_id)

            await update_preview_status(
                preview_id=preview_id,
                status=PreviewStatus.FAILED
            )

            await update_job_status(
                job_id=job_id,
                status=JobStatus.FAILED,
                error=error_msg
            )
            return

        # Update preview in database - set generation_phase to 'preview' (not complete)
        await update_preview_status(
            preview_id=preview_id,
            status=PreviewStatus.ACTIVE,
            hires_images=hires_images,
            preview_images=preview_images,  # From incremental updates
            story_pages=story_pages,
            generation_phase='preview',  # Mark as preview only
            preview_page_count=len(story_pages),
            total_page_count=total_pages
            # NOTE: pdf_url is NOT set - will be generated after payment
        )

        # Mark job as completed
        await update_job_status(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            progress=100,
            result_data={
                "preview_count": len(preview_images),
                "hires_count": len(hires_images),
                "generation_phase": "preview",
                "pages_generated": len(story_pages)
            }
        )

        logger.info(
            "StoryGift PREVIEW generation completed (5 pages)",
            preview_id=preview_id,
            hires_count=len(hires_images),
            preview_count=len(preview_images),
            generation_phase="preview"
        )

        # ============================================
        # PHASE 4: Send Preview Ready Email (only if user opted in)
        # ============================================
        try:
            # Get customer email and notify preference from preview record
            preview_data = db.table("previews").select(
                "customer_email", "notify_on_complete"
            ).eq("preview_id", preview_id).execute()

            if preview_data.data:
                record = preview_data.data[0]
                customer_email = record.get("customer_email")
                notify_on_complete = record.get("notify_on_complete", False)

                # Only send email if user explicitly opted in via the popup
                if notify_on_complete and customer_email:
                    settings = get_settings()

                    # Build preview URL using frontend_url config (hash routing)
                    preview_url = f"{settings.frontend_url}#/preview/{preview_id}"

                    email_service = get_email_service()
                    await email_service.send_preview_ready_email(
                        to_email=customer_email,
                        child_name=safe_child_name,
                        preview_url=preview_url
                    )
                    logger.info("Preview ready email sent", to=customer_email, preview_id=preview_id)
                else:
                    logger.info(
                        "Skipping preview notification (user did not opt in)",
                        preview_id=preview_id,
                        has_email=bool(customer_email),
                        notify_flag=notify_on_complete
                    )
        except Exception as email_error:
            # Email failure should not fail the preview generation
            logger.error("Failed to send preview ready email (non-fatal)", error=str(email_error))

    except Exception as e:
        logger.error(
            "StoryGift preview generation failed",
            preview_id=preview_id,
            error=str(e)
        )

        await update_job_status(
            job_id=job_id,
            status=JobStatus.FAILED,
            error=str(e)
        )

        await update_preview_status(
            preview_id=preview_id,
            status=PreviewStatus.FAILED
        )


async def generate_remaining_pages_and_pdf(
    order_id: str,
    preview_id: str,
    child_name: str,
    max_retries: int = 3
):
    """
    Generate remaining 5 pages (6-10) after payment, then create full 10-page PDF.
    
    Called by webhook after successful payment. Uses stored analyzed_features
    from preview generation for consistency across all pages.
    
    Args:
        order_id: Shopify order ID
        preview_id: Preview to complete
        child_name: Child's name for story
        max_retries: Max retry attempts (default 3)
    """
    retry_count = 0
    last_error = None
    
    while retry_count < max_retries:
        try:
            # Sanitize child name to prevent prompt injection
            safe_child_name = sanitize_child_name(child_name)

            logger.info(
                "Starting remaining page generation",
                order_id=order_id,
                preview_id=preview_id,
                child_name=safe_child_name,
                attempt=retry_count + 1,
                max_retries=max_retries
            )

            # Get preview data from database
            db = get_db()
            preview_result = db.table("previews").select("*").eq("preview_id", preview_id).execute()

            if not preview_result.data:
                raise StorageError(f"Preview not found: {preview_id}")

            preview_data = preview_result.data[0]

            # Get existing data from preview phase
            existing_hires = preview_data.get("hires_images", [])
            existing_story_pages = preview_data.get("story_pages", [])
            analyzed_features = preview_data.get("analyzed_features", "a cute child")
            photo_url = preview_data.get("photo_url")
            theme = preview_data.get("theme", "storygift_enchanted_forest")
            style = preview_data.get("style", "photorealistic")
            
            if not existing_hires or not existing_story_pages:
                raise StorageError(f"No preview pages found for: {preview_id}")
            
            if len(existing_story_pages) >= 10:
                logger.info("Preview already has 10 pages, skipping generation", preview_id=preview_id)
                # Just generate PDF
                pass
            else:
                # Mark as generating
                db.table("previews").update({
                    "generation_phase": "generating_full"
                }).eq("preview_id", preview_id).execute()
                
                db.table("orders").update({
                    "status": OrderStatus.GENERATING_PDF.value
                }).eq("order_id", order_id).execute()
                
                # Get theme template
                template = get_theme(theme)
                
                # Initialize pipeline
                pipeline = get_pipeline_for_style(style)
                
                # Get pages 6-10 from template
                pages_to_generate = template.pages[5:10]  # Pages 6-10 (0-indexed: 5-9)
                
                logger.info(
                    f"Generating remaining {len(pages_to_generate)} pages",
                    preview_id=preview_id,
                    start_page=6,
                    end_page=10
                )
                
                # Generate remaining pages
                hires_images = list(existing_hires)
                story_pages = list(existing_story_pages)
                
                for i, page_template in enumerate(pages_to_generate):
                    page_num = 6 + i  # Pages 6, 7, 8, 9, 10
                    
                    try:
                        prompt = page_template.realistic_prompt or page_template.artistic_prompt or ""
                        
                        if not prompt:
                            logger.warning(f"No prompt found for page {page_num}, skipping")
                            continue
                        
                        logger.info(f"Generating page {page_num} (post-payment)")
                        
                        # Generate using stored analyzed_features for consistency
                        result = await pipeline.generate_with_face_analysis(
                            prompt=prompt,
                            face_url=photo_url,
                            child_name=safe_child_name,
                            analyzed_features=analyzed_features
                        )

                        if result.success and result.image_url:
                            # Store in cloud
                            storage_path = f"final/{preview_id}/page_{page_num:02d}.jpg"
                            stored_url = await StorageService().download_and_upload(
                                result.image_url, storage_path
                            )

                            hires_images.append({"page": page_num, "url": stored_url})

                            # Use sanitize_for_prompt to safely insert name
                            story_text_value = sanitize_for_prompt(page_template.story_text, safe_child_name)
                            story_pages.append({
                                'page': page_num,
                                'image_url': stored_url,
                                'text': story_text_value,
                                'story_text': story_text_value,
                                'dialogue': [],
                                'realistic_prompt': prompt
                            })
                            
                            logger.info(f"Page {page_num} generated successfully")
                        else:
                            logger.error(f"Page {page_num} generation failed: {result.error_message}")
                            raise ImageGenerationError(f"Failed to generate page {page_num}")
                    
                    except Exception as e:
                        logger.error(f"Error generating page {page_num}", error=str(e))
                        raise
                
                # Update preview with all 10 pages
                db.table("previews").update({
                    "hires_images": hires_images,
                    "story_pages": story_pages,
                    "generation_phase": "complete",
                    "preview_page_count": len(story_pages)
                }).eq("preview_id", preview_id).execute()
            
            # ============================================
            # Now generate full 10-page PDF
            # ============================================
            logger.info("Generating full 10-page PDF", preview_id=preview_id)
            
            # Reload data to get all 10 pages
            preview_result = db.table("previews").select("*").eq("preview_id", preview_id).execute()
            preview_data = preview_result.data[0]
            all_hires = preview_data.get("hires_images", [])
            all_story_pages = preview_data.get("story_pages", [])
            
            pdf_generator = StoryGiftPDFGeneratorService()

            # Get story title from theme (using sanitized name)
            template = get_theme(theme)
            story_title = template.get_title(safe_child_name) if hasattr(template, 'get_title') else f"{safe_child_name}'s Adventure"
            
            # Use dedicated cover_url if available, otherwise fallback to first page
            cover_url = preview_data.get("cover_url")
            if not cover_url and all_hires and isinstance(all_hires[0], dict):
                cover_url = all_hires[0]["url"]
                logger.info("No dedicated cover found, using first page as cover")
            
            pdf_url = await pdf_generator.generate_storygift_pdf(
                preview_id=preview_id,
                child_name=safe_child_name,
                story_pages=all_story_pages,
                story_title=story_title,
                cover_image_url=cover_url
            )
            
            # Update preview with PDF URL
            db.table("previews").update({
                "pdf_url": pdf_url,
                "status": PreviewStatus.PURCHASED.value
            }).eq("preview_id", preview_id).execute()
            
            # Update order as completed
            db.table("orders").update({
                "pdf_url": pdf_url,
                "status": OrderStatus.COMPLETED.value,
                "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }).eq("order_id", order_id).execute()
            
            logger.info(
                "Full book generation completed successfully",
                order_id=order_id,
                preview_id=preview_id,
                total_pages=len(all_story_pages),
                pdf_url=pdf_url
            )
            
            # ============================================
            # Send completion email
            # ============================================
            try:
                # Get customer email from order
                order_result = db.table("orders").select("customer_email").eq("order_id", order_id).execute()
                if order_result.data and order_result.data[0].get("customer_email"):
                    customer_email = order_result.data[0]["customer_email"]

                    email_service = get_email_service()
                    await email_service.send_book_ready_email(
                        to_email=customer_email,
                        child_name=safe_child_name,
                        story_title=story_title,
                        download_url=pdf_url
                    )
                    logger.info("Completion email sent", to=customer_email)
                else:
                    logger.warning("No customer email found, skipping email notification")
            except Exception as email_error:
                # Email failure should not fail the whole order
                logger.error("Failed to send completion email (non-fatal)", error=str(email_error))
            
            return pdf_url
            
        except Exception as e:
            retry_count += 1
            last_error = e
            
            logger.error(
                f"Generation attempt {retry_count} failed",
                order_id=order_id,
                preview_id=preview_id,
                error=str(e),
                retries_remaining=max_retries - retry_count
            )
            
            if retry_count < max_retries:
                # Wait before retry (exponential backoff)
                import asyncio
                await asyncio.sleep(2 ** retry_count)
                continue
            else:
                # All retries exhausted
                logger.error(
                    "All retry attempts exhausted",
                    order_id=order_id,
                    preview_id=preview_id,
                    total_attempts=max_retries
                )
                
                # Mark order as failed
                try:
                    db = get_db()
                    db.table("orders").update({
                        "status": OrderStatus.FAILED.value,
                        "error_message": f"Generation failed after {max_retries} attempts: {str(last_error)}"
                    }).eq("order_id", order_id).execute()
                    
                    db.table("previews").update({
                        "generation_phase": "failed"
                    }).eq("preview_id", preview_id).execute()
                except Exception as db_error:
                    logger.error("Failed to update failure status", error=str(db_error))
                
                raise last_error


# Legacy alias for backward compatibility
async def generate_storygift_pdf_from_order(order_id: str, preview_id: str, child_name: str):
    """Legacy wrapper - now generates remaining pages + PDF."""
    return await generate_remaining_pages_and_pdf(order_id, preview_id, child_name)


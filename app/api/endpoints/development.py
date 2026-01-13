"""
Development endpoints for testing - bypasses payment verification.
WARNING: These endpoints should only be used in development/testing environments.
"""

import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import structlog

from app.models.database import get_db
from app.models.enums import OrderStatus, PreviewStatus
from app.background.tasks import generate_pdf as generate_pdf_task
from app.config import get_settings

logger = structlog.get_logger()
router = APIRouter()


@router.get("/debug/preview/{preview_id}")
async def debug_preview(preview_id: str):
    """
    Debug endpoint to see what's actually stored in the database.
    Shows raw data from previews and generation_jobs tables.
    """
    try:
        db = get_db()

        # Get preview record
        preview_result = db.table("previews").select("*").eq("preview_id", preview_id).execute()

        if not preview_result.data:
            raise HTTPException(status_code=404, detail=f"Preview {preview_id} not found")

        preview = preview_result.data[0]

        # Get job record
        job_result = db.table("generation_jobs").select("*").eq("reference_id", preview_id).execute()

        job = job_result.data[0] if job_result.data else None

        return {
            "preview_id": preview_id,
            "preview_data": {
                "status": preview.get("status"),
                "theme": preview.get("theme"),
                "style": preview.get("style"),
                "child_name": preview.get("child_name"),
                "photo_url": preview.get("photo_url"),
                "hires_images": preview.get("hires_images"),
                "hires_images_type": type(preview.get("hires_images")).__name__,
                "hires_images_count": len(preview.get("hires_images", [])) if isinstance(preview.get("hires_images"), list) else "not_a_list",
                "preview_images": preview.get("preview_images"),
                "preview_images_type": type(preview.get("preview_images")).__name__,
                "preview_images_count": len(preview.get("preview_images", [])) if isinstance(preview.get("preview_images"), list) else "not_a_list",
                "story_pages": preview.get("story_pages"),
                "story_pages_type": type(preview.get("story_pages")).__name__,
                "story_pages_count": len(preview.get("story_pages", [])) if isinstance(preview.get("story_pages"), list) else "not_a_list",
                "created_at": preview.get("created_at"),
            },
            "job_data": {
                "job_id": job.get("job_id") if job else None,
                "status": job.get("status") if job else None,
                "progress": job.get("progress") if job else None,
                "current_step": job.get("current_step") if job else None,
                "error_message": job.get("error_message") if job else None,
                "result_data": job.get("result_data") if job else None,
                "queued_at": job.get("queued_at") if job else None,
                "started_at": job.get("started_at") if job else None,
                "completed_at": job.get("completed_at") if job else None,
                "attempts": job.get("attempts") if job else None,
            } if job else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Debug endpoint failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


class DevPdfGenerationRequest(BaseModel):
    """Request model for development PDF generation."""
    preview_id: str
    customer_email: str = "test@example.com"
    customer_name: str = "Test Customer"


class DevPdfGenerationResponse(BaseModel):
    """Response model for development PDF generation."""
    success: bool
    order_id: str
    preview_id: str
    message: str


@router.post("/dev/generate-pdf", response_model=DevPdfGenerationResponse)
async def dev_generate_pdf(
    request: DevPdfGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Development endpoint to generate PDF without payment verification.

    This endpoint:
    1. Validates that the preview exists and is ready
    2. Creates an order record with status 'PAID' (bypassing Shopify)
    3. Triggers PDF generation background task
    4. Returns order_id for tracking

    WARNING: This bypasses all payment verification and should only be used for testing.
    """
    try:
        settings = get_settings()

        # Log security warning for non-development environments
        if settings.app_env not in ["development", "testing", "local"]:
            logger.warning(
                "Development PDF generation endpoint called in production environment",
                environment=settings.app_env,
                preview_id=request.preview_id
            )
            raise HTTPException(
                status_code=403,
                detail="Development endpoints are disabled in production"
            )

        logger.info(
            "Development PDF generation requested",
            preview_id=request.preview_id,
            customer_email=request.customer_email
        )

        db = get_db()

        # 1. Validate preview exists and is ready
        preview_response = db.table("previews").select("*").eq("preview_id", request.preview_id).execute()

        if not preview_response.data:
            logger.warning("Preview not found", preview_id=request.preview_id)
            raise HTTPException(status_code=404, detail="Preview not found")

        preview = preview_response.data[0]

        # Check preview status
        if preview["status"] != PreviewStatus.ACTIVE.value:
            logger.warning(
                "Preview not ready for PDF generation",
                preview_id=request.preview_id,
                status=preview["status"]
            )
            raise HTTPException(
                status_code=400,
                detail=f"Preview is not ready. Current status: {preview['status']}"
            )

        # Check if preview has expired
        expiry_date = datetime.fromisoformat(preview["expires_at"].replace("Z", "+00:00"))
        if datetime.utcnow().replace(tzinfo=expiry_date.tzinfo) > expiry_date:
            logger.warning("Preview has expired", preview_id=request.preview_id)
            raise HTTPException(status_code=400, detail="Preview has expired")

        # 2. Check if order already exists for this preview (allow retry for failed orders)
        existing_order_response = db.table("orders").select("*").eq("preview_id", request.preview_id).execute()

        if existing_order_response.data:
            existing_order = existing_order_response.data[0]
            logger.info(
                "Order already exists for preview",
                preview_id=request.preview_id,
                order_id=existing_order["order_id"],
                status=existing_order["status"]
            )
            
            # If order failed OR paid but no PDF generated yet, allow retry
            should_retry = (
                existing_order["status"] == OrderStatus.FAILED.value or
                (existing_order["status"] == OrderStatus.PAID.value and not existing_order.get("pdf_url"))
            )
            
            if should_retry:
                logger.info("Retrying PDF generation", order_id=existing_order["order_id"], status=existing_order["status"])
                
                # Update order status for retry
                db.table("orders").update({
                    "status": OrderStatus.GENERATING_PDF.value,
                    "error_message": None,
                    "retry_count": existing_order.get("retry_count", 0) + 1
                }).eq("order_id", existing_order["order_id"]).execute()
                
                # Trigger PDF generation again
                background_tasks.add_task(
                    generate_pdf_task,
                    order_id=existing_order["order_id"],
                    preview_id=request.preview_id,
                    child_name=preview["child_name"]
                )
                
                return DevPdfGenerationResponse(
                    success=True,
                    order_id=existing_order["order_id"],
                    preview_id=request.preview_id,
                    message=f"PDF generation started (attempt #{existing_order.get('retry_count', 0) + 1})"
                )
            
            # For completed orders, return existing order info
            return DevPdfGenerationResponse(
                success=True,
                order_id=existing_order["order_id"],
                preview_id=request.preview_id,
                message=f"Order already exists with status: {existing_order['status']}. PDF URL: {existing_order.get('pdf_url', 'none')}"
            )

        # 3. Generate order ID and create order record
        order_id = f"DEV-{uuid.uuid4().hex[:16].upper()}"

        order_data = {
            "order_id": order_id,
            "preview_id": request.preview_id,
            "customer_email": request.customer_email,
            "customer_name": request.customer_name,
            "total_amount": 0.00,  # Free for development
            "currency": "USD",
            "status": OrderStatus.PAID.value,  # Skip payment verification
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),  # 30 days for downloads
            "payment_method": "DEV_BYPASS",
            "is_development_order": True  # Flag to identify dev orders
        }

        # Insert order record
        order_response = db.table("orders").insert(order_data).execute()

        if not order_response.data:
            logger.error("Failed to create order record", order_id=order_id)
            raise HTTPException(status_code=500, detail="Failed to create order")

        logger.info(
            "Development order created",
            order_id=order_id,
            preview_id=request.preview_id,
            status=OrderStatus.PAID.value
        )

        # 4. Trigger PDF generation background task
        background_tasks.add_task(
            generate_pdf_task,
            order_id=order_id,
            preview_id=request.preview_id,
            child_name=preview["child_name"]
        )

        logger.info(
            "PDF generation task queued",
            order_id=order_id,
            preview_id=request.preview_id
        )

        return DevPdfGenerationResponse(
            success=True,
            order_id=order_id,
            preview_id=request.preview_id,
            message="PDF generation started. Use order_id to track progress."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Development PDF generation failed",
            preview_id=request.preview_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/dev/order-status/{order_id}")
async def dev_get_order_status(order_id: str):
    """
    Development endpoint to check order status.

    Returns the current status of an order including PDF generation progress.
    """
    try:
        db = get_db()

        # Get order details
        order_response = db.table("orders").select("*").eq("order_id", order_id).execute()

        if not order_response.data:
            raise HTTPException(status_code=404, detail="Order not found")

        order = order_response.data[0]

        # Get preview details
        preview_response = db.table("previews").select("*").eq("preview_id", order["preview_id"]).execute()
        preview = preview_response.data[0] if preview_response.data else None

        return {
            "success": True,
            "order": {
                "order_id": order["order_id"],
                "preview_id": order["preview_id"],
                "status": order["status"],
                "created_at": order["created_at"],
                "customer_email": order["customer_email"],
                "is_development_order": order.get("is_development_order", False)
            },
            "preview": {
                "status": preview["status"] if preview else "unknown",
                "expires_at": preview["expires_at"] if preview else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get order status", order_id=order_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/dev/info")
async def dev_info():
    """
    Development endpoint info and available operations.
    """
    settings = get_settings()

    return {
        "service": "Magictales Development Endpoints",
        "environment": settings.app_env,
        "warning": "These endpoints bypass payment verification and should only be used for testing",
        "available_endpoints": [
            {
                "endpoint": "POST /api/dev/generate-pdf",
                "description": "Generate PDF without payment (requires preview_id)",
                "required_fields": ["preview_id"],
                "optional_fields": ["customer_email", "customer_name"]
            },
            {
                "endpoint": "GET /api/dev/order-status/{order_id}",
                "description": "Check order and PDF generation status"
            },
            {
                "endpoint": "GET /api/dev/info",
                "description": "This info endpoint"
            }
        ],
        "complete_testing_flow": [
            "1. Upload photo: POST /api/upload-photo",
            "2. Create preview: POST /api/preview",
            "3. Wait for preview completion: GET /api/preview-status/{job_id}",
            "4. [DEV] Generate PDF: POST /api/dev/generate-pdf",
            "5. Check PDF status: GET /api/dev/order-status/{order_id}",
            "6. Download PDF: GET /api/download/{order_id}"
        ]
    }


@router.post("/test/single-generation")
async def test_single_generation(request: dict):
    """Test single image generation with Flux PuLID."""
    try:
        from app.ai.factory import get_storybook_pipeline

        pipeline = get_storybook_pipeline()

        result = await pipeline.generate_page(
            scene_prompt=request["scene_prompt"],
            child_photo_url=request["child_photo_url"],
            child_name=request["child_name"],
            child_age=request["child_age"],
            child_gender=request["child_gender"],
            output_path=f"test_generations/single_{int(time.time())}.jpg",
            costume=request.get("costume", "casual outfit"),
            seed=request.get("seed", 12345),
            id_weight=request.get("id_weight", 0.90)
        )

        return {
            "success": result.success,
            "image_url": result.image_url if result.success else None,
            "cost": result.cost,
            "latency_ms": result.latency_ms,
            "model_used": result.model_used,
            "metadata": result.metadata,
            "error_message": result.error_message if not result.success else None
        }

    except Exception as e:
        logger.error("Single generation test failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


@router.post("/test/pipeline")
async def test_pipeline_direct(request: dict):
    """Direct pipeline testing for development."""
    try:
        from app.ai.factory import get_storybook_pipeline

        pipeline = get_storybook_pipeline()
        method = request.get("method", "generate_page")
        params = request.get("params", {})

        if method == "generate_page":
            result = await pipeline.generate_page(**params)
            return {
                "success": result.success,
                "result": {
                    "image_url": result.image_url,
                    "cost": result.cost,
                    "latency_ms": result.latency_ms,
                    "model_used": result.model_used,
                    "metadata": result.metadata
                },
                "error": result.error_message if not result.success else None
            }
        else:
            return {"error": f"Method {method} not supported"}

    except Exception as e:
        logger.error("Pipeline test failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Pipeline test failed: {str(e)}")


@router.post("/test/face-anchor")
async def test_face_anchor(request: dict):
    """Test face-anchor functionality for identity preservation."""
    try:
        from app.ai.factory import get_storybook_pipeline

        pipeline = get_storybook_pipeline()

        result = await pipeline.generate_page(
            scene_prompt=request["test_prompt"],
            child_photo_url=request["photo_url"],
            child_name="TestChild",
            child_age=8,
            child_gender="female",
            output_path=f"test_generations/face_anchor_{int(time.time())}.jpg",
            costume="casual outfit",
            id_weight=request.get("id_weight", 0.90)
        )

        return {
            "success": result.success,
            "face_anchor_enabled": request.get("enable_face_anchor", True),
            "id_weight_used": request.get("id_weight", 0.90),
            "result": {
                "image_url": result.image_url,
                "cost": result.cost,
                "latency_ms": result.latency_ms,
                "metadata": result.metadata
            } if result.success else None,
            "error": result.error_message if not result.success else None
        }

    except Exception as e:
        logger.error("Face anchor test failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Face anchor test failed: {str(e)}")


import time


@router.post("/generate/full-comic")
async def generate_full_comic(request: dict):
    """Generate full 10-page comic with 20 panels using Flux PuLID."""
    try:
        from app.ai.factory import get_storybook_pipeline
        from app.stories.themes.magic_castle import MAGIC_CASTLE_COMIC_THEME

        pipeline = get_storybook_pipeline()
        preview_id = request["preview_id"]

        logger.info("Starting full comic generation", preview_id=preview_id)

        # Get preview data to fetch child info
        db = get_db()
        preview_response = db.table("previews").select("*").eq("preview_id", preview_id).execute()

        if not preview_response.data:
            raise HTTPException(status_code=404, detail="Preview not found")

        preview = preview_response.data[0]

        result = await pipeline.generate_comic_panels(
            comic_pages=MAGIC_CASTLE_COMIC_THEME,
            child_photo_url=preview["photo_url"],
            child_name=preview["child_name"],
            child_age=preview["child_age"],
            child_gender=preview["child_gender"],
            preview_id=preview_id,
            id_weight=0.90
        )

        return {
            "success": True,
            "preview_id": preview_id,
            "pages_generated": len(result["pages"]),
            "failed_panels": len(result["failed_panels"]),
            "total_cost": result["total_cost"],
            "total_time_ms": result["total_latency_ms"],
            "result_summary": {
                "total_panels": len(result["pages"]) * 2,
                "success_rate": len(result["pages"]) / len(MAGIC_CASTLE_COMIC_THEME) * 100,
                "cost_per_panel": result["total_cost"] / (len(result["pages"]) * 2) if result["pages"] else 0
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Full comic generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Comic generation failed: {str(e)}")


@router.post("/generate/pdf")
async def generate_pdf(request: dict):
    """Generate StoryGift-style comic PDF from generated pages."""
    try:
        from app.services.comic_pdf_generator import ComicPDFGeneratorService

        preview_id = request["preview_id"]
        pdf_format = request.get("format", "comic")
        title = request.get("title", "Magical Adventure")

        logger.info("Starting PDF generation", preview_id=preview_id)

        # Get preview data
        db = get_db()
        preview_response = db.table("previews").select("*").eq("preview_id", preview_id).execute()

        if not preview_response.data:
            raise HTTPException(status_code=404, detail="Preview not found")

        preview = preview_response.data[0]

        # Check if we have generated pages
        if not preview.get("hires_images"):
            raise HTTPException(status_code=400, detail="No generated images found. Generate comic first.")

        pdf_generator = ComicPDFGeneratorService()

        # For this test, we'll use the existing story pages format
        # In a real implementation, this would use the proper page structure
        test_pages = []
        for i, story_page in enumerate(preview.get("story_pages", []), 1):
            test_pages.append({
                "page_number": i,
                "narrative": story_page.get("text", f"Page {i} story"),
                "left_panel": {
                    "image_url": f"https://example.com/page_{i}_left.jpg",
                    "dialogue": [{"speaker": "HERO", "text": "This is test dialogue"}]
                },
                "right_panel": {
                    "image_url": f"https://example.com/page_{i}_right.jpg",
                    "dialogue": [{"speaker": "FRIEND", "text": "Response dialogue"}]
                }
            })

        pdf_bytes = await pdf_generator.generate_comic_pdf(
            pages=test_pages[:5],  # First 5 pages for testing
            title=title,
            child_name=preview["child_name"],
            theme="magic_castle"
        )

        # In a real implementation, this would be saved to storage
        pdf_filename = f"test_comic_{preview_id}.pdf"

        return {
            "success": True,
            "pdf_url": f"https://storage.com/final/{pdf_filename}",
            "pdf_size_bytes": len(pdf_bytes),
            "pages_included": len(test_pages[:5]),
            "format": pdf_format,
            "title": title,
            "download_expires": "2024-12-30T12:00:00Z"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("PDF generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
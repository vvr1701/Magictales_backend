"""
Download endpoint for completed orders.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
import structlog

from app.models.schemas import DownloadResponse
from app.models.database import get_db
from app.models.enums import OrderStatus
from app.services.storage import StorageService

logger = structlog.get_logger()
router = APIRouter()


@router.get("/download/{order_id}", response_model=DownloadResponse)
async def get_download(order_id: str):
    """
    Get download links for completed order.

    Returns signed URLs for PDF and individual images.
    Links are time-limited for security.
    """

    try:
        logger.info("Getting download links", order_id=order_id)

        db = get_db()

        # Get order record
        order_response = db.table("orders").select("*").eq("order_id", order_id).execute()

        if not order_response.data:
            raise HTTPException(status_code=404, detail="Order not found")

        order = order_response.data[0]

        # Check order status
        if order["status"] == OrderStatus.GENERATING_PDF.value:
            return DownloadResponse(
                status="generating",
                progress=75,
                message="Your book is still being created. Please check back in a few minutes."
            )

        if order["status"] != OrderStatus.COMPLETED.value:
            if order["status"] == OrderStatus.FAILED.value:
                raise HTTPException(
                    status_code=500,
                    detail="Order generation failed. Please contact support."
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Order status: {order['status']}"
                )

        # Check if order has expired
        if order.get("expires_at"):
            expires_at = datetime.fromisoformat(order["expires_at"].replace('Z', '+00:00'))
            if expires_at < datetime.utcnow().replace(tzinfo=expires_at.tzinfo):
                raise HTTPException(status_code=410, detail="Download links have expired")
        else:
            # Default expiry to 30 days from creation if not set
            created_at = datetime.fromisoformat(order.get("created_at", datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            expires_at = created_at + timedelta(days=30)

        # Get preview data for image URLs
        preview_response = db.table("previews").select("*").eq("preview_id", order["preview_id"]).execute()

        if not preview_response.data:
            raise HTTPException(status_code=404, detail="Associated preview not found")

        preview = preview_response.data[0]

        # Generate signed URLs
        storage = StorageService()

        # PDF download
        pdf_path = f"final/{order['preview_id']}/book.pdf"
        pdf_signed_url = storage.generate_signed_url(pdf_path, expires_in=3600)  # 1 hour

        # Get PDF file size
        try:
            pdf_size_bytes = await storage.get_file_size(pdf_path)
            pdf_size_mb = round(pdf_size_bytes / 1024 / 1024, 1)
        except:
            pdf_size_mb = None

        # Individual image downloads
        image_downloads = []
        if preview.get("hires_images"):
            for img_data in preview["hires_images"]:
                # Extract path from full URL
                image_path = f"final/{order['preview_id']}/page_{img_data['page']:02d}.jpg"
                image_signed_url = storage.generate_signed_url(image_path, expires_in=3600)

                image_downloads.append({
                    "page": img_data["page"],
                    "url": image_signed_url,
                    "filename": f"page_{img_data['page']:02d}.jpg"
                })

        # Calculate days remaining
        days_remaining = max(0, (expires_at - datetime.utcnow().replace(tzinfo=expires_at.tzinfo)).days)

        return DownloadResponse(
            status="ready",
            downloads={
                "pdf": {
                    "url": pdf_signed_url,
                    "filename": f"{preview['child_name'].replace(' ', '_')}_Storybook.pdf",
                    "size_mb": pdf_size_mb,
                    "expires_in_seconds": 3600
                },
                "images": image_downloads
            },
            expires_at=expires_at,
            days_remaining=days_remaining
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error("Failed to get download links", order_id=order_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve download links. Please try again."
        )
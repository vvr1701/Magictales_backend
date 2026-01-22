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


@router.get("/download/{identifier}", response_model=DownloadResponse)
async def get_download(identifier: str):
    """
    Get download links for completed order.

    Returns signed URLs for PDF and individual images.
    Links are time-limited for security.

    Accepts either order_id or preview_id - will look up the order accordingly.
    """

    try:
        logger.info("Getting download links", identifier=identifier)

        db = get_db()

        # Try to find order by order_id first, then by preview_id
        order_response = db.table("orders").select("*").eq("order_id", identifier).execute()

        if not order_response.data:
            # Try looking up by preview_id
            order_response = db.table("orders").select("*").eq("preview_id", identifier).execute()
            logger.info("Looking up order by preview_id", preview_id=identifier)

        if not order_response.data:
            raise HTTPException(status_code=404, detail="Order not found")

        order = order_response.data[0]

        # Check order status - only COMPLETED orders can be downloaded
        # Order flow: PAID -> GENERATING_PDF -> COMPLETED
        # B-4 FIX: Only allow COMPLETED to prevent broken download links
        valid_download_statuses = [OrderStatus.COMPLETED.value]
        
        if order["status"] == OrderStatus.GENERATING_PDF.value:
            return DownloadResponse(
                status="generating",
                progress=75,
                message="Your book is still being created. Please check back in a few minutes."
            )
        
        # B-4 FIX: PAID status means PDF is still being generated
        if order["status"] == OrderStatus.PAID.value:
            return DownloadResponse(
                status="generating",
                progress=25,
                message="Payment received! Your book is now being created. Please check back in a few minutes."
            )

        if order["status"] not in valid_download_statuses:
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

        # PDF download - use public URL directly since R2 bucket is public
        # Format: ChildName_ThemeName_Book.pdf (e.g. Vishnu_Enchanted_Forest_Book.pdf)
        theme_name = preview.get('theme', 'Story').replace('storygift_', '').replace('_', ' ').title().replace(' ', '_')
        child_name_clean = preview['child_name'].strip().replace(' ', '_')
        pdf_filename = f"{child_name_clean}_{theme_name}_Book.pdf"
        
        # Path is standard: final/{preview_id}/storygift_book.pdf
        pdf_path = f"final/{order['preview_id']}/storygift_book.pdf"
        
        # Use public URL directly - the R2 bucket has public access enabled
        # This is simpler and more reliable than S3 presigned URLs
        pdf_signed_url = f"{storage.settings.r2_public_url}/{pdf_path}"
        logger.info("Using public R2 URL for download", pdf_path=pdf_path, url=pdf_signed_url)

        # Get PDF file size (optional, don't fail if not available)
        pdf_size_mb = None
        try:
            # Try to get size from R2
            pdf_size_bytes = await storage.get_file_size(pdf_path)
            pdf_size_mb = round(pdf_size_bytes / 1024 / 1024, 1)
        except:
            pass

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
                    "filename": pdf_filename,
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
        logger.error("Failed to get download links", identifier=identifier, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve download links. Please try again."
        )
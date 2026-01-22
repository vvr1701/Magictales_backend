"""
Photo upload endpoint.
"""

import uuid
import imghdr
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Request
from typing import Optional
import structlog

from app.models.schemas import PhotoUploadResponse, ErrorResponse
from app.services.face_validation import FaceValidationService
from app.services.storage import StorageService
from app.core.exceptions import FaceValidationError, StorageError
from app.core.rate_limiter import limiter

logger = structlog.get_logger()
router = APIRouter()

# Allowed image types (validated by magic bytes)
ALLOWED_IMAGE_TYPES = {'jpeg', 'png', 'gif', 'webp'}


def validate_image_magic_bytes(file_bytes: bytes) -> str:
    """
    Validate image by checking magic bytes (file signature).
    More secure than trusting Content-Type header which can be spoofed.

    Returns the detected image type or raises HTTPException.
    """
    # imghdr.what() checks magic bytes, not file extension
    image_type = imghdr.what(None, h=file_bytes)

    if image_type not in ALLOWED_IMAGE_TYPES:
        logger.warning(
            "Invalid image magic bytes",
            detected_type=image_type,
            allowed_types=list(ALLOWED_IMAGE_TYPES)
        )
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_IMAGE_FORMAT",
                "message": f"Invalid image format. Allowed formats: JPEG, PNG, GIF, WebP. Detected: {image_type or 'unknown'}",
                "detected_type": image_type
            }
        )

    return image_type


@router.post("/upload-photo", response_model=PhotoUploadResponse)
@limiter.limit("10/minute")
async def upload_photo(
    request: Request,
    photo: UploadFile = File(..., description="Child's photo for face validation"),
    session_id: Optional[str] = Form(None, description="Optional session ID")
):
    """
    Upload and validate child photo.

    - Validates file type and size
    - Detects and validates face presence
    - Uploads to storage if valid
    - Returns photo URL for use in preview creation
    """

    try:
        logger.info("Photo upload started", filename=photo.filename, session_id=session_id)

        # Read file bytes first
        photo_bytes = await photo.read()

        # Validate file size (10MB limit)
        if len(photo_bytes) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail="File too large. Please upload an image smaller than 10MB."
            )

        # Validate image by magic bytes (more secure than Content-Type header)
        detected_type = validate_image_magic_bytes(photo_bytes)

        logger.info(
            "Photo file validated",
            size_bytes=len(photo_bytes),
            detected_type=detected_type,
            content_type=photo.content_type
        )

        # Validate face
        face_validator = FaceValidationService()
        validation_result = face_validator.validate(photo_bytes)

        if not validation_result.is_valid:
            logger.warning("Face validation failed", error=validation_result.error_code)
            raise HTTPException(
                status_code=400,
                detail={
                    "code": validation_result.error_code,
                    "message": validation_result.error_message,
                    "face_count": validation_result.face_count
                }
            )

        # Generate unique photo ID
        photo_id = str(uuid.uuid4())

        # Upload to storage
        storage = StorageService()
        photo_path = f"uploads/{photo_id}/photo.jpg"
        photo_url = await storage.upload_image(
            photo_bytes,
            photo_path,
            content_type="image/jpeg"
        )

        logger.info("Photo uploaded successfully", photo_id=photo_id, url=photo_url)

        return PhotoUploadResponse(
            photo_id=photo_id,
            photo_url=photo_url,
            face_valid=True,
            face_count=1
        )

    except FaceValidationError as e:
        logger.warning("Face validation error", error=str(e))
        raise HTTPException(
            status_code=400,
            detail={
                "code": e.code,
                "message": e.message,
                "details": e.details
            }
        )

    except StorageError as e:
        logger.error("Storage error during upload", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to upload photo. Please try again."
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error("Unexpected error during photo upload", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again."
        )
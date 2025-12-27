"""
Photo upload endpoint.
"""

import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import Optional
import structlog

from app.models.schemas import PhotoUploadResponse, ErrorResponse
from app.services.face_validation import FaceValidationService
from app.services.storage import StorageService
from app.core.exceptions import FaceValidationError, StorageError

logger = structlog.get_logger()
router = APIRouter()


@router.post("/upload-photo", response_model=PhotoUploadResponse)
async def upload_photo(
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

        # Validate file type
        if not photo.content_type or not photo.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an image file."
            )

        # Validate file size (10MB limit)
        photo_bytes = await photo.read()
        if len(photo_bytes) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail="File too large. Please upload an image smaller than 10MB."
            )

        logger.info("Photo file validated", size_bytes=len(photo_bytes))

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
"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models.enums import PreviewStatus, OrderStatus, JobStatus, JobType, BookStyle, Theme


# ==================
# Request Schemas
# ==================

class PhotoUploadRequest(BaseModel):
    """Request for uploading a child's photo."""
    session_id: Optional[str] = None


class PreviewCreateRequest(BaseModel):
    """Request to create a new preview."""
    photo_url: str = Field(..., description="URL of uploaded photo")
    child_name: str = Field(..., min_length=2, max_length=50)
    child_age: int = Field(..., ge=2, le=12)
    child_gender: str = Field(..., pattern="^(male|female)$")
    theme: Theme
    style: BookStyle = BookStyle.ARTISTIC
    session_id: Optional[str] = None
    customer_email: Optional[str] = None

    @validator("child_name")
    def validate_name(cls, v):
        """Validate name contains only letters and spaces."""
        if not all(c.isalpha() or c.isspace() for c in v):
            raise ValueError("Name must contain only letters and spaces")
        return v.strip()


# ==================
# Response Schemas
# ==================

class FaceValidationResult(BaseModel):
    """Result of face validation."""
    is_valid: bool
    face_count: int
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class PhotoUploadResponse(BaseModel):
    """Response after successful photo upload."""
    photo_id: str
    photo_url: str
    face_valid: bool
    face_count: int


class JobStartResponse(BaseModel):
    """Response when a background job is started."""
    job_id: str
    preview_id: str
    status: JobStatus
    estimated_time_seconds: int
    message: str


class JobStatusResponse(BaseModel):
    """Response for job status polling."""
    job_id: str
    status: JobStatus
    progress: int = Field(..., ge=0, le=100)
    current_step: Optional[str] = None
    preview_id: Optional[str] = None
    redirect_url: Optional[str] = None
    error: Optional[str] = None
    can_retry: bool = False


class PageData(BaseModel):
    """Data for a single storybook page."""
    page_number: int
    image_url: str
    story_text: str
    is_watermarked: bool = False
    is_locked: bool = False


class PreviewResponse(BaseModel):
    """Complete preview data for display."""
    preview_id: str
    status: PreviewStatus
    story_title: str
    child_name: str
    theme: Theme
    style: BookStyle
    preview_pages: List[PageData]
    locked_pages: Optional[List[PageData]] = None
    total_pages: int
    preview_pages_count: int
    locked_pages_count: int
    expires_at: datetime
    days_remaining: int
    purchase: dict


class DownloadInfo(BaseModel):
    """Download information for a file."""
    url: str
    filename: str
    size_mb: Optional[float] = None
    expires_in_seconds: int


class DownloadResponse(BaseModel):
    """Response with download links."""
    status: str
    downloads: Optional[dict] = None
    progress: Optional[int] = None
    message: Optional[str] = None
    expires_at: Optional[datetime] = None
    days_remaining: Optional[int] = None


# ==================
# Database Models (for type hints)
# ==================

class PreviewRecord(BaseModel):
    """Preview record from database."""
    id: int
    preview_id: UUID
    session_id: Optional[str]
    customer_id: Optional[str]
    customer_email: Optional[str]
    child_name: str
    child_age: int
    child_gender: str
    theme: str
    style: str
    photo_url: str
    photo_validated: bool
    status: str
    hires_images: List[dict]
    preview_images: List[dict]
    story_pages: List[dict]
    created_at: datetime
    updated_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class OrderRecord(BaseModel):
    """Order record from database."""
    id: int
    order_id: str
    order_number: Optional[str]
    preview_id: UUID
    customer_email: str
    customer_name: Optional[str]
    status: str
    pdf_url: Optional[str]
    pdf_generated_at: Optional[datetime]
    shipping_address: Optional[dict]
    tracking_number: Optional[str]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    expires_at: datetime

    class Config:
        from_attributes = True


class GenerationJobRecord(BaseModel):
    """Generation job record from database."""
    id: int
    job_id: UUID
    job_type: str
    reference_id: str
    status: str
    progress: int
    queued_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    attempts: int
    max_attempts: int
    error_message: Optional[str]
    result_data: Optional[dict]

    class Config:
        from_attributes = True


# ==================
# Error Response
# ==================

class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: dict = Field(..., description="Error details")


class SuccessResponse(BaseModel):
    """Standard success response."""
    success: bool = True
    data: dict

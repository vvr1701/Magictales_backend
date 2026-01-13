"""
Job status polling endpoint.
"""

from fastapi import APIRouter, HTTPException
import structlog

from app.models.schemas import JobStatusResponse
from app.models.database import get_db
from app.models.enums import JobStatus

logger = structlog.get_logger()
router = APIRouter()


async def _get_job_status_internal(job_id: str):
    """Internal function to get job status (shared by both endpoints)."""
    logger.info("Getting job status", job_id=job_id)

    db = get_db()

    # Get job record
    job_response = db.table("generation_jobs").select("*").eq("job_id", job_id).execute()

    if not job_response.data:
        raise HTTPException(status_code=404, detail="Job not found")

    job = job_response.data[0]

    # Get current step or default message
    current_step = None
    if job["status"] == JobStatus.QUEUED.value:
        current_step = "Queued for processing..."
    elif job["status"] == JobStatus.PROCESSING.value:
        current_step = job.get("current_step", "Generating images...")
    elif job["status"] == JobStatus.COMPLETED.value:
        current_step = "Generation completed!"
    elif job["status"] == JobStatus.FAILED.value:
        current_step = "Generation failed"

    # Build response based on status
    response_data = {
        "job_id": job_id,
        "status": JobStatus(job["status"]),
        "progress": job["progress"],
        "current_step": current_step,
        "preview_id": job["reference_id"],  # Always include preview_id
        "can_retry": False
    }

    # Add redirect for completed jobs
    if job["status"] == JobStatus.COMPLETED.value:
        response_data.update({
            "redirect_url": f"/preview/{job['reference_id']}"
        })

    # Add error info for failed jobs
    if job["status"] == JobStatus.FAILED.value:
        response_data.update({
            "error": job.get("error_message", "Generation failed"),
            "can_retry": job["attempts"] < job["max_attempts"]
        })

    return JobStatusResponse(**response_data)


@router.get("/preview-status/{job_id}", response_model=JobStatusResponse)
async def get_preview_status(job_id: str):
    """
    Get status of a preview generation job.

    Used for polling by frontend to track generation progress.
    Returns progress percentage and current step.
    """
    try:
        return await _get_job_status_internal(job_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job status", job_id=job_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve job status. Please try again."
        )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Alias for get_preview_status for frontend compatibility.
    Frontend expects /status/{job_id} endpoint.
    """
    try:
        return await _get_job_status_internal(job_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job status", job_id=job_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve job status. Please try again."
        )
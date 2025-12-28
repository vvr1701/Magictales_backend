"""
Fal.ai Face Swap implementation.
"""

import asyncio
import httpx
import time
import structlog

from app.config import get_settings
from app.ai.base import FaceSwapService, GenerationResult
from app.ai.model_registry import ModelConfig

logger = structlog.get_logger()


class FalFaceSwapService(FaceSwapService):
    """Fal.ai face swap implementation."""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.settings = get_settings()
        self.base_url = "https://queue.fal.run"

    async def swap_face(
        self,
        base_image_url: str,
        face_image_url: str,
        **kwargs
    ) -> GenerationResult:
        """Swap face onto base image using FAL.ai async queue API."""

        start_time = time.time()

        payload = {
            "base_image_url": base_image_url,
            "swap_image_url": face_image_url,
            **kwargs
        }

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                logger.info(
                    "Submitting face swap to queue",
                    model=self.config.model_id,
                    base_url=base_image_url[:100]
                )

                # Step 1: Submit to queue
                response = await client.post(
                    f"{self.base_url}/{self.config.endpoint}",
                    json=payload,
                    headers={
                        "Authorization": f"Key {self.settings.fal_api_key}",
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                queue_response = response.json()

                logger.info("Face swap queued",
                           request_id=queue_response.get("request_id"),
                           status=queue_response.get("status"),
                           queue_position=queue_response.get("queue_position", 0))

                request_id = queue_response["request_id"]
                status_url = queue_response["status_url"]
                response_url = queue_response["response_url"]

                # Step 2: Poll for completion
                max_polls = 30  # Max ~2 minutes of polling
                poll_interval = 4  # seconds

                for poll_count in range(max_polls):
                    if poll_count > 0:  # Don't wait on first check
                        await asyncio.sleep(poll_interval)

                    status_response = await client.get(
                        status_url,
                        headers={"Authorization": f"Key {self.settings.fal_api_key}"}
                    )
                    status_response.raise_for_status()
                    status_data = status_response.json()

                    current_status = status_data.get("status")
                    logger.info(f"Face swap status check {poll_count + 1}",
                               status=current_status,
                               request_id=request_id)

                    if current_status == "COMPLETED":
                        break
                    elif current_status == "FAILED":
                        return GenerationResult(
                            success=False,
                            error_message="Face swap generation failed on server",
                            model_used=self.config.model_id,
                            latency_ms=int((time.time() - start_time) * 1000)
                        )
                    elif current_status not in ["IN_QUEUE", "IN_PROGRESS"]:
                        return GenerationResult(
                            success=False,
                            error_message=f"Unexpected status: {current_status}",
                            model_used=self.config.model_id,
                            latency_ms=int((time.time() - start_time) * 1000)
                        )
                else:
                    # Polling timeout
                    return GenerationResult(
                        success=False,
                        error_message="Face swap generation timed out",
                        model_used=self.config.model_id,
                        latency_ms=int((time.time() - start_time) * 1000)
                    )

                # Step 3: Get final result
                final_response = await client.get(
                    response_url,
                    headers={"Authorization": f"Key {self.settings.fal_api_key}"}
                )
                final_response.raise_for_status()
                result = final_response.json()

                # Log the actual API response for debugging
                logger.info("Fal.ai Face Swap final result",
                           result_keys=list(result.keys()) if isinstance(result, dict) else None,
                           result_type=type(result).__name__,
                           result_sample=str(result)[:500])

                # Extract image URL from face swap format: {"image": {"url": "..."}}
                image_url = None
                if "image" in result and result["image"] is not None:
                    image_data = result["image"]
                    if isinstance(image_data, dict):
                        image_url = image_data.get("url")
                    elif isinstance(image_data, str):
                        image_url = image_data

                if not image_url:
                    return GenerationResult(
                        success=False,
                        error_message="Face swap did not return image URL",
                        model_used=self.config.model_id,
                        latency_ms=int((time.time() - start_time) * 1000)
                    )

                latency_ms = int((time.time() - start_time) * 1000)

                logger.info(
                    "Face swap successful",
                    model=self.config.model_id,
                    latency_ms=latency_ms,
                    image_url=image_url[:100]
                )

                return GenerationResult(
                    success=True,
                    image_url=image_url,
                    latency_ms=latency_ms,
                    model_used=self.config.model_id,
                    cost=self.config.cost_per_image
                )

        except httpx.HTTPStatusError as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
            logger.error("Face swap failed", error=error_msg, latency_ms=latency_ms)
            return GenerationResult(
                success=False,
                error_message=error_msg,
                model_used=self.config.model_id,
                latency_ms=latency_ms
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            logger.error("Face swap failed", error=error_msg, latency_ms=latency_ms)
            return GenerationResult(
                success=False,
                error_message=error_msg,
                model_used=self.config.model_id,
                latency_ms=latency_ms
            )

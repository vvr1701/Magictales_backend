"""
IP-Adapter Face-ID implementation.
"""

import asyncio
import httpx
import time
from typing import Optional
import structlog

from app.config import get_settings
from app.ai.base import FaceEmbeddingService, GenerationResult
from app.ai.model_registry import ModelConfig

logger = structlog.get_logger()


class IpAdapterFaceIdService(FaceEmbeddingService):
    """IP-Adapter Face-ID face-embedded generation."""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.settings = get_settings()
        self.base_url = "https://queue.fal.run"

    async def generate_with_face(
        self,
        prompt: str,
        face_image_url: str,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> GenerationResult:
        """Generate image with embedded face using IP-Adapter Face-ID."""

        start_time = time.time()

        payload = {
            "prompt": prompt,
            "face_image_url": face_image_url,  # Correct parameter per fal.ai documentation
            **self.config.default_params,
            **kwargs
        }

        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        if seed is not None:
            payload["seed"] = seed

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                logger.info(
                    "Submitting IP-Adapter Face-ID to queue",
                    model=self.config.model_id,
                    prompt=prompt[:100],
                    endpoint=f"{self.base_url}/{self.config.endpoint}",
                    payload_keys=list(payload.keys())
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

                logger.info("IP-Adapter Face-ID queued",
                           request_id=queue_response.get("request_id"),
                           status=queue_response.get("status"),
                           queue_position=queue_response.get("queue_position", 0))

                request_id = queue_response["request_id"]
                status_url = queue_response["status_url"]
                response_url = queue_response["response_url"]

                # Step 2: Poll for completion
                max_polls = 35  # Max ~3 minutes of polling (IP-Adapter is typically faster than PuLID)
                poll_interval = 5  # seconds

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
                    logger.info(f"IP-Adapter Face-ID status check {poll_count + 1}",
                               status=current_status,
                               request_id=request_id)

                    if current_status == "COMPLETED":
                        break
                    elif current_status == "FAILED":
                        return GenerationResult(
                            success=False,
                            error_message="IP-Adapter Face-ID generation failed on server",
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
                        error_message="IP-Adapter Face-ID generation timed out",
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
                logger.info("Fal.ai IP-Adapter Face-ID final result",
                           result_keys=list(result.keys()) if isinstance(result, dict) else None,
                           result_type=type(result).__name__,
                           result_sample=str(result)[:500])

                # Extract image URL - IP-Adapter may use different formats
                image_url = None

                # Try multiple possible response formats
                if "images" in result and result["images"] is not None:
                    if isinstance(result["images"], list) and len(result["images"]) > 0:
                        first_image = result["images"][0]
                        if isinstance(first_image, dict):
                            image_url = first_image.get("url")
                        elif isinstance(first_image, str):
                            image_url = first_image

                # Alternative format: direct image field
                elif "image" in result:
                    if isinstance(result["image"], dict):
                        image_url = result["image"].get("url")
                    elif isinstance(result["image"], str):
                        image_url = result["image"]

                # Alternative format: direct url field
                elif "url" in result:
                    image_url = result["url"]

                if not image_url:
                    return GenerationResult(
                        success=False,
                        error_message="IP-Adapter Face-ID did not return image URL",
                        model_used=self.config.model_id,
                        latency_ms=int((time.time() - start_time) * 1000)
                    )

                latency_ms = int((time.time() - start_time) * 1000)

                logger.info(
                    "Image generated successfully with IP-Adapter Face-ID",
                    model=self.config.model_id,
                    latency_ms=latency_ms,
                    image_url=image_url[:100]
                )

                return GenerationResult(
                    success=True,
                    image_url=image_url,
                    latency_ms=latency_ms,
                    model_used=self.config.model_id,
                    cost=self.config.cost_per_image,
                    metadata={"seed": seed}
                )

        except httpx.HTTPStatusError as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
            logger.error("IP-Adapter Face-ID generation failed", error=error_msg, latency_ms=latency_ms)
            return GenerationResult(
                success=False,
                error_message=error_msg,
                model_used=self.config.model_id,
                latency_ms=latency_ms
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            logger.error("IP-Adapter Face-ID generation failed", error=error_msg, latency_ms=latency_ms)
            return GenerationResult(
                success=False,
                error_message=error_msg,
                model_used=self.config.model_id,
                latency_ms=latency_ms
            )
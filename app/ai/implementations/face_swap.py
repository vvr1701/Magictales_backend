"""
Fal.ai Face Swap implementation.
"""

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
        """Swap face onto base image."""

        start_time = time.time()

        payload = {
            "base_image_url": base_image_url,
            "swap_image_url": face_image_url,
            **kwargs
        }

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                logger.info(
                    "Swapping face",
                    model=self.config.model_id,
                    base_url=base_image_url[:100]
                )

                response = await client.post(
                    f"{self.base_url}/{self.config.endpoint}",
                    json=payload,
                    headers={
                        "Authorization": f"Key {self.settings.fal_api_key}",
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                result = response.json()

                image_url = result.get("image", {}).get("url")
                latency_ms = int((time.time() - start_time) * 1000)

                logger.info(
                    "Face swap successful",
                    model=self.config.model_id,
                    latency_ms=latency_ms
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

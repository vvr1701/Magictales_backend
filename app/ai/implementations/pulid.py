"""
Flux PuLID face embedding implementation.
"""

import httpx
import time
from typing import Optional
import structlog

from app.config import get_settings
from app.ai.base import FaceEmbeddingService, GenerationResult
from app.ai.model_registry import ModelConfig

logger = structlog.get_logger()


class FluxPulidService(FaceEmbeddingService):
    """Flux PuLID face-embedded generation."""

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
        """Generate image with embedded face."""

        start_time = time.time()

        payload = {
            "prompt": prompt,
            "reference_images": [face_image_url],
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
                    "Generating image with Flux PuLID",
                    model=self.config.model_id,
                    prompt=prompt[:100]
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

                image_url = None
                if "images" in result and len(result["images"]) > 0:
                    image_url = result["images"][0].get("url")

                latency_ms = int((time.time() - start_time) * 1000)

                logger.info(
                    "Image generated successfully with PuLID",
                    model=self.config.model_id,
                    latency_ms=latency_ms
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
            logger.error("PuLID generation failed", error=error_msg, latency_ms=latency_ms)
            return GenerationResult(
                success=False,
                error_message=error_msg,
                model_used=self.config.model_id,
                latency_ms=latency_ms
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            logger.error("PuLID generation failed", error=error_msg, latency_ms=latency_ms)
            return GenerationResult(
                success=False,
                error_message=error_msg,
                model_used=self.config.model_id,
                latency_ms=latency_ms
            )

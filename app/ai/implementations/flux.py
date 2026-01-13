"""
Flux model implementations (schnell, dev, pro).
"""

import httpx
import time
import asyncio
from typing import Optional
import structlog

from app.config import get_settings
from app.ai.base import BaseGenerationService, GenerationResult
from app.ai.model_registry import ModelConfig

logger = structlog.get_logger()


class FluxGenerationService(BaseGenerationService):
    """Flux.1 text-to-image implementation."""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.settings = get_settings()
        self.base_url = "https://queue.fal.run"

    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        width: int = 1024,
        height: int = 1365,  # 3:4 aspect ratio for storybook
        **kwargs
    ) -> GenerationResult:
        """Generate image using Flux model."""

        start_time = time.time()

        # Build request payload using camelCase naming (required by fal.ai)
        payload = {
            "prompt": prompt,
            "imageSize": {
                "width": width,
                "height": height
            },
            **self.config.default_params,
            **kwargs
        }

        # Add optional parameters using camelCase
        if negative_prompt and self.config.supports_negative_prompt:
            payload["negativePrompt"] = negative_prompt

        if seed is not None and self.config.supports_seed:
            payload["seed"] = seed

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                logger.info(
                    "Generating image with Flux",
                    model=self.config.model_id,
                    prompt=prompt[:100]
                )

                # Submit to queue
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

                logger.info(
                    "Fal.ai initial response received",
                    model=self.config.model_id,
                    status=result.get("status"),
                    request_id=result.get("request_id")
                )

                # Handle queue-based response
                if result.get("status") == "IN_QUEUE":
                    # Poll for completion
                    image_url = await self._poll_for_result(client, result, start_time)
                    if not image_url:
                        return GenerationResult(
                            success=False,
                            error_message="Flux generation failed or timed out",
                            model_used=self.config.model_id,
                            latency_ms=int((time.time() - start_time) * 1000)
                        )
                else:
                    # Direct response (legacy or immediate completion)
                    image_url = self._extract_image_url(result)
                    if not image_url:
                        return GenerationResult(
                            success=False,
                            error_message="Flux generation did not return image URL",
                            model_used=self.config.model_id,
                            latency_ms=int((time.time() - start_time) * 1000)
                        )

                latency_ms = int((time.time() - start_time) * 1000)

                logger.info(
                    "Image generation completed",
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
                    metadata={"seed": seed, "prompt": prompt[:100]}
                )

        except httpx.HTTPStatusError as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
            logger.error(
                "Image generation failed",
                model=self.config.model_id,
                error=error_msg,
                latency_ms=latency_ms
            )
            return GenerationResult(
                success=False,
                error_message=error_msg,
                model_used=self.config.model_id,
                latency_ms=latency_ms
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            logger.error(
                "Image generation failed",
                model=self.config.model_id,
                error=error_msg,
                latency_ms=latency_ms
            )
            return GenerationResult(
                success=False,
                error_message=error_msg,
                model_used=self.config.model_id,
                latency_ms=latency_ms
            )

    async def _poll_for_result(self, client: httpx.AsyncClient, initial_result: dict, start_time: float) -> Optional[str]:
        """Poll Fal.ai for job completion and extract image URL."""
        status_url = initial_result.get("status_url")
        response_url = initial_result.get("response_url")
        request_id = initial_result.get("request_id")

        if not status_url or not response_url:
            logger.error("Missing status_url or response_url in queue response")
            return None

        logger.info(
            "Starting polling for job completion",
            model=self.config.model_id,
            request_id=request_id
        )

        max_polls = 60  # 5 minutes with 5-second intervals
        poll_interval = 5

        for poll_count in range(max_polls):
            try:
                # Check status
                status_response = await client.get(
                    status_url,
                    headers={"Authorization": f"Key {self.settings.fal_api_key}"}
                )
                status_response.raise_for_status()
                status_data = status_response.json()

                status = status_data.get("status")
                logger.info(
                    "Polling status check",
                    model=self.config.model_id,
                    poll=poll_count + 1,
                    status=status,
                    elapsed_seconds=int(time.time() - start_time)
                )

                if status == "COMPLETED":
                    # Fetch final result
                    result_response = await client.get(
                        response_url,
                        headers={"Authorization": f"Key {self.settings.fal_api_key}"}
                    )
                    result_response.raise_for_status()
                    final_result = result_response.json()

                    logger.info(
                        "Job completed, extracting image URL",
                        model=self.config.model_id,
                        final_result_keys=list(final_result.keys())
                    )

                    return self._extract_image_url(final_result)

                elif status in ["FAILED", "CANCELLED"]:
                    logger.error(
                        "Job failed or cancelled",
                        model=self.config.model_id,
                        status=status,
                        error=status_data.get("error")
                    )
                    return None

                # Still in progress, wait and try again
                await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error(
                    "Error during polling",
                    model=self.config.model_id,
                    poll=poll_count + 1,
                    error=str(e)
                )
                await asyncio.sleep(poll_interval)

        logger.error(
            "Polling timeout reached",
            model=self.config.model_id,
            max_polls=max_polls
        )
        return None

    def _extract_image_url(self, result: dict) -> Optional[str]:
        """Extract image URL from various response formats."""
        if not result or not isinstance(result, dict):
            return None

        # Try different response formats from fal.ai
        if "images" in result and result["images"] is not None and isinstance(result["images"], list) and len(result["images"]) > 0:
            # Format: {"images": [{"url": "..."}]}
            first_image = result["images"][0]
            if isinstance(first_image, dict):
                return first_image.get("url")
            elif isinstance(first_image, str):
                return first_image
        elif "image" in result and result["image"] is not None:
            # Format: {"image": {"url": "..."}} or {"image": "..."}
            image_data = result["image"]
            if isinstance(image_data, dict):
                return image_data.get("url")
            elif isinstance(image_data, str):
                return image_data
        elif "url" in result and result["url"] is not None:
            # Format: {"url": "..."}
            return result["url"]
        elif "data" in result and result["data"] is not None and isinstance(result["data"], list) and len(result["data"]) > 0:
            # Format: {"data": [{"url": "..."}]}
            first_item = result["data"][0]
            if isinstance(first_item, dict):
                return first_item.get("url")

        return None

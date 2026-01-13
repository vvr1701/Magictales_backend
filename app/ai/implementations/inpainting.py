"""
Flux Inpainting Service - For face refinement in 2-step pipeline.

Uses fal-ai/flux-general/inpainting to repaint face regions while
preserving the rest of the scene. This avoids the "uncanny valley"
effect of simple face-swapping.
"""

import asyncio
import httpx
import time
import structlog

from app.config import get_settings
from app.ai.base import GenerationResult
from app.ai.model_registry import ModelConfig

logger = structlog.get_logger()


class FluxInpaintingService:
    """
    Flux inpainting service for selective image editing.
    
    Used in 2-step pipeline to refine faces while preserving scenes.
    """

    def __init__(self, config: ModelConfig):
        self.config = config
        self.settings = get_settings()
        self.base_url = "https://queue.fal.run"

    async def inpaint(
        self,
        image_url: str,
        mask_url: str,
        prompt: str,
        strength: float = None,
        negative_prompt: str = None,
        seed: int = None,
        **kwargs
    ) -> GenerationResult:
        """
        Inpaint a region of an image using Flux.
        
        Args:
            image_url: URL of the base image (scene from Step 1)
            mask_url: URL of the mask image (white=repaint, black=keep)
            prompt: Text prompt describing desired face/content
            strength: Denoising strength (0.0-1.0, default 0.55)
            negative_prompt: What to avoid in generation
            seed: Random seed for reproducibility
            
        Returns:
            GenerationResult with inpainted image URL
        """
        start_time = time.time()

        # Use default strength from config if not provided
        if strength is None:
            strength = self.config.default_params.get("strength", 0.55)

        payload = {
            "image_url": image_url,
            "mask_url": mask_url,
            "prompt": prompt,
            "strength": strength,
            **self.config.default_params,
            **kwargs
        }

        # Remove strength from default_params to avoid duplication
        payload.pop("strength", None)
        payload["strength"] = strength

        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        if seed is not None:
            payload["seed"] = seed

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                logger.info(
                    "Submitting inpainting request to queue",
                    model=self.config.model_id,
                    image_url=image_url[:80] if image_url else None,
                    strength=strength,
                    endpoint=f"{self.base_url}/{self.config.endpoint}"
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

                logger.info(
                    "Inpainting request queued",
                    request_id=queue_response.get("request_id"),
                    status=queue_response.get("status"),
                    queue_position=queue_response.get("queue_position", 0)
                )

                request_id = queue_response["request_id"]
                status_url = queue_response["status_url"]
                response_url = queue_response["response_url"]

                # Step 2: Poll for completion
                max_polls = 40  # Max ~3 minutes
                poll_interval = 5  # seconds

                for poll_count in range(max_polls):
                    if poll_count > 0:
                        await asyncio.sleep(poll_interval)

                    status_response = await client.get(
                        status_url,
                        headers={"Authorization": f"Key {self.settings.fal_api_key}"}
                    )
                    status_response.raise_for_status()
                    status_data = status_response.json()

                    current_status = status_data.get("status")
                    logger.info(
                        f"Inpainting status check {poll_count + 1}",
                        status=current_status,
                        request_id=request_id
                    )

                    if current_status == "COMPLETED":
                        break
                    elif current_status == "FAILED":
                        return GenerationResult(
                            success=False,
                            error_message="Inpainting failed on server",
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
                    return GenerationResult(
                        success=False,
                        error_message="Inpainting request timed out",
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

                logger.info(
                    "Inpainting result received",
                    result_keys=list(result.keys()) if isinstance(result, dict) else None,
                    result_sample=str(result)[:300]
                )

                # Extract image URL - handle different response formats
                image_url_result = None
                if "images" in result and result["images"]:
                    first_image = result["images"][0]
                    if isinstance(first_image, dict):
                        image_url_result = first_image.get("url")
                    elif isinstance(first_image, str):
                        image_url_result = first_image
                elif "image" in result and result["image"]:
                    image_data = result["image"]
                    if isinstance(image_data, dict):
                        image_url_result = image_data.get("url")
                    elif isinstance(image_data, str):
                        image_url_result = image_data

                if not image_url_result:
                    return GenerationResult(
                        success=False,
                        error_message="Inpainting did not return image URL",
                        model_used=self.config.model_id,
                        latency_ms=int((time.time() - start_time) * 1000)
                    )

                latency_ms = int((time.time() - start_time) * 1000)

                logger.info(
                    "Inpainting completed successfully",
                    model=self.config.model_id,
                    latency_ms=latency_ms,
                    image_url=image_url_result[:100]
                )

                return GenerationResult(
                    success=True,
                    image_url=image_url_result,
                    latency_ms=latency_ms,
                    model_used=self.config.model_id,
                    cost=self.config.cost_per_image,
                    metadata={"strength": strength, "seed": seed}
                )

        except httpx.HTTPStatusError as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
            logger.error("Inpainting failed", error=error_msg, latency_ms=latency_ms)
            return GenerationResult(
                success=False,
                error_message=error_msg,
                model_used=self.config.model_id,
                latency_ms=latency_ms
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            logger.error("Inpainting failed", error=error_msg, latency_ms=latency_ms)
            return GenerationResult(
                success=False,
                error_message=error_msg,
                model_used=self.config.model_id,
                latency_ms=latency_ms
            )

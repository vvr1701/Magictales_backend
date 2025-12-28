"""
Photorealistic Pipeline - Single model with face embedding.
"""

import structlog
from typing import Optional

from app.ai.factory import ModelFactory
from app.ai.base import GenerationResult
from app.services.storage import StorageService
from app.config import get_settings

logger = structlog.get_logger()


class RealisticPipeline:
    """
    Photorealistic storybook pipeline.

    Flow:
    1. Generate image with face embedded (single call)
    2. Upload to storage
    """

    def __init__(self, model_id: Optional[str] = None):
        """
        Initialize pipeline with optional model override.

        Args:
            model_id: Override for face embedding model
        """
        self.settings = get_settings()
        self.storage = StorageService()

        # Create model instance
        self.face_embedder = ModelFactory.create_face_embedder(model_id)

        logger.info(
            "Realistic pipeline initialized",
            model=model_id or self.settings.realistic_model
        )

    async def generate_page(
        self,
        prompt: str,
        child_photo_url: str,
        output_path: str,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None
    ) -> GenerationResult:
        """Generate a single page with photorealistic style."""

        logger.info("Generating photorealistic page", prompt=prompt[:50])

        result = await self.face_embedder.generate_with_face(
            prompt=prompt,
            face_image_url=child_photo_url,
            negative_prompt=negative_prompt,
            seed=seed
        )

        if not result.success:
            logger.error("Generation failed", error=result.error_message)

            # Try fallback
            if self.settings.enable_model_fallback:
                logger.info("Trying fallback model")
                fallback_embedder = ModelFactory.create_face_embedder(
                    self.settings.fallback_realistic_model
                )
                result = await fallback_embedder.generate_with_face(
                    prompt=prompt,
                    face_image_url=child_photo_url,
                    negative_prompt=negative_prompt,
                    seed=seed
                )

                if not result.success:
                    return result
            else:
                return result

        # Check if we got a valid image URL
        if not result.image_url:
            logger.error("AI service returned None for image_url",
                        model=result.model_used,
                        success=result.success,
                        error=result.error_message)
            return GenerationResult(
                success=False,
                error_message="AI service did not return image URL",
                model_used=result.model_used,
                latency_ms=result.latency_ms
            )

        # Upload to storage
        final_url = await self.storage.download_and_upload(
            source_url=result.image_url,
            dest_path=output_path
        )

        return GenerationResult(
            success=True,
            image_url=final_url,
            latency_ms=result.latency_ms,
            model_used=result.model_used,
            cost=result.cost,
            metadata=result.metadata
        )

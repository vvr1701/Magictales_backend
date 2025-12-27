"""
Artistic Pipeline - Base Generation + Face Swap
Supports model switching via configuration.
"""

import structlog
from typing import Optional

from app.ai.factory import ModelFactory
from app.ai.base import GenerationResult
from app.services.storage import StorageService
from app.config import get_settings

logger = structlog.get_logger()


class ArtisticPipeline:
    """
    Artistic storybook pipeline.

    Flow:
    1. Generate base illustration (configurable model)
    2. Swap face onto illustration (configurable model)
    3. Upload final result to storage
    """

    def __init__(
        self,
        base_model_id: Optional[str] = None,
        face_model_id: Optional[str] = None
    ):
        """
        Initialize pipeline with optional model overrides.

        Args:
            base_model_id: Override for base generation model
            face_model_id: Override for face swap model
        """
        self.settings = get_settings()
        self.storage = StorageService()

        # Create model instances (uses config defaults if not overridden)
        self.base_generator = ModelFactory.create_base_generator(base_model_id)
        self.face_swapper = ModelFactory.create_face_swapper(face_model_id)

        logger.info(
            "Artistic pipeline initialized",
            base_model=base_model_id or self.settings.artistic_base_model,
            face_model=face_model_id or self.settings.artistic_face_model
        )

    async def generate_page(
        self,
        prompt: str,
        child_photo_url: str,
        output_path: str,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None
    ) -> GenerationResult:
        """
        Generate a single page with artistic style.

        Steps:
        1. Generate base illustration
        2. Upload to temporary storage
        3. Swap face onto illustration
        4. Upload final to output path
        """

        # Step 1: Generate base illustration
        logger.info("Generating base illustration", prompt=prompt[:50])

        base_result = await self.base_generator.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed
        )

        if not base_result.success:
            logger.error("Base generation failed", error=base_result.error_message)

            # Try fallback model
            if self.settings.enable_model_fallback:
                logger.info("Trying fallback model")
                fallback_generator = ModelFactory.create_base_generator(
                    self.settings.fallback_base_model
                )
                base_result = await fallback_generator.generate(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    seed=seed
                )

                if not base_result.success:
                    return base_result
            else:
                return base_result

        # Step 2: Swap face
        logger.info("Swapping face onto illustration")

        swap_result = await self.face_swapper.swap_face(
            base_image_url=base_result.image_url,
            face_image_url=child_photo_url
        )

        if not swap_result.success:
            logger.error("Face swap failed", error=swap_result.error_message)
            return swap_result

        # Step 3: Upload to final storage
        logger.info("Uploading to storage", path=output_path)

        final_url = await self.storage.download_and_upload(
            source_url=swap_result.image_url,
            dest_path=output_path
        )

        # Calculate total cost
        total_cost = base_result.cost + swap_result.cost
        total_latency = base_result.latency_ms + swap_result.latency_ms

        return GenerationResult(
            success=True,
            image_url=final_url,
            latency_ms=total_latency,
            model_used=f"{base_result.model_used}+{swap_result.model_used}",
            cost=total_cost,
            metadata={
                "base_model": base_result.model_used,
                "face_model": swap_result.model_used,
                "seed": seed
            }
        )

"""
NanoBanana Pipeline - StoryGift-style photorealistic generation.

Replicates StoryGift's superior approach:
- VLM face analysis using LLaVA-Next
- NanoBanana model for face-embedded generation
- Sequential generation to avoid API limits
- 5:4 aspect ratio optimized for print
"""

import time
import structlog
from typing import Optional, Dict, List, Any
import httpx

from app.ai.base import GenerationResult
from app.services.storage import StorageService
from app.config import get_settings

logger = structlog.get_logger()


class NanoBananaPipeline:
    """
    NanoBanana pipeline implementing StoryGift's proven approach.

    Flow:
    1. Analyze child's face using LLaVA-Next VLM (like StoryGift)
    2. Generate each page with NanoBanana using face analysis + prompt
    3. Sequential generation to avoid API concurrency limits
    4. Store results in cloud storage
    """

    def __init__(self, model_override: Optional[str] = None):
        """
        Initialize NanoBanana pipeline.

        Args:
            model_override: Optional model override (defaults to nano_banana)
        """
        self.settings = get_settings()
        self.storage = StorageService()

        # NanoBanana model configuration (from StoryGift)
        self.model_id = "fal-ai/nano-banana/edit"
        self.model_name = "nano_banana"

        logger.info(
            "NanoBanana pipeline initialized",
            model_id=self.model_id,
            testing_mode=self.settings.testing_mode_enabled
        )

    async def analyze_face(self, face_image_url: str) -> str:
        """
        Analyze child's face using LLaVA-Next VLM.

        This replicates StoryGift's analyzeImage function (lines 118-138).
        Extracts detailed facial features for consistent generation.

        Args:
            face_image_url: URL of child's reference photo

        Returns:
            Detailed facial description string
        """
        try:
            logger.info("Starting VLM face analysis", image_url=face_image_url)
            start_time = time.time()

            # Use LLaVA-Next for face analysis (same as StoryGift)
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://fal.run/fal-ai/llava-next",
                    headers={
                        "Authorization": f"Key {self.settings.fal_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "image_url": face_image_url,
                        # CRITICAL: Exact prompt from StoryGift for consistent analysis
                        "prompt": "Describe the child's face, hair color, hair texture, eye color, nose shape, and body type in detail. Be precise about facial features to ensure resemblance. Do not describe the clothing or background. Example: 'a cute chubby toddler with round cheeks, button nose, curly brown hair and big expressive hazel eyes'.",
                        "max_tokens": 150
                    }
                )

            if response.status_code == 200:
                result = response.json()
                analysis_result = result.get("output", "")

                latency = int((time.time() - start_time) * 1000)
                logger.info(
                    "VLM face analysis completed",
                    latency_ms=latency,
                    analysis_length=len(analysis_result)
                )

                return analysis_result or "a cute child"  # Fallback
            else:
                logger.error(
                    "VLM analysis failed",
                    status_code=response.status_code,
                    response=response.text
                )
                return "a cute child"  # Fallback

        except Exception as e:
            logger.error("VLM analysis error", error=str(e))
            return "a cute child"  # Fallback

    async def generate_with_face_analysis(
        self,
        prompt: str,
        face_url: str,
        child_name: str,
        analyzed_features: Optional[str] = None,
        aspect_ratio: str = "5:4",  # Default for story pages, use "1:1" for covers
        seed: Optional[int] = None
    ) -> GenerationResult:
        """
        Generate single image using NanoBanana with face analysis.

        Args:
            prompt: Scene description prompt
            face_url: Child's reference photo URL
            child_name: Child's name for prompt personalization
            analyzed_features: Pre-analyzed facial features (optional)
            seed: Random seed for generation

        Returns:
            GenerationResult with image URL and metadata
        """
        start_time = time.time()

        try:
            # Use pre-analyzed features or analyze now
            if not analyzed_features:
                analyzed_features = await self.analyze_face(face_url)

            # Build enhanced prompt with facial analysis (StoryGift approach)
            enhanced_prompt = self._build_enhanced_prompt(
                prompt, child_name, analyzed_features
            )

            logger.info(
                "Starting NanoBanana generation",
                prompt_length=len(enhanced_prompt),
                child_name=child_name
            )

            # NanoBanana API call with StoryGift configuration
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "prompt": enhanced_prompt,
                    "image_urls": [face_url],  # NanoBanana uses image_urls array
                    "aspect_ratio": aspect_ratio,  # 5:4 for pages, 1:1 for cover
                    "negative_prompt": "black bars, letterbox, scope, cinema bars, blurry, low quality, distorted face",
                }

                if seed:
                    payload["seed"] = seed

                response = await client.post(
                    "https://fal.run/fal-ai/nano-banana/edit",
                    headers={
                        "Authorization": f"Key {self.settings.fal_api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )

            if response.status_code == 200:
                result = response.json()
                images = result.get("images", [])

                if images and len(images) > 0:
                    image_url = images[0].get("url")

                    latency = int((time.time() - start_time) * 1000)

                    logger.info(
                        "NanoBanana generation successful",
                        latency_ms=latency,
                        image_url=image_url
                    )

                    return GenerationResult(
                        success=True,
                        image_url=image_url,
                        latency_ms=latency,
                        model_used=self.model_name,
                        cost=0.04,  # NanoBanana cost per image
                        metadata={
                            "analyzed_features": analyzed_features,
                            "seed": seed,
                            "aspect_ratio": aspect_ratio
                        }
                    )
                else:
                    return GenerationResult(
                        success=False,
                        error_message="No images returned from NanoBanana",
                        latency_ms=int((time.time() - start_time) * 1000),
                        model_used=self.model_name
                    )
            else:
                error_msg = f"NanoBanana API error: {response.status_code}"
                logger.error(error_msg, response_text=response.text)

                return GenerationResult(
                    success=False,
                    error_message=error_msg,
                    latency_ms=int((time.time() - start_time) * 1000),
                    model_used=self.model_name
                )

        except Exception as e:
            error_msg = f"NanoBanana generation failed: {str(e)}"
            logger.error(error_msg, error=e)

            return GenerationResult(
                success=False,
                error_message=error_msg,
                latency_ms=int((time.time() - start_time) * 1000),
                model_used=self.model_name
            )

    async def generate_all_pages(
        self,
        story_pages: List[Dict[str, Any]],
        face_url: str,
        child_name: str,
        preview_id: str,
        testing_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Generate all story pages sequentially (StoryGift approach).

        Args:
            story_pages: List of page data with prompts
            face_url: Child's reference photo URL
            child_name: Child's name
            preview_id: Preview ID for storage paths
            testing_mode: If True, generate only 5 pages, else 10 pages

        Returns:
            Dict with successful pages and generation metadata
        """
        logger.info(
            "Starting batch page generation",
            total_pages=len(story_pages),
            testing_mode=testing_mode,
            preview_id=preview_id
        )

        # Determine page count based on testing mode
        page_count = self.settings.testing_mode_pages if testing_mode else len(story_pages)
        pages_to_generate = story_pages[:page_count]

        logger.info(f"Generating {page_count} pages in {'testing' if testing_mode else 'production'} mode")

        # Analyze face once for all generations (efficiency)
        analyzed_features = await self.analyze_face(face_url)

        successful_pages = []
        failed_pages = []
        total_cost = 0.0

        # Sequential generation to avoid API limits (StoryGift approach)
        for i, page_data in enumerate(pages_to_generate):
            page_number = i + 1
            logger.info(f"Generating page {page_number}/{page_count}")

            try:
                # Get prompt from page data
                prompt = page_data.get("prompt", page_data.get("realistic_prompt", ""))
                if not prompt:
                    logger.warning(f"No prompt found for page {page_number}")
                    continue

                # Generate the page
                result = await self.generate_with_face_analysis(
                    prompt=prompt,
                    face_url=face_url,
                    child_name=child_name,
                    analyzed_features=analyzed_features
                )

                if result.success:
                    # Store in cloud storage
                    storage_path = f"final/{preview_id}/page_{page_number:02d}.jpg"
                    stored_url = await self.storage.store_from_url(
                        result.image_url, storage_path
                    )

                    successful_pages.append({
                        "page_number": page_number,
                        "image_url": stored_url,
                        "original_prompt": prompt,
                        "latency_ms": result.latency_ms
                    })

                    total_cost += result.cost
                    logger.info(f"Page {page_number} generated successfully")
                else:
                    logger.error(f"Page {page_number} generation failed: {result.error_message}")
                    failed_pages.append({
                        "page_number": page_number,
                        "error": result.error_message
                    })

            except Exception as e:
                logger.error(f"Page {page_number} generation error", error=str(e))
                failed_pages.append({
                    "page_number": page_number,
                    "error": str(e)
                })

        logger.info(
            "Batch generation completed",
            successful_pages=len(successful_pages),
            failed_pages=len(failed_pages),
            total_cost=total_cost
        )

        return {
            "successful_pages": successful_pages,
            "failed_pages": failed_pages,
            "total_cost": total_cost,
            "analyzed_features": analyzed_features,
            "testing_mode": testing_mode,
            "pages_generated": len(successful_pages)
        }

    def _build_enhanced_prompt(
        self,
        base_prompt: str,
        child_name: str,
        analyzed_features: str
    ) -> str:
        """
        Build enhanced prompt with facial analysis (StoryGift approach).

        This replicates StoryGift's prompt layering system:
        - Subject + Appearance
        - Scene Action
        - Style constraints
        """
        # Replace {name} tokens with actual child name
        personalized_prompt = base_prompt.replace("{name}", child_name)

        # Build layered prompt (StoryGift style)
        enhanced_prompt = f"""Subject: The child named {child_name}.
Appearance: {analyzed_features}.

Scene Action: {personalized_prompt}.

Environment: Masterpiece, 8k resolution, photorealistic, intricate details, sharp focus, ray tracing, soft volumetric lighting.

Style: an award-winning cinematic photograph, hyper-realistic, highly detailed skin texture, 8k resolution, deep depth of field, sharp background, soft natural lighting, shot on 35mm film.

Constraint: identical character face, consistent clothing, perfect face integration."""

        return enhanced_prompt
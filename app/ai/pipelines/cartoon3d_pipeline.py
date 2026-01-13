"""
Cartoon3D Pipeline - Disney/Pixar 3D Animation style generation.

Uses the same NanoBanana model but with different prompts optimized for
3D animated cartoon style (Disney/Pixar aesthetic).

Architecture note: This is a separate pipeline so we can easily swap to a
different model in the future if needed.
"""

import time
import structlog
from typing import Optional, Dict, List, Any
import httpx

from app.ai.base import GenerationResult
from app.services.storage import StorageService
from app.config import get_settings

logger = structlog.get_logger()


# Style block for 3D cartoon (Disney/Pixar) prompts
CARTOON_3D_STYLE_BLOCK = """
Disney Pixar 3D animation style, Dreamworks quality CGI, adorable cartoon character,
big expressive eyes, smooth stylized features, vibrant saturated colors,
soft ambient occlusion, subsurface scattering on skin, 3D rendered quality,
Toy Story aesthetic, How to Train Your Dragon quality, cute and charming expression,
professional 3D animation studio quality, Zootopia-level character design,
warm inviting lighting, magical whimsical atmosphere, 8K render, CGI masterpiece.
"""

# Negative prompt for cartoon style - avoid photorealistic elements
CARTOON_3D_NEGATIVE_PROMPT = """
photorealistic, photograph, real person, realistic skin texture, pores,
blurry, low quality, distorted, deformed, ugly, bad anatomy, extra limbs,
extra fingers, mutated hands, poorly drawn face, mutation, watermark,
signature, cropped, out of frame, duplicate, multiple heads,
dark horror scary, gore violence, adult mature content,
2D flat cartoon, anime style, sketch, line art, pencil drawing
"""


class Cartoon3DPipeline:
    """
    Cartoon3D pipeline for Disney/Pixar style generation.

    Flow:
    1. Analyze child's face using LLaVA-Next VLM (same as NanoBanana)
    2. Generate each page with NanoBanana using cartoon-optimized prompts
    3. Sequential generation to avoid API limits
    4. Store results in cloud storage
    """

    def __init__(self, model_override: Optional[str] = None):
        """
        Initialize Cartoon3D pipeline.

        Args:
            model_override: Optional model override (defaults to nano_banana)
        """
        self.settings = get_settings()
        self.storage = StorageService()

        # Uses same NanoBanana model - can be swapped later if needed
        self.model_id = "fal-ai/nano-banana/edit"
        self.model_name = "cartoon_3d"

        logger.info(
            "Cartoon3D pipeline initialized",
            model_id=self.model_id,
            testing_mode=self.settings.testing_mode_enabled
        )

    async def analyze_face(self, face_image_url: str) -> str:
        """
        Analyze child's face using LLaVA-Next VLM.

        This replicates StoryGift's analyzeImage function.
        Extracts detailed facial features for consistent generation.

        Args:
            face_image_url: URL of child's reference photo

        Returns:
            Detailed facial description string
        """
        try:
            logger.info("Starting VLM face analysis for cartoon", image_url=face_image_url)
            start_time = time.time()

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://fal.run/fal-ai/llava-next",
                    headers={
                        "Authorization": f"Key {self.settings.fal_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "image_url": face_image_url,
                        # Adjusted prompt for cartoon style - focus on key identifying features
                        "prompt": "Describe the child's key features for a cartoon character: hair color, hair style, eye color, and any distinctive features. Be concise but accurate. Example: 'curly brown hair, big hazel eyes, round cheerful face'.",
                        "max_tokens": 100
                    }
                )

            if response.status_code == 200:
                result = response.json()
                analysis_result = result.get("output", "")

                latency = int((time.time() - start_time) * 1000)
                logger.info(
                    "VLM face analysis for cartoon completed",
                    latency_ms=latency,
                    analysis_length=len(analysis_result)
                )

                return analysis_result or "a cute child with expressive features"
            else:
                logger.error(
                    "VLM analysis failed",
                    status_code=response.status_code,
                    response_text=response.text
                )
                return "a cute child with expressive features"

        except Exception as e:
            logger.error("VLM analysis error", error=str(e))
            return "a cute child with expressive features"

    async def generate_with_face_analysis(
        self,
        prompt: str,
        face_url: str,
        child_name: str,
        analyzed_features: Optional[str] = None,
        seed: Optional[int] = None
    ) -> GenerationResult:
        """
        Generate single image using NanoBanana with cartoon-style prompts.

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

            # Build enhanced prompt with cartoon styling
            enhanced_prompt = self._build_cartoon_prompt(
                prompt, child_name, analyzed_features
            )

            logger.info(
                "Starting Cartoon3D generation",
                prompt_length=len(enhanced_prompt),
                child_name=child_name
            )

            # NanoBanana API call with cartoon configuration
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "prompt": enhanced_prompt,
                    "image_urls": [face_url],
                    "aspect_ratio": "5:4",
                    "negative_prompt": CARTOON_3D_NEGATIVE_PROMPT.strip(),
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
                        "Cartoon3D generation successful",
                        latency_ms=latency,
                        image_url=image_url
                    )

                    return GenerationResult(
                        success=True,
                        image_url=image_url,
                        latency_ms=latency,
                        model_used=self.model_name,
                        cost=0.04,
                        metadata={
                            "analyzed_features": analyzed_features,
                            "seed": seed,
                            "aspect_ratio": "5:4",
                            "style": "cartoon_3d"
                        }
                    )
                else:
                    return GenerationResult(
                        success=False,
                        error_message="No images returned from Cartoon3D generation",
                        latency_ms=int((time.time() - start_time) * 1000),
                        model_used=self.model_name
                    )
            else:
                error_msg = f"Cartoon3D API error: {response.status_code}"
                logger.error(
                    error_msg,
                    response_text=response.text,
                    url="https://fal.run/fal-ai/nano-banana/edit"
                )

                return GenerationResult(
                    success=False,
                    error_message=f"{error_msg}: {response.text}",
                    latency_ms=int((time.time() - start_time) * 1000),
                    model_used=self.model_name
                )

        except Exception as e:
            error_msg = f"Cartoon3D generation failed: {str(e)}"
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
        Generate all story pages sequentially with cartoon style.

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
            "Starting batch cartoon page generation",
            total_pages=len(story_pages),
            testing_mode=testing_mode,
            preview_id=preview_id
        )

        page_count = self.settings.testing_mode_pages if testing_mode else len(story_pages)
        pages_to_generate = story_pages[:page_count]

        # Analyze face once for all generations
        analyzed_features = await self.analyze_face(face_url)

        successful_pages = []
        failed_pages = []
        total_cost = 0.0

        for i, page_data in enumerate(pages_to_generate):
            page_number = i + 1
            logger.info(f"Generating cartoon page {page_number}/{page_count}")

            try:
                prompt = page_data.get("prompt", page_data.get("realistic_prompt", ""))
                if not prompt:
                    logger.warning(f"No prompt found for page {page_number}")
                    continue

                result = await self.generate_with_face_analysis(
                    prompt=prompt,
                    face_url=face_url,
                    child_name=child_name,
                    analyzed_features=analyzed_features
                )

                if result.success:
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
                    logger.info(f"Cartoon page {page_number} generated successfully")
                else:
                    logger.error(f"Cartoon page {page_number} failed: {result.error_message}")
                    failed_pages.append({
                        "page_number": page_number,
                        "error": result.error_message
                    })

            except Exception as e:
                logger.error(f"Cartoon page {page_number} error", error=str(e))
                failed_pages.append({
                    "page_number": page_number,
                    "error": str(e)
                })

        logger.info(
            "Batch cartoon generation completed",
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

    def _build_cartoon_prompt(
        self,
        base_prompt: str,
        child_name: str,
        analyzed_features: str
    ) -> str:
        """
        Build enhanced prompt with cartoon styling (Disney/Pixar).

        This uses the same layered approach as NanoBanana but with
        cartoon-specific style modifiers.
        """
        # Replace {name} tokens with actual child name
        personalized_prompt = base_prompt.replace("{name}", child_name)

        # Build layered prompt with cartoon styling
        enhanced_prompt = f"""Subject: A cute 3D animated cartoon child character inspired by {child_name}.
Appearance: Cartoon version with {analyzed_features}, stylized in Disney Pixar 3D animation style.

Scene Action: {personalized_prompt}.

{CARTOON_3D_STYLE_BLOCK.strip()}

Character Design: Big expressive eyes, rounded adorable features, smooth stylized skin,
charming animated expressions, consistent character design throughout.

Constraint: Maintain consistent cartoon character design, keep the recognizable features
from reference but stylized as 3D animation character."""

        return enhanced_prompt

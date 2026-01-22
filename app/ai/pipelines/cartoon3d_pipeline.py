"""
Cartoon3D Pipeline - Cinematic Stylized Painting Style.

Uses the same NanoBanana model but with prompts optimized for
a CINEMATIC PAINTING style that PRESERVES the child's actual facial identity
while adding artistic stylization.

Architecture note: This is a separate pipeline so we can easily swap to a
different model in the future if needed.

Style Philosophy: 
- "Parents should instantly recognize their child"
- Hyper-detailed skin textures + stylized artistic lighting
- Inspired by: Pixar concept art, Spider-Verse, Arcane, DreamWorks, high-end book covers
- Goal: Look like a $500 commissioned digital painting, not a plastic 3D render
"""

import time
import structlog
from typing import Optional, Dict, List, Any
import httpx

from app.ai.base import GenerationResult
from app.services.storage import StorageService
from app.config import get_settings

logger = structlog.get_logger()


# =============================================================================
# ENHANCED VLM FACE ANALYSIS PROMPT
# Captures precise facial geometry for identity preservation
# =============================================================================
FACE_ANALYSIS_PROMPT = """Analyze this child's face with PRECISE DETAIL for identity preservation:

FACIAL STRUCTURE:
- Face shape (oval, round, square, heart, etc.)
- Forehead height and width
- Cheekbone position and prominence
- Jawline shape and chin

DISTINCTIVE FEATURES:
- Eye shape (almond, round, hooded, etc.), spacing, and exact color
- Nose shape (button, straight, upturned tip, bridge width)
- Lip shape (full, thin, cupid's bow prominence)
- Eyebrow shape and thickness

HAIR:
- Color (be specific: honey brown, jet black, strawberry blonde, etc.)
- Texture (curly, wavy, straight, coiled)
- Style and length

AGE MARKERS:
- Approximate age (toddler 2-4, child 5-8, etc.)
- Baby fat presence on cheeks
- Tooth visibility if smiling

Output a DETAILED description focusing on what makes THIS child unique and recognizable.
Example: 'A 4-year-old girl with an oval face, round cheeks with soft baby fat, wide-set almond-shaped eyes with dark brown irises, a small button nose with slightly upturned tip, full rosy lips, thick curved eyebrows, and curly dark brown hair reaching her shoulders.'"""


# =============================================================================
# CINEMATIC PAINTING STYLE
# Hyper-realistic digital painting with cinematic stylization
# Reference: Pixar concept art, Spider-Verse, Arcane, high-end book illustration
# Goal: Premium commissioned artwork feel - realistic yet unmistakably artistic
# =============================================================================
CINEMATIC_PAINTING_STYLE = """
Art Style: Premium cinematic digital painting, hyper-detailed character portrait.

SKIN & FACE RENDERING (CRITICAL - PRIORITY 1):
- Skin must have VISIBLE TEXTURE: pores, peach fuzz, natural imperfections
- Subsurface Scattering (SSS) for warm, translucent, lifelike skin tones
- NO plastic, waxy, or CG-doll appearance - must look touchable and real
- Eyes: Ultra-detailed iris with depth, reflections, and life - the "window to the soul"
- Natural skin color variations: rosy cheeks, slight shadows under eyes

LIGHTING & ATMOSPHERE:
- Dramatic cinematic lighting with rim lights and key light separation
- Rich color grading inspired by Pixar, DreamWorks concept art
- Volumetric light rays, atmospheric depth, bokeh in background
- Golden hour warmth or dramatic sunset gradients

ARTISTIC STYLIZATION:
- Painterly brush strokes visible in background and clothing
- Character silhouettes enhanced with subtle stylization
- Environment rendered with impressionistic detail - not photorealistic
- Color palette: Vibrant, saturated, emotionally evocative

IDENTITY PRESERVATION (NON-NEGOTIABLE):
- Maintain EXACT facial geometry from reference (nose shape, eye spacing, face shape)
- Child's unique features must be immediately recognizable
- Natural child proportions - no anime/chibi distortion
- Expression: Dynamic, full of life and personality
"""


# =============================================================================
# NEGATIVE PROMPT - Blocks cheap CG looks, ensures premium painting quality
# =============================================================================
CINEMATIC_NEGATIVE_PROMPT = """
plastic skin, waxy finish, CG doll, vinyl toy look, airbrushed, over-smoothed,
flat lifeless texture, soft focus everywhere, low resolution, jpeg artifacts,
bad anatomy, distorted proportions, extra limbs, mutated hands,
watermark, signature, text, logo,
oversized anime eyes, chibi proportions, 2D vector art, simple clipart,
generic 3D render, unity engine, unreal engine default lighting,
harsh unflattering shadows, overexposed, burnout, HDR artifacts,
scary, creepy, uncanny valley, horror, adult features on child,
generic stock photo, amateur photography, passport photo,
face completely different from reference, unrecognizable child,
adult face on child body, wrong age features, aging, wrinkles,
cheap mobile game art, low-budget animation, flash animation
"""


class Cartoon3DPipeline:
    """
    Cartoon3D pipeline for Premium Animated Portrait Painting style.

    Flow:
    1. Analyze child's face using LLaVA-Next VLM with ENHANCED geometry analysis
    2. Generate each page with NanoBanana using identity-preserving prompts
    3. Sequential generation to avoid API limits
    4. Store results in cloud storage
    
    Style: Premium digital painting that preserves the child's actual facial identity.
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
        self.model_name = "animated_portrait"  # Updated style name

        logger.info(
            "Cartoon3D pipeline initialized",
            model_id=self.model_id,
            testing_mode=self.settings.testing_mode_enabled
        )

    async def analyze_face(self, face_image_url: str) -> str:
        """
        Analyze child's face using LLaVA-Next VLM with ENHANCED geometry analysis.

        Uses detailed facial structure analysis to capture unique identifying
        features that make the child recognizable.

        Args:
            face_image_url: URL of child's reference photo

        Returns:
            Detailed facial description string with precise geometry
        """
        try:
            logger.info("Starting ENHANCED VLM face analysis for animated portrait", image_url=face_image_url)
            start_time = time.time()

            async with httpx.AsyncClient(timeout=45.0) as client:  # Increased timeout for detailed analysis
                response = await client.post(
                    "https://fal.run/fal-ai/llava-next",
                    headers={
                        "Authorization": f"Key {self.settings.fal_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "image_url": face_image_url,
                        # ENHANCED: Detailed facial geometry prompt for identity preservation
                        "prompt": FACE_ANALYSIS_PROMPT,
                        "max_tokens": 250  # Increased for detailed description
                    }
                )

            if response.status_code == 200:
                result = response.json()
                analysis_result = result.get("output", "")

                latency = int((time.time() - start_time) * 1000)
                logger.info(
                    "Enhanced VLM face analysis completed",
                    latency_ms=latency,
                    analysis_length=len(analysis_result),
                    analysis_preview=analysis_result[:150] if analysis_result else "empty"
                )

                return analysis_result or "a young child with natural, expressive features"
            else:
                logger.error(
                    "VLM analysis failed",
                    status_code=response.status_code,
                    response_text=response.text
                )
                return "a young child with natural, expressive features"

        except Exception as e:
            logger.error("VLM analysis error", error=str(e))
            return "a young child with natural, expressive features"

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

            # NanoBanana API call with animated portrait configuration
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "prompt": enhanced_prompt,
                    "image_urls": [face_url],
                    "aspect_ratio": "5:4",
                    "negative_prompt": CINEMATIC_NEGATIVE_PROMPT.strip(),
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
                            "style": "animated_portrait"
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
        Builds prompt with cinematic painting style instructions.
        
        This creates a unified visual language for both cover and story pages,
        ensuring consistency across the entire book.
        """
        # Replace {name} tokens with actual child name
        personalized_prompt = base_prompt.replace("{name}", child_name)

        # Build enhanced prompt with cinematic painting style
        # The styling instructions wrap the scene to ensure consistent output
        enhanced_prompt = f"""[ARTISTIC DIRECTION: Premium Digital Painting]

SCENE: {personalized_prompt}

CHILD CHARACTER: {child_name}
FACIAL REFERENCE: {analyzed_features}

[SKIN & FACE RENDERING - CRITICAL]
- Render {child_name}'s face with HYPER-REALISTIC skin texture
- Visible pores, fine fuzz, natural imperfections - NOT smooth CG plastic
- Use Subsurface Scattering (SSS) for warm, luminous, lifelike skin
- Eyes must be ultra-detailed with iris depth, reflections, and life
- Rosy cheeks, natural skin color variations

{CINEMATIC_PAINTING_STYLE.strip()}

FINAL OUTPUT: A premium cinematic digital painting worthy of a $500 commissioned artwork.
The child should be immediately recognizable to their parents."""

        return enhanced_prompt

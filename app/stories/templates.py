"""
Story template structure and base classes.
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class PageTemplate:
    """Template for a single story page."""
    page_number: int
    scene_description: str
    realistic_prompt: str     # For NanoBanana pipeline (photorealistic)
    story_text: str           # Text with {name} placeholder
    artistic_prompt: Optional[str] = None  # For comic book style with Flux Dev + Face Swap
    costume: Optional[str] = None
    scene_type: Optional[str] = None  # For cinematic enhancement: "heroic", "intimate", "action", etc.
    camera_style: Optional[str] = None  # Override camera angle if needed
    lighting_style: Optional[str] = None  # Override lighting if needed


# Base cover prompt template with zone-based composition for typography
# Optimized for consistent photorealistic face rendering
COVER_PROMPT_TEMPLATE = """
A high-quality DSLR photograph of a real child in a fantasy setting. 
Professional portrait photography with natural lighting. RAW photo quality.

COMPOSITION (STRICT):

TOP ZONE (Upper 20%):
- {header_atmosphere}
- Empty space for typography - no characters or objects here

MAIN SUBJECT (Center 65%):
- A real human child named {name} stands confidently in the center
- Position the child's face in the center of the frame, fully visible
- CRITICAL FACE REQUIREMENTS:
  * Real human child photographed with a DSLR camera
  * Natural skin with pores and texture visible
  * Realistic eyes with natural light reflections
  * No CGI, no 3D rendering, no illustration style
  * No fantasy glow on skin or face
  * Sharp focus on face, like a portrait photograph
- Child wearing {costume}
- {magical_elements}

FOOTER ZONE (Bottom 15%):
- {footer_description}
- Clean space suitable for text overlay

PHOTOGRAPHY STYLE:
- Shot on Canon EOS R5 with 85mm portrait lens
- Natural golden hour lighting
- Shallow depth of field (f/2.8)
- The child looks REAL and PHOTOGRAPHED, not illustrated
- Fantasy elements in background only, child remains photographic

ABSOLUTE RULES:
- NO text, letters, or watermarks
- Face must be photorealistic - like an actual photograph
- NO cartoon, anime, or illustrated style on the child
- Child's skin must have natural human texture

Professional portrait photograph of a child in fantasy scenery.
"""

# =============================================================================
# CINEMATIC PAINTING COVER TEMPLATE
# For cartoon3d/animated style - matches the interior page styling
# Inspired by: Pixar concept art posters, Spider-Verse, DreamWorks key art
# =============================================================================
CINEMATIC_COVER_PROMPT_TEMPLATE = """
A premium cinematic digital painting for a children's book cover.
High-end illustrated character portrait with hyper-detailed face rendering.

COMPOSITION (STRICT):

TOP ZONE (Upper 20%):
- {header_atmosphere}
- Empty space for typography - no characters or objects here
- Painted atmospheric effects (clouds, magic, light rays)

MAIN SUBJECT (Center 65%):
- A child hero named {name} in a dynamic, confident pose
- Position the child's face prominently in the center, fully visible
- CRITICAL FACE REQUIREMENTS:
  * Hyper-realistic skin texture with visible pores and natural imperfections
  * Subsurface scattering for warm, lifelike skin tones
  * Ultra-detailed eyes with iris depth, reflections, and life
  * NOT flat CG, NOT plastic doll, NOT airbrushed smooth
  * Natural child proportions (no chibi/anime distortion)
  * Rosy cheeks, natural skin color variations
- Child wearing {costume}
- {magical_elements}

FOOTER ZONE (Bottom 15%):
- {footer_description}
- Clean space suitable for text overlay

ARTISTIC STYLE:
- Premium cinematic digital painting (Pixar concept art quality)
- Dramatic rim lighting and key light separation
- Rich color grading with vibrant, saturated colors
- Volumetric light rays, atmospheric depth
- Painterly brush strokes in background and costume details
- Golden hour warmth or dramatic sunset gradients
- Bokeh and depth of field in environment

ABSOLUTE RULES:
- NO text, letters, or watermarks
- Face must have realistic skin texture - parents must recognize their child
- NO cheap CG look, NO mobile game art, NO generic 3D render
- Must look like a $500 commissioned artwork

Premium children's book cover illustration with cinematic lighting.
"""



@dataclass
class StoryTemplate:
    """Complete story template with all pages."""
    theme_id: str
    title_template: str       # "{name}'s Magical Adventure"
    description: str
    default_costume: str
    protagonist_description: str
    pages: List[PageTemplate]
    # Cover page settings
    cover_setting: Optional[str] = None  # Theme-specific cover setting description
    cover_costume: Optional[str] = None  # Special costume for cover (if different)
    cover_header_atmosphere: Optional[str] = None  # Top zone atmosphere
    cover_magical_elements: Optional[str] = None  # Magical elements around child
    cover_footer_description: Optional[str] = None  # Footer zone description

    def get_title(self, child_name: str) -> str:
        """Get formatted title for this story."""
        return self.title_template.format(name=child_name)
    
    def get_cover_prompt(self, child_name: str, style: str = "photorealistic") -> str:
        """
        Get formatted cover page prompt with zone-based composition.
        
        Args:
            child_name: Child's name for personalization
            style: Art style - 'photorealistic' (default) or 'cartoon3d'/'animated'
                   Uses different prompt templates for visual consistency
        
        Returns:
            Formatted cover prompt matching the selected art style
        """
        # Choose template based on style
        if style in ("cartoon3d", "animated", "cinematic_painting"):
            template = CINEMATIC_COVER_PROMPT_TEMPLATE
        else:
            template = COVER_PROMPT_TEMPLATE
        
        return template.format(
            name=child_name,
            header_atmosphere=self.cover_header_atmosphere or "Dark or softly glowing magical sky, forest canopy, or mist",
            costume=self.cover_costume or self.default_costume,
            magical_elements=self.cover_magical_elements or "Magical sparkles and particles surround the body, but NOT the face",
            footer_description=self.cover_footer_description or "Ground, forest floor, path, or subtle darker gradient"
        )

    def get_page_prompt(
        self,
        page_number: int,
        style: str,
        child_name: str,
        child_age: int,
        child_gender: str,
        enable_cinematic: bool = True
    ) -> dict:
        """Get formatted prompt for a specific page and style."""
        if page_number < 1 or page_number > len(self.pages):
            raise ValueError(f"Invalid page number: {page_number}")

        page = self.pages[page_number - 1]

        # Choose appropriate prompt based on style
        if style == "artistic" and page.artistic_prompt:
            base_prompt = page.artistic_prompt
            style_block = ARTISTIC_STYLE_BLOCK
        else:
            base_prompt = page.realistic_prompt
            style_block = REALISTIC_STYLE_BLOCK

        # Build protagonist description
        if style == "artistic":
            protagonist = f"a {child_age}-year-old {child_gender} child character, {self.protagonist_description}"
        else:
            protagonist = f"a {child_age}-year-old {child_gender} child with the exact face from the reference photo, {self.protagonist_description}"

        # Get costume for this page
        costume = page.costume or self.default_costume

        # Apply cinematic enhancements if enabled and using realistic style
        enhanced_style_block = style_block
        if enable_cinematic and page.scene_type and style != "artistic":
            enhanced_style_block = self._enhance_with_cinematics(
                style_block,
                page.scene_type,
                page.camera_style,
                page.lighting_style
            )

        # Replace placeholders
        final_prompt = base_prompt.format(
            protagonist=protagonist,
            costume=costume,
            age=child_age,
            gender=child_gender,
            realistic_style_block=enhanced_style_block,
            artistic_style_block=enhanced_style_block
        )

        # Add face composition requirements for artistic style (needed for face swap)
        if style == "artistic":
            face_requirements = FACE_COMPOSITION_REQUIREMENTS
            final_prompt = final_prompt.strip() + "\n\n" + face_requirements.strip()

        return {
            "prompt": final_prompt.strip(),
            "negative_prompt": NEGATIVE_PROMPT.strip()
        }

    def _enhance_with_cinematics(
        self,
        base_style: str,
        scene_type: str,
        camera_override: Optional[str] = None,
        lighting_override: Optional[str] = None
    ) -> str:
        """Enhance style block with cinematic modifiers based on scene type."""

        # Scene type to cinematic mapping
        scene_mappings = {
            "arrival": {"camera": "establishing", "lighting": "golden", "mood": "adventurous"},
            "test": {"camera": "dramatic", "lighting": "magical", "mood": "determined"},
            "revelation": {"camera": "establishing", "lighting": "epic", "mood": "adventurous"},
            "chaos": {"camera": "dynamic", "lighting": "dramatic", "mood": "adventurous"},
            "bonding": {"camera": "intimate", "lighting": "natural", "mood": "peaceful"},
            "action": {"camera": "dynamic", "lighting": "dramatic", "mood": "joyful"},
            "flight": {"camera": "heroic", "lighting": "epic", "mood": "joyful"},
            "mischief": {"camera": "dynamic", "lighting": "dramatic", "mood": "joyful"},
            "friendship": {"camera": "intimate", "lighting": "golden", "mood": "peaceful"},
            "peaceful": {"camera": "dramatic", "lighting": "magical", "mood": "peaceful"}
        }

        # Get cinematic elements for this scene
        scene_config = scene_mappings.get(scene_type, {"camera": "establishing", "lighting": "golden", "mood": "adventurous"})

        # Apply overrides if provided
        camera_type = camera_override or scene_config["camera"]
        lighting_type = lighting_override or scene_config["lighting"]
        mood_type = scene_config["mood"]

        # Build enhanced style block
        camera_modifier = CINEMATIC_MODIFIERS["camera_angles"].get(camera_type, "")
        lighting_modifier = CINEMATIC_MODIFIERS["lighting_styles"].get(lighting_type, "")
        mood_modifier = CINEMATIC_MODIFIERS["mood"].get(mood_type, "")
        composition_modifier = CINEMATIC_MODIFIERS["composition"]["rule_of_thirds"]  # Default composition

        # Combine all modifiers with base style
        enhanced_style = f"{base_style.strip()}\n\n{camera_modifier}, {lighting_modifier}, {composition_modifier}, {mood_modifier}"

        return enhanced_style.strip()

    def get_story_text(self, page_number: int, child_name: str) -> str:
        """Get formatted story text for a page."""
        if page_number < 1 or page_number > len(self.pages):
            raise ValueError(f"Invalid page number: {page_number}")

        page = self.pages[page_number - 1]
        return page.story_text.format(name=child_name)


@dataclass
class DialogueBubble:
    """Single speech bubble in a comic panel."""
    speaker: str  # Character name or "{name}" placeholder
    text: str
    position: str = "left"  # "left", "right", "bottom"


@dataclass
class ComicPanel:
    """Single comic panel with image prompt and dialogue."""
    image_prompt: str
    dialogue: List[DialogueBubble] = field(default_factory=list)
    characters_in_panel: List[str] = field(default_factory=list)


@dataclass
class ComicPageTemplate:
    """A comic book page with two side-by-side panels."""
    page_number: int
    narrative: str  # The story text displayed below panels
    left_panel: ComicPanel
    right_panel: ComicPanel
    costume: Optional[str] = None


# Enhanced cinematic style blocks for different scene types
CINEMATIC_MODIFIERS = {
    "camera_angles": {
        "heroic": "low angle shot, hero pose, empowering perspective",
        "intimate": "close-up portrait, emotional connection, shallow depth of field",
        "dynamic": "dutch angle, action shot, motion blur elements",
        "establishing": "wide shot, environmental storytelling, grand perspective",
        "dramatic": "high angle shot, dramatic shadows, theatrical lighting"
    },
    "lighting_styles": {
        "magical": "rim lighting, ethereal glow, mystical atmosphere, particle effects",
        "golden": "golden hour lighting, warm backlighting, lens flares, cinematic warmth",
        "dramatic": "chiaroscuro lighting, strong shadows, high contrast, mood lighting",
        "natural": "soft natural lighting, window light, gentle shadows",
        "epic": "dramatic sky lighting, storm lighting, epic scale atmosphere"
    },
    "composition": {
        "rule_of_thirds": "rule of thirds composition, balanced framing",
        "leading_lines": "leading lines composition, visual flow",
        "symmetrical": "symmetrical composition, centered framing",
        "dynamic": "dynamic diagonal composition, movement flow",
        "layered": "layered composition, foreground, midground, background"
    },
    "mood": {
        "adventurous": "sense of adventure, excitement, wonder in expression",
        "peaceful": "serene expression, calm atmosphere, tranquil mood",
        "determined": "focused determination, brave expression, strong pose",
        "joyful": "genuine happiness, bright smile, energetic pose",
        "mysterious": "mysterious atmosphere, curious expression, intrigue"
    }
}


# ===================
# FACE-ANCHOR PROMPTS FOR IDENTITY PRESERVATION
# ===================

# Face-anchor clause to append to ALL image generation prompts
# This ensures consistent facial identity across all story pages
FACE_ANCHOR_CLAUSE = """
[face-anchor] Preserve the facial identity from reference photo: maintain exact facial structure,
same eye shape and spacing, same nose shape, natural skin texture matching reference,
child-proportioned face with age-appropriate features, consistent expression style,
preserve subtle facial characteristics across all pose and lighting variations.
"""

# Storybook-optimized style block for NanoBanana generation
STORYBOOK_ILLUSTRATION_STYLE = """
Whimsical storybook illustration, watercolor art style with soft edges,
golden hour warm lighting, rich vibrant colors, ultra-fine brushwork details,
children's book aesthetic, magical dreamy atmosphere, professional illustration quality,
consistent character design throughout, expressive dynamic poses,
high detail 8K quality, soft shadows, enchanted fairy tale feel.
"""


# Enhanced style block for photorealistic prompts with cinematic elements
REALISTIC_STYLE_BLOCK = """
Ultra-realistic cinematic photography, professional DSLR quality with ARRI Alexa camera,
natural lighting with golden hour warmth, shallow depth of field f/1.4,
8K resolution, movie still aesthetic, National Geographic quality,
lifelike details and textures, photojournalistic style, magical atmosphere,
film grain texture, color grading, cinematic composition.
"""

# Style block for artistic comic book style
ARTISTIC_STYLE_BLOCK = """
Comic book illustration style, graphic novel art, professional comic book artist,
detailed line art with bold outlines, vibrant saturated colors, dynamic comic book lighting,
DC/Marvel comic style, superhero comic book aesthetic, digital comic book art,
speech bubbles and sound effects integrated naturally, comic book panel composition,
detailed fantasy illustration style, high quality comic book artwork.
"""

# Face composition requirements for face swap compatibility
# These ensure the generated image has a detectable face for the face swap API
FACE_COMPOSITION_REQUIREMENTS = """
[CRITICAL FACE REQUIREMENTS - MUST FOLLOW]
- The child character MUST be the PRIMARY SUBJECT in the foreground
- Child's FACE must be CLEARLY VISIBLE and FRONT-FACING (facing camera, 0-30 degree angle maximum)
- Face must occupy at least 15-20% of the total image area
- FULL FACE visible: both eyes, nose, and mouth clearly shown, no obstructions
- Face well-lit with even lighting, no harsh shadows hiding facial features
- NO profile views, NO back-of-head shots, NO obscured faces
- Child positioned prominently in frame, not small in background
- Portrait or upper-body composition preferred
- Face must have clear, defined features suitable for face detection
"""

# Negative prompt for all styles
NEGATIVE_PROMPT = """
blurry, low quality, distorted, deformed, ugly, bad anatomy, extra limbs,
extra fingers, mutated hands, poorly drawn face, mutation, watermark,
signature, cropped, out of frame, duplicate, multiple heads,
dark horror scary, gore violence, adult mature content, photorealistic when comic style,
face obscured, back of head, profile view only, face in shadow, tiny distant figure
"""
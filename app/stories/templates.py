"""
Story template structure and base classes.
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class PageTemplate:
    """Template for a single story page."""
    page_number: int
    scene_description: str
    realistic_prompt: str     # For Flux PuLID (photorealistic only)
    story_text: str           # Text with {name} placeholder
    costume: Optional[str] = None
    scene_type: Optional[str] = None  # For cinematic enhancement: "heroic", "intimate", "action", etc.
    camera_style: Optional[str] = None  # Override camera angle if needed
    lighting_style: Optional[str] = None  # Override lighting if needed


@dataclass
class StoryTemplate:
    """Complete story template with all pages."""
    theme_id: str
    title_template: str       # "{name}'s Magical Adventure"
    description: str
    default_costume: str
    protagonist_description: str
    pages: List[PageTemplate]

    def get_title(self, child_name: str) -> str:
        """Get formatted title for this story."""
        return self.title_template.format(name=child_name)

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

        # Get base prompt (photorealistic only)
        base_prompt = page.realistic_prompt

        # Build protagonist description
        protagonist = f"a {child_age}-year-old {child_gender} child with the exact face from the reference photo, {self.protagonist_description}"

        # Get costume for this page
        costume = page.costume or self.default_costume

        # Apply cinematic enhancements if enabled
        enhanced_style_block = REALISTIC_STYLE_BLOCK
        if enable_cinematic and page.scene_type:
            enhanced_style_block = self._enhance_with_cinematics(
                REALISTIC_STYLE_BLOCK,
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
            realistic_style_block=enhanced_style_block
        )

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

# Enhanced style block for photorealistic prompts with cinematic elements
REALISTIC_STYLE_BLOCK = """
Ultra-realistic cinematic photography, professional DSLR quality with ARRI Alexa camera,
natural lighting with golden hour warmth, shallow depth of field f/1.4,
8K resolution, movie still aesthetic, National Geographic quality,
lifelike details and textures, photojournalistic style, magical atmosphere,
film grain texture, color grading, cinematic composition.
"""

# Negative prompt for photorealistic style
NEGATIVE_PROMPT = """
blurry, low quality, distorted, deformed, ugly, bad anatomy, extra limbs,
extra fingers, mutated hands, poorly drawn face, mutation, watermark,
text overlay, signature, cropped, out of frame, duplicate, multiple heads,
anime style, manga style, chibi, dark horror scary, gore violence,
adult mature content
"""
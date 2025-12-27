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
    artistic_prompt: str      # For Flux.1 [dev] + Face Swap
    realistic_prompt: str     # For Flux PuLID
    story_text: str           # Text with {name} placeholder
    costume: Optional[str] = None


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
        child_gender: str
    ) -> dict:
        """Get formatted prompt for a specific page and style."""
        if page_number < 1 or page_number > len(self.pages):
            raise ValueError(f"Invalid page number: {page_number}")

        page = self.pages[page_number - 1]

        # Get base prompt for style
        if style == "artistic":
            base_prompt = page.artistic_prompt
        else:
            base_prompt = page.realistic_prompt

        # Build protagonist description
        protagonist = f"a {child_age}-year-old {child_gender} child with the exact face from the reference photo, {self.protagonist_description}"

        # Get costume for this page
        costume = page.costume or self.default_costume

        # Replace placeholders
        final_prompt = base_prompt.format(
            protagonist=protagonist,
            costume=costume,
            age=child_age,
            gender=child_gender,
            artistic_style_block=ARTISTIC_STYLE_BLOCK if style == "artistic" else "",
            realistic_style_block=REALISTIC_STYLE_BLOCK if style == "photorealistic" else ""
        )

        return {
            "prompt": final_prompt.strip(),
            "negative_prompt": NEGATIVE_PROMPT.strip()
        }

    def get_story_text(self, page_number: int, child_name: str) -> str:
        """Get formatted story text for a page."""
        if page_number < 1 or page_number > len(self.pages):
            raise ValueError(f"Invalid page number: {page_number}")

        page = self.pages[page_number - 1]
        return page.story_text.format(name=child_name)


# Style blocks to append to prompts
ARTISTIC_STYLE_BLOCK = """
Professional children's comic book illustration style, bold black ink outlines 2px thickness,
cel-shaded flat coloring with subtle gradients, vibrant saturated colors
(primary palette: royal purple, gold, forest green, sky blue),
Marvel-meets-Pixar aesthetic, dramatic lighting with rim lights on characters,
whimsical and enchanting atmosphere, storybook quality, warm inviting mood.
"""

REALISTIC_STYLE_BLOCK = """
Ultra-realistic cinematic photography, professional DSLR quality with Canon EOS R5,
natural lighting with golden hour warmth, shallow depth of field f/2.8,
8K resolution, movie still aesthetic, National Geographic quality,
lifelike details and textures, photojournalistic style, magical atmosphere.
"""

# Negative prompt for both styles
NEGATIVE_PROMPT = """
blurry, low quality, distorted, deformed, ugly, bad anatomy, extra limbs,
extra fingers, mutated hands, poorly drawn face, mutation, watermark,
text overlay, signature, cropped, out of frame, duplicate, multiple heads,
anime style, manga style, chibi, dark horror scary, gore violence,
adult mature content, realistic photo (for artistic only)
"""
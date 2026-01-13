"""
Page Composition Service - Shared logic for creating complete book page layouts.

This service contains the sophisticated page layout logic extracted from the PDF generator,
making it reusable for both preview generation and final PDF creation.
"""

import re
from typing import Dict, List, Optional, Any
import structlog

logger = structlog.get_logger()


class PageCompositionService:
    """Service for composing complete book pages with layout, typography, and formatting."""

    def __init__(self):
        """Initialize the page composition service."""
        self.logger = logger

    def compose_page(
        self,
        page_number: int,
        image_url: str,
        story_text: str,
        story_template: Optional[Any] = None,
        is_preview: bool = False,
        add_watermark: bool = False
    ) -> Dict[str, Any]:
        """
        Compose a complete page with layout, typography, and formatting.

        Args:
            page_number: The page number (1-based)
            image_url: URL to the page image
            story_text: Raw story text for the page
            story_template: Story template object (for scene type detection)
            is_preview: Whether this is for preview (affects quality/layout)
            add_watermark: Whether to add watermark overlay

        Returns:
            Dict containing complete page data with layout information
        """
        try:
            # Detect optimal layout based on content and scene
            layout_class = self._detect_page_layout(page_number, story_template, story_text)

            # Parse text into structured components
            parsed_text = self._parse_story_text(story_text, page_number, story_template)

            # Get scene type for additional context
            scene_type = self._get_scene_type(page_number, story_template)

            # Generate layout-specific HTML
            page_html = self._generate_page_html(
                layout_class=layout_class,
                image_url=image_url,
                parsed_text=parsed_text,
                page_number=page_number,
                is_preview=is_preview,
                add_watermark=add_watermark
            )

            return {
                "page_number": page_number,
                "layout_class": layout_class,
                "scene_type": scene_type,
                "image_url": image_url,
                "parsed_text": parsed_text,
                "story_text": story_text,
                "page_html": page_html,
                "is_preview": is_preview,
                "has_watermark": add_watermark
            }

        except Exception as e:
            self.logger.error(f"Failed to compose page {page_number}", error=str(e))
            # Return basic fallback
            return {
                "page_number": page_number,
                "layout_class": "layout-hero",
                "scene_type": "unknown",
                "image_url": image_url,
                "parsed_text": {"combined": story_text, "dialogue": "", "narrative": story_text, "thoughts": ""},
                "story_text": story_text,
                "page_html": self._generate_fallback_html(image_url, story_text, page_number, add_watermark),
                "is_preview": is_preview,
                "has_watermark": add_watermark
            }

    def _analyze_content_complexity(self, story_text: str) -> Dict[str, bool]:
        """
        Analyze story text to understand content patterns.

        Returns complexity metrics used for layout selection.
        """
        # Count dialogue (text in quotes)
        dialogue_count = len(re.findall(r'"[^"]*"', story_text))

        # Count action words (verbs indicating movement/action)
        action_words = ['ran', 'jumped', 'flew', 'dashed', 'crashed', 'swooped', 'leaped',
                       'tumbled', 'soared', 'zoomed', 'burst', 'exploded', 'charged']
        action_word_count = sum(1 for word in action_words if word.lower() in story_text.lower())

        # Count sentences
        sentence_count = len([s for s in story_text.split('.') if s.strip()])

        # Count characters mentioned (capitalized names)
        character_count = len(set(re.findall(r'\b[A-Z][a-z]+\b', story_text)))

        return {
            'is_dialogue_heavy': dialogue_count >= 2,
            'is_action_heavy': action_word_count >= 2,
            'is_complex': sentence_count >= 4,
            'is_conversation': character_count >= 2
        }

    def _detect_page_layout(self, page_number: int, story_template: Optional[Any] = None, story_text: str = "") -> str:
        """Enhanced layout detection based on scene type and content analysis."""

        # Analyze content complexity
        content_analysis = self._analyze_content_complexity(story_text)

        # Get base scene type
        base_scene = "unknown"
        if story_template and hasattr(story_template, 'pages'):
            try:
                page_template = story_template.pages[page_number - 1]
                base_scene = getattr(page_template, 'scene_type', 'unknown')
            except (IndexError, AttributeError):
                pass

        # Advanced layout selection based on content + scene

        # For dialogue-heavy content, prefer intimate or action layouts
        if content_analysis['is_dialogue_heavy'] or content_analysis['is_conversation']:
            if base_scene in ["bonding", "friendship", "peaceful"]:
                return "layout-intimate"
            elif base_scene in ["test", "chaos", "action", "mischief"]:
                return "layout-action"
            else:
                return "layout-intimate"  # Default for dialogue

        # For action-heavy content, prefer action or sequence layouts
        elif content_analysis['is_action_heavy']:
            if content_analysis['is_complex']:
                return "layout-sequence"  # Complex action needs multiple panels
            else:
                return "layout-action"

        # For complex content (multiple sentences), use sequence layout
        elif content_analysis['is_complex'] and base_scene == "mischief":
            return "layout-sequence"

        # Default scene-based mapping (enhanced)
        scene_mapping = {
            "arrival": "layout-hero",
            "test": "layout-action",
            "revelation": "layout-hero",
            "chaos": "layout-sequence" if content_analysis['is_complex'] else "layout-action",
            "bonding": "layout-intimate",
            "action": "layout-action",
            "flight": "layout-hero",
            "mischief": "layout-sequence",
            "friendship": "layout-intimate",
            "peaceful": "layout-intimate"
        }

        return scene_mapping.get(base_scene, "layout-hero")

    def _parse_story_text(self, story_text: str, page_number: int, story_template: Optional[Any] = None) -> Dict[str, str]:
        """
        Parse story text to identify dialogue, narrative, and special elements.

        Returns a dict with parsed text components for typography formatting.
        """
        # Detect dialogue patterns (quotes or character speech)
        dialogue_pattern = r'"([^"]*)"'
        dialogue_matches = re.findall(dialogue_pattern, story_text)

        # Detect character actions/thoughts (italicized or in parentheses)
        thought_pattern = r'\(([^)]*)\)'
        thought_matches = re.findall(thought_pattern, story_text)

        # Detect narrator voice vs dialogue
        sentences = story_text.split('.')

        dialogue_text = ""
        narrative_text = ""
        thought_text = ""

        for match in dialogue_matches:
            dialogue_text += f'<div class="speech-bubble">{match.strip()}</div>\n'

        for match in thought_matches:
            thought_text += f'<div class="thought-bubble">{match.strip()}</div>\n'

        # Remove quoted dialogue and thoughts from narrative
        clean_narrative = story_text
        for match in dialogue_matches:
            clean_narrative = clean_narrative.replace(f'"{match}"', '')
        for match in thought_matches:
            clean_narrative = clean_narrative.replace(f'({match})', '')

        # Clean up the narrative text
        clean_narrative = re.sub(r'\s+', ' ', clean_narrative).strip()
        if clean_narrative:
            narrative_text = f'<div class="narrative-text">{clean_narrative}</div>'

        # Detect scene-specific text elements
        scene_type = self._get_scene_type(page_number, story_template)

        # Special formatting for action scenes
        if scene_type in ["chaos", "action", "test"] and "!" in story_text:
            # Extract exclamatory phrases as sound effects
            exclamations = re.findall(r'([A-Z]+!)', story_text)
            for exclamation in exclamations[:1]:  # Take first one
                narrative_text = narrative_text.replace(exclamation, f'<div class="sound-effect">{exclamation}</div>')

        return {
            "dialogue": dialogue_text,
            "narrative": narrative_text,
            "thoughts": thought_text,
            "combined": dialogue_text + thought_text + narrative_text if dialogue_text or thought_text else narrative_text
        }

    def _get_scene_type(self, page_number: int, story_template: Optional[Any] = None) -> str:
        """Get scene type for a specific page."""
        if not story_template or not hasattr(story_template, 'pages'):
            return "unknown"

        try:
            page_template = story_template.pages[page_number - 1]
            return getattr(page_template, 'scene_type', 'unknown')
        except (IndexError, AttributeError):
            return "unknown"

    def _generate_page_html(
        self,
        layout_class: str,
        image_url: str,
        parsed_text: Dict[str, str],
        page_number: int,
        is_preview: bool = False,
        add_watermark: bool = False
    ) -> str:
        """Generate complete HTML for a page with the specified layout."""

        # Base CSS classes for preview vs final
        page_classes = f"{layout_class} {'preview-page' if is_preview else 'final-page'}"
        if add_watermark:
            page_classes += " watermarked"

        # Watermark overlay
        watermark_html = ""
        if add_watermark:
            watermark_html = '''
            <div class="watermark-overlay">
                <div class="watermark-text">PREVIEW - zelavokids.com</div>
            </div>
            '''

        # Layout-specific HTML structure
        if layout_class == "layout-hero":
            html = f'''
            <div class="page-container {page_classes}" data-page="{page_number}">
                <div class="hero-image">
                    <img src="{image_url}" alt="Page {page_number} illustration" />
                </div>
                <div class="hero-text">
                    {parsed_text.get("combined", "")}
                </div>
                {watermark_html}
            </div>
            '''
        elif layout_class == "layout-intimate":
            html = f'''
            <div class="page-container {page_classes}" data-page="{page_number}">
                <div class="intimate-layout">
                    <div class="character-portrait">
                        <img src="{image_url}" alt="Page {page_number} illustration" />
                    </div>
                    <div class="dialogue-area">
                        {parsed_text.get("dialogue", "")}
                        {parsed_text.get("thoughts", "")}
                        {parsed_text.get("narrative", "")}
                    </div>
                </div>
                {watermark_html}
            </div>
            '''
        elif layout_class == "layout-action":
            html = f'''
            <div class="page-container {page_classes}" data-page="{page_number}">
                <div class="action-layout">
                    <div class="main-panel">
                        <img src="{image_url}" alt="Page {page_number} illustration" />
                    </div>
                    <div class="text-panel">
                        {parsed_text.get("combined", "")}
                    </div>
                </div>
                {watermark_html}
            </div>
            '''
        elif layout_class == "layout-sequence":
            html = f'''
            <div class="page-container {page_classes}" data-page="{page_number}">
                <div class="sequence-layout">
                    <div class="main-sequence">
                        <img src="{image_url}" alt="Page {page_number} illustration" />
                    </div>
                    <div class="sequence-text">
                        {parsed_text.get("combined", "")}
                    </div>
                </div>
                {watermark_html}
            </div>
            '''
        else:
            # Fallback to hero layout
            html = f'''
            <div class="page-container {page_classes}" data-page="{page_number}">
                <div class="hero-image">
                    <img src="{image_url}" alt="Page {page_number} illustration" />
                </div>
                <div class="hero-text">
                    {parsed_text.get("combined", "")}
                </div>
                {watermark_html}
            </div>
            '''

        return html

    def _generate_fallback_html(self, image_url: str, story_text: str, page_number: int, add_watermark: bool = False) -> str:
        """Generate simple fallback HTML when composition fails."""
        watermark_html = ""
        if add_watermark:
            watermark_html = '''
            <div class="watermark-overlay">
                <div class="watermark-text">PREVIEW - zelavokids.com</div>
            </div>
            '''

        return f'''
        <div class="page-container layout-hero fallback" data-page="{page_number}">
            <div class="hero-image">
                <img src="{image_url}" alt="Page {page_number} illustration" />
            </div>
            <div class="hero-text">
                <div class="narrative-text">{story_text}</div>
            </div>
            {watermark_html}
        </div>
        '''
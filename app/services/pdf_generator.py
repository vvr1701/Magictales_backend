"""
PDF Generator Service using WeasyPrint.
Creates premium comic book style PDFs from story pages.
"""

import asyncio
import httpx
import os
import re
from io import BytesIO
from typing import List, Dict, Optional, Tuple
import structlog
from jinja2 import Template

from app.config import get_settings
from app.core.exceptions import StorageError

logger = structlog.get_logger()


class PDFGeneratorService:
    """Service for generating print-ready storybook PDFs."""

    def __init__(self):
        self.settings = get_settings()

    async def generate_storybook_pdf(
        self,
        pages: List[Dict],  # List of page data with image_url, story_text, page_number
        title: str,
        child_name: str,
        theme: str,
        story_template: Optional[object] = None  # StoryTemplate object with scene types
    ) -> bytes:
        """
        Generate complete premium storybook PDF with comic book layouts.

        Args:
            pages: List of page dictionaries with image_url, story_text, page_number
            title: Story title (e.g., "Arjun's First Day of Magic")
            child_name: Child's name
            theme: Theme ID (e.g., "magic_castle")
            story_template: StoryTemplate object containing scene types for layout detection

        Returns:
            PDF bytes with premium comic book styling
        """
        try:
            logger.info("Generating PDF", title=title, page_count=len(pages))

            # Download all images first
            image_data = {}
            for page in pages:
                logger.info(f"Downloading image for page {page['page_number']}")
                image_bytes = await self._download_image(page['image_url'])
                image_data[page['page_number']] = image_bytes

            # Generate HTML content with premium comic book styling
            # Uses advanced CSS layouts, speech bubbles, typography, and sound effects
            html_content = self._generate_premium_html(pages, image_data, title, child_name, theme, story_template)

            # Convert HTML to PDF using WeasyPrint
            pdf_bytes = await self._html_to_pdf(html_content)

            logger.info("PDF generated successfully", title=title, size_bytes=len(pdf_bytes))
            return pdf_bytes

        except Exception as e:
            logger.error("Failed to generate PDF", title=title, error=str(e))
            raise StorageError(f"PDF generation failed: {str(e)}")

    async def _download_image(self, url: str) -> bytes:
        """Download image from URL."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except httpx.HTTPError as e:
            raise StorageError(f"Failed to download image: {str(e)}")

    def _load_comic_book_css(self) -> str:
        """Load the comic book CSS framework."""
        try:
            css_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'css', 'comic-book-layouts.css')
            with open(css_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not load comic book CSS: {e}")
            # Fallback to basic styling
            return ""

    def _analyze_content_complexity(self, story_text: str) -> Dict[str, any]:
        """Analyze story text to determine content complexity and characteristics."""
        # Count different text elements
        dialogue_count = len(re.findall(r'"([^"]*)"', story_text))
        sentence_count = len([s for s in story_text.split('.') if s.strip()])
        exclamation_count = story_text.count('!')
        question_count = story_text.count('?')
        word_count = len(story_text.split())

        # Detect multiple characters (names in dialogue attribution)
        character_indicators = re.findall(r'(\w+)\s+(?:said|shouted|whispered|declared|asked)', story_text, re.IGNORECASE)
        character_count = len(set(character_indicators))

        # Detect action intensity
        action_words = ['ran', 'jumped', 'flew', 'crashed', 'exploded', 'soared', 'rushed', 'burst']
        action_intensity = sum(1 for word in action_words if word.lower() in story_text.lower())

        return {
            'dialogue_count': dialogue_count,
            'sentence_count': sentence_count,
            'exclamation_count': exclamation_count,
            'question_count': question_count,
            'word_count': word_count,
            'character_count': character_count,
            'action_intensity': action_intensity,
            'is_dialogue_heavy': dialogue_count >= 2,
            'is_action_heavy': action_intensity >= 2 or exclamation_count >= 2,
            'is_complex': sentence_count >= 4,
            'is_conversation': character_count >= 2
        }

    def _detect_page_layout(self, page_number: int, story_template: Optional[object] = None, story_text: str = "") -> str:
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

    def _generate_premium_html(
        self,
        pages: List[Dict],
        image_data: Dict[int, bytes],
        title: str,
        child_name: str,
        theme: str,
        story_template: Optional[object] = None
    ) -> str:
        """Generate premium HTML content with comic book layouts."""

        # Load comic book CSS framework
        comic_css = self._load_comic_book_css()

        # Generate premium cover and back cover designs
        cover_design = self._generate_premium_cover_design(title, child_name, theme, story_template)
        back_cover_design = self._generate_premium_back_cover(title, child_name, theme, story_template)

        # Premium HTML template
        html_template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <style>
        {{ comic_book_css }}

        /* Additional PDF-specific optimizations */
        .story-page {
            page-break-before: always;
            position: relative;
            height: 100vh;
            overflow: hidden;
        }

        .page-image {
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }

        /* Ensure proper image embedding */
        .embedded-image {
            background-image: url("data:image/jpeg;base64,{{ '{{' }} page.image_base64 {{ '}}' }}");
        }

        /* PDF print optimizations */
        @media print {
            .story-page {
                page-break-inside: avoid;
                height: 100vh;
            }
        }
    </style>
</head>
<body>
    <!-- Premium Cover Page -->
    <div class="{{ cover_design.cover_class }}" style="{{ cover_design.background_style }}">
        <div class="cover-title {{ cover_design.title_effect_class }}">{{ title }}</div>
        <div class="cover-subtitle">{{ cover_design.personalized_subtitle }}</div>
        <div class="cover-author">Starring {{ child_name }}</div>
        <div class="decorative-elements {{ cover_design.special_effects_class }}">
            {{ cover_design.decorative_elements }}
        </div>
    </div>

    <!-- Story Pages with Dynamic Layouts -->
    {% for page in pages %}
    <div class="story-page {{ page.layout_class }}">
        {% if page.layout_class == "layout-hero" %}
            <div class="hero-image page-image" style="background-image: url('data:image/jpeg;base64,{{ page.image_base64 }}');"></div>
            <div class="hero-text">
                {% if page.parsed_dialogue %}
                    {{ page.parsed_dialogue | safe }}
                {% endif %}
                {% if page.parsed_thoughts %}
                    {{ page.parsed_thoughts | safe }}
                {% endif %}
                {{ page.parsed_narrative | safe }}
            </div>
        {% elif page.layout_class == "layout-action" %}
            <div class="main-panel page-image" style="background-image: url('data:image/jpeg;base64,{{ page.image_base64 }}');"></div>
            <div class="text-panel">
                {% if page.parsed_dialogue %}
                    {{ page.parsed_dialogue | safe }}
                {% else %}
                    <div class="dialogue-text">{{ page.parsed_narrative | safe }}</div>
                {% endif %}
            </div>
            <div class="sound-panel">
                <div class="sound-effect">{{ page.sound_effect | default("WHOOSH!") }}</div>
            </div>
        {% elif page.layout_class == "layout-intimate" %}
            <div class="character-panel page-image" style="background-image: url('data:image/jpeg;base64,{{ page.image_base64 }}');"></div>
            <div class="dialogue-panel">
                {% if page.parsed_dialogue %}
                    {{ page.parsed_dialogue | safe }}
                {% elif page.parsed_thoughts %}
                    {{ page.parsed_thoughts | safe }}
                {% else %}
                    <div class="speech-bubble">{{ page.parsed_narrative | safe }}</div>
                {% endif %}
            </div>
        {% elif page.layout_class == "layout-sequence" %}
            <div class="panel-1 page-image" style="background-image: url('data:image/jpeg;base64,{{ page.image_base64 }}');"></div>
            <div class="panel-2">
                {% if page.enhanced_text is mapping %}
                    {{ page.enhanced_text.panel1 | safe }}
                {% else %}
                    {{ page.parsed_narrative | safe }}
                {% endif %}
            </div>
            <div class="panel-3">
                {% if page.enhanced_text is mapping %}
                    {{ page.enhanced_text.panel2 | safe }}
                {% else %}
                    <div class="sound-effect clang">{{ page.sound_effect | default("CLANG!") }}</div>
                {% endif %}
            </div>
            <div class="panel-4">
                {% if page.enhanced_text is mapping %}
                    {{ page.enhanced_text.panel3 | safe }}
                {% else %}
                    <div class="caption-text">Page {{ page.page_number }}</div>
                {% endif %}
            </div>
        {% else %}
            <!-- Fallback layout with enhanced typography -->
            <div class="hero-image page-image" style="background-image: url('data:image/jpeg;base64,{{ page.image_base64 }}');"></div>
            <div class="hero-text">
                {% if page.enhanced_text %}
                    {{ page.enhanced_text | safe }}
                {% else %}
                    <div class="narrative-text">{{ page.story_text }}</div>
                {% endif %}
            </div>
        {% endif %}

        <div class="page-number">{{ page.page_number }}</div>
    </div>
    {% endfor %}

    <!-- Premium Back Cover -->
    <div class="back-cover-premium {{ cover_design.cover_class }}">
        <div class="credits-section">
            {{ back_cover_design.credits_content | safe }}
        </div>
    </div>
</body>
</html>
        """)

        # Prepare pages with base64 images, layout detection, and enhanced typography
        pages_with_layouts = []
        for page in pages:
            import base64
            image_base64 = base64.b64encode(image_data[page['page_number']]).decode('utf-8')

            # Detect appropriate layout based on scene type and content analysis
            layout_class = self._detect_page_layout(page['page_number'], story_template, page['story_text'])

            # Generate dynamic sound effect based on content and scene
            sound_effect = self._generate_sound_effect(page['page_number'], story_template, page['story_text'])

            # Parse and enhance story text with typography and visual effects
            scene_type = self._get_scene_type(page['page_number'], story_template)
            content_analysis = self._analyze_content_complexity(page['story_text'])
            parsed_text = self._parse_story_text(page['story_text'], page['page_number'], story_template)
            enhanced_text = self._apply_typography_enhancement(page['story_text'], layout_class, scene_type, content_analysis)

            # Add dynamic text effects and visual elements
            dynamic_text = self._create_dynamic_text_effects(page['story_text'], scene_type, layout_class)
            visual_elements = self._add_contextual_visual_elements(page['story_text'], scene_type)

            pages_with_layouts.append({
                'page_number': page['page_number'],
                'story_text': page['story_text'],  # Original text
                'enhanced_text': enhanced_text,    # Typography enhanced
                'dynamic_text': dynamic_text,      # Dynamic text effects
                'parsed_dialogue': parsed_text['dialogue'],
                'parsed_narrative': parsed_text['narrative'],
                'parsed_thoughts': parsed_text['thoughts'],
                'image_base64': image_base64,
                'layout_class': layout_class,
                'sound_effect': sound_effect,
                'scene_type': scene_type,
                'visual_effects': visual_elements,
                'content_analysis': content_analysis
            })

        # Theme display names
        theme_names = {
            'magic_castle': 'Magic Castle',
            'space_adventure': 'Space Adventure',
            'underwater': 'Underwater Kingdom',
            'forest_friends': 'Forest Friends'
        }

        return html_template.render(
            title=title,
            child_name=child_name,
            theme_display=theme_names.get(theme, theme.title()),
            pages=pages_with_layouts,
            comic_book_css=comic_css,
            cover_design=cover_design,
            back_cover_design=back_cover_design
        )

    def _analyze_story_context_for_sounds(self, story_text: str, scene_type: str) -> List[str]:
        """Analyze story text to extract contextual sound effects."""

        # Detect specific actions and objects that make sounds
        sound_triggers = {
            # Magic sounds
            'spell|magic|wand|staff': ['✨ SPARKLE ✨', 'SHIMMER!', 'TWINKLE!', '⭐ MAGIC! ⭐'],
            'gate|door|lock': ['CLANG!', 'CREAK...', 'SLAM!', 'CLICK!'],

            # Movement sounds
            'fly|flying|soar|float': ['SWOOSH!', 'WHOOSH!', 'ZOOM!', '💨 WHIZZ! 💨'],
            'run|rush|burst|dash': ['THUD! THUD!', 'PATTER!', 'ZOOM!', 'DASH!'],

            # Animal sounds
            'dragon|beast': ['ROAR!', 'GROWL!', 'SNORT!', '🔥 FLAME! 🔥'],
            'cat|purr': ['PURR...', 'MEOW!', 'MROW...', '🐱'],
            'owl|hoot': ['HOOT! HOOT!', 'WHO-OOO!', '🦉'],

            # Emotional sounds
            'laugh|giggle|happy': ['HA HA!', 'GIGGLE!', 'HEHE!', '😄'],
            'gasp|surprise|shock': ['GASP!', 'OH!', 'WOW!', '😱'],
            'whisper|quiet': ['shh...', 'psst...', 'whisper...'],

            # Action sounds
            'crash|break|explode': ['CRASH!', 'BANG!', 'BOOM!', 'SMASH!'],
            'open|reveal': ['CREAK!', 'WHOMP!', 'TA-DA!', '✨'],

            # Magic school specific
            'book|library|page': ['FLIP!', 'RUSTLE!', 'THUMP!', '📚'],
            'broom|broomstick': ['SWOOSH!', 'WHIZZ!', '🧹'],
            'test|spell|cast': ['ZAP!', 'FIZZ!', 'POP!', '⚡'],
        }

        detected_sounds = []
        story_lower = story_text.lower()

        for trigger_pattern, sound_options in sound_triggers.items():
            if any(word in story_lower for word in trigger_pattern.split('|')):
                # Select appropriate sound based on scene type intensity
                if scene_type in ['chaos', 'action', 'test']:
                    # High energy scenes get dramatic sounds
                    detected_sounds.append(sound_options[0])  # Most dramatic option
                elif scene_type in ['bonding', 'friendship', 'peaceful']:
                    # Gentle scenes get softer sounds
                    detected_sounds.append(sound_options[-1])  # Gentler option
                else:
                    # Default scenes get varied sounds
                    import random
                    detected_sounds.append(random.choice(sound_options))

                break  # Only take first match to avoid cluttering

        return detected_sounds

    def _generate_dynamic_sound_effect(self, page_number: int, story_text: str, scene_type: str, story_template: Optional[object] = None) -> str:
        """Generate dynamic sound effects based on story content and context."""

        # First try to detect contextual sounds from story text
        contextual_sounds = self._analyze_story_context_for_sounds(story_text, scene_type)

        if contextual_sounds:
            return contextual_sounds[0]

        # Fallback to scene-based mapping with variations
        scene_sound_variations = {
            "arrival": ["WHOOSH!", "✨ ARRIVE! ✨", "STEP... STEP...", "🚪"],
            "test": ["ZAP!", "⚡ MAGIC! ⚡", "FIZZ!", "SPARK!"],
            "revelation": ["GASP!", "😮 WOW! 😮", "OOOOH!", "✨"],
            "chaos": ["CRASH!", "BANG!", "💥 BOOM! 💥", "SMASH!"],
            "bonding": ["PURR...", "🥰", "♥", "aww..."],
            "action": ["ZOOM!", "DASH!", "💨 SPEED! 💨", "WHIZZ!"],
            "flight": ["SWOOSH!", "🧹 FLY! 🧹", "SOAR!", "WHOOSH!"],
            "mischief": ["BANG!", "OOPS!", "😈 MISCHIEF! 😈", "hehe..."],
            "friendship": ["♪♫", "💕", "YAY!", "🌟"],
            "peaceful": ["...", "💤", "ahhh...", "🌙"]
        }

        import random
        variations = scene_sound_variations.get(scene_type, ["WHOOSH!", "✨", "...", "🌟"])
        return random.choice(variations)

    def _generate_sound_effect(self, page_number: int, story_template: Optional[object] = None, story_text: str = "") -> str:
        """Generate appropriate sound effect for a page (legacy method - use _generate_dynamic_sound_effect)."""
        scene_type = self._get_scene_type(page_number, story_template)

        if story_text:
            return self._generate_dynamic_sound_effect(page_number, story_text, scene_type, story_template)

        # Original simple mapping as fallback
        sound_mapping = {
            "arrival": "WHOOSH!",
            "test": "ZAP!",
            "revelation": "GASP!",
            "chaos": "CRASH!",
            "bonding": "PURR...",
            "action": "ZOOM!",
            "flight": "SWOOSH!",
            "mischief": "BANG!",
            "friendship": "♪♫",
            "peaceful": "..."
        }

        return sound_mapping.get(scene_type, "WHOOSH!")

    def _create_dynamic_text_effects(self, text: str, scene_type: str, layout_class: str) -> str:
        """Create dynamic visual text effects for enhanced comic book experience."""

        # Detect emphasis words and add special styling
        emphasis_patterns = {
            # Magic words get sparkly effects
            r'\b(magic|magical|spell|enchant)\b': r'<span class="text-sparkle">\1</span>',
            r'\b(ALOHOMORA|ZAP|MAGICAL)\b': r'<span class="sound-effect magic">\1</span>',

            # Character names get special highlighting
            r'\b(Professor|Midnight|Sparky)\b': r'<span class="character-name">\1</span>',

            # Emotional words get enhanced styling
            r'\b(wonderful|amazing|incredible|magical|beautiful)\b': r'<span class="text-glow">\1</span>',
            r'\b(scary|frightening|dangerous|terrible)\b': r'<span class="text-dramatic">\1</span>',

            # Action words get dynamic effects
            r'\b(CRASH|BANG|BOOM|SMASH|EXPLODED|BURST)\b': r'<span class="sound-effect boom">\1</span>',
            r'\b(flew|soared|zoomed|dashed|rushed)\b': r'<span class="text-speed">\1</span>',
        }

        enhanced_text = text
        for pattern, replacement in emphasis_patterns.items():
            enhanced_text = re.sub(pattern, replacement, enhanced_text, flags=re.IGNORECASE)

        # Add scene-specific enhancements
        if scene_type in ['action', 'chaos', 'test']:
            # Add motion effects for action scenes
            enhanced_text = re.sub(r'!', '<span class="exclamation-burst">!</span>', enhanced_text)

        elif scene_type in ['bonding', 'friendship', 'peaceful']:
            # Add gentle effects for calm scenes
            enhanced_text = re.sub(r'\.\.\.', '<span class="text-gentle">...</span>', enhanced_text)

        elif scene_type == 'flight':
            # Add flowing effects for flight scenes
            enhanced_text = re.sub(r'\b(up|high|sky|clouds|flew|flying)\b', r'<span class="text-float">\1</span>', enhanced_text, flags=re.IGNORECASE)

        return enhanced_text

    def _add_contextual_visual_elements(self, story_text: str, scene_type: str) -> Dict[str, str]:
        """Add contextual visual elements like emojis and special effects based on story content."""

        visual_elements = {
            'background_effect': '',
            'decorative_elements': '',
            'mood_indicator': ''
        }

        # Detect story elements and add appropriate visuals
        story_lower = story_text.lower()

        # Magic effects
        if any(word in story_lower for word in ['magic', 'spell', 'wand', 'magical']):
            visual_elements['decorative_elements'] = '✨ ⭐ 🌟 ✨'
            visual_elements['background_effect'] = 'magical-sparkle'

        # Animal presence
        if 'dragon' in story_lower or 'sparky' in story_lower:
            visual_elements['decorative_elements'] += ' 🐲 🔥'
        if 'cat' in story_lower or 'midnight' in story_lower:
            visual_elements['decorative_elements'] += ' 🐱 💤'
        if 'owl' in story_lower or 'professor hoot' in story_lower:
            visual_elements['decorative_elements'] += ' 🦉 📚'

        # Flight/movement
        if any(word in story_lower for word in ['flew', 'flying', 'soar', 'broom']):
            visual_elements['decorative_elements'] += ' 🧹 💨 ☁️'
            visual_elements['background_effect'] = 'flight-trail'

        # Emotional context
        if scene_type in ['bonding', 'friendship', 'peaceful']:
            visual_elements['mood_indicator'] = '💕 🌙 ⭐'
        elif scene_type in ['action', 'chaos', 'test']:
            visual_elements['mood_indicator'] = '⚡ 💥 🔥'
        elif scene_type == 'arrival':
            visual_elements['mood_indicator'] = '🚪 ✨ 🏰'

        return visual_elements

    def _generate_premium_cover_design(self, title: str, child_name: str, theme: str, story_template: Optional[object] = None) -> Dict[str, str]:
        """Generate premium cover design based on theme and story content."""

        # Theme-specific cover designs
        theme_covers = {
            'magic_castle': {
                'cover_class': 'cover-premium magic-theme',
                'background_gradient': 'linear-gradient(135deg, #2E1065 0%, #6A5ACD 50%, #FFD700 100%)',
                'title_effect': 'magical-title-glow',
                'decorative_elements': '🏰 ✨ 🧙‍♂️ ⭐ 🌟 🔮 ✨ 🏰',
                'subtitle': 'A Magical Adventure at the Grand Academy',
                'special_effects': 'floating-sparkles'
            },
            'space_adventure': {
                'cover_class': 'cover-premium space-theme',
                'background_gradient': 'linear-gradient(135deg, #000428 0%, #004e92 50%, #009ffd 100%)',
                'title_effect': 'cosmic-title-glow',
                'decorative_elements': '🚀 ⭐ 🌌 🛸 💫 🌟 ⭐ 🚀',
                'subtitle': 'An Intergalactic Journey Through the Stars',
                'special_effects': 'cosmic-drift'
            },
            'underwater': {
                'cover_class': 'cover-premium ocean-theme',
                'background_gradient': 'linear-gradient(135deg, #006994 0%, #4ECDC4 50%, #44A08D 100%)',
                'title_effect': 'wave-title-effect',
                'decorative_elements': '🌊 🐠 🐙 💎 🏝️ 🐚 🐠 🌊',
                'subtitle': 'A Deep Sea Adventure in the Ocean Kingdom',
                'special_effects': 'underwater-bubbles'
            },
            'forest_friends': {
                'cover_class': 'cover-premium forest-theme',
                'background_gradient': 'linear-gradient(135deg, #134E5E 0%, #71B280 50%, #8FBC8F 100%)',
                'title_effect': 'nature-title-glow',
                'decorative_elements': '🌳 🦋 🐿️ 🍄 🌺 🦉 🐿️ 🌳',
                'subtitle': 'A Woodland Adventure with Forest Friends',
                'special_effects': 'nature-whisper'
            }
        }

        # Get theme-specific design or default to magic
        cover_design = theme_covers.get(theme, theme_covers['magic_castle'])

        # Personalize title with child's name
        personalized_title = cover_design['subtitle'].replace('Adventure', f"Adventure for {child_name}")

        # Analyze story content for additional personalization
        theme_elements = []
        if story_template and hasattr(story_template, 'pages'):
            # Extract unique story elements from all pages
            all_story_text = ' '.join([page.story_text.format(name=child_name)
                                     for page in story_template.pages
                                     if hasattr(page, 'story_text')])

            # Add story-specific decorative elements
            if 'dragon' in all_story_text.lower():
                theme_elements.append('🐲')
            if 'owl' in all_story_text.lower():
                theme_elements.append('🦉')
            if 'cat' in all_story_text.lower():
                theme_elements.append('🐱')
            if 'magic' in all_story_text.lower():
                theme_elements.append('⚡')

        # Enhanced decorative elements
        enhanced_decoratives = cover_design['decorative_elements']
        if theme_elements:
            enhanced_decoratives += ' ' + ' '.join(theme_elements)

        return {
            'cover_class': cover_design['cover_class'],
            'background_style': f"background: {cover_design['background_gradient']};",
            'title_effect_class': cover_design['title_effect'],
            'decorative_elements': enhanced_decoratives,
            'personalized_subtitle': personalized_title,
            'special_effects_class': cover_design['special_effects']
        }

    def _generate_premium_back_cover(self, title: str, child_name: str, theme: str, story_template: Optional[object] = None) -> Dict[str, str]:
        """Generate premium back cover with story summary and credits."""

        # Generate story summary based on theme
        theme_summaries = {
            'magic_castle': f"""
            Join {child_name} on their first magical day at the Grand Academy of Arcane Arts!
            From meeting Professor Hoot the wise owl to befriending Sparky the baby dragon,
            every page brings new wonder and adventure. Watch as {child_name} discovers
            the magic within themselves and finds their place in an extraordinary world.
            """,
            'space_adventure': f"""
            Blast off with {child_name} on an incredible journey through the cosmos!
            From distant planets to friendly aliens, experience the wonders of space
            exploration and discover that the greatest adventures happen when you
            believe in yourself among the stars.
            """,
            'underwater': f"""
            Dive deep with {child_name} into the magical underwater kingdom!
            Meet colorful sea creatures, explore coral castles, and discover
            that friendship flows like ocean currents, connecting all who dare
            to explore the depths of adventure.
            """,
            'forest_friends': f"""
            Venture into the enchanted forest with {child_name}! Make friends
            with woodland creatures, learn the secrets of nature, and discover
            that the greatest treasures are the friendships we make along
            the winding forest paths.
            """
        }

        summary = theme_summaries.get(theme, theme_summaries['magic_castle']).strip()

        return {
            'story_summary': summary,
            'credits_content': f"""
            <div class="logo-text">{title}</div>
            <div class="summary-text">{summary}</div>
            <br>
            <div class="credits-info">
                ✨ Personalized for {child_name} ✨<br>
                Created with Advanced AI Technology<br>
                Premium Comic Book Edition<br>
                <br>
                <div style="font-size: 10pt; opacity: 0.8;">
                    Generated with ❤️ by Zelavo Kids<br>
                    Your AI-Powered Storybook Creator<br>
                    Premium Quality • Unlimited Imagination
                </div>
            </div>
            """
        }

    def _parse_story_text(self, story_text: str, page_number: int, story_template: Optional[object] = None) -> Dict[str, str]:
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

    def _get_scene_type(self, page_number: int, story_template: Optional[object] = None) -> str:
        """Get scene type for a specific page."""
        if not story_template or not hasattr(story_template, 'pages'):
            return "unknown"

        try:
            page_template = story_template.pages[page_number - 1]
            return getattr(page_template, 'scene_type', 'unknown')
        except (IndexError, AttributeError):
            return "unknown"

    def _create_intelligent_panel_flow(self, text: str, layout_class: str, content_analysis: Dict) -> Dict[str, str]:
        """Create intelligent text flow across panels based on content analysis."""

        if layout_class != "layout-sequence":
            return {"single": text}

        # Parse different text elements
        dialogue_matches = re.findall(r'"([^"]*)"', text)
        sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]

        # Smart panel distribution for sequence layout
        panels = {"panel1": "", "panel2": "", "panel3": ""}

        if content_analysis['is_dialogue_heavy'] and len(dialogue_matches) >= 2:
            # Dialogue-heavy sequence: distribute dialogue across panels
            panels["panel1"] = f'<div class="speech-bubble">{dialogue_matches[0]}</div>' if dialogue_matches else ""
            panels["panel2"] = f'<div class="speech-bubble">{dialogue_matches[1]}</div>' if len(dialogue_matches) > 1 else ""

            # Remaining narrative in panel 3
            clean_text = text
            for dialogue in dialogue_matches[:2]:
                clean_text = clean_text.replace(f'"{dialogue}"', '')
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            panels["panel3"] = f'<div class="caption-text">{clean_text}</div>' if clean_text else ""

        elif content_analysis['is_action_heavy']:
            # Action sequence: narrative → action → result
            if len(sentences) >= 3:
                panels["panel1"] = f'<div class="narrative-text">{sentences[0]}</div>'
                panels["panel2"] = f'<div class="dialogue-text">{sentences[1]}</div>'
                panels["panel3"] = f'<div class="caption-text">{". ".join(sentences[2:])}</div>'
            else:
                # Split action evenly
                mid_point = len(sentences) // 2
                panels["panel1"] = f'<div class="narrative-text">{". ".join(sentences[:mid_point])}</div>'
                panels["panel2"] = f'<div class="dialogue-text">{". ".join(sentences[mid_point:])}</div>'
                panels["panel3"] = f'<div class="sound-effect">{"WHOOSH!" if "!" not in text else "BANG!"}</div>'

        else:
            # Default: distribute sentences evenly
            if len(sentences) >= 3:
                panels["panel1"] = f'<div class="narrative-text">{sentences[0]}</div>'
                panels["panel2"] = f'<div class="dialogue-text">{sentences[1]}</div>'
                panels["panel3"] = f'<div class="caption-text">{". ".join(sentences[2:])}</div>'
            elif len(sentences) == 2:
                panels["panel1"] = f'<div class="narrative-text">{sentences[0]}</div>'
                panels["panel2"] = f'<div class="dialogue-text">{sentences[1]}</div>'
                panels["panel3"] = f'<div class="caption-text">...</div>'
            else:
                panels["panel1"] = f'<div class="narrative-text">{text}</div>'
                panels["panel2"] = f'<div class="sound-effect">WHOOSH!</div>'
                panels["panel3"] = f'<div class="caption-text">Continue...</div>'

        return panels

    def _apply_typography_enhancement(self, text: str, layout_class: str, scene_type: str, content_analysis: Dict = None) -> str:
        """Apply enhanced typography based on layout, scene type, and content analysis."""

        if content_analysis is None:
            content_analysis = self._analyze_content_complexity(text)

        # Different typography for different layouts
        if layout_class == "layout-action":
            # For action scenes, emphasize dynamic elements
            text = re.sub(r'([A-Z]+!)', r'<span class="sound-effect">\1</span>', text)
            text = re.sub(r'"([^"]*)"', r'<div class="speech-bubble dialogue-text">\1</div>', text)

        elif layout_class == "layout-intimate":
            # For intimate scenes, use softer typography
            text = re.sub(r'"([^"]*)"', r'<div class="speech-bubble dialogue-text">\1</div>', text)
            text = re.sub(r'\(([^)]*)\)', r'<div class="thought-bubble">\1</div>', text)

        elif layout_class == "layout-sequence":
            # For sequence layouts, create intelligent panel flow
            return self._create_intelligent_panel_flow(text, layout_class, content_analysis)

        # Default: wrap in appropriate narrative class
        if not re.search(r'<div class=', text):
            text = f'<div class="narrative-text">{text}</div>'

        return text

    def _generate_html(
        self,
        pages: List[Dict],
        image_data: Dict[int, bytes],
        title: str,
        child_name: str,
        theme: str
    ) -> str:
        """Generate HTML content for PDF (legacy method - use _generate_premium_html for new features)."""

        # HTML template for the storybook
        html_template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <style>
        @page {
            size: 8in 8in; /* Square format for children's books */
            margin: 0.5in;
            @bottom-center {
                content: "{{ child_name }}'s Personalized Storybook";
                font-family: 'Georgia', serif;
                font-size: 10pt;
                color: #666;
            }
        }

        body {
            font-family: 'Georgia', serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background: white;
        }

        .cover-page {
            page-break-after: always;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 7in;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 20px;
            margin: 0.25in;
        }

        .cover-title {
            font-size: 32pt;
            font-weight: bold;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .cover-subtitle {
            font-size: 18pt;
            margin-bottom: 30px;
        }

        .cover-author {
            font-size: 14pt;
            font-style: italic;
        }

        .story-page {
            page-break-before: always;
            height: 7in;
            display: flex;
            flex-direction: column;
            padding: 0.25in;
        }

        .page-image {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            overflow: hidden;
        }

        .page-image img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 10px;
        }

        .page-text {
            background: rgba(102, 126, 234, 0.05);
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            font-size: 14pt;
            line-height: 1.8;
            text-align: justify;
            min-height: 80px;
            display: flex;
            align-items: center;
        }

        .page-number {
            position: absolute;
            bottom: 0.3in;
            right: 0.5in;
            font-size: 12pt;
            color: #666;
        }

        .back-cover {
            page-break-before: always;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 7in;
            text-align: center;
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            color: white;
            border-radius: 20px;
            margin: 0.25in;
        }

        .credits {
            font-size: 14pt;
            line-height: 2;
        }

        .magic-border {
            border: 3px solid;
            border-image: linear-gradient(45deg, #ffd700, #ff6b6b, #4ecdc4, #45b7d1) 1;
            border-radius: 15px;
            margin: 10px;
        }
    </style>
</head>
<body>
    <!-- Cover Page -->
    <div class="cover-page magic-border">
        <div class="cover-title">{{ title }}</div>
        <div class="cover-subtitle">A Personalized Adventure</div>
        <div class="cover-author">Starring {{ child_name }}</div>
    </div>

    <!-- Story Pages -->
    {% for page in pages %}
    <div class="story-page">
        <div class="page-image">
            <img src="data:image/jpeg;base64,{{ page.image_base64 }}" alt="Page {{ page.page_number }}" />
        </div>
        <div class="page-text">
            {{ page.story_text }}
        </div>
        <div class="page-number">{{ page.page_number }}</div>
    </div>
    {% endfor %}

    <!-- Back Cover -->
    <div class="back-cover magic-border">
        <div class="credits">
            <div>🌟 Created with Magic 🌟</div>
            <div>Personalized for {{ child_name }}</div>
            <div>Theme: {{ theme_display }}</div>
            <br>
            <div style="font-size: 12pt; color: #ddd;">
                Generated with ❤️ by Zelavo Kids<br>
                Your AI-Powered Storybook Creator
            </div>
        </div>
    </div>
</body>
</html>
        """)

        # Prepare pages with base64 encoded images
        pages_with_images = []
        for page in pages:
            import base64
            image_base64 = base64.b64encode(image_data[page['page_number']]).decode('utf-8')
            pages_with_images.append({
                'page_number': page['page_number'],
                'story_text': page['story_text'],
                'image_base64': image_base64
            })

        # Theme display names
        theme_names = {
            'magic_castle': 'Magic Castle Adventure',
            'space_adventure': 'Space Adventure',
            'underwater': 'Underwater Kingdom',
            'forest_friends': 'Forest Friends'
        }

        return html_template.render(
            title=title,
            child_name=child_name,
            theme_display=theme_names.get(theme, theme.title()),
            pages=pages_with_images
        )

    async def _html_to_pdf(self, html_content: str) -> bytes:
        """Convert HTML to PDF using WeasyPrint."""
        try:
            # Run WeasyPrint in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()

            def _generate_pdf():
                from weasyprint import HTML, CSS
                from io import StringIO

                # Create HTML object
                html_obj = HTML(string=html_content)

                # Generate PDF
                pdf_bytes = html_obj.write_pdf()
                return pdf_bytes

            # Run in thread pool
            pdf_bytes = await loop.run_in_executor(None, _generate_pdf)

            return pdf_bytes

        except ImportError:
            raise StorageError("WeasyPrint not available. Please install weasyprint.")
        except Exception as e:
            raise StorageError(f"PDF conversion failed: {str(e)}")

    def get_estimated_pdf_size_mb(self, page_count: int) -> float:
        """Estimate PDF file size based on page count."""
        # Rough estimate: ~1.5MB per page (includes high-res images)
        return page_count * 1.5
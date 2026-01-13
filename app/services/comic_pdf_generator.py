"""
Comic PDF Generator Service - StoryGift-Style Layout
Creates professional comic book PDFs with side-by-side panels,
speech bubbles, and drop cap narrative text.
"""

import asyncio
import httpx
import base64
from io import BytesIO
from typing import List, Dict, Optional
import structlog
from jinja2 import Template

from app.config import get_settings
from app.core.exceptions import StorageError

logger = structlog.get_logger()


class ComicPDFGeneratorService:
    """
    Service for generating StoryGift-style comic book PDFs.

    Features:
    - Side-by-side panel layout (2 panels per page)
    - 9:16 portrait aspect ratio per panel
    - Black borders and professional framing
    - Speech bubbles with speaker labels
    - Drop cap narrative text
    - Decorative page numbers
    """

    def __init__(self):
        self.settings = get_settings()

    async def generate_comic_pdf(
        self,
        pages: List[Dict],  # List of comic page data
        title: str,
        child_name: str,
        theme: str
    ) -> bytes:
        """
        Generate complete comic book PDF with StoryGift-style layout.

        Args:
            pages: List of page dicts containing:
                - page_number: int
                - narrative: str (story text)
                - left_panel: {"image_url": str, "dialogue": [{"speaker": str, "text": str, "position": str}]}
                - right_panel: {"image_url": str, "dialogue": [{"speaker": str, "text": str, "position": str}]}
            title: Story title
            child_name: Child's name for personalization
            theme: Theme ID

        Returns:
            PDF bytes
        """
        try:
            logger.info("Generating comic PDF", title=title, page_count=len(pages))

            # Download all images
            image_data = {}
            for page in pages:
                page_num = page['page_number']
                left_bytes = await self._download_image(page['left_panel']['image_url'])
                right_bytes = await self._download_image(page['right_panel']['image_url'])
                image_data[f"{page_num}_left"] = base64.b64encode(left_bytes).decode('utf-8')
                image_data[f"{page_num}_right"] = base64.b64encode(right_bytes).decode('utf-8')

            # Generate HTML
            html_content = self._generate_comic_html(pages, image_data, title, child_name, theme)

            # Convert to PDF
            pdf_bytes = await self._html_to_pdf(html_content)

            logger.info("Comic PDF generated successfully", size_bytes=len(pdf_bytes))
            return pdf_bytes

        except Exception as e:
            logger.error("Failed to generate comic PDF", error=str(e))
            raise StorageError(f"Comic PDF generation failed: {str(e)}")

    async def _download_image(self, url: str) -> bytes:
        """Download image from URL."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content

    def _generate_comic_html(
        self,
        pages: List[Dict],
        image_data: Dict[str, str],
        title: str,
        child_name: str,
        theme: str
    ) -> str:
        """Generate StoryGift-style HTML for comic book."""

        html_template = Template('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Georgia&family=Inter:wght@400;700;900&display=swap');

        @page {
            size: 11in 8.5in; /* Landscape for side-by-side panels */
            margin: 0.5in;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: white;
            color: #1a1a1a;
        }

        /* ===== COVER PAGE ===== */
        .cover-page {
            page-break-after: always;
            height: 7.5in;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            border-radius: 12px;
            padding: 2in;
        }

        .cover-title {
            font-size: 42pt;
            font-weight: 900;
            color: white;
            text-shadow: 0 4px 20px rgba(0,0,0,0.5);
            margin-bottom: 20px;
            letter-spacing: -1px;
        }

        .cover-subtitle {
            font-size: 16pt;
            color: rgba(255,255,255,0.7);
            font-style: italic;
            margin-bottom: 40px;
        }

        .cover-author {
            font-size: 18pt;
            color: #ffd700;
            font-weight: 700;
        }

        /* ===== STORY PAGE (StoryGift Style) ===== */
        .story-page {
            page-break-before: always;
            background: white;
            padding: 0.25in;
            height: 7.5in;
        }

        /* White outer container with shadow */
        .page-container {
            background: white;
            padding: 12px;
            border-radius: 4px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            height: 100%;
            display: flex;
            flex-direction: column;
        }

        /* Black container for panel grid */
        .panels-container {
            background: #000000;
            padding: 12px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            flex: 0 0 auto;
            height: 4.5in;
        }

        /* Individual panel */
        .comic-panel {
            position: relative;
            background: #f4f4f4;
            border: 4px solid #000000;
            overflow: hidden;
            aspect-ratio: 9 / 16;
            height: 100%;
        }

        .comic-panel img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        /* Speech bubble styling */
        .speech-bubble {
            position: absolute;
            max-width: 80%;
            padding: 10px 14px;
            background: white;
            color: #000000;
            font-size: 9pt;
            font-weight: 700;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            border: 2px solid #000000;
            z-index: 10;
        }

        .speech-bubble.position-left {
            top: 12px;
            left: 12px;
            border-bottom-left-radius: 4px;
        }

        .speech-bubble.position-right {
            top: 12px;
            right: 12px;
            border-bottom-right-radius: 4px;
        }

        .speech-bubble.position-bottom {
            bottom: 12px;
            left: 50%;
            transform: translateX(-50%);
            border-bottom-left-radius: 4px;
            border-bottom-right-radius: 4px;
        }

        .speaker-label {
            display: block;
            font-size: 7pt;
            color: #666666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
        }

        /* Narrative text section */
        .narrative-section {
            padding: 32px 48px;
            background: white;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .narrative-text {
            font-family: 'Georgia', serif;
            font-size: 13pt;
            line-height: 1.9;
            color: #2a2a2a;
            text-align: justify;
            max-width: 720px;
            margin: 0 auto;
        }

        /* Drop cap styling */
        .drop-cap {
            float: left;
            font-size: 48pt;
            font-weight: 700;
            font-family: 'Georgia', serif;
            line-height: 0.8;
            margin-right: 8px;
            margin-top: 4px;
            color: #1a1a1a;
        }

        /* Page number */
        .page-number {
            margin-top: 24px;
            padding-top: 16px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            font-size: 10pt;
            font-weight: 700;
            color: #cccccc;
            text-transform: uppercase;
            letter-spacing: 3px;
        }

        /* ===== BACK COVER ===== */
        .back-cover {
            page-break-before: always;
            height: 7.5in;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background: linear-gradient(135deg, #0f3460 0%, #16213e 50%, #1a1a2e 100%);
            border-radius: 12px;
            padding: 2in;
        }

        .credits-text {
            font-size: 14pt;
            color: rgba(255,255,255,0.8);
            line-height: 2.5;
        }

        .credits-highlight {
            color: #ffd700;
            font-weight: 700;
        }

        .credits-small {
            font-size: 10pt;
            color: rgba(255,255,255,0.5);
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <!-- Cover Page -->
    <div class="cover-page">
        <div class="cover-title">{{ title }}</div>
        <div class="cover-subtitle">A Personalized Comic Adventure</div>
        <div class="cover-author">★ Starring {{ child_name }} ★</div>
    </div>

    <!-- Story Pages -->
    {% for page in pages %}
    <div class="story-page">
        <div class="page-container">

            <!-- Side-by-side panels -->
            <div class="panels-container">

                <!-- Left Panel -->
                <div class="comic-panel">
                    <img src="data:image/jpeg;base64,{{ page.left_image_b64 }}" alt="Left panel" />
                    {% for bubble in page.left_dialogue %}
                    <div class="speech-bubble position-{{ bubble.position }}">
                        <span class="speaker-label">{{ bubble.speaker }}</span>
                        "{{ bubble.text }}"
                    </div>
                    {% endfor %}
                </div>

                <!-- Right Panel -->
                <div class="comic-panel">
                    <img src="data:image/jpeg;base64,{{ page.right_image_b64 }}" alt="Right panel" />
                    {% for bubble in page.right_dialogue %}
                    <div class="speech-bubble position-{{ bubble.position }}">
                        <span class="speaker-label">{{ bubble.speaker }}</span>
                        "{{ bubble.text }}"
                    </div>
                    {% endfor %}
                </div>

            </div>

            <!-- Narrative text with drop cap -->
            <div class="narrative-section">
                <p class="narrative-text">
                    <span class="drop-cap">{{ page.narrative_first_char }}</span>{{ page.narrative_rest }}
                </p>
                <div class="page-number">— {{ page.page_number }} —</div>
            </div>

        </div>
    </div>
    {% endfor %}

    <!-- Back Cover -->
    <div class="back-cover">
        <div class="credits-text">
            ✨ Created with Magic ✨<br>
            Personalized for <span class="credits-highlight">{{ child_name }}</span><br>
            Theme: {{ theme_display }}
        </div>
        <div class="credits-small">
            Generated with ❤️ by Zelavo Kids<br>
            AI-Powered Personalized Storybooks
        </div>
    </div>
</body>
</html>
        ''')

        # Prepare pages with base64 images and parsed narrative
        pages_with_data = []
        for page in pages:
            page_num = page['page_number']
            narrative = page['narrative'].replace('{name}', child_name)

            pages_with_data.append({
                'page_number': page_num,
                'left_image_b64': image_data[f"{page_num}_left"],
                'right_image_b64': image_data[f"{page_num}_right"],
                'left_dialogue': page.get('left_panel', {}).get('dialogue', []),
                'right_dialogue': page.get('right_panel', {}).get('dialogue', []),
                'narrative_first_char': narrative[0] if narrative else '',
                'narrative_rest': narrative[1:] if len(narrative) > 1 else ''
            })

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
            pages=pages_with_data
        )

    async def _html_to_pdf(self, html_content: str) -> bytes:
        """Convert HTML to PDF using WeasyPrint."""
        loop = asyncio.get_event_loop()

        def _generate():
            from weasyprint import HTML
            return HTML(string=html_content).write_pdf()

        return await loop.run_in_executor(None, _generate)
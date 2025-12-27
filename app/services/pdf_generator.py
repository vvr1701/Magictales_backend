"""
PDF Generator Service using WeasyPrint.
Creates print-ready PDFs from story pages.
"""

import asyncio
import httpx
from io import BytesIO
from typing import List, Dict
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
        theme: str
    ) -> bytes:
        """
        Generate complete storybook PDF from pages.

        Args:
            pages: List of page dictionaries with image_url, story_text, page_number
            title: Story title (e.g., "Arjun's First Day of Magic")
            child_name: Child's name
            theme: Theme ID (e.g., "magic_castle")

        Returns:
            PDF bytes
        """
        try:
            logger.info("Generating PDF", title=title, page_count=len(pages))

            # Download all images first
            image_data = {}
            for page in pages:
                logger.info(f"Downloading image for page {page['page_number']}")
                image_bytes = await self._download_image(page['image_url'])
                image_data[page['page_number']] = image_bytes

            # Generate HTML content
            html_content = self._generate_html(pages, image_data, title, child_name, theme)

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

    def _generate_html(
        self,
        pages: List[Dict],
        image_data: Dict[int, bytes],
        title: str,
        child_name: str,
        theme: str
    ) -> str:
        """Generate HTML content for PDF."""

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
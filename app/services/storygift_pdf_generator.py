"""
StoryGift-style PDF Generator Service.

Pure ReportLab approach for production-ready PDF generation:
- Direct image + text → PDF (no browser needed)
- 10x10 inch square pages matching frontend preview
- 80% image area / 20% text area layout
- Fast (~2-5 seconds for 10 pages)
"""

import asyncio
import os
import tempfile
from io import BytesIO
from typing import List, Dict, Optional, Any
import structlog
import httpx
from PIL import Image

from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import Color, white, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from app.config import get_settings
from app.core.exceptions import StorageError
from app.services.storage import StorageService

logger = structlog.get_logger()

# Page dimensions: 10x10 inch square
PAGE_WIDTH = 10 * inch
PAGE_HEIGHT = 10 * inch

# Layout: 80% image, 20% text
IMAGE_HEIGHT = 8 * inch  # 80% of page
TEXT_HEIGHT = 2 * inch   # 20% of page


class StoryGiftPDFGeneratorService:
    """
    PDF Generator using pure ReportLab approach.

    Flow:
    1. Download images from R2 storage
    2. Create PDF with ReportLab
    3. For each page: draw image (80%) + text (20%)
    4. Upload to R2 and return URL
    """

    def __init__(self):
        self.settings = get_settings()
        self.storage = StorageService()
        logger.info("StoryGift PDF generator initialized (ReportLab-only)")

    async def generate_storygift_pdf(
        self,
        preview_id: str,
        child_name: str,
        story_pages: List[Dict[str, Any]],
        story_title: str,
        cover_image_url: Optional[str] = None
    ) -> str:
        """
        Generate StoryGift-style PDF from story pages.

        Args:
            preview_id: Preview ID for storage paths
            child_name: Child's name for personalization
            story_pages: List of page data with image_url, story_text
            story_title: Story title for cover page
            cover_image_url: Optional cover image URL

        Returns:
            PDF file URL in storage
        """
        try:
            logger.info(
                "Starting ReportLab PDF generation",
                preview_id=preview_id,
                child_name=child_name,
                page_count=len(story_pages)
            )

            # Download all images first
            page_images = await self._download_all_images(story_pages, cover_image_url)

            # Generate PDF
            pdf_bytes = self._create_pdf(
                story_pages=story_pages,
                page_images=page_images,
                child_name=child_name,
                story_title=story_title,
                cover_image=page_images.get('cover')
            )

            # Upload to storage
            storage_path = f"final/{preview_id}/storygift_book.pdf"
            pdf_url = await self.storage.upload_pdf(pdf_bytes, storage_path)

            logger.info(
                "PDF generated successfully",
                preview_id=preview_id,
                pdf_url=pdf_url,
                page_count=len(story_pages),
                size_bytes=len(pdf_bytes)
            )

            return pdf_url

        except Exception as e:
            logger.error(
                "PDF generation failed",
                preview_id=preview_id,
                error=str(e)
            )
            raise StorageError(f"PDF generation failed: {str(e)}")

    async def _download_all_images(
        self,
        story_pages: List[Dict[str, Any]],
        cover_image_url: Optional[str]
    ) -> Dict[str, bytes]:
        """Download all images concurrently for faster processing."""
        images = {}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Download cover image
            if cover_image_url:
                try:
                    response = await client.get(cover_image_url)
                    response.raise_for_status()
                    images['cover'] = response.content
                    logger.info("Cover image downloaded")
                except Exception as e:
                    logger.warning(f"Failed to download cover image: {e}")

            # Download page images
            for i, page in enumerate(story_pages):
                page_num = page.get('page', i + 1)
                image_url = page.get('image_url', '')
                
                if image_url:
                    try:
                        response = await client.get(image_url)
                        response.raise_for_status()
                        images[f'page_{page_num}'] = response.content
                    except Exception as e:
                        logger.warning(f"Failed to download page {page_num} image: {e}")

        logger.info(f"Downloaded {len(images)} images for PDF")
        return images

    def _create_pdf(
        self,
        story_pages: List[Dict[str, Any]],
        page_images: Dict[str, bytes],
        child_name: str,
        story_title: str,
        cover_image: Optional[bytes] = None
    ) -> bytes:
        """Create the PDF using ReportLab canvas for precise control."""
        
        # Create temporary file for PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Create canvas
            c = canvas.Canvas(tmp_path, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
            
            # Generate cover page if we have a cover image
            if cover_image:
                self._draw_cover_page(c, cover_image, story_title, child_name)
                c.showPage()

            # Generate story pages
            for i, page_data in enumerate(story_pages):
                page_num = page_data.get('page', i + 1)
                story_text = page_data.get('story_text', page_data.get('text', ''))
                image_bytes = page_images.get(f'page_{page_num}')
                
                self._draw_story_page(c, image_bytes, story_text, page_num)
                
                # Add page break (except for last page)
                if i < len(story_pages) - 1:
                    c.showPage()

            c.save()

            # Read the generated PDF
            with open(tmp_path, 'rb') as f:
                pdf_bytes = f.read()

            return pdf_bytes

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _draw_cover_page(
        self,
        c: canvas.Canvas,
        cover_image: bytes,
        story_title: str,
        child_name: str
    ):
        """Draw the cover page with background image and title overlay.
        
        Matches the frontend CoverPageCard.tsx styling:
        - Amber-400 title text in top area
        - White child name in bottom area
        - Gradient overlays (simulated with semi-transparent rects)
        """
        try:
            # Draw cover image as full-page background
            img = Image.open(BytesIO(cover_image))
            img_reader = ImageReader(img)
            c.drawImage(
                img_reader,
                0, 0,
                width=PAGE_WIDTH,
                height=PAGE_HEIGHT,
                preserveAspectRatio=True,
                anchor='c'
            )

            # Extract just the theme title (remove child name prefix like "vishn and the ")
            # to match CoverPageCard.tsx displayTitle logic
            display_title = story_title
            if child_name.lower() in story_title.lower():
                # Remove patterns like "Child's Adventure" or "Child and the Adventure"
                import re
                patterns = [
                    rf"{re.escape(child_name)}'?s?\s*",       # "Child's " or "Childs "
                    rf"{re.escape(child_name)}\s+and\s+the\s+",  # "Child and the "
                    r"^and\s+the\s+",                         # "and the " at start
                    r"^the\s+",                                # "the " at start
                ]
                for pattern in patterns:
                    display_title = re.sub(pattern, '', display_title, flags=re.IGNORECASE)
                display_title = display_title.strip()
            
            # Top gradient overlay (semi-transparent black, top 25% of page)
            c.saveState()
            c.setFillColor(Color(0, 0, 0, alpha=0.6))
            c.rect(0, PAGE_HEIGHT - 2.5*inch, PAGE_WIDTH, 2.5*inch, fill=1, stroke=0)
            c.restoreState()

            # Title text in AMBER-400 color: rgb(251, 191, 36) = #fbbf24
            c.saveState()
            c.setFillColor(Color(251/255, 191/255, 36/255))  # Amber-400
            c.setFont("Helvetica-Bold", 42)
            
            # Center the title - use uppercase to match preview
            title_upper = display_title.upper()
            title_width = c.stringWidth(title_upper, "Helvetica-Bold", 42)
            
            # Handle long titles by reducing font size
            if title_width > PAGE_WIDTH - 40:
                c.setFont("Helvetica-Bold", 32)
                title_width = c.stringWidth(title_upper, "Helvetica-Bold", 32)
            
            title_x = (PAGE_WIDTH - title_width) / 2
            c.drawString(title_x, PAGE_HEIGHT - 1.3*inch, title_upper)
            c.restoreState()

            # Bottom gradient overlay (semi-transparent black, bottom 20% of page)
            c.saveState()
            c.setFillColor(Color(0, 0, 0, alpha=0.75))
            c.rect(0, 0, PAGE_WIDTH, 2*inch, fill=1, stroke=0)
            c.restoreState()

            # "STARRING" label in gray
            c.saveState()
            c.setFillColor(Color(0.8, 0.8, 0.8, alpha=1))  # Light gray like preview
            c.setFont("Helvetica", 12)
            starring_text = "STARRING"
            starring_width = c.stringWidth(starring_text, "Helvetica", 12)
            c.drawString((PAGE_WIDTH - starring_width) / 2, 1.3*inch, starring_text)
            c.restoreState()

            # Child name in WHITE, bold
            c.saveState()
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 28)
            name_upper = child_name.upper()
            name_width = c.stringWidth(name_upper, "Helvetica-Bold", 28)
            c.drawString((PAGE_WIDTH - name_width) / 2, 0.8*inch, name_upper)
            c.restoreState()

        except Exception as e:
            logger.error(f"Failed to draw cover page: {e}")
            # Draw a fallback cover
            c.setFillColor(Color(0.4, 0.2, 0.6))
            c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1)
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 48)
            c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT/2, story_title)

    def _draw_story_page(
        self,
        c: canvas.Canvas,
        image_bytes: Optional[bytes],
        story_text: str,
        page_num: int
    ):
        """Draw a story page with image (top 80%) and text (bottom 20%)."""
        
        # Background
        c.setFillColor(white)
        c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

        # Draw image in top 80%
        if image_bytes:
            try:
                img = Image.open(BytesIO(image_bytes))
                img_reader = ImageReader(img)
                
                # Image area: top 80% of page
                img_y = TEXT_HEIGHT  # Start above text area
                
                c.drawImage(
                    img_reader,
                    0, img_y,  # x, y (bottom-left of image area)
                    width=PAGE_WIDTH,
                    height=IMAGE_HEIGHT,
                    preserveAspectRatio=True,
                    anchor='c'  # Center the image
                )
            except Exception as e:
                logger.error(f"Failed to draw image for page {page_num}: {e}")
                # Draw placeholder
                c.setFillColor(Color(0.95, 0.95, 0.95))
                c.rect(0, TEXT_HEIGHT, PAGE_WIDTH, IMAGE_HEIGHT, fill=1, stroke=0)
                c.setFillColor(Color(0.7, 0.7, 0.7))
                c.setFont("Helvetica", 24)
                c.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT/2 + inch, f"Page {page_num}")
        else:
            # No image - draw placeholder
            c.setFillColor(Color(0.95, 0.95, 0.95))
            c.rect(0, TEXT_HEIGHT, PAGE_WIDTH, IMAGE_HEIGHT, fill=1, stroke=0)

        # Draw border line between image and text
        c.setStrokeColor(Color(0.9, 0.9, 0.9))
        c.setLineWidth(1)
        c.line(0, TEXT_HEIGHT, PAGE_WIDTH, TEXT_HEIGHT)

        # Draw text in bottom 20%
        self._draw_story_text(c, story_text, page_num)

    def _draw_story_text(self, c: canvas.Canvas, story_text: str, page_num: int):
        """Draw the story text in the bottom 20% of the page."""
        if not story_text:
            # No text - draw decorative dots
            c.setFillColor(Color(0.6, 0.65, 0.7))
            c.setFont("Helvetica", 14)
            c.drawCentredString(PAGE_WIDTH/2, TEXT_HEIGHT/2, "• • •")
            return

        # Text area padding
        padding_x = 0.5 * inch
        padding_y = 0.3 * inch
        text_area_width = PAGE_WIDTH - (2 * padding_x)
        
        # Set up text styling
        c.setFillColor(Color(0.22, 0.25, 0.32))  # Dark gray (#374151)
        
        # Calculate font size based on text length (responsive sizing)
        text_length = len(story_text)
        if text_length > 250:
            font_size = 14
        elif text_length > 150:
            font_size = 16
        elif text_length > 80:
            font_size = 18
        else:
            font_size = 20

        c.setFont("Helvetica", font_size)
        
        # Simple text wrapping
        words = story_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if c.stringWidth(test_line, "Helvetica", font_size) <= text_area_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)

        # Calculate vertical centering
        line_height = font_size * 1.4
        total_text_height = len(lines) * line_height
        start_y = (TEXT_HEIGHT + total_text_height) / 2

        # Draw lines centered
        for i, line in enumerate(lines):
            y_pos = start_y - (i * line_height)
            if y_pos > padding_y:  # Don't draw below padding
                c.drawCentredString(PAGE_WIDTH/2, y_pos, line)

    # Legacy compatibility methods
    async def generate_storybook_pdf(
        self,
        pages: List[Dict],
        title: str,
        child_name: str,
        theme: str,
        story_template: Optional[object] = None
    ) -> bytes:
        """Legacy compatibility method for existing API."""
        logger.info("Legacy PDF generation called, using ReportLab approach")

        pdf_url = await self.generate_storygift_pdf(
            preview_id=f"legacy_{child_name}_{theme}",
            child_name=child_name,
            story_pages=pages,
            story_title=title
        )

        # Download PDF bytes for legacy return format
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(pdf_url)
            response.raise_for_status()
            return response.content


# Legacy class alias for backward compatibility
class PDFGeneratorService(StoryGiftPDFGeneratorService):
    """Backward compatibility alias."""
    pass
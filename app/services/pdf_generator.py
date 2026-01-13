"""
PDF Generator Service using StoryGift approach.
Creates superior PDFs with Playwright + reportlab approach.

This service now inherits from StoryGiftPDFGeneratorService
to provide the superior layout and generation quality.
"""

from app.services.storygift_pdf_generator import StoryGiftPDFGeneratorService

# Main service inherits from StoryGift implementation
class PDFGeneratorService(StoryGiftPDFGeneratorService):
    """
    PDF Generator Service with StoryGift's superior approach.

    This maintains backward compatibility while providing
    the upgraded Playwright + reportlab PDF generation.
    """
    pass  # All functionality inherited from StoryGiftPDFGeneratorService
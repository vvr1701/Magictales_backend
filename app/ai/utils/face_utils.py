"""
Face Detection Utilities - Using MediaPipe for accurate face detection.

Provides face detection and mask generation for the inpainting pipeline.
White mask = area to repaint, Black mask = area to preserve.
"""

import io
import httpx
import structlog
from typing import Optional, Tuple
from PIL import Image, ImageDraw

logger = structlog.get_logger()

# MediaPipe import with robust fallback
MEDIAPIPE_AVAILABLE = False
mp_face_detection = None

try:
    import mediapipe as mp
    # Check if solutions attribute exists (some versions/installations have issues)
    if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_detection'):
        mp_face_detection = mp.solutions.face_detection
        MEDIAPIPE_AVAILABLE = True
        logger.info("MediaPipe face detection loaded successfully")
    else:
        logger.warning("MediaPipe installed but face_detection not available, using fallback")
except ImportError:
    logger.warning("MediaPipe not installed, using fallback face detection")
except Exception as e:
    logger.warning(f"MediaPipe initialization failed: {e}, using fallback")


class FaceDetector:
    """
    Face detector using MediaPipe Face Detection.
    
    Generates soft-edged masks for inpainting pipelines.
    Falls back to center-region detection if MediaPipe unavailable.
    """

    def __init__(self):
        self.face_detection = None
        
        if MEDIAPIPE_AVAILABLE and mp_face_detection is not None:
            try:
                self.face_detection = mp_face_detection.FaceDetection(
                    model_selection=1,  # 1 = full range model
                    min_detection_confidence=0.5
                )
                logger.info("FaceDetector initialized with MediaPipe")
            except Exception as e:
                logger.warning(f"Failed to create MediaPipe detector: {e}, using fallback")
                self.face_detection = None
        else:
            logger.info("FaceDetector initialized with fallback (center-region detection)")

    async def download_image(self, image_url: str) -> Optional[Image.Image]:
        """Download image from URL and return PIL Image."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_data = io.BytesIO(response.content)
                image = Image.open(image_data)
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                return image
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            return None

    def detect_face_bbox(
        self,
        image: Image.Image,
        expand_ratio: float = 0.3
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect face bounding box in image.
        
        Args:
            image: PIL Image
            expand_ratio: How much to expand the detected bbox (0.3 = 30% larger)
            
        Returns:
            Tuple of (x1, y1, x2, y2) or None if no face detected
        """
        import numpy as np
        
        if not MEDIAPIPE_AVAILABLE or self.face_detection is None:
            # Fallback: assume face is in upper-center region
            logger.warning("Using fallback face detection (center region)")
            w, h = image.size
            # Assume face is in upper-center 40% of image
            center_x, center_y = w // 2, int(h * 0.35)
            face_size = min(w, h) // 3
            x1 = max(0, center_x - face_size // 2)
            y1 = max(0, center_y - face_size // 2)
            x2 = min(w, center_x + face_size // 2)
            y2 = min(h, center_y + face_size // 2)
            return (x1, y1, x2, y2)

        # Convert PIL to numpy for MediaPipe
        image_np = np.array(image)
        
        # Run face detection
        results = self.face_detection.process(image_np)
        
        if not results.detections:
            logger.warning("No face detected in image")
            return None

        # Get first (largest) detection
        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box
        
        # Convert relative coords to absolute
        h, w = image_np.shape[:2]
        x1 = int(bbox.xmin * w)
        y1 = int(bbox.ymin * h)
        box_w = int(bbox.width * w)
        box_h = int(bbox.height * h)
        x2 = x1 + box_w
        y2 = y1 + box_h
        
        # Expand bounding box for better inpainting results
        expand_w = int(box_w * expand_ratio)
        expand_h = int(box_h * expand_ratio)
        
        x1 = max(0, x1 - expand_w)
        y1 = max(0, y1 - expand_h)
        x2 = min(w, x2 + expand_w)
        y2 = min(h, y2 + expand_h)
        
        logger.info(
            "Face detected",
            bbox=(x1, y1, x2, y2),
            confidence=detection.score[0]
        )
        
        return (x1, y1, x2, y2)

    def generate_mask(
        self,
        image: Image.Image,
        bbox: Tuple[int, int, int, int],
        feather_radius: int = 20
    ) -> Image.Image:
        """
        Generate inpainting mask for face region.
        
        Creates a white ellipse on black background for the face area.
        White = area to repaint, Black = area to keep.
        
        Args:
            image: Original image (for size reference)
            bbox: Face bounding box (x1, y1, x2, y2)
            feather_radius: Soft edge radius (not used in simple version)
            
        Returns:
            PIL Image with mask (RGB, same size as input)
        """
        w, h = image.size
        x1, y1, x2, y2 = bbox
        
        # Create black background
        mask = Image.new('RGB', (w, h), (0, 0, 0))
        draw = ImageDraw.Draw(mask)
        
        # Draw white ellipse for face region (softer than rectangle)
        draw.ellipse([x1, y1, x2, y2], fill=(255, 255, 255))
        
        logger.info(
            "Mask generated",
            mask_size=(w, h),
            face_region=bbox
        )
        
        return mask

    async def create_face_mask(
        self,
        image_url: str,
        expand_ratio: float = 0.3
    ) -> Tuple[Optional[Image.Image], Optional[Image.Image]]:
        """
        Complete pipeline: download image, detect face, generate mask.
        
        Args:
            image_url: URL of source image
            expand_ratio: How much to expand face bbox
            
        Returns:
            Tuple of (original_image, mask_image) or (None, None) on failure
        """
        # Download image
        image = await self.download_image(image_url)
        if image is None:
            return None, None
        
        # Detect face
        bbox = self.detect_face_bbox(image, expand_ratio)
        if bbox is None:
            # If no face detected, use center fallback
            w, h = image.size
            center_size = min(w, h) // 3
            cx, cy = w // 2, int(h * 0.35)
            bbox = (
                max(0, cx - center_size // 2),
                max(0, cy - center_size // 2),
                min(w, cx + center_size // 2),
                min(h, cy + center_size // 2)
            )
            logger.warning("Using fallback center region for mask")
        
        # Generate mask
        mask = self.generate_mask(image, bbox)
        
        return image, mask


async def upload_mask_to_storage(
    mask: Image.Image,
    storage_service,
    preview_id: str,
    page_number: int
) -> Optional[str]:
    """
    Upload mask image to storage and return URL.
    
    Args:
        mask: PIL Image mask
        storage_service: StorageService instance
        preview_id: Preview ID for path
        page_number: Page number for path
        
    Returns:
        Public URL of uploaded mask or None on failure
    """
    try:
        # Convert mask to bytes
        buffer = io.BytesIO()
        mask.save(buffer, format='PNG')
        buffer.seek(0)
        mask_bytes = buffer.read()
        
        # Upload to storage using existing method
        mask_path = f"masks/{preview_id}/page_{page_number:02d}_mask.png"
        mask_url = await storage_service.upload_image(
            mask_bytes,
            mask_path,
            content_type="image/png"
        )
        
        logger.info("Mask uploaded", mask_url=mask_url[:80] if mask_url else None)
        return mask_url
        
    except Exception as e:
        logger.error(f"Failed to upload mask: {e}")
        return None

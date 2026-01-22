"""
Enums for database status fields.
"""

from enum import Enum


class PreviewStatus(str, Enum):
    """Preview generation and lifecycle status."""
    PENDING = "pending"
    VALIDATING = "validating"
    GENERATING = "generating"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    PURCHASED = "purchased"


class OrderStatus(str, Enum):
    """Order processing status."""
    PAID = "paid"
    GENERATING_PDF = "generating_pdf"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class JobStatus(str, Enum):
    """Background job status."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobType(str, Enum):
    """Type of background job."""
    PREVIEW_GENERATION = "preview_generation"
    PDF_CREATION = "pdf_creation"


class BookStyle(str, Enum):
    """Storybook visual style."""
    PHOTOREALISTIC = "photorealistic"
    CARTOON_3D = "cartoon_3d"  # Disney/Pixar 3D animation style


class Theme(str, Enum):
    """Available story themes."""
    # Primary StoryGift themes (superior quality, 10 pages each)
    STORYGIFT_MAGIC_CASTLE = "storygift_magic_castle"
    STORYGIFT_ENCHANTED_FOREST = "storygift_enchanted_forest"
    STORYGIFT_SPY_MISSION = "storygift_spy_mission"
    # New premium themes
    STORYGIFT_COSMIC_DREAMER = "storygift_cosmic_dreamer"
    STORYGIFT_MIGHTY_GUARDIAN = "storygift_mighty_guardian"
    STORYGIFT_OCEAN_EXPLORER = "storygift_ocean_explorer"
    STORYGIFT_BIRTHDAY_MAGIC = "storygift_birthday_magic"
    # Newest premium themes (Safari & Dream Weaver)
    STORYGIFT_SAFARI_ADVENTURE = "storygift_safari_adventure"
    STORYGIFT_DREAM_WEAVER = "storygift_dream_weaver"

    # Legacy themes (for backward compatibility)
    MAGIC_CASTLE = "magic_castle"
    SPACE_ADVENTURE = "space_adventure"
    UNDERWATER = "underwater"
    FOREST_FRIENDS = "forest_friends"


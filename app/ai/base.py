"""
Base classes and interfaces for AI services.
All model implementations must follow these interfaces.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class GenerationResult:
    """Result from any image generation operation."""
    success: bool
    image_url: Optional[str] = None
    error_message: Optional[str] = None
    latency_ms: int = 0
    model_used: str = ""
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseGenerationService(ABC):
    """Interface for base image generation (text-to-image)."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        width: int = 1024,
        height: int = 1365,  # 3:4 aspect ratio for storybook
        **kwargs
    ) -> GenerationResult:
        """Generate image from text prompt."""
        pass


class FaceEmbeddingService(ABC):
    """Interface for face-embedded generation."""

    @abstractmethod
    async def generate_with_face(
        self,
        prompt: str,
        face_image_url: str,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> GenerationResult:
        """Generate image with face from reference."""
        pass


class FaceSwapService(ABC):
    """Interface for face swapping."""

    @abstractmethod
    async def swap_face(
        self,
        base_image_url: str,
        face_image_url: str,
        **kwargs
    ) -> GenerationResult:
        """Swap face onto base image."""
        pass

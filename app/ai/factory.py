"""
Model Factory - Creates model instances based on configuration.
"""

from typing import Union

from app.config import get_settings
from app.ai.model_registry import get_model, ModelType
from app.ai.base import (
    BaseGenerationService,
    FaceEmbeddingService,
    FaceSwapService
)

# Import implementations
from app.ai.implementations.flux import FluxGenerationService
from app.ai.implementations.pulid import FluxPulidService
from app.ai.implementations.face_swap import FalFaceSwapService


class ModelFactory:
    """Factory for creating AI model instances."""

    # Mapping of model IDs to implementation classes
    IMPLEMENTATIONS = {
        # Base generation
        "flux_schnell": FluxGenerationService,
        "flux_dev": FluxGenerationService,
        "flux_pro": FluxGenerationService,

        # Face embedding
        "flux_pulid": FluxPulidService,
        "instant_id": FluxPulidService,  # Uses same implementation

        # Face swap
        "fal_face_swap": FalFaceSwapService,
    }

    @classmethod
    def create_base_generator(cls, model_id: str = None) -> BaseGenerationService:
        """Create a base image generation service."""
        settings = get_settings()
        model_id = model_id or settings.artistic_base_model

        config = get_model(model_id)
        implementation_class = cls.IMPLEMENTATIONS.get(model_id)

        if not implementation_class:
            raise ValueError(f"No implementation for model: {model_id}")

        return implementation_class(config)

    @classmethod
    def create_face_embedder(cls, model_id: str = None) -> FaceEmbeddingService:
        """Create a face embedding service."""
        settings = get_settings()
        model_id = model_id or settings.realistic_model

        config = get_model(model_id)
        implementation_class = cls.IMPLEMENTATIONS.get(model_id)

        if not implementation_class:
            raise ValueError(f"No implementation for model: {model_id}")

        return implementation_class(config)

    @classmethod
    def create_face_swapper(cls, model_id: str = None) -> FaceSwapService:
        """Create a face swap service."""
        settings = get_settings()
        model_id = model_id or settings.artistic_face_model

        config = get_model(model_id)
        implementation_class = cls.IMPLEMENTATIONS.get(model_id)

        if not implementation_class:
            raise ValueError(f"No implementation for model: {model_id}")

        return implementation_class(config)


# Convenience functions
def get_artistic_pipeline():
    """Get configured artistic pipeline (base + face swap)."""
    return (
        ModelFactory.create_base_generator(),
        ModelFactory.create_face_swapper()
    )


def get_realistic_pipeline():
    """Get configured realistic pipeline (face embedding)."""
    return ModelFactory.create_face_embedder()

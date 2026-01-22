"""
Model Factory - Creates model instances based on configuration.
"""

from typing import Union

from app.config import get_settings
from app.ai.model_registry import get_model, ModelType
from app.ai.base import (
    BaseGenerationService,
    FaceSwapService,
    FaceEmbeddingService
)

# Import implementations
from app.ai.implementations.flux import FluxGenerationService
from app.ai.implementations.face_swap import FalFaceSwapService
# PuLID removed - using NanoBanana and Cartoon3D pipelines only
from app.ai.implementations.ip_adapter_face_id import IpAdapterFaceIdService
from app.ai.pipelines.nanoBanana_pipeline import NanoBananaPipeline


class ModelFactory:
    """Factory for creating AI model instances."""

    # Mapping of model IDs to implementation classes
    IMPLEMENTATIONS = {
        # Base generation (artistic pipeline - step 1)
        "flux_schnell": FluxGenerationService,
        "flux_dev": FluxGenerationService,
        "flux_pro": FluxGenerationService,
        "flux_general": FluxGenerationService,  # IP-Adapter support for photorealistic
        "recraft_v3": FluxGenerationService,  # Uses same implementation

        # Face swap (artistic pipeline - step 2)
        "fal_face_swap": FalFaceSwapService,

        # Face embedding (photorealistic pipeline only)
        # PuLID removed - using NanoBanana and Cartoon3D pipelines only
        "ip_adapter_face_id": IpAdapterFaceIdService,

        # StoryGift-style pipeline (NanoBanana with VLM analysis)
        "nano_banana": NanoBananaPipeline,
    }

    @classmethod
    def create_face_embedder(cls, model_id: str = None) -> FaceEmbeddingService:
        """Create a face embedding service (photorealistic pipeline)."""
        settings = get_settings()
        model_id = model_id or settings.realistic_model

        config = get_model(model_id)
        implementation_class = cls.IMPLEMENTATIONS.get(model_id)

        if not implementation_class:
            raise ValueError(f"No implementation for model: {model_id}")

        return implementation_class(config)

    @classmethod
    def create_base_generator(cls, model_id: str = None) -> BaseGenerationService:
        """Create a base image generation service (artistic pipeline - step 1)."""
        settings = get_settings()
        model_id = model_id or settings.artistic_base_model

        config = get_model(model_id)
        implementation_class = cls.IMPLEMENTATIONS.get(model_id)

        if not implementation_class:
            raise ValueError(f"No implementation for base generator model: {model_id}")

        return implementation_class(config)

    @classmethod
    def create_face_swapper(cls, model_id: str = None) -> FaceSwapService:
        """Create a face swap service (artistic pipeline - step 2)."""
        settings = get_settings()
        model_id = model_id or settings.artistic_face_model

        config = get_model(model_id)
        implementation_class = cls.IMPLEMENTATIONS.get(model_id)

        if not implementation_class:
            raise ValueError(f"No implementation for face swap model: {model_id}")

        return implementation_class(config)

    @classmethod
    def create_nanoBanana_pipeline(cls) -> "NanoBananaPipeline":
        """Create the NanoBanana pipeline (only pipeline used for all generation)."""
        return NanoBananaPipeline()


# Convenience function
def get_nanoBanana_pipeline():
    """Get NanoBanana pipeline (only pipeline used for all generation)."""
    return ModelFactory.create_nanoBanana_pipeline()


def get_pipeline_for_style(style: str):
    """
    Get appropriate pipeline based on art style.
    
    Args:
        style: Either 'photorealistic' or 'cartoon_3d'
        
    Returns:
        Pipeline instance (NanoBananaPipeline or Cartoon3DPipeline)
    """
    if style == "cartoon_3d":
        from app.ai.pipelines.cartoon3d_pipeline import Cartoon3DPipeline
        return Cartoon3DPipeline()
    else:
        # Default to photorealistic (NanoBanana)
        return get_nanoBanana_pipeline()

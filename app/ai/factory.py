"""
Model Factory - Creates model instances based on configuration.
"""

from typing import Union

from app.config import get_settings
from app.ai.model_registry import get_model, ModelType
from app.ai.base import (
    FaceEmbeddingService
)

# Import implementations
from app.ai.implementations.pulid import FluxPulidService


class ModelFactory:
    """Factory for creating AI model instances."""

    # Mapping of model IDs to implementation classes
    IMPLEMENTATIONS = {
        # Face embedding (photorealistic pipeline only)
        "flux_pulid": FluxPulidService,
        "instant_id": FluxPulidService,  # Uses same implementation
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


# Convenience functions
def get_realistic_pipeline():
    """Get configured realistic pipeline (face embedding)."""
    return ModelFactory.create_face_embedder()

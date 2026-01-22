"""
Model Registry - Central configuration for all AI models.
Add new models here without changing other code.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum


class ModelType(Enum):
    """Type of AI model."""
    BASE_GENERATION = "base_generation"      # Text-to-image
    FACE_EMBEDDING = "face_embedding"        # Face in generation
    FACE_SWAP = "face_swap"                  # Post-process face swap


@dataclass
class ModelConfig:
    """Configuration for a single AI model."""
    model_id: str
    endpoint: str
    model_type: ModelType
    cost_per_image: float
    avg_latency_seconds: float
    max_retries: int = 3
    timeout_seconds: int = 120
    supports_negative_prompt: bool = True
    supports_seed: bool = True
    default_params: Dict[str, Any] = field(default_factory=dict)


# ===================
# MODEL DEFINITIONS
# ===================

MODELS: Dict[str, ModelConfig] = {

    # ========== BASE GENERATION MODELS ==========

    "flux_general": ModelConfig(
        model_id="flux_general",
        endpoint="fal-ai/flux-general",
        model_type=ModelType.BASE_GENERATION,
        cost_per_image=0.045,
        avg_latency_seconds=8,
        supports_negative_prompt=True,
        supports_seed=True,
        timeout_seconds=180,
        default_params={
            "numInferenceSteps": 50,
            "guidanceScale": 7.5,
            "imageSize": {"width": 1024, "height": 1365},  # 4:3 storybook ratio
            "enableSafetyChecker": True,
            "syncMode": True,
            "numImages": 1
        }
    ),

    "flux_schnell": ModelConfig(
        model_id="flux_schnell",
        endpoint="fal-ai/flux/schnell",
        model_type=ModelType.BASE_GENERATION,
        cost_per_image=0.003,
        avg_latency_seconds=2,
        default_params={
            "numInferenceSteps": 4,  # Schnell is optimized for fewer steps
            "guidanceScale": 3.5,
        }
    ),

    "flux_dev": ModelConfig(
        model_id="flux_dev",
        endpoint="fal-ai/flux/dev",
        model_type=ModelType.BASE_GENERATION,
        cost_per_image=0.025,
        avg_latency_seconds=5,
        default_params={
            "numInferenceSteps": 28,
            "guidanceScale": 7.5,
        }
    ),

    "flux_pro": ModelConfig(
        model_id="flux_pro",
        endpoint="fal-ai/flux-pro",
        model_type=ModelType.BASE_GENERATION,
        cost_per_image=0.05,
        avg_latency_seconds=8,
        default_params={
            "numInferenceSteps": 35,
            "guidanceScale": 7.5,
        }
    ),

    # ========== ENHANCED MODELS FOR 2-STEP APPROACH ==========

    "flux_dev_scenes": ModelConfig(
        model_id="flux_dev_scenes",
        endpoint="fal-ai/flux/dev",
        model_type=ModelType.BASE_GENERATION,
        cost_per_image=0.025,
        avg_latency_seconds=8,
        supports_negative_prompt=True,
        supports_seed=True,
        timeout_seconds=180,
        default_params={
            "numInferenceSteps": 35,         # Higher for scene detail
            "guidanceScale": 8.0,            # Stronger prompt adherence for detailed scenes
            "imageSize": {"width": 1024, "height": 1024},  # Square format for better composition
            "enableSafetyChecker": True,
            "syncMode": True,
            "numImages": 1
        }
    ),

    # PuLID models removed - using NanoBanana and Cartoon3D pipelines only

    # ========== FACE EMBEDDING MODELS ==========



    # ========== STORYGIFT-STYLE MODELS ==========

    "nano_banana": ModelConfig(
        model_id="nano_banana",
        endpoint="fal-ai/nano-banana/edit",
        model_type=ModelType.FACE_EMBEDDING,
        cost_per_image=0.04,
        avg_latency_seconds=8,
        supports_negative_prompt=True,
        supports_seed=True,
        timeout_seconds=180,
        default_params={
            # StoryGift configuration from analysis
            "aspect_ratio": "5:4",                    # StoryGift's optimized aspect ratio
            "negative_prompt": "black bars, letterbox, scope, cinema bars, blurry, low quality, distorted face",
        }
    ),

    # ========== INPAINTING MODELS ==========

    "flux_inpainting": ModelConfig(
        model_id="flux_inpainting",
        endpoint="fal-ai/flux-general/inpainting",
        model_type=ModelType.BASE_GENERATION,
        cost_per_image=0.03,
        avg_latency_seconds=8,
        supports_negative_prompt=True,
        supports_seed=True,
        timeout_seconds=180,
        default_params={
            "strength": 0.55,            # Sweet spot for face refinement
            "numInferenceSteps": 30,
            "guidanceScale": 7.5,
        }
    ),

    # ========== FACE SWAP MODELS ==========

    "fal_face_swap": ModelConfig(
        model_id="fal_face_swap",
        endpoint="fal-ai/face-swap",
        model_type=ModelType.FACE_SWAP,
        cost_per_image=0.015,
        avg_latency_seconds=3,
        supports_negative_prompt=False,
        supports_seed=False,
        default_params={}
    ),
}


def get_model(model_id: str) -> ModelConfig:
    """Get model configuration by ID."""
    if model_id not in MODELS:
        raise ValueError(f"Unknown model: {model_id}. Available: {list(MODELS.keys())}")
    return MODELS[model_id]


def get_models_by_type(model_type: ModelType) -> Dict[str, ModelConfig]:
    """Get all models of a specific type."""
    return {
        model_id: config
        for model_id, config in MODELS.items()
        if config.model_type == model_type
    }


def list_available_models() -> Dict[str, list]:
    """List all available models grouped by type."""
    result = {}
    for model_type in ModelType:
        models = get_models_by_type(model_type)
        result[model_type.value] = list(models.keys())
    return result

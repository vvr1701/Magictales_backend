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

    "flux_schnell": ModelConfig(
        model_id="flux_schnell",
        endpoint="fal-ai/flux/schnell",
        model_type=ModelType.BASE_GENERATION,
        cost_per_image=0.003,
        avg_latency_seconds=2,
        default_params={
            "num_inference_steps": 4,  # Schnell is optimized for fewer steps
            "guidance_scale": 3.5,
        }
    ),

    "flux_dev": ModelConfig(
        model_id="flux_dev",
        endpoint="fal-ai/flux/dev",
        model_type=ModelType.BASE_GENERATION,
        cost_per_image=0.025,
        avg_latency_seconds=5,
        default_params={
            "num_inference_steps": 28,
            "guidance_scale": 7.5,
        }
    ),

    "flux_pro": ModelConfig(
        model_id="flux_pro",
        endpoint="fal-ai/flux-pro",
        model_type=ModelType.BASE_GENERATION,
        cost_per_image=0.05,
        avg_latency_seconds=8,
        default_params={
            "num_inference_steps": 35,
            "guidance_scale": 7.5,
        }
    ),

    # ========== FACE EMBEDDING MODELS ==========

    "flux_pulid": ModelConfig(
        model_id="flux_pulid",
        endpoint="fal-ai/flux-pulid",
        model_type=ModelType.FACE_EMBEDDING,
        cost_per_image=0.045,
        avg_latency_seconds=12,
        default_params={
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
            "id_weight": 0.85,
        }
    ),

    "instant_id": ModelConfig(
        model_id="instant_id",
        endpoint="fal-ai/instantid",
        model_type=ModelType.FACE_EMBEDDING,
        cost_per_image=0.04,
        avg_latency_seconds=10,
        default_params={
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
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

# ZELAVO KIDS - AI MODEL CONFIGURATION
## Model-Agnostic Architecture for Easy Switching

**Purpose:** Define pluggable AI model system for easy switching between providers
**Version:** 3.0
**Default Models:** Flux.1 [dev] + Face Swap

---

# MODEL ARCHITECTURE OVERVIEW

## Design Principles

1. **Interface-based:** All models implement common interfaces
2. **Config-driven:** Switch models via environment variables
3. **Factory pattern:** Create model instances dynamically
4. **Fallback support:** Automatic fallback if primary model fails
5. **A/B testing ready:** Easy to test different models

---

# AVAILABLE MODELS ON FAL.AI

## Base Image Generation Models

| Model ID | Fal.ai Endpoint | Speed | Quality | Cost/Image | Style |
|----------|-----------------|-------|---------|------------|-------|
| `flux_schnell` | `fal-ai/flux/schnell` | ⚡ 1-2s | Good | $0.003 | General |
| `flux_dev` | `fal-ai/flux/dev` | 3-5s | Very Good | $0.025 | General |
| `flux_pro` | `fal-ai/flux-pro` | 5-10s | Excellent | $0.05 | General |
| `recraft_v3` | `fal-ai/recraft/v3` | 3-5s | Excellent | $0.04 | Illustration |
| `ideogram_v3` | `fal-ai/ideogram/v3` | 3-5s | Very Good | $0.03 | Text+Image |

## Face Embedding Models

| Model ID | Fal.ai Endpoint | Speed | Face Quality | Cost/Image |
|----------|-----------------|-------|--------------|------------|
| `flux_pulid` | `fal-ai/flux-pulid` | 10-15s | Very Good | $0.04-0.05 |
| `instant_id` | `fal-ai/instantid` | 8-12s | Excellent | $0.04 |

## Face Swap Models

| Model ID | Fal.ai Endpoint | Speed | Quality | Cost/Image |
|----------|-----------------|-------|---------|------------|
| `fal_face_swap` | `fal-ai/face-swap` | 2-3s | Very Good | $0.01-0.02 |

## Character Consistency Models

| Model ID | Fal.ai Endpoint | Speed | Consistency | Cost/Image |
|----------|-----------------|-------|-------------|------------|
| `flux_kontext` | `fal-ai/flux-pro/kontext` | 5-8s | Excellent | $0.04-0.08 |
| `flux_redux` | `fal-ai/flux/dev/redux` | 3-5s | Good | $0.025 |

---

# RECOMMENDED CONFIGURATIONS

## Configuration 1: Cost-Optimized (Default)

```env
# Artistic Pipeline
ARTISTIC_BASE_MODEL=flux_dev
ARTISTIC_FACE_MODEL=fal_face_swap

# Photorealistic Pipeline
REALISTIC_MODEL=flux_pulid

# Fallbacks
ARTISTIC_FALLBACK_MODEL=flux_schnell
REALISTIC_FALLBACK_MODEL=instant_id
```

**Cost per 10-page book:**
- Artistic: (10 × $0.025) + (10 × $0.015) = $0.40 = ₹33
- Photorealistic: 10 × $0.045 = $0.45 = ₹38

---

## Configuration 2: Quality-Optimized

```env
# Artistic Pipeline
ARTISTIC_BASE_MODEL=recraft_v3
ARTISTIC_FACE_MODEL=fal_face_swap

# Photorealistic Pipeline
REALISTIC_MODEL=flux_pulid

# Fallbacks
ARTISTIC_FALLBACK_MODEL=flux_dev
REALISTIC_FALLBACK_MODEL=flux_pulid
```

**Cost per 10-page book:**
- Artistic: (10 × $0.04) + (10 × $0.015) = $0.55 = ₹46
- Photorealistic: 10 × $0.045 = $0.45 = ₹38

---

## Configuration 3: Speed-Optimized (For Previews)

```env
# Use faster models for preview generation
PREVIEW_BASE_MODEL=flux_schnell
PREVIEW_FACE_MODEL=fal_face_swap

# Use better models for final generation
FINAL_BASE_MODEL=flux_dev
FINAL_FACE_MODEL=fal_face_swap
```

---

# IMPLEMENTATION

## Environment Variables

```env
# ===================
# AI MODEL CONFIGURATION
# ===================

# Provider API Key
FAL_API_KEY=your_fal_api_key

# Artistic Pipeline Models
ARTISTIC_BASE_MODEL=flux_dev
ARTISTIC_FACE_MODEL=fal_face_swap
ARTISTIC_STYLE=digital_illustration

# Photorealistic Pipeline Model
REALISTIC_MODEL=flux_pulid

# Fallback Models (used if primary fails)
FALLBACK_BASE_MODEL=flux_schnell
FALLBACK_FACE_MODEL=fal_face_swap
FALLBACK_REALISTIC_MODEL=instant_id

# Model Settings
DEFAULT_SEED=42
GUIDANCE_SCALE=7.5
NUM_INFERENCE_STEPS=30

# Feature Flags
ENABLE_MODEL_FALLBACK=true
ENABLE_MODEL_LOGGING=true
```

---

## Model Registry

**File:** `app/ai/model_registry.py`

```python
"""
Model Registry - Central configuration for all AI models.
Add new models here without changing other code.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ModelType(Enum):
    BASE_GENERATION = "base_generation"      # Text-to-image
    FACE_EMBEDDING = "face_embedding"        # Face in generation
    FACE_SWAP = "face_swap"                  # Post-process face swap
    CONSISTENCY = "consistency"              # Character consistency


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
    default_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.default_params is None:
            self.default_params = {}


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
    
    "recraft_v3": ModelConfig(
        model_id="recraft_v3",
        endpoint="fal-ai/recraft/v3/text-to-image",
        model_type=ModelType.BASE_GENERATION,
        cost_per_image=0.04,
        avg_latency_seconds=5,
        supports_negative_prompt=False,  # Recraft doesn't use negative prompts
        default_params={
            "style": "digital_illustration/hand_drawn",
        }
    ),
    
    "ideogram_v3": ModelConfig(
        model_id="ideogram_v3",
        endpoint="fal-ai/ideogram/v3/generate",
        model_type=ModelType.BASE_GENERATION,
        cost_per_image=0.03,
        avg_latency_seconds=5,
        default_params={}
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
    
    # ========== CONSISTENCY MODELS ==========
    
    "flux_kontext": ModelConfig(
        model_id="flux_kontext",
        endpoint="fal-ai/flux-pro/kontext",
        model_type=ModelType.CONSISTENCY,
        cost_per_image=0.06,
        avg_latency_seconds=8,
        default_params={
            "guidance_scale": 7.5,
        }
    ),
    
    "flux_redux": ModelConfig(
        model_id="flux_redux",
        endpoint="fal-ai/flux/dev/redux",
        model_type=ModelType.CONSISTENCY,
        cost_per_image=0.025,
        avg_latency_seconds=5,
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
```

---

## Base AI Service Interface

**File:** `app/ai/base.py`

```python
"""
Base classes and interfaces for AI services.
All model implementations must follow these interfaces.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class GenerationResult:
    """Result from any image generation."""
    success: bool
    image_url: Optional[str] = None
    error_message: Optional[str] = None
    latency_ms: int = 0
    model_used: str = ""
    cost: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseGenerationService(ABC):
    """Interface for base image generation (text-to-image)."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        width: int = 1024,
        height: int = 1024,
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


class ConsistencyService(ABC):
    """Interface for character consistency."""
    
    @abstractmethod
    async def generate_consistent(
        self,
        prompt: str,
        reference_image_url: str,
        **kwargs
    ) -> GenerationResult:
        """Generate image maintaining consistency with reference."""
        pass
```

---

## Model Factory

**File:** `app/ai/factory.py`

```python
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
from app.ai.implementations.recraft import RecraftGenerationService
from app.ai.implementations.pulid import FluxPulidService
from app.ai.implementations.instant_id import InstantIdService
from app.ai.implementations.face_swap import FalFaceSwapService


class ModelFactory:
    """Factory for creating AI model instances."""
    
    # Mapping of model IDs to implementation classes
    IMPLEMENTATIONS = {
        # Base generation
        "flux_schnell": FluxGenerationService,
        "flux_dev": FluxGenerationService,
        "flux_pro": FluxGenerationService,
        "recraft_v3": RecraftGenerationService,
        
        # Face embedding
        "flux_pulid": FluxPulidService,
        "instant_id": InstantIdService,
        
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
```

---

## Flux Implementation

**File:** `app/ai/implementations/flux.py`

```python
"""
Flux model implementations (schnell, dev, pro).
"""

import httpx
import time
from typing import Optional
from app.config import get_settings
from app.ai.base import BaseGenerationService, GenerationResult
from app.ai.model_registry import ModelConfig


class FluxGenerationService(BaseGenerationService):
    """Flux.1 text-to-image implementation."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.settings = get_settings()
        self.base_url = "https://queue.fal.run"
    
    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        width: int = 1024,
        height: int = 1365,  # 3:4 aspect ratio for storybook
        **kwargs
    ) -> GenerationResult:
        """Generate image using Flux model."""
        
        start_time = time.time()
        
        # Build request payload
        payload = {
            "prompt": prompt,
            "image_size": {
                "width": width,
                "height": height
            },
            **self.config.default_params,
            **kwargs
        }
        
        # Add optional parameters
        if negative_prompt and self.config.supports_negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        if seed is not None and self.config.supports_seed:
            payload["seed"] = seed
        
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                # Submit to queue
                response = await client.post(
                    f"{self.base_url}/{self.config.endpoint}",
                    json=payload,
                    headers={
                        "Authorization": f"Key {self.settings.fal_api_key}",
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # Extract image URL
                image_url = None
                if "images" in result and len(result["images"]) > 0:
                    image_url = result["images"][0].get("url")
                elif "image" in result:
                    image_url = result["image"].get("url")
                
                latency_ms = int((time.time() - start_time) * 1000)
                
                return GenerationResult(
                    success=True,
                    image_url=image_url,
                    latency_ms=latency_ms,
                    model_used=self.config.model_id,
                    cost=self.config.cost_per_image,
                    metadata={"seed": seed, "prompt": prompt[:100]}
                )
                
        except httpx.HTTPStatusError as e:
            return GenerationResult(
                success=False,
                error_message=f"HTTP error: {e.response.status_code} - {e.response.text}",
                model_used=self.config.model_id
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                error_message=str(e),
                model_used=self.config.model_id
            )
```

---

## Face Swap Implementation

**File:** `app/ai/implementations/face_swap.py`

```python
"""
Fal.ai Face Swap implementation.
"""

import httpx
import time
from app.config import get_settings
from app.ai.base import FaceSwapService, GenerationResult
from app.ai.model_registry import ModelConfig


class FalFaceSwapService(FaceSwapService):
    """Fal.ai face swap implementation."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.settings = get_settings()
        self.base_url = "https://queue.fal.run"
    
    async def swap_face(
        self,
        base_image_url: str,
        face_image_url: str,
        **kwargs
    ) -> GenerationResult:
        """Swap face onto base image."""
        
        start_time = time.time()
        
        payload = {
            "base_image_url": base_image_url,
            "swap_image_url": face_image_url,
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/{self.config.endpoint}",
                    json=payload,
                    headers={
                        "Authorization": f"Key {self.settings.fal_api_key}",
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                image_url = result.get("image", {}).get("url")
                latency_ms = int((time.time() - start_time) * 1000)
                
                return GenerationResult(
                    success=True,
                    image_url=image_url,
                    latency_ms=latency_ms,
                    model_used=self.config.model_id,
                    cost=self.config.cost_per_image
                )
                
        except Exception as e:
            return GenerationResult(
                success=False,
                error_message=str(e),
                model_used=self.config.model_id
            )
```

---

## Flux PuLID Implementation

**File:** `app/ai/implementations/pulid.py`

```python
"""
Flux PuLID face embedding implementation.
"""

import httpx
import time
from typing import Optional
from app.config import get_settings
from app.ai.base import FaceEmbeddingService, GenerationResult
from app.ai.model_registry import ModelConfig


class FluxPulidService(FaceEmbeddingService):
    """Flux PuLID face-embedded generation."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.settings = get_settings()
        self.base_url = "https://queue.fal.run"
    
    async def generate_with_face(
        self,
        prompt: str,
        face_image_url: str,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> GenerationResult:
        """Generate image with embedded face."""
        
        start_time = time.time()
        
        payload = {
            "prompt": prompt,
            "reference_images": [face_image_url],
            **self.config.default_params,
            **kwargs
        }
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        if seed is not None:
            payload["seed"] = seed
        
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/{self.config.endpoint}",
                    json=payload,
                    headers={
                        "Authorization": f"Key {self.settings.fal_api_key}",
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                image_url = None
                if "images" in result and len(result["images"]) > 0:
                    image_url = result["images"][0].get("url")
                
                latency_ms = int((time.time() - start_time) * 1000)
                
                return GenerationResult(
                    success=True,
                    image_url=image_url,
                    latency_ms=latency_ms,
                    model_used=self.config.model_id,
                    cost=self.config.cost_per_image,
                    metadata={"seed": seed}
                )
                
        except Exception as e:
            return GenerationResult(
                success=False,
                error_message=str(e),
                model_used=self.config.model_id
            )
```

---

## Pipeline with Model Switching

**File:** `app/ai/pipelines/artistic.py`

```python
"""
Artistic Pipeline - Base Generation + Face Swap
Supports model switching via configuration.
"""

import structlog
from typing import Optional
from app.ai.factory import ModelFactory
from app.ai.base import GenerationResult
from app.services.storage import StorageService
from app.config import get_settings

logger = structlog.get_logger()


class ArtisticPipeline:
    """
    Artistic storybook pipeline.
    
    Flow:
    1. Generate base illustration (configurable model)
    2. Swap face onto illustration (configurable model)
    3. Upload final result to storage
    """
    
    def __init__(
        self,
        base_model_id: Optional[str] = None,
        face_model_id: Optional[str] = None
    ):
        """
        Initialize pipeline with optional model overrides.
        
        Args:
            base_model_id: Override for base generation model
            face_model_id: Override for face swap model
        """
        self.settings = get_settings()
        self.storage = StorageService()
        
        # Create model instances (uses config defaults if not overridden)
        self.base_generator = ModelFactory.create_base_generator(base_model_id)
        self.face_swapper = ModelFactory.create_face_swapper(face_model_id)
        
        logger.info(
            "Artistic pipeline initialized",
            base_model=base_model_id or self.settings.artistic_base_model,
            face_model=face_model_id or self.settings.artistic_face_model
        )
    
    async def generate_page(
        self,
        prompt: str,
        child_photo_url: str,
        output_path: str,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None
    ) -> GenerationResult:
        """
        Generate a single page with artistic style.
        
        Steps:
        1. Generate base illustration
        2. Upload to temporary storage
        3. Swap face onto illustration
        4. Upload final to output path
        """
        
        # Step 1: Generate base illustration
        logger.info("Generating base illustration", prompt=prompt[:50])
        
        base_result = await self.base_generator.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed
        )
        
        if not base_result.success:
            logger.error("Base generation failed", error=base_result.error_message)
            
            # Try fallback model
            if self.settings.enable_model_fallback:
                logger.info("Trying fallback model")
                fallback_generator = ModelFactory.create_base_generator(
                    self.settings.fallback_base_model
                )
                base_result = await fallback_generator.generate(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    seed=seed
                )
                
                if not base_result.success:
                    return base_result
            else:
                return base_result
        
        # Step 2: Swap face
        logger.info("Swapping face onto illustration")
        
        swap_result = await self.face_swapper.swap_face(
            base_image_url=base_result.image_url,
            face_image_url=child_photo_url
        )
        
        if not swap_result.success:
            logger.error("Face swap failed", error=swap_result.error_message)
            return swap_result
        
        # Step 3: Upload to final storage
        logger.info("Uploading to storage", path=output_path)
        
        final_url = await self.storage.download_and_upload(
            source_url=swap_result.image_url,
            dest_path=output_path
        )
        
        # Calculate total cost
        total_cost = base_result.cost + swap_result.cost
        total_latency = base_result.latency_ms + swap_result.latency_ms
        
        return GenerationResult(
            success=True,
            image_url=final_url,
            latency_ms=total_latency,
            model_used=f"{base_result.model_used}+{swap_result.model_used}",
            cost=total_cost,
            metadata={
                "base_model": base_result.model_used,
                "face_model": swap_result.model_used,
                "seed": seed
            }
        )
```

---

## Pipeline with Model Switching (Photorealistic)

**File:** `app/ai/pipelines/realistic.py`

```python
"""
Photorealistic Pipeline - Single model with face embedding.
"""

import structlog
from typing import Optional
from app.ai.factory import ModelFactory
from app.ai.base import GenerationResult
from app.services.storage import StorageService
from app.config import get_settings

logger = structlog.get_logger()


class RealisticPipeline:
    """
    Photorealistic storybook pipeline.
    
    Flow:
    1. Generate image with face embedded (single call)
    2. Upload to storage
    """
    
    def __init__(self, model_id: Optional[str] = None):
        """
        Initialize pipeline with optional model override.
        
        Args:
            model_id: Override for face embedding model
        """
        self.settings = get_settings()
        self.storage = StorageService()
        
        # Create model instance
        self.face_embedder = ModelFactory.create_face_embedder(model_id)
        
        logger.info(
            "Realistic pipeline initialized",
            model=model_id or self.settings.realistic_model
        )
    
    async def generate_page(
        self,
        prompt: str,
        child_photo_url: str,
        output_path: str,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None
    ) -> GenerationResult:
        """Generate a single page with photorealistic style."""
        
        logger.info("Generating photorealistic page", prompt=prompt[:50])
        
        result = await self.face_embedder.generate_with_face(
            prompt=prompt,
            face_image_url=child_photo_url,
            negative_prompt=negative_prompt,
            seed=seed
        )
        
        if not result.success:
            logger.error("Generation failed", error=result.error_message)
            
            # Try fallback
            if self.settings.enable_model_fallback:
                logger.info("Trying fallback model")
                fallback_embedder = ModelFactory.create_face_embedder(
                    self.settings.fallback_realistic_model
                )
                result = await fallback_embedder.generate_with_face(
                    prompt=prompt,
                    face_image_url=child_photo_url,
                    negative_prompt=negative_prompt,
                    seed=seed
                )
                
                if not result.success:
                    return result
            else:
                return result
        
        # Upload to storage
        final_url = await self.storage.download_and_upload(
            source_url=result.image_url,
            dest_path=output_path
        )
        
        return GenerationResult(
            success=True,
            image_url=final_url,
            latency_ms=result.latency_ms,
            model_used=result.model_used,
            cost=result.cost,
            metadata=result.metadata
        )
```

---

# UPDATED PROJECT STRUCTURE

```
app/
├── ai/
│   ├── __init__.py
│   ├── base.py                      # Abstract interfaces
│   ├── model_registry.py            # Model configurations
│   ├── factory.py                   # Model factory
│   │
│   ├── implementations/
│   │   ├── __init__.py
│   │   ├── flux.py                  # Flux schnell/dev/pro
│   │   ├── recraft.py               # Recraft V3
│   │   ├── pulid.py                 # Flux PuLID
│   │   ├── instant_id.py            # InstantID
│   │   └── face_swap.py             # Fal Face Swap
│   │
│   └── pipelines/
│       ├── __init__.py
│       ├── artistic.py              # Base + Face Swap pipeline
│       └── realistic.py             # Face embedding pipeline
```

---

# SWITCHING MODELS

## Via Environment Variables

```bash
# Switch to Recraft for better illustrations
export ARTISTIC_BASE_MODEL=recraft_v3

# Switch to faster model for testing
export ARTISTIC_BASE_MODEL=flux_schnell

# Switch photorealistic model
export REALISTIC_MODEL=instant_id
```

## Via API (for A/B testing)

```python
# In your generation task
from app.ai.pipelines.artistic import ArtisticPipeline

# Use default models from config
pipeline = ArtisticPipeline()

# Or override for specific request
pipeline = ArtisticPipeline(
    base_model_id="recraft_v3",
    face_model_id="fal_face_swap"
)
```

## Via Admin Endpoint (future)

```
POST /admin/config/models
{
    "artistic_base_model": "recraft_v3",
    "realistic_model": "instant_id"
}
```

---

# COST COMPARISON (Updated)

| Configuration | Per Image | Per 10-Page Book | INR |
|---------------|-----------|------------------|-----|
| **Flux Dev + Face Swap** | $0.04 | $0.40 | ₹33 |
| **Flux Schnell + Face Swap** | $0.018 | $0.18 | ₹15 |
| **Recraft V3 + Face Swap** | $0.055 | $0.55 | ₹46 |
| **Flux PuLID (realistic)** | $0.045 | $0.45 | ₹38 |

---

# SUMMARY

## Default Configuration

| Pipeline | Base Model | Face Model | Cost/Book |
|----------|------------|------------|-----------|
| **Artistic** | Flux.1 [dev] | Fal Face Swap | ₹33 |
| **Photorealistic** | Flux PuLID | (built-in) | ₹38 |

## How to Switch Models

1. **Environment variable:** Change `ARTISTIC_BASE_MODEL` in `.env`
2. **Code override:** Pass `model_id` to pipeline constructor
3. **Add new model:** Add config to `model_registry.py`, create implementation

## Available Models

```
Base Generation: flux_schnell, flux_dev, flux_pro, recraft_v3, ideogram_v3
Face Embedding:  flux_pulid, instant_id
Face Swap:       fal_face_swap
```

---

**END OF DOCUMENT**

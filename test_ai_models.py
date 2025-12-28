#!/usr/bin/env python3
"""
Test AI model integrations with Fal.ai
"""

import asyncio
import os
from dotenv import load_dotenv
from app.ai.model_registry import MODELS, ModelType
from app.ai.factory import ModelFactory

# Load environment variables
load_dotenv()

async def test_ai_models():
    """Test various AI model integrations."""
    try:
        print("🧪 Testing AI Model Integrations with Fal.ai")
        print("=" * 50)

        # Check FAL_API_KEY
        fal_api_key = os.getenv("FAL_API_KEY")
        if not fal_api_key:
            raise ValueError("FAL_API_KEY environment variable is required")

        print(f"🔑 FAL API Key: {'*' * 20}...{fal_api_key[-10:]}")

        # Test 1: List available models
        print(f"\n📋 Available Models in Registry:")
        for model_id, config in MODELS.items():
            print(f"  - {model_id}: {config.model_type.value} (${config.cost_per_image}/image)")

        # Test 2: Flux.1 Dev Model (Base Generation)
        print(f"\n🎨 Testing Flux.1 Dev Model...")
        flux_service = ModelFactory.create_base_generator("flux_dev")

        test_prompt = "A cute 6-year-old child wizard in a purple robe with stars, standing in front of a magical castle, cartoon style, bright colors"

        try:
            print(f"📝 Prompt: {test_prompt}")
            print(f"⏱️ Generating image (this may take 30-60 seconds)...")

            result = await flux_service.generate(
                prompt=test_prompt,
                num_inference_steps=20,  # Faster for testing
                guidance_scale=7.5,
                seed=42
            )

            if result.image_url:
                print(f"✅ Flux.1 Dev generation successful!")
                print(f"📸 Image URL: {result.image_url}")
                print(f"⏱️ Generation time: {result.generation_time_ms}ms")
            else:
                print(f"❌ Flux.1 Dev generation failed - no image URL returned")

        except Exception as e:
            print(f"❌ Flux.1 Dev generation failed: {e}")

        # Test 3: PuLID Model (Face-consistent generation)
        print(f"\n👤 Testing PuLID Model...")
        try:
            pulid_service = ModelFactory.create_face_embedder("flux_pulid")

            # We need a reference image URL for PuLID - let's use a placeholder
            print(f"⚠️ PuLID requires reference image - skipping detailed test")
            print(f"✅ PuLID service initialized successfully")

        except Exception as e:
            print(f"❌ PuLID service initialization failed: {e}")

        # Test 4: Face Swap Model
        print(f"\n🔄 Testing Face Swap Model...")
        try:
            face_swap_service = ModelFactory.create_face_swapper("fal_face_swap")

            # Face swap requires two images - let's just test initialization
            print(f"⚠️ Face Swap requires two images - skipping detailed test")
            print(f"✅ Face Swap service initialized successfully")

        except Exception as e:
            print(f"❌ Face Swap service initialization failed: {e}")

        # Test 5: Artistic Pipeline
        print(f"\n🎭 Testing Artistic Pipeline...")
        try:
            from app.ai.pipelines.artistic import ArtisticPipeline

            artistic_pipeline = ArtisticPipeline()

            print(f"✅ Artistic Pipeline initialized successfully")

        except Exception as e:
            print(f"❌ Artistic Pipeline initialization failed: {e}")

        # Test 6: Realistic Pipeline
        print(f"\n📷 Testing Realistic Pipeline...")
        try:
            from app.ai.pipelines.realistic import RealisticPipeline

            realistic_pipeline = RealisticPipeline()

            print(f"✅ Realistic Pipeline initialized successfully")

        except Exception as e:
            print(f"❌ Realistic Pipeline initialization failed: {e}")

        print(f"\n🎉 AI Model Integration Testing Completed!")
        return True

    except Exception as e:
        print(f"❌ AI Model testing failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_models())
    exit(0 if success else 1)
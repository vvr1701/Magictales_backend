"""
Application settings loaded from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator
from functools import lru_cache
from typing import Self


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # App Configuration
    app_env: str = "development"
    app_debug: bool = False
    app_secret_key: str

    # Database (Supabase)
    supabase_url: str
    supabase_key: str
    database_url: str

    # Storage (Cloudflare R2)
    r2_account_id: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str = "zelavo-storage"
    r2_public_url: str
    r2_endpoint_url: str

    # AI Services
    fal_api_key: str

    # StoryGift AI Model Configuration
    realistic_model: str = "nano_banana"  # Primary model: NanoBanana with VLM analysis

    # Legacy model configurations (kept for backward compatibility)
    fallback_base_model: str = "flux_schnell"
    fallback_realistic_model: str = "nano_banana"  # Fallback uses same NanoBanana model

    # Testing Configuration
    testing_mode_enabled: bool = True  # Toggle for development vs production
    testing_mode_pages: int = 5        # Generate only 5 pages in testing mode
    production_pages: int = 10         # Full 10 pages for production

    # NanoBanana Specific Settings
    nanobana_vlm_model: str = "fal-ai/llava-next"  # Vision Language Model for face analysis
    nanobana_aspect_ratio: str = "5:4"            # StoryGift's optimized aspect ratio
    nanobana_quality: float = 0.95                # JPEG quality for PDF generation

    # Parallel Generation Settings
    parallel_batch_size: int = 3  # Number of pages to generate simultaneously (2-3 recommended)

    # Model Settings
    default_seed: int = 42
    guidance_scale: float = 7.5
    num_inference_steps: int = 30

    # Feature Flags
    enable_model_fallback: bool = True
    enable_model_logging: bool = True

    # Shopify (optional in development, required in production)
    shopify_shop_domain: str = ""
    shopify_webhook_secret: str = ""
    shopify_api_secret: str = ""  # For App Proxy HMAC verification

    # Rate Limiting
    rate_limit_previews_per_day: int = 3
    rate_limit_uploads_per_hour: int = 10

    # Email (Resend)
    resend_api_key: str = ""  # Get from resend.com
    from_email: str = "StoryGift <noreply@storygift.in>"

    # StoryGift Generation Settings
    default_theme: str = "storygift_magic_castle"  # Primary StoryGift theme
    default_style: str = "photorealistic"          # Only style supported now
    image_quality: str = "high"
    pdf_page_size: str = "10x10"                   # Square format (inches) for StoryGift layout

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @model_validator(mode="after")
    def validate_production_settings(self) -> Self:
        """Validate that required settings are present in production mode."""
        if self.app_env == "production":
            errors = []
            
            if not self.shopify_webhook_secret:
                errors.append(
                    "SHOPIFY_WEBHOOK_SECRET is required in production. "
                    "Get it from Shopify Admin > Settings > Notifications > Webhooks"
                )
            
            if not self.shopify_api_secret:
                errors.append(
                    "SHOPIFY_API_SECRET is required in production. "
                    "Get it from Shopify Partners > Your App > API credentials"
                )
            
            if not self.shopify_shop_domain:
                errors.append(
                    "SHOPIFY_SHOP_DOMAIN is required in production. "
                    "Example: your-store.myshopify.com"
                )
            
            if errors:
                raise ValueError(
                    "Production configuration errors:\n" + 
                    "\n".join(f"  - {e}" for e in errors)
                )
        
        return self


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

"""
Application settings loaded from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


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

    # AI Model Configuration
    artistic_base_model: str = "flux_dev"
    artistic_face_model: str = "fal_face_swap"
    realistic_model: str = "flux_pulid"

    # Fallback Models
    fallback_base_model: str = "flux_schnell"
    fallback_realistic_model: str = "instant_id"

    # Model Settings
    default_seed: int = 42
    guidance_scale: float = 7.5
    num_inference_steps: int = 30

    # Feature Flags
    enable_model_fallback: bool = True
    enable_model_logging: bool = True

    # Shopify
    shopify_shop_domain: str
    shopify_webhook_secret: str

    # Rate Limiting
    rate_limit_previews_per_day: int = 3
    rate_limit_uploads_per_hour: int = 10

    # Generation Settings
    preview_pages: int = 5
    full_book_pages: int = 10
    image_quality: str = "high"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


_PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(_PROJECT_ROOT / ".env", override=False)


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    backend_host: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    openai_timeout_seconds: float = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "20"))
    openai_vision_enabled: bool = os.getenv("OPENAI_VISION_ENABLED", "false").lower() == "true"
    openai_verification_enabled: bool = os.getenv("OPENAI_VERIFICATION_ENABLED", "false").lower() == "true"
    vision_frame_dir: str | None = os.getenv("VISION_FRAME_DIR")
    openai_vision_context: str = os.getenv("OPENAI_VISION_CONTEXT", "")
    product_image_search_enabled: bool = os.getenv("PRODUCT_IMAGE_SEARCH_ENABLED", "false").lower() == "true"
    product_image_search_base_url: str = os.getenv("PRODUCT_IMAGE_SEARCH_BASE_URL", "")
    product_image_search_provider: str = os.getenv("PRODUCT_IMAGE_SEARCH_PROVIDER", "search")
    product_image_search_api_key: str | None = os.getenv("PRODUCT_IMAGE_SEARCH_API_KEY") or None
    product_image_search_timeout_seconds: float = float(os.getenv("PRODUCT_IMAGE_SEARCH_TIMEOUT_SECONDS", "5"))
    product_image_cache_ttl_seconds: float = float(os.getenv("PRODUCT_IMAGE_CACHE_TTL_SECONDS", "86400"))


settings = Settings()

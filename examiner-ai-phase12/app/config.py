from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "ExaminerAI Backend"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_prefix: str = "/api"
    log_level: str = "INFO"

    supabase_url: str = Field(default="", description="Supabase project URL")
    supabase_service_role_key: str = Field(default="", description="Server-side Supabase key")

    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_generation_model: str = "gemini-3.8-flash"
    gemini_embedding_model: str = "gemini-embedding-2"
    gemini_embedding_dimension: int = Field(default=768, ge=128, le=3072)
    web_rag_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

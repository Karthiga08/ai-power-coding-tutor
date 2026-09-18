"""Production-ready configuration with enhanced security."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database configuration
    database_url: str = "postgresql+asyncpg://tutor:tutor@localhost:5432/ai_coding_tutor"

    # JWT configuration
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # AI Provider configuration
    ai_provider: str = "gemini"  # "openai" or "gemini" (gemini is cheaper)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"

    # Code runner configuration
    code_runner_image: str = "ai-tutor-runner-python:latest"
    code_runner_image_java: str = "ai-tutor-runner-java:latest"
    code_runner_image_ruby: str = "ai-tutor-runner-ruby:latest"
    code_runner_timeout_seconds: int = 10
    code_runner_memory_limit: str = "128m"
    code_runner_memory_limit_java: str = "256m"
    code_runner_cpu_quota: int = 50000  # 50% of one CPU

    # CORS configuration
    cors_origins: List[str] = ["http://localhost:5173"]

    # Application environment
    environment: str = "development"  # "development", "staging", "production"
    debug: bool = False

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def database_echo(self) -> bool:
        """Only log SQL queries in development."""
        return not self.is_production


# Load settings
settings = Settings()

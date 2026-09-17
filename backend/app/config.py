from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://tutor:tutor@localhost:5432/ai_coding_tutor"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    ai_provider: str = "openai"  # "openai" or "gemini"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"

    code_runner_image: str = "ai-tutor-runner-python:latest"
    code_runner_image_java: str = "ai-tutor-runner-java:latest"
    code_runner_image_ruby: str = "ai-tutor-runner-ruby:latest"
    code_runner_timeout_seconds: int = 10
    code_runner_memory_limit: str = "128m"
    # The JVM itself needs headroom beyond the student's program just to start up.
    code_runner_memory_limit_java: str = "256m"
    code_runner_cpu_quota: int = 50000  # 50% of one CPU (cpu_period default 100000)

    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()

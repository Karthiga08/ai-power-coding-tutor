from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import field_validator
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

    # "docker" runs submissions in local sandbox containers (needs a Docker
    # daemon — VM hosting). "judge0" sends them to a Judge0 API instead, for
    # hosts without Docker (Render, Railway, ...).
    code_runner_backend: str = "docker"

    code_runner_image: str = "ai-tutor-runner-python:latest"
    code_runner_image_java: str = "ai-tutor-runner-java:latest"
    code_runner_image_ruby: str = "ai-tutor-runner-ruby:latest"
    code_runner_timeout_seconds: int = 10
    code_runner_memory_limit: str = "128m"
    # The JVM itself needs headroom beyond the student's program just to start up.
    code_runner_memory_limit_java: str = "256m"
    code_runner_cpu_quota: int = 50000  # 50% of one CPU (cpu_period default 100000)

    # Judge0 (used when code_runner_backend == "judge0"). The default is the
    # RapidAPI-hosted Judge0 CE; point judge0_url at a self-hosted instance to
    # use X-Auth-Token auth instead.
    judge0_url: str = "https://judge0-ce.p.rapidapi.com"
    judge0_api_key: str = ""
    # Judge0 CE language ids (GET {judge0_url}/languages lists them).
    judge0_language_python: int = 92  # Python 3.11
    judge0_language_java: int = 91  # Java (JDK 17)
    judge0_language_ruby: int = 72  # Ruby 2.7 (newest on Judge0 CE)

    # Accepts a JSON list or a comma-separated string, e.g.
    # CORS_ORIGINS=https://app.vercel.app,https://example.com
    cors_origins: str | list[str] = ["http://localhost:5173"]

    @field_validator("database_url")
    @classmethod
    def _asyncpg_database_url(cls, url: str) -> str:
        # Hosted Postgres (Neon, Supabase, Render) hands out
        # postgres:// / postgresql:// URLs with libpq options like
        # sslmode=require. SQLAlchemy needs the asyncpg driver in the scheme,
        # and asyncpg rejects libpq-only params, so translate them.
        parts = urlsplit(url)
        scheme = parts.scheme
        if scheme in ("postgres", "postgresql"):
            scheme = "postgresql+asyncpg"
        if scheme != "postgresql+asyncpg":
            return url

        query = []
        for key, value in parse_qsl(parts.query):
            if key == "sslmode":
                if value != "disable":
                    query.append(("ssl", "require"))
            elif key != "channel_binding":
                query.append((key, value))
        return urlunsplit(parts._replace(scheme=scheme, query=urlencode(query)))

    @field_validator("cors_origins")
    @classmethod
    def _split_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()

from pathlib import Path
import re
import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_ROOT / ".env"
ENV_EXAMPLE_FILE = BACKEND_ROOT / ".env.example"
PLACEHOLDER_JWT_VALUES = {
    "",
    "change-me-in-production",
    "replace-this-with-a-long-random-secret",
    "auto-generate-for-local-dev",
}


def _generate_jwt_secret() -> str:
    """Generate a strong local JWT secret."""
    return secrets.token_urlsafe(64)


def _ensure_local_jwt_secret() -> None:
    """Create/update backend .env with a stable JWT secret for local development.

    The generated secret is persisted in backend/.env so tokens remain valid
    across backend restarts. Existing non-placeholder secrets are never
    overwritten. Production deployments should inject JWT_SECRET explicitly.
    """
    if not ENV_FILE.exists():
        if ENV_EXAMPLE_FILE.exists():
            ENV_FILE.write_text(ENV_EXAMPLE_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            ENV_FILE.write_text("", encoding="utf-8")

    env_text = ENV_FILE.read_text(encoding="utf-8")
    match = re.search(r"(?m)^JWT_SECRET\s*=\s*(.*)$", env_text)
    current_value = match.group(1).strip().strip('"').strip("'") if match else None

    if current_value is not None and current_value not in PLACEHOLDER_JWT_VALUES:
        return

    generated_secret = _generate_jwt_secret()
    if match:
        env_text = re.sub(
            r"(?m)^JWT_SECRET\s*=\s*.*$",
            f"JWT_SECRET={generated_secret}",
            env_text,
            count=1,
        )
    else:
        if env_text and not env_text.endswith("\n"):
            env_text += "\n"
        env_text += f"JWT_SECRET={generated_secret}\n"

    ENV_FILE.write_text(env_text, encoding="utf-8")


_ensure_local_jwt_secret()


class Settings(BaseSettings):
    app_name: str = "AI Resume Intelligence"
    environment: str = "local"
    database_url: str = "sqlite:///./resume_ai.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    ollama_base_url: str = "http://localhost:11434"
    default_ai_provider: str = "ollama"
    default_generation_model: str = "llama3.1:8b"
    default_embedding_model: str = "nomic-embed-text"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
    cors_origin_regex: str = r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+)(:\d+)?"

    model_config = SettingsConfigDict(env_file=str(ENV_FILE), extra="ignore")


settings = Settings()

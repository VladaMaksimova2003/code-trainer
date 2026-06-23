"""Application settings. Previously: src/config/settings.py"""
import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_ENV_FILE = _BACKEND_ROOT / ".env"
_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER", "").strip().lower() in {"1", "true", "yes"}
_PLACEHOLDER_VALUES = {
    "change-me",
    "changeme",
    "default",
    "password",
    "secret",
    "test",
}


class RunnersSettings:
    """Deprecated — language docker config lives in backend/languages/*.yml."""
    SETTINGS: dict = {}


class DBSettings(BaseModel):
    name: str = "code_trainer"
    host: str = "localhost"
    port: int = 5432
    user: str = "user"
    password: str = "secret"
    dialect: str = "postgresql+psycopg2"
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False

    @property
    def dsn(self) -> str:
        return f"{self.dialect}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class CheckerSettings(BaseModel):
    """Deprecated — AST uses embedding clustering, not JSON tables."""
    base_directory: str = ""


class AuthSettings(BaseModel):
    secret_key: str = "change-me"
    issuer: str = "code-trainer"
    audience: str = "code-trainer-users"
    algorithm: str = "HS256"
    access_token_ttl_minutes: int = 120
    refresh_token_ttl_days: int = 30
    login_max_attempts: int = 5
    login_window_seconds: int = 300
    login_block_seconds: int = 300


class OAuthSettings(BaseModel):
    """Social login (VK ID, Google, Yandex ID). Leave client ids empty to disable a provider."""

    frontend_url: str = "http://localhost:5173"
    redirect_base: str = "http://localhost:8000"
    vk_client_id: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    yandex_client_id: str = ""
    yandex_client_secret: str = ""

    def callback_url(self, provider: str) -> str:
        base = self.redirect_base.rstrip("/")
        return f"{base}/auth/oauth/{provider}/callback"

    def frontend_callback_url(
        self,
        *,
        access_token: str | None = None,
        refresh_token: str | None = None,
        error: str | None = None,
    ) -> str:
        from urllib.parse import quote, urlencode

        base = f"{self.frontend_url.rstrip('/')}/login/callback"
        if error:
            return f"{base}?error={quote(error)}"
        params = urlencode(
            {
                "access_token": access_token or "",
                "refresh_token": refresh_token or "",
                "token_type": "bearer",
            }
        )
        return f"{base}?{params}"

    def is_provider_configured(self, provider: str) -> bool:
        if provider == "vk":
            return bool(self.vk_client_id.strip())
        if provider == "google":
            return bool(self.google_client_id.strip() and self.google_client_secret.strip())
        if provider == "yandex":
            return bool(self.yandex_client_id.strip() and self.yandex_client_secret.strip())
        return False


class SecuritySettings(BaseModel):
    request_body_max_bytes: int = 128 * 1024
    code_max_length: int = 100_000
    execution_output_max_bytes: int = 32 * 1024


class GuestModeSettings(BaseModel):
    """Anonymous demo for thesis defense / quick try without registration."""
    enabled: bool = True
    max_checks_per_minute: int = 8
    max_concurrent_checks: int = 1


class SmtpSettings(BaseModel):
    """Outgoing mail for verification codes. One server sends to any user email."""
    host: str = "localhost"
    port: int = 1025
    user: str = ""
    password: str = ""
    from_email: str = "noreply@code-trainer.local"
    use_tls: bool = False


class RedisSettings(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0


class CurriculumSettings(BaseModel):
    """When catalog_sync_enabled is False, tasks are read/written only from DB."""

    catalog_sync_enabled: bool = False


_DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
)


class Settings(BaseSettings):
    runners: RunnersSettings = RunnersSettings()
    db: DBSettings = DBSettings()
    auth: AuthSettings = AuthSettings()
    smtp: SmtpSettings = SmtpSettings()
    redis: RedisSettings = RedisSettings()
    security: SecuritySettings = SecuritySettings()
    guest_mode: GuestModeSettings = GuestModeSettings()
    oauth: OAuthSettings = OAuthSettings()
    curriculum: CurriculumSettings = CurriculumSettings()
    cors_origins: str = Field(
        default=",".join(_DEFAULT_CORS_ORIGINS),
        validation_alias="CORS_ORIGINS",
    )

    def cors_origin_list(self) -> list[str]:
        parsed = [item.strip() for item in self.cors_origins.split(",") if item.strip()]
        return parsed or list(_DEFAULT_CORS_ORIGINS)

    @model_validator(mode="after")
    def validate_security_values(self) -> "Settings":
        if len(self.auth.secret_key.strip()) < 32:
            raise ValueError("AUTH__SECRET_KEY must be at least 32 characters long.")
        if self.auth.secret_key.strip().lower() in _PLACEHOLDER_VALUES:
            raise ValueError(
                "AUTH__SECRET_KEY must be a random secret (32+ chars), not a placeholder."
            )
        if self.db.password.strip().lower() in _PLACEHOLDER_VALUES:
            raise ValueError(
                "DB__PASSWORD must be provided explicitly and must not use placeholder values."
            )
        return self

    model_config = SettingsConfigDict(
        env_file=None if _IN_DOCKER else str(_ENV_FILE),
        env_nested_delimiter="__",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

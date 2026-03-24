from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Beisser Internal Operations Platform"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    secret_key: str = "change-me-please-123"
    access_token_expire_minutes: int = 60 * 8
    algorithm: str = "HS256"

    database_url: str = "postgresql+psycopg2://beisser:beisser@db:5432/beisser_ops"

    cors_allowed_origins: str = "http://localhost:5173"
    local_storage_dir: str = "./data_storage"
    max_attachment_size_bytes: int = 10 * 1024 * 1024
    max_import_size_bytes: int = 5 * 1024 * 1024
    allowed_attachment_extensions: str = ".pdf,.png,.jpg,.jpeg,.csv,.txt,.doc,.docx,.xlsx"

    seed_admin_email: str = "admin@beisser-internal.com"
    seed_admin_password: str = "ChangeMe123!"
    seed_admin_full_name: str = "Internal Admin"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @property
    def allowed_attachment_extensions_set(self) -> set[str]:
        return {ext.strip().lower() for ext in self.allowed_attachment_extensions.split(",") if ext.strip()}

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        lowered = value.lower()
        if lowered not in {"development", "test", "production"}:
            raise ValueError("ENVIRONMENT must be one of: development, test, production")
        return lowered

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if len(value.strip()) < 16:
            raise ValueError("SECRET_KEY must be at least 16 characters")
        return value

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR"}
        upper = value.upper()
        if upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(sorted(allowed))}")
        return upper

    @field_validator("local_storage_dir")
    @classmethod
    def validate_storage_dir(cls, value: str) -> str:
        path = Path(value)
        if path.is_absolute() or value.startswith("."):
            return value
        return f"./{value}"

    @field_validator("max_attachment_size_bytes", "max_import_size_bytes")
    @classmethod
    def validate_positive_sizes(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("File size limits must be greater than zero")
        return value

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Beisser Internal Operations Platform"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 8
    algorithm: str = "HS256"

    database_url: str = "postgresql+psycopg2://beisser:beisser@db:5432/beisser_ops"

    frontend_origin: str = "http://localhost:5173"

    seed_admin_email: str = "admin@beisser-internal.local"
    seed_admin_password: str = "ChangeMe123!"
    seed_admin_full_name: str = "Internal Admin"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    # جدا از Settings تا alembic بدون توکن هم کار کنه
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://bookzma:bookzma@localhost:5432/bookzma"


class Settings(DatabaseSettings):
    bot_token: SecretStr
    log_level: str = "INFO"

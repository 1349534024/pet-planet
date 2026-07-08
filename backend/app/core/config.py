from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "pet-planet"
    app_env: str = "local"
    debug: bool = True
    cors_origins: str = "http://localhost:3000"

    database_url: str = "sqlite:///./pet_planet.db"

    jwt_secret_key: str = "please-change-this-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 120
    jwt_refresh_token_expire_days: int = 30

    rabbitmq_url: str = "amqp://guest:guest@127.0.0.1:5672/"

    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    chroma_persist_dir: str = "./data/chroma"

    object_storage_provider: str = "local"
    object_storage_bucket: str = "pet-planet"
    object_storage_public_base_url: str = "http://127.0.0.1:8000/static"

    sms_provider: str = "mock"
    sms_access_key: str | None = None
    sms_secret_key: str | None = None

    alipay_sandbox_app_id: str | None = None
    alipay_sandbox_private_key: str | None = None
    alipay_sandbox_public_key: str | None = None
    alipay_sandbox_gateway: str = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"
    alipay_sandbox_notify_url: str | None = None
    alipay_sandbox_return_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

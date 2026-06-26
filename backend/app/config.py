import os
import json

from pydantic_settings import BaseSettings, SettingsConfigDict


APP_ENV = os.getenv("APP_ENV", "development")


class Settings(BaseSettings):
    app_name: str = "Collaborative Todo"
    app_env: str = "development"
    app_debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./todo.db"
    session_secret: str = "replace-this-secret"
    cors_allowed_origins: str = "http://localhost:5500,http://127.0.0.1:5500,http://localhost:4173"
    enable_https_redirect: bool = False
    expose_test_otp: bool = True
    otp_resend_cooldown_seconds: int = 30

    oauth_google_client_id: str = ""
    oauth_google_client_secret: str = ""
    oauth_google_redirect_uri: str = "http://localhost:5500/"

    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{APP_ENV}"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        value = self.cors_allowed_origins
        if not value:
            return []
        value = value.strip()

        # Support either comma-separated values or JSON array strings.
        if value.startswith("["):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(origin).strip() for origin in parsed if str(origin).strip()]
            except json.JSONDecodeError:
                pass

        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Collaborative Todo"
    app_env: str = "development"
    database_url: str = "sqlite+aiosqlite:///./todo.db"
    session_secret: str = "replace-this-secret"

    oauth_google_client_id: str = ""
    oauth_google_client_secret: str = ""
    oauth_google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    app_name: str = "Personal Research Lab API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/personal_lab"
    secret_key: str = "change-this-in-production"
    access_token_minutes: int = 60
    auto_create_tables: bool = True
    cors_origins: str = "http://localhost:3000"
    owner_email: str = "owner@example.com"
    owner_password: str = "change-this-password"
    media_root: str = "/app/data/media"
    storage_driver: str = "local"
    s3_endpoint_url: str | None = None
    s3_bucket: str | None = None
    s3_bucket_name: str | None = None
    s3_region: str | None = None
    s3_access_key: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_key: str | None = None
    s3_secret_access_key: str | None = None
    public_site_url: str = "http://localhost:3000"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_starttls: bool = True
    turnstile_secret_key: str | None = None
    turnstile_site_key: str | None = None
    turnstile_enabled: bool = False
    github_timeout_seconds: int = 8

    @model_validator(mode="after")
    def validate_production(self):
        if self.environment.lower() == "production":
            if len(self.secret_key) < 32 or self.secret_key == "change-this-in-production":
                raise ValueError("Production SECRET_KEY must be a long random secret")
            if self.owner_password == "change-this-password":
                raise ValueError("Production OWNER_PASSWORD must be changed")
            if self.auto_create_tables:
                raise ValueError("Set AUTO_CREATE_TABLES=false in production and run migrations explicitly")
            if self.turnstile_enabled and (not self.turnstile_secret_key or not self.turnstile_site_key):
                raise ValueError("TURNSTILE_SECRET_KEY and TURNSTILE_SITE_KEY are required when TURNSTILE_ENABLED=true")
        return self

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()

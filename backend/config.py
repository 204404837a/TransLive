from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    libretranslate_url: str = "http://localhost:5000"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    max_text_length: int = 5000
    request_timeout: float = 30.0


settings = Settings()

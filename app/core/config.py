from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Smart AI Business Assistant"
    secret_key: str = "dev-secret"
    database_url: str = "sqlite:///./data/business_assistant.db"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    chroma_path: str = "./data/chroma"
    access_token_expire_minutes: int = 1440

    model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore",
)



settings = Settings()

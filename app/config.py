from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BizAssist AI"
    secret_key: str = "change-this-secret"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/bizassist"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    chroma_path: str = "./data/chroma"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

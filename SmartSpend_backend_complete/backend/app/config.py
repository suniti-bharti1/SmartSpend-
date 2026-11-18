from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/smartspend"
    secret_key: str = "CHANGE_ME_BEFORE_DEPLOYMENT"
    access_token_expire_minutes: int = 60
    frontend_origin: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file="backend/.env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    GOOGLE_CLIENT_ID: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

 
    SPORTS_API_KEY: str
    SPORTS_API_BASE_URL: str
    REDIS_URL: str
    # -------------------------------
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
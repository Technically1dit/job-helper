import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./local.db"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8001/api/auth/google/callback"
    GMAIL_REDIRECT_URI: str = "http://localhost:8001/api/gmail/callback"
    SESSION_SECRET: str = "zP3uY-ZTqNkoP0eObFl-B4V4aE6-5ml1P0h9PZz5a2k"
    ENCRYPTION_KEY: str = "xasyiQV60_ZnbXGO0noyS03CZU0BdUN0UBV4KY6k9CE="
    SERPAPI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8001"

    class Config:
        env_file = ".env"

settings = Settings()

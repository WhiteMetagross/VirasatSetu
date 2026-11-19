import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Virasat Setu"
    DATABASE_URL: str = "sqlite:///./virasat_setu.db"
    SECRET_KEY: str = "virasat-setu-super-secret-key-college-prototype-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALLOWED_ORIGINS: str = "http://127.0.0.1:5173,http://127.0.0.1:3000,http://127.0.0.1:8000,*"
    UPLOAD_DIR: str = "/tmp/uploads" if (os.environ.get("VERCEL") or not os.access(".", os.W_OK)) else "./uploads"
    ENABLE_MOCK_EMAIL: bool = True
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@virasatsetu.gov.in"

    # Supabase Cloud Configuration
    SUPABASE_PROJECT_ID: str = "elmvmptsxmkzcowwnmlk"
    SUPABASE_REGION: str = "ap-southeast-2"
    SUPABASE_URL: str = "https://elmvmptsxmkzcowwnmlk.supabase.co"
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

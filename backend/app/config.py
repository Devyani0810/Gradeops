from functools import lru_cache
from typing import Literal
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_NAME: str = "GradeOps"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "temporary_secret_key_development_only_gradeops_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = "postgresql+asyncpg://postgres:secretpassword@localhost:5432/gradeops"
    DATABASE_URL_SYNC: str = "postgresql://postgres:secretpassword@localhost:5432/gradeops"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    STORAGE_BACKEND: Literal["local", "s3"] = "local"
    LOCAL_UPLOAD_DIR: str = "./uploads"
    LLM_MODEL: str = "gpt-4o"
    GROQ_API_KEY: str = ""
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 1024
    PLAGIARISM_THRESHOLD: float = 0.85
    OCR_SERVICE_URL: str = "http://localhost:8001"
    SENTRY_DSN: str | None = None
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str): return [i.strip() for i in v.split(",")]
        return v
    @property
    def is_production(self) -> bool: return self.APP_ENV == "production"

@lru_cache
def get_settings() -> Settings: return Settings()
settings = get_settings()

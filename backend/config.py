from functools import lru_cache
from pydantic import BaseSettings, AnyHttpUrl, validator
from typing import List, Optional


class Settings(BaseSettings):
    app_name: str = "ACCA MCQ API"
    environment: str = "development"

    database_url: str
    allowed_origins: List[AnyHttpUrl] = []

    hf_api_key: Optional[str] = None
    hf_model_endpoint: str = "https://api-inference.huggingface.co/models/google/flan-t5-small"

    max_upload_size_mb: int = 15
    explanation_batch_limit: int = 50
    ocr_dpi: int = 220

    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False

    @validator("allowed_origins", pre=True)
    def split_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache()
def get_settings() -> Settings:
    return Settings()

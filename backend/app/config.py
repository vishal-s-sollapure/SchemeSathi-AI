from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SchemeSathi AI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    # Optional regex to match specific preview deployments (e.g. project-specific preview domains)
    # Never defaults to unrestricted wildcards like ".*\.vercel\.app"
    CORS_ORIGIN_REGEX: Union[str, None] = None

    # Database
    DATABASE_URL: str = "sqlite:///./schemesathi.db"
    
    # Document Intelligence & Uploads
    UPLOAD_DIR: str = "app/uploads"
    MAX_UPLOAD_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    ALLOWED_EXTENSIONS: Union[List[str], str] = [".pdf"]
    
    # Supported Languages
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: Union[List[str], str] = ["en", "kn", "hi"]

    # AI & RAG Configuration
    GEMINI_API_KEY: Union[str, None] = None
    LLM_PROVIDER: str = "auto"  # auto, gemini, grounded_engine
    LLM_MODEL: str = "gemini-1.5-flash"
    RAG_TOP_K: int = 4
    RAG_MIN_SIMILARITY: float = 0.25
    EMBEDDING_DIM: int = 128

    @field_validator("BACKEND_CORS_ORIGINS", "SUPPORTED_LANGUAGES", "ALLOWED_EXTENSIONS", mode="after")
    @classmethod
    def parse_string_or_list(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v: Union[bool, str]) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            normalized = v.strip().lower()
            if normalized in ("release", "false", "0", "prod", "production"):
                return False
            if normalized in ("debug", "true", "1", "dev", "development"):
                return True
        return bool(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

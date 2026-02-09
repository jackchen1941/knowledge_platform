"""
Application Configuration

This module handles all configuration settings for the knowledge management platform,
including database connections, security settings, and external service configurations.
"""

import secrets
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "Knowledge Management Platform"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 8
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./knowledge_platform.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_ECHO: bool = False
    DATABASE_SSL_MODE: Optional[str] = None  # require, prefer, disable
    DATABASE_SSL_CERT: Optional[str] = None
    DATABASE_SSL_KEY: Optional[str] = None
    DATABASE_SSL_CA: Optional[str] = None
    
    # MongoDB (optional document store)
    MONGODB_URL: Optional[str] = None
    MONGODB_DATABASE: str = "knowledge_platform"
    
    # Database Connection Security
    DATABASE_CONNECTION_TIMEOUT: int = 30
    DATABASE_QUERY_TIMEOUT: int = 60
    DATABASE_MAX_CONNECTIONS: int = 20
    DATABASE_MIN_CONNECTIONS: int = 1
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # 5 minutes
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX_PREFIX: str = "kmp"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf", "text/plain", "text/markdown",
        "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "audio/mpeg", "audio/wav", "video/mp4", "video/webm"
    ]
    
    # Email (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # External Platform APIs
    CSDN_API_KEY: Optional[str] = None
    NOTION_API_KEY: Optional[str] = None
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Security Headers
    SECURITY_HEADERS: Dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from environment variable."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: str) -> str:
        """Validate and adjust database URL format."""
        if v.startswith("sqlite://"):
            # Convert to async SQLite
            return v.replace("sqlite://", "sqlite+aiosqlite://")
        elif v.startswith("postgresql://"):
            # Convert to async PostgreSQL
            return v.replace("postgresql://", "postgresql+asyncpg://")
        elif v.startswith("mysql://"):
            # Convert to async MySQL
            return v.replace("mysql://", "mysql+aiomysql://")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
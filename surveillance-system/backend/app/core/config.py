"""
Application configuration using Pydantic Settings.
Loads configuration from environment variables.
"""

from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Surveillance System API"
    DEBUG: bool = Field(default=False, env="DEBUG")
    SECRET_KEY: str = Field(default="change-me-in-production", env="SECRET_KEY")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://surveillance:surveillance@localhost:5432/surveillance_db",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_POOL_SIZE: int = Field(default=50, env="REDIS_POOL_SIZE")
    
    # MinIO
    MINIO_ENDPOINT: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", env="MINIO_SECRET_KEY")
    MINIO_SECURE: bool = Field(default=False, env="MINIO_SECURE")
    MINIO_BUCKET_LIVE: str = "surveillance-live"
    MINIO_BUCKET_SUBJECTS: str = "surveillance-subjects"
    MINIO_BUCKET_ARCHIVE: str = "surveillance-archive"
    MINIO_BUCKET_TEMP: str = "surveillance-temp"
    
    # Authentication
    JWT_SECRET: str = Field(default="jwt-secret-change-me", env="JWT_SECRET")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    JWT_REFRESH_EXPIRATION_DAYS: int = Field(default=7, env="JWT_REFRESH_EXPIRATION_DAYS")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # AI/ML Settings
    DETECTION_MODEL_PATH: str = Field(
        default="/models/yolov8n-face.onnx",
        env="DETECTION_MODEL_PATH"
    )
    RECOGNITION_MODEL_PATH: str = Field(
        default="/models/arcface_r50.onnx",
        env="RECOGNITION_MODEL_PATH"
    )
    DETECTION_THRESHOLD: float = Field(default=0.7, env="DETECTION_THRESHOLD")
    RECOGNITION_THRESHOLD: float = Field(default=0.6, env="RECOGNITION_THRESHOLD")
    EMBEDDING_DIMENSION: int = 512
    
    # Stream Processing
    STREAM_FRAME_SAMPLE_RATE: int = Field(default=2, env="STREAM_FRAME_SAMPLE_RATE")
    STREAM_RECONNECT_ATTEMPTS: int = Field(default=5, env="STREAM_RECONNECT_ATTEMPTS")
    STREAM_RECONNECT_DELAY: int = Field(default=5, env="STREAM_RECONNECT_DELAY")
    
    # GDPR/Compliance
    GDPR_DEFAULT_RETENTION_DAYS: int = Field(default=90, env="GDPR_DEFAULT_RETENTION_DAYS")
    AUDIT_LOG_RETENTION_DAYS: int = Field(default=365, env="AUDIT_LOG_RETENTION_DAYS")
    
    # Monitoring
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = Field(default=30, env="WS_HEARTBEAT_INTERVAL")
    WS_MAX_CONNECTIONS: int = Field(default=1000, env="WS_MAX_CONNECTIONS")
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()

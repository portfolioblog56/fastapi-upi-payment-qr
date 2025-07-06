from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with production defaults."""
    
    # Environment
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    HOST: str = Field(default="0.0.0.0", description="Host to bind to")
    PORT: int = Field(default=8000, description="Port to bind to")
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = Field(
        default=["*"],  # Allow all origins in production, configure as needed
        description="Allowed CORS origins"
    )
    
    # QR Code Configuration
    QR_CODE_MAX_SIZE: int = Field(default=1000, description="Maximum QR code size")
    QR_CODE_MIN_SIZE: int = Field(default=100, description="Minimum QR code size")
    QR_CODE_DEFAULT_SIZE: int = Field(default=300, description="Default QR code size")
    
    # File Upload Configuration
    MAX_LOGO_SIZE_MB: int = Field(default=5, description="Maximum logo file size in MB")
    ALLOWED_LOGO_EXTENSIONS: List[str] = Field(
        default=[".png", ".jpg", ".jpeg", ".gif"],
        description="Allowed logo file extensions"
    )
    
    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Rate limit requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

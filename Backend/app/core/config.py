"""
Application configuration using Pydantic Settings
"""
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(default="Sentinel Health API", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    
    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    
    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        alias="CORS_ORIGINS"
    )
    
    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins"""
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    
    # PostgreSQL
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="sentinel_health", alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres123", alias="POSTGRES_PASSWORD")
    postgres_pool_size: int = Field(default=5, alias="POSTGRES_POOL_SIZE")
    postgres_max_overflow: int = Field(default=10, alias="POSTGRES_MAX_OVERFLOW")
    
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    # MongoDB
    mongodb_url: Optional[str] = Field(default=None, alias="MONGODB_URL")
    mongodb_host: str = Field(default="localhost", alias="MONGODB_HOST")
    mongodb_port: int = Field(default=27017, alias="MONGODB_PORT")
    mongodb_db: str = Field(default="sentinel_health", alias="MONGODB_DB")
    mongodb_user: Optional[str] = Field(default=None, alias="MONGODB_USER")
    mongodb_password: Optional[str] = Field(default=None, alias="MONGODB_PASSWORD")
    mongodb_max_pool_size: int = Field(default=10, alias="MONGODB_MAX_POOL_SIZE")
    
    def get_mongodb_url(self) -> str:
        """
        Construct MongoDB connection URL
        Priority: MONGODB_URL env var > constructed from components
        """
        # If direct URL is provided, use it
        if self.mongodb_url:
            return self.mongodb_url
        
        # Otherwise construct from components
        # Only include auth if both username and password are provided and non-empty
        if self.mongodb_user and self.mongodb_password and self.mongodb_user.strip() and self.mongodb_password.strip():
            return (
                f"mongodb://{self.mongodb_user}:{self.mongodb_password}"
                f"@{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}"
            )
        
        # No authentication
        return f"mongodb://{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}"
    
    # Redis
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    
    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # Authentication
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        alias="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    
    # Feature Flags
    enable_swagger_ui: bool = Field(default=True, alias="ENABLE_SWAGGER_UI")
    enable_redoc: bool = Field(default=True, alias="ENABLE_REDOC")
    
    # AI/LLM
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    langsmith_api_key: Optional[str] = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(
        default="sentinel-health",
        alias="LANGSMITH_PROJECT"
    )


# Global settings instance
settings = Settings()

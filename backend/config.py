"""
Configuration management for the workout optimizer.
Uses pydantic-settings for robust environment variable loading and validation.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Core App Settings
    APP_NAME: str = "Workout Optimizer"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # LLM Settings
    AGENT_MODEL: str = "openai:gpt-4o-mini" # Default model
    
    # API Keys (Required)
    OPENAI_API_KEY: str = Field(..., description="OpenAI API Key")
    HEVY_API_KEY: str = Field(..., description="Hevy API Key")
    DATABASE_URL: str = Field(..., description="Database Connection URL")
    
    # API Keys (Optional)
    ANTHROPIC_API_KEY: Optional[str] = Field(None, description="Anthropic API Key")
    GOOGLE_API_KEY: Optional[str] = Field(None, description="Google Gemini API Key")
    
    # Observability
    LOGFIRE_TOKEN: Optional[str] = Field(None, description="Logfire Token")
    
    # External Services
    HEVY_BASE_URL: str = "https://api.hevyapp.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True, # We use UPPERCASE attributes
        extra="ignore" # Ignore extra env vars
    )

# Create global settings instance
# This replaces the old 'config' object
settings = Settings()

# Alias for backward compatibility if needed, but 'settings' is preferred
config = settings
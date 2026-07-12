"""AI Marketing Studio PRO - Configuration System Package.

Provides a thread-safe, singleton, validated configuration management engine with support for
environment variables, cascade auditing, file persistence (JSON/YAML), and automatic workspace directory provisioning.
"""

from src.config.exceptions import (
    ConfigException,
    ConfigLoadError,
    ConfigSaveError,
    ConfigValidationError,
    ConfigFileNotFoundError,
)
from src.config.validators import ConfigValidators
from src.config.config_models import (
    SystemConfig,
    ApplicationConfig,
    GeminiConfig,
    FishSpeechConfig,
    FFmpegConfig,
    VideoConfig,
    AudioConfig,
    DatabaseConfig,
    AssetsConfig,
)
from src.config.config_manager import ConfigManager

__all__ = [
    # Manager
    "ConfigManager",
    
    # Schemas
    "SystemConfig",
    "ApplicationConfig",
    "GeminiConfig",
    "FishSpeechConfig",
    "FFmpegConfig",
    "VideoConfig",
    "AudioConfig",
    "DatabaseConfig",
    "AssetsConfig",
    
    # Validators
    "ConfigValidators",
    
    # Exceptions
    "ConfigException",
    "ConfigLoadError",
    "ConfigSaveError",
    "ConfigValidationError",
    "ConfigFileNotFoundError",
]

"""Custom exception classes for the AI Marketing Studio PRO Configuration System.

This module defines the hierarchy of exceptions raised by the configuration manager,
validators, and data models to allow precise error handling across the application.
"""

class ConfigException(Exception):
    """Base exception for all configuration system errors."""
    pass


class ConfigLoadError(ConfigException):
    """Raised when the configuration cannot be loaded, parsed, or deserialized."""
    pass


class ConfigValidationError(ConfigException):
    """Raised when configuration values fail schema-level or business-level validation."""
    pass


class ConfigSaveError(ConfigException):
    """Raised when configuration state fails to serialize or write to disk."""
    pass


class ConfigFileNotFoundError(ConfigException):
    """Raised when a required configuration file is missing and cannot be created."""
    pass

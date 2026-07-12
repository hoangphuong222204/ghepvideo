"""Central logging package for AIMS Pro.

Exports LoggerManager, LoggerFactory, LoggerConfig, decorators, and custom exceptions.
"""

import logging
from typing import Optional

from src.logger.log_config import LoggerConfig
from src.logger.logger_manager import LoggerManager
from src.logger.logger_factory import LoggerFactory
from src.logger.performance_logger import PerformanceTimer
from src.logger.decorators import log_execution_time
from src.logger.exceptions import (
    LoggerException,
    LoggerConfigurationError,
    LogDirectoryCreationError,
)

# Convenient shorthand accessors
def get_logger(name: str) -> logging.Logger:
    """Convenient helper to retrieve a configured system logger immediately.

    Args:
        name: Name of target logger module (e.g. "gemini", "database").

    Returns:
        The configured Python Logger.
    """
    return LoggerManager().get_logger(name)


def log_exception(logger_name: str, message: str, exception: Exception) -> None:
    """Convenient helper to log exceptions cleanly with standard traces.

    Args:
        logger_name: Name of target logger (e.g. "ui", "database").
        message: Explicit context message.
        exception: The raw Exception object.
    """
    LoggerManager().log_exception(logger_name, message, exception)


__all__ = [
    "LoggerConfig",
    "LoggerManager",
    "LoggerFactory",
    "PerformanceTimer",
    "log_execution_time",
    "LoggerException",
    "LoggerConfigurationError",
    "LogDirectoryCreationError",
    "get_logger",
    "log_exception",
]

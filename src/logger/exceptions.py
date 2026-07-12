"""Custom exceptions for the AIMS Pro Logger System."""

class LoggerException(Exception):
    """Base exception for all logging-related errors in AIMS Pro."""
    pass


class LoggerConfigurationError(LoggerException):
    """Raised when there is an error in the logging configuration."""
    pass


class LogDirectoryCreationError(LoggerException):
    """Raised when the logging directory cannot be created."""
    pass

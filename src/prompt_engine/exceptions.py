"""Custom exception classes for the Prompt Engine (Module 06)."""


class PromptEngineError(Exception):
    """Base exception class for all errors originating in the Prompt Engine."""
    pass


class ValidationError(PromptEngineError):
    """Raised when prompt validation fails (e.g., missing variables, invalid format)."""
    pass


class TemplateNotFoundError(PromptEngineError):
    """Raised when a requested prompt template cannot be located in storage or repository."""
    pass


class RenderError(PromptEngineError):
    """Raised when template compilation or rendering fails due to syntax or variable issues."""
    pass


class ResolveError(PromptEngineError):
    """Raised when a variable cannot be resolved or is missing required fallbacks."""
    pass


class VersionError(PromptEngineError):
    """Raised when versioning operations (e.g., conflict, invalid semver) fail."""
    pass


class SerializationError(PromptEngineError):
    """Raised when exporting or importing templates fails."""
    pass


class StorageError(PromptEngineError):
    """Raised when reading or writing templates to physical or cloud databases fails."""
    pass


class OptimizerError(PromptEngineError):
    """Raised when prompt optimization or compression algorithms fail."""
    pass


class ConfigError(PromptEngineError):
    """Raised when template/prompt engine configurations are mismatched or invalid."""
    pass

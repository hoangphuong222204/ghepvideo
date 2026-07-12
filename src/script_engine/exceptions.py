"""Custom exceptions for the AI Script Engine module."""

class ScriptEngineError(Exception):
    """Base exception for all AI Script Engine operations."""
    pass


class ValidationError(ScriptEngineError):
    """Raised when request or config validation fails."""
    pass


class PolicyError(ScriptEngineError):
    """Raised when content violates platform policy and cannot be resolved."""
    pass


class JSONParseError(ScriptEngineError):
    """Raised when JSON parsing or structure extraction fails."""
    pass


class QualityError(ScriptEngineError):
    """Raised when script quality falls below defined thresholds."""
    pass


class AnalysisError(ScriptEngineError):
    """Raised when product or audience analysis fails."""
    pass


class GenerationError(ScriptEngineError):
    """Raised when script generation fails due to prompt or LLM issues."""
    pass


class FormattingError(JSONParseError):
    """Raised when JSON formatting or parsing fails."""
    pass


class PolicyViolationError(PolicyError):
    """Raised when generated content violates safety or policy guidelines."""
    pass

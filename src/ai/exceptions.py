"""Custom exceptions for the AI client module."""

class AIError(Exception):
    """Base exception for all AI/Gemini client operations."""
    pass


class ConfigurationError(AIError):
    """Raised when there is a configuration-related issue (missing API key, invalid model, etc.)."""
    pass


class ValidationError(AIError):
    """Raised when request validation fails (e.g., parameter range validation)."""
    pass


class ProviderError(AIError):
    """Base class for errors returned by the AI provider."""
    pass


class APIError(ProviderError):
    """Raised when the AI provider returns a non-200 HTTP status code."""
    def __init__(self, message: str, status_code: int = 500, response_text: str = "") -> None:
        super().__init__(f"API Error ({status_code}): {message}")
        self.status_code = status_code
        self.response_text = response_text


class NetworkError(ProviderError):
    """Raised when network/timeout issues occur during API communication."""
    pass


class QuotaError(ProviderError):
    """Raised when the provider's rate limits or quotas are exceeded."""
    pass


class RateLimitError(QuotaError):
    """Raised when rate limiter blocks a request locally."""
    pass


class SafetyError(AIError):
    """Raised when the prompt or response is blocked by safety filters."""
    pass


class ParseError(AIError):
    """Raised when response parsing or structure validation fails."""
    pass


class TokenLimitError(ValidationError):
    """Raised when a request exceeds the model's max token length."""
    pass

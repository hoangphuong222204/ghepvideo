"""Exception hierarchy for Module 14: FastAPI Service.

This module defines all custom exceptions raised within the API, router,
and middleware layers of AI Marketing Studio PRO, covering routing, validation,
authentication, authorization, rate-limiting, and serialization failures.
"""

class APIServiceError(Exception):
    """Base exception class for all errors originating in the FastAPI Service (Module 14)."""
    pass


class APIConfigurationError(APIServiceError):
    """Raised when there is an invalid configuration for the API or server setup."""
    pass


class APIInitializationError(APIServiceError):
    """Raised when API initialization, router mounting, or ASGI setup fails."""
    pass


class DependencyResolutionError(APIServiceError):
    """Raised when resolving API router dependencies fails."""
    pass


class InvalidAPIRequestError(APIServiceError):
    """Raised when an API request is malformed or invalid."""
    pass


class RequestValidationError(InvalidAPIRequestError):
    """Raised when request payload or parameters fail Pydantic or manual validation."""
    pass


class AuthenticationError(APIServiceError):
    """Base exception for all API-level authentication failures."""
    pass


class MissingCredentialsError(AuthenticationError):
    """Raised when required authentication credentials are not provided."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when provided authentication credentials are invalid."""
    pass


class ExpiredCredentialsError(AuthenticationError):
    """Raised when provided authentication credentials have expired."""
    pass


class AuthorizationError(APIServiceError):
    """Base exception for all API-level authorization and permission failures."""
    pass


class ForbiddenOperationError(AuthorizationError):
    """Raised when an authenticated principal lacks permission for the requested operation."""
    pass


class RateLimitExceededError(APIServiceError):
    """Raised when client request frequency exceeds configured rate limits."""
    pass


class ResourceNotFoundError(APIServiceError):
    """Raised when a requested resource is not found."""
    pass


class ResourceConflictError(APIServiceError):
    """Raised when a request conflicts with current server state (e.g. project lock)."""
    pass


class IdempotencyConflictError(APIServiceError):
    """Raised when an idempotent request has a conflict (e.g. key reuse with different parameters)."""
    pass


class InvalidIdempotencyKeyError(APIServiceError):
    """Raised when a supplied idempotency key is malformed or invalid."""
    pass


class RequestTimeoutError(APIServiceError):
    """Raised when a request exceeds its maximum allowed execution time."""
    pass


class ServiceUnavailableError(APIServiceError):
    """Raised when the API or a required service is temporarily unavailable."""
    pass


class DownstreamServiceError(APIServiceError):
    """Raised when an error occurs in an underlying domain module or external API."""
    pass


class ProjectAPIError(APIServiceError):
    """Raised when project operations or project-management endpoints fail."""
    pass


class AssetAPIError(APIServiceError):
    """Raised when asset operations, uploads, or file-staging endpoints fail."""
    pass


class WorkflowAPIError(APIServiceError):
    """Raised when workflow execution or orchestration endpoints fail."""
    pass


class WorkflowEventError(APIServiceError):
    """Raised when subscribing or publishing to workflow events fails."""
    pass


class ProgressStreamError(APIServiceError):
    """Raised when delivering Server-Sent Events or WebSocket stream progress fails."""
    pass


class ResponseSerializationError(APIServiceError):
    """Raised when serializing responses into HTTP payloads fails."""
    pass


class PaginationError(APIServiceError):
    """Raised when page-number or offset parameters fail pagination verification."""
    pass


class MiddlewareError(APIServiceError):
    """Raised when execution of middleware layers encounters errors."""
    pass


class OpenAPIConfigurationError(APIServiceError):
    """Raised when configuring OpenAPI schemas, descriptions, or metadata fails."""
    pass


class ShutdownError(APIServiceError):
    """Raised when graceful server shutdown, connection draining, or task flushing fails on exit."""
    pass

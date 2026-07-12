"""Structural typing protocols and dependency interfaces for Module 14: FastAPI Service.

This module defines all structural interface protocols used for dependency injection,
decoupling the FastAPI web layer from concrete service implementations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Union, runtime_checkable
from pathlib import Path


@runtime_checkable
class LoggerProtocol(Protocol):
    """Protocol for loggers integrated with Module 14."""

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an informational message."""
        ...

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        ...

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        ...

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a debugging message."""
        ...


@runtime_checkable
class ClockProtocol(Protocol):
    """Protocol for retrieving timezone-aware datetime objects."""

    def now(self) -> datetime:
        """Return the current timezone-aware datetime in UTC."""
        ...


@runtime_checkable
class IdProviderProtocol(Protocol):
    """Protocol for generating unique, stable identifiers."""

    def generate_id(self, prefix: Optional[str] = None) -> str:
        """Generate a random unique identifier with an optional prefix."""
        ...


@runtime_checkable
class IdempotencyStoreProtocol(Protocol):
    """Protocol for validating idempotency keys and storing responses."""

    def get_response(self, key: str, scope: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored response matching key and scope, if available."""
        ...

    def store_response(self, key: str, scope: str, response_data: Dict[str, Any]) -> None:
        """Persist a response mapping for key and scope."""
        ...

    def remove_key(self, key: str, scope: str) -> None:
        """Manually clear a stored idempotency record."""
        ...


@runtime_checkable
class RateLimiterBackendProtocol(Protocol):
    """Protocol for managing client rate limits across operations."""

    def check_rate_limit(self, client_id: str, limit_category: str, max_requests: int, window_seconds: float) -> tuple[bool, float]:
        """Check if request exceeds rate bounds.

        Returns:
            A tuple of (is_limited, retry_after_seconds).
        """
        ...


@runtime_checkable
class ProgressBrokerProtocol(Protocol):
    """Protocol for routing real-time workflow events to active SSE/WS connections."""

    def publish_event(self, workflow_id: str, event_data: Dict[str, Any]) -> None:
        """Distribute a workflow event to all active matching subscribers."""
        ...

    async def subscribe(self, workflow_id: str, client_id: str) -> Any:
        """Initialize a subscription channel for a specific workflow."""
        ...

    def unsubscribe(self, workflow_id: str, client_id: str) -> None:
        """Clean up and tear down a client's subscription channel."""
        ...


@runtime_checkable
class AuthenticationProviderProtocol(Protocol):
    """Protocol for parsing and validating client credentials."""

    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate provided key, returning matching principal metadata if valid."""
        ...

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate an external bearer token, returning principal metadata."""
        ...


@runtime_checkable
class AuthorizationProviderProtocol(Protocol):
    """Protocol for enforcing role and permission assignments."""

    def has_permission(self, principal: Dict[str, Any], required_permission: str) -> bool:
        """Assert whether the given principal carries the required permission."""
        ...

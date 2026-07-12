"""Configuration settings and validation models for Module 14: FastAPI Service.

This module defines configuration classes using Pydantic v2 to validate
network host bindings, security parameters, and limits for the API process.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from src.api.api_models import AuthenticationScheme


class APIConfig(BaseModel):
    """Configuration schema for the Module 14 FastAPI Service."""

    host: str = Field(
        default="127.0.0.1",
        description="The host network interface address to bind to. Default is localhost.",
    )
    port: int = Field(
        default=3000,
        description="The port number to expose the HTTP server on.",
    )
    debug: bool = Field(
        default=False,
        description="Enable development-friendly debug stack traces and auto-reload.",
    )
    api_version: str = Field(
        default="v1",
        description="The version prefix to mount on all routes, e.g. /api/v1.",
    )
    auth_mode: AuthenticationScheme = Field(
        default=AuthenticationScheme.NONE,
        description="The active authentication mechanism: API_KEY, BEARER, or NONE.",
    )
    api_key_secret: Optional[str] = Field(
        default=None,
        description="Secure constant-time matched key for API_KEY mode authentication.",
    )
    cors_allowed_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        description="List of safe browser origins permitted to bypass CORS security policies.",
    )
    max_request_size_bytes: int = Field(
        default=10 * 1024 * 1024,
        gt=0,
        description="Maximum accepted size of a standard JSON request body in bytes (default 10MB).",
    )
    max_upload_size_bytes: int = Field(
        default=100 * 1024 * 1024,
        gt=0,
        description="Maximum accepted size of a multipart/form-data upload in bytes (default 100MB).",
    )
    rate_limiting_enabled: bool = Field(
        default=True,
        description="Enable local rate limiting for desktop or multi-user security.",
    )
    idempotency_enabled: bool = Field(
        default=True,
        description="Enable idempotency verification via X-Idempotency-Key headers.",
    )
    docs_enabled: bool = Field(
        default=True,
        description="Expose Swagger documentation UI at /docs and OpenAPI schemas.",
    )

    @field_validator("port")
    @classmethod
    def validate_port_range(cls, v: int) -> int:
        """Validate port is within standard ephemeral boundaries."""
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535 inclusive.")
        return v

    @field_validator("host")
    @classmethod
    def validate_host_ip(cls, v: str) -> str:
        """Enforce host formatting constraints."""
        v = v.strip()
        if not v:
            raise ValueError("Network bind host interface cannot be blank.")
        return v

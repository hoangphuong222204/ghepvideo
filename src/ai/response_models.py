"""Standardized dataclass representing the unified AI response payload."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class TokenUsage:
    """Standardized representation of token usage metrics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class AIResponse:
    """Unified response object returned by all AI providers."""
    text: str
    model_name: str
    usage: TokenUsage = field(default_factory=TokenUsage)
    cached: bool = False
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

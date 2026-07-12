"""Dataclass definitions for AI requests, parameters, and payloads."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Message:
    """Represents a single chat or system message."""
    role: str  # 'system', 'user', or 'model'
    content: str


@dataclass
class GenerationConfig:
    """Configuration options for content generation."""
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    max_output_tokens: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    json_mode: bool = False
    response_schema: Optional[Dict[str, Any]] = None  # Expected JSON schema for structured outputs
    system_instruction: Optional[str] = None


@dataclass
class AIRequest:
    """Consolidated payload representing a generation or chat request."""
    prompt: Optional[str] = None
    messages: List[Message] = field(default_factory=list)
    model_name: Optional[str] = None
    config: GenerationConfig = field(default_factory=GenerationConfig)
    use_cache: bool = True
    cache_ttl: Optional[int] = None  # None uses system default
    safety_settings: Optional[Dict[str, str]] = None  # Category -> Threshold mapping

    def __post_init__(self) -> None:
        """Helper to ensure prompt or messages is specified."""
        if not self.prompt and not self.messages:
            raise ValueError("Either prompt or messages must be specified in AIRequest.")

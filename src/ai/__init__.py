"""AI and Gemini Client module initialization for AI Marketing Studio PRO."""

from src.ai.exceptions import (
    AIError,
    ConfigurationError,
    ValidationError,
    ProviderError,
    APIError,
    NetworkError,
    QuotaError,
    RateLimitError,
    SafetyError,
    ParseError,
    TokenLimitError,
)
from src.ai.request_models import Message, GenerationConfig, AIRequest
from src.ai.response_models import TokenUsage, AIResponse
from src.ai.prompt_templates import (
    VERTICAL_VIDEO_SCRIPT_TEMPLATE,
    PRODUCT_PITCH_COPY_TEMPLATE,
    VOICE_HOOK_GENERATOR_TEMPLATE,
)
from src.ai.prompt_builder import PromptBuilder
from src.ai.response_parser import ResponseParser
from src.ai.tokenizer import Tokenizer
from src.ai.cache_manager import CacheManager
from src.ai.retry import retry, retry_async
from src.ai.rate_limiter import RateLimiter, RateLimiterManager
from src.ai.safety import SafetyConfig
from src.ai.validators import RequestValidator
from src.ai.provider_base import AIProviderBase
from src.ai.gemini_client import GeminiClient
from src.ai.provider_factory import ProviderFactory
from src.ai.ai_manager import AIManager

__all__ = [
    # Exceptions
    "AIError",
    "ConfigurationError",
    "ValidationError",
    "ProviderError",
    "APIError",
    "NetworkError",
    "QuotaError",
    "RateLimitError",
    "SafetyError",
    "ParseError",
    "TokenLimitError",
    
    # Models
    "Message",
    "GenerationConfig",
    "AIRequest",
    "TokenUsage",
    "AIResponse",
    
    # Templates & Prompting
    "VERTICAL_VIDEO_SCRIPT_TEMPLATE",
    "PRODUCT_PITCH_COPY_TEMPLATE",
    "VOICE_HOOK_GENERATOR_TEMPLATE",
    "PromptBuilder",
    "ResponseParser",
    "Tokenizer",
    
    # Caching & Reliability
    "CacheManager",
    "retry",
    "retry_async",
    "RateLimiter",
    "RateLimiterManager",
    "SafetyConfig",
    "RequestValidator",
    
    # Provider Abstractions
    "AIProviderBase",
    "GeminiClient",
    "ProviderFactory",
    "AIManager",
]

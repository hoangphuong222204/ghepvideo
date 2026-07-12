"""Factory for provisioning and caching AI provider instances dynamically."""

import threading
from typing import Dict, Type, Optional
from src.ai.provider_base import AIProviderBase
from src.ai.gemini_client import GeminiClient

class ProviderFactory:
    """Enterprise-grade factory class managing the registration and lifecycle of AI client providers."""

    _providers: Dict[str, Type[AIProviderBase]] = {
        "gemini": GeminiClient,
    }
    
    # Store singleton/cached provider instances
    _instances: Dict[str, AIProviderBase] = {}
    _lock = threading.Lock()

    @classmethod
    def register_provider(cls, name: str, provider_cls: Type[AIProviderBase]) -> None:
        """Registers a new AI provider class with the factory.

        Args:
            name: Lowercase provider identifier (e.g., 'openai').
            provider_cls: Subclass implementing AIProviderBase.
        """
        key = name.lower().strip()
        with cls._lock:
            cls._providers[key] = provider_cls

    @classmethod
    def get_provider(cls, name: str, **kwargs) -> AIProviderBase:
        """Retrieves or provisions a cached provider instance.

        Args:
            name: Target provider key (e.g., 'gemini').
            **kwargs: Configuration parameters passed directly to instantiation.

        Returns:
            The instantiated and configured AIProviderBase.
        """
        key = name.lower().strip()
        
        with cls._lock:
            if key not in cls._providers:
                supported = list(cls._providers.keys())
                raise ValueError(f"AI Provider '{name}' is not registered. Supported: {supported}")

            # Return cached instance if no specific parameters are passed
            if not kwargs and key in cls._instances:
                return cls._instances[key]

            provider_class = cls._providers[key]
            instance = provider_class(**kwargs)
            
            # Cache instance if standard
            if not kwargs:
                cls._instances[key] = instance
                
            return instance

    @classmethod
    def clear(cls) -> None:
        """Clears all cached provider instances."""
        with cls._lock:
            cls._instances.clear()

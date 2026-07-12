"""Abstract Base Class specifying the universal AI provider contract."""

from abc import ABC, abstractmethod
from typing import Generator, AsyncGenerator
from src.ai.request_models import AIRequest
from src.ai.response_models import AIResponse

class AIProviderBase(ABC):
    """Abstract Base Class (ABC) that every provider plugin must implement."""

    @abstractmethod
    def generate_content(self, request: AIRequest) -> AIResponse:
        """Executes a synchronous content generation call to the provider.

        Args:
            request: Standardized request payload containing prompts, configs, and filters.

        Returns:
            Unified AIResponse object.
        """
        pass

    @abstractmethod
    async def generate_content_async(self, request: AIRequest) -> AIResponse:
        """Executes an asynchronous non-blocking content generation call to the provider.

        Args:
            request: Standardized request payload.

        Returns:
            Unified AIResponse object.
        """
        pass

    @abstractmethod
    def generate_content_stream(self, request: AIRequest) -> Generator[str, None, None]:
        """Streams content generation chunks synchronously.

        Args:
            request: Standardized request payload.

        Yields:
            Text chunks (str) as they are produced in real-time.
        """
        pass

    @abstractmethod
    async def generate_content_stream_async(self, request: AIRequest) -> AsyncGenerator[str, None]:
        """Streams content generation chunks asynchronously.

        Args:
            request: Standardized request payload.

        Yields:
            Text chunks (str) as they are produced in real-time.
        """
        pass

"""Thread-safe Singleton AI Manager orchestrating model routing and audit logging."""

import threading
import logging
from typing import Optional, Generator, AsyncGenerator, Dict, Any

from src.ai.request_models import AIRequest, Message, GenerationConfig
from src.ai.response_models import AIResponse
from src.ai.provider_factory import ProviderFactory
from src.ai.prompt_builder import PromptBuilder
from src.ai.response_parser import ResponseParser
from src.ai.exceptions import ConfigurationError

# Optional database integration
try:
    from src.database.database_manager import DatabaseManager
    _has_db = True
except ImportError:
    _has_db = False

logger = logging.getLogger("AIMSPro.AI")

class AIManager:
    """Singleton Thread-safe AI Manager.

    The central gateway for all AI activities across AI Marketing Studio PRO.
    """

    _instance: Optional["AIManager"] = None
    _lock = threading.RLock()

    def __new__(cls, *args: Any, **kwargs: Any) -> "AIManager":
        """Ensures a strict thread-safe Singleton instantiation."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, default_provider: str = "gemini") -> None:
        """Initializes the AIManager once."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return
            
            self._default_provider = default_provider
            self._initialized = True
            logger.info("AIManager Singleton orchestrator successfully initialized.")

    def _resolve_provider_and_model(self, request: AIRequest) -> tuple[str, str]:
        """Auto-routes request to appropriate provider based on model naming convention."""
        model = request.model_name
        
        # Default fallback
        if not model:
            from src.ai.constants import DEFAULT_TEXT_MODEL
            model = DEFAULT_TEXT_MODEL
            request.model_name = model

        # Naming convention routing (e.g., gemini- -> gemini provider)
        if model.startswith("gemini-"):
            provider_name = "gemini"
        else:
            provider_name = self._default_provider

        return provider_name, model

    def _log_audit_event(self, model: str, prompt_len: int, response_len: int, status: str = "SUCCESS") -> None:
        """Saves generating telemetry metrics cleanly into the relational database layer."""
        if not _has_db:
            return

        try:
            db_manager = DatabaseManager()
            with db_manager.unit_of_work() as uow:
                uow.logs.log_event(
                    event_type="AI_GENERATION",
                    description=(
                        f"AI Generation | Model: {model} | Status: {status} | "
                        f"Prompt characters: {prompt_len} | Response characters: {response_len}"
                    )
                )
            logger.debug("AI Generation transaction recorded in database audit logs.")
        except Exception as e:
            # Database log failures should not block client responses (soft-fail)
            logger.warning(f"Failed to write AI audit event to relational database: {e}")

    def generate(self, request: AIRequest) -> AIResponse:
        """Executes a synchronous model query via the appropriate provider.

        Args:
            request: Consolidated prompt, config, and settings payload.

        Returns:
            The parsed, unified AIResponse.
        """
        provider_name, model = self._resolve_provider_and_model(request)
        provider = ProviderFactory.get_provider(provider_name)
        
        prompt_str = request.prompt or ""
        if request.messages:
            prompt_str += f"\n[Chat messages: {len(request.messages)}]"

        try:
            response = provider.generate_content(request)
            self._log_audit_event(
                model=model,
                prompt_len=len(prompt_str),
                response_len=len(response.text),
                status="SUCCESS"
            )
            return response
        except Exception as e:
            self._log_audit_event(
                model=model,
                prompt_len=len(prompt_str),
                response_len=0,
                status=f"FAILURE: {type(e).__name__}"
            )
            raise

    async def generate_async(self, request: AIRequest) -> AIResponse:
        """Executes an asynchronous non-blocking model query via the routed provider."""
        provider_name, model = self._resolve_provider_and_model(request)
        provider = ProviderFactory.get_provider(provider_name)

        prompt_str = request.prompt or ""
        if request.messages:
            prompt_str += f"\n[Chat messages: {len(request.messages)}]"

        try:
            response = await provider.generate_content_async(request)
            self._log_audit_event(
                model=model,
                prompt_len=len(prompt_str),
                response_len=len(response.text),
                status="SUCCESS"
            )
            return response
        except Exception as e:
            self._log_audit_event(
                model=model,
                prompt_len=len(prompt_str),
                response_len=0,
                status=f"FAILURE: {type(e).__name__}"
            )
            raise

    def generate_stream(self, request: AIRequest) -> Generator[str, None, None]:
        """Streams back generation chunks synchronously."""
        provider_name, model = self._resolve_provider_and_model(request)
        provider = ProviderFactory.get_provider(provider_name)

        prompt_str = request.prompt or ""
        text_accumulator = []

        try:
            for chunk in provider.generate_content_stream(request):
                text_accumulator.append(chunk)
                yield chunk
            
            full_response = "".join(text_accumulator)
            self._log_audit_event(
                model=model,
                prompt_len=len(prompt_str),
                response_len=len(full_response),
                status="SUCCESS"
            )
        except Exception as e:
            self._log_audit_event(
                model=model,
                prompt_len=len(prompt_str),
                response_len=0,
                status=f"STREAM_FAILURE: {type(e).__name__}"
            )
            raise

    async def generate_stream_async(self, request: AIRequest) -> AsyncGenerator[str, None]:
        """Streams back generation chunks asynchronously."""
        provider_name, model = self._resolve_provider_and_model(request)
        provider = ProviderFactory.get_provider(provider_name)

        prompt_str = request.prompt or ""
        text_accumulator = []

        try:
            async for chunk in provider.generate_content_stream_async(request):
                text_accumulator.append(chunk)
                yield chunk
            
            full_response = "".join(text_accumulator)
            self._log_audit_event(
                model=model,
                prompt_len=len(prompt_str),
                response_len=len(full_response),
                status="SUCCESS"
            )
        except Exception as e:
            self._log_audit_event(
                model=model,
                prompt_len=len(prompt_str),
                response_len=0,
                status=f"STREAM_FAILURE: {type(e).__name__}"
            )
            raise

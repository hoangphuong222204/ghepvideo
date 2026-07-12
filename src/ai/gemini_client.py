"""Production-ready Enterprise Google Gemini Client implementing direct HTTP REST protocol."""

import json
import time
import urllib.request
import urllib.error
import logging
from typing import Generator, AsyncGenerator, Dict, Any, Optional, List

from src.config.config_manager import ConfigManager
from src.logger.logger_manager import LoggerManager
from src.ai.provider_base import AIProviderBase
from src.ai.request_models import AIRequest
from src.ai.response_models import AIResponse, TokenUsage
from src.ai.exceptions import (
    APIError,
    ConfigurationError,
    NetworkError,
    QuotaError,
    SafetyError,
)
from src.ai.validators import RequestValidator
from src.ai.rate_limiter import RateLimiterManager
from src.ai.cache_manager import CacheManager
from src.ai.safety import SafetyConfig
from src.ai.tokenizer import Tokenizer
from src.ai.retry import retry, retry_async

logger = LoggerManager().get_logger("gemini")

class GeminiClient(AIProviderBase):
    """Production-ready Enterprise Gemini Client.

    Uses native REST requests to interact with Gemini API endpoints securely.
    Fully implements:
    - Thread-safe sliding window RPM/TPM rate limiting
    - SQLite-backed Prompt/Response caching with custom TTL
    - Seamless error mapping and safety threshold filter alignments
    - Automatic fallback parameter validation
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "gemini-2.5-flash",
        cache_manager: Optional[CacheManager] = None
    ) -> None:
        """Initializes the Gemini client.

        Args:
            api_key: Optional Google Gemini API key. If omitted, fetched from ConfigManager.
            default_model: Fallback model to use.
            cache_manager: Active cache manager instance. If omitted, initializes default.
        """
        self._custom_api_key = api_key
        self._default_model = default_model
        
        # Initialize Cache
        self._cache = cache_manager or CacheManager()
        
        # Rate Limiters Manager (RPM/TPM sliding windows)
        self._rate_limiters = RateLimiterManager()

    def _get_api_key(self) -> str:
        """Resolves the Gemini API key from parameters, environment, or system configuration."""
        if self._custom_api_key:
            return self._custom_api_key
        
        # Fallback to ConfigManager
        try:
            config = ConfigManager().config
            if config and config.gemini and config.gemini.api_key:
                return config.gemini.api_key
        except Exception as e:
            logger.debug(f"Could not read config from ConfigManager: {e}")

        # Final environment variable check
        import os
        env_key = os.environ.get("GEMINI_API_KEY")
        if env_key:
            return env_key

        raise ConfigurationError(
            "Gemini API Key is missing. Provide it during initialization, "
            "set GEMINI_API_KEY environment variable, or configure it via the ConfigManager."
        )

    def _get_model_name(self, request: AIRequest) -> str:
        """Resolves the active target model."""
        return request.model_name or self._default_model

    def _build_payload(self, request: AIRequest) -> Dict[str, Any]:
        """Assembles the official Gemini API payload from standardized parameters."""
        contents = []
        
        # 1. Populate Chat Messages (if present)
        for msg in request.messages:
            role = "model" if msg.role in {"model", "assistant"} else "user"
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })

        # 2. Add current User prompt
        if request.prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": request.prompt}]
            })

        payload: Dict[str, Any] = {"contents": contents}

        # 3. Apply System Instructions
        if request.config.system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": request.config.system_instruction}]
            }

        # 4. Compile generation configs
        generation_config: Dict[str, Any] = {}
        if request.config.temperature is not None:
            generation_config["temperature"] = request.config.temperature
        if request.config.top_p is not None:
            generation_config["topP"] = request.config.top_p
        if request.config.top_k is not None:
            generation_config["topK"] = request.config.top_k
        if request.config.max_output_tokens is not None:
            generation_config["maxOutputTokens"] = request.config.max_output_tokens
        if request.config.stop_sequences:
            generation_config["stopSequences"] = request.config.stop_sequences
        if request.config.json_mode:
            generation_config["responseMimeType"] = "application/json"
        if request.config.response_schema:
            generation_config["responseSchema"] = request.config.response_schema

        if generation_config:
            payload["generationConfig"] = generation_config

        # 5. Populate formatted Safety settings
        payload["safetySettings"] = SafetyConfig.format_for_api(request.safety_settings)

        return payload

    def _execute_http_call(self, model: str, payload: Dict[str, Any], action: str = "generateContent") -> Dict[str, Any]:
        """Performs a raw POST HTTP transaction with the Google Gemini endpoint."""
        api_key = self._get_api_key()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:{action}?key={api_key}"
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "aistudio-build"
            },
            method="POST"
        )

        try:
            logger.info(f"🤖 Sending request to Google Gemini API (Model: {model})")
            with urllib.request.urlopen(req, timeout=45) as response:
                resp_bytes = response.read()
                return json.loads(resp_bytes.decode("utf-8"))
        except urllib.error.HTTPError as e:
            # Parse error responses for exact causes
            err_body = ""
            try:
                err_body = e.read().decode("utf-8")
                err_json = json.loads(err_body)
                err_msg = err_json.get("error", {}).get("message", str(e))
                status_code = e.code
                
                # Standard HTTP Error Mapping
                if status_code == 429:
                    logger.error("❌ Gemini Rate Limit or Quota Exceeded (429)")
                    raise QuotaError(f"Quota Exceeded: {err_msg}") from e
                elif status_code == 400:
                    logger.error(f"❌ Gemini Request Validation Error: {err_msg}")
                    raise ValidationError(f"Bad Request: {err_msg}") from e
                elif status_code in {401, 403}:
                    logger.error("❌ Gemini Authentication Failure")
                    raise ConfigurationError(f"Authentication Failure: {err_msg}") from e
                
                raise APIError(err_msg, status_code=status_code, response_text=err_body) from e
            except Exception as parse_ex:
                if isinstance(parse_ex, (QuotaError, ValidationError, ConfigurationError, APIError)):
                    raise parse_ex
                raise APIError(str(e), status_code=e.code, response_text=err_body) from e
        except urllib.error.URLError as e:
            logger.error(f"❌ Gemini Network connection failure: {e}")
            raise NetworkError(f"Network error communicating with Gemini API: {e}") from e
        except Exception as e:
            logger.error(f"❌ Gemini Unexpected exception during HTTP execution: {e}")
            raise APIError(f"Unexpected error: {e}") from e

    @retry()
    def generate_content(self, request: AIRequest) -> AIResponse:
        """Executes a synchronous content generation call to Google Gemini."""
        model = self._get_model_name(request)
        
        # 1. Validate parameters
        RequestValidator.validate_model_name(model)
        RequestValidator.validate_generation_config(
            temperature=request.config.temperature,
            top_p=request.config.top_p,
            top_k=request.config.top_k,
            max_output_tokens=request.config.max_output_tokens,
            model_name=model,
        )

        # Build prompt string for caching & token estimation
        full_prompt = request.prompt or ""
        if request.messages:
            full_prompt += "\n".join(f"{m.role}: {m.content}" for m in request.messages)

        # 2. Check local prompt cache
        cache_key = ""
        if request.use_cache:
            cfg_dict = {
                "temperature": request.config.temperature,
                "top_p": request.config.top_p,
                "top_k": request.config.top_k,
                "max_tokens": request.config.max_output_tokens,
                "json_mode": request.config.json_mode,
            }
            cache_key = self._cache.generate_key(
                model_name=model,
                prompt=full_prompt,
                system_instruction=request.config.system_instruction,
                config_dict=cfg_dict
            )
            cached_text = self._cache.get(cache_key)
            if cached_text is not None:
                # Estimate token counts for metrics compliance
                est_in = Tokenizer.count_tokens(full_prompt)
                est_out = Tokenizer.count_tokens(cached_text)
                return AIResponse(
                    text=cached_text,
                    model_name=model,
                    usage=TokenUsage(prompt_tokens=est_in, completion_tokens=est_out, total_tokens=est_in + est_out),
                    cached=True,
                    finish_reason="STOP",
                    metadata={"cache_key": cache_key}
                )

        # 3. Enforce local Rate Limiting (estimate prompt size)
        est_prompt_tokens = Tokenizer.count_tokens(full_prompt)
        limiter = self._rate_limiters.get_limiter(model)
        limiter.acquire(tokens=est_prompt_tokens, wait=True)

        # 4. Construct payload and dispatch
        payload = self._build_payload(request)
        result = self._execute_http_call(model, payload)

        # 5. Parse unified response and safety filters
        candidates = result.get("candidates", [])
        if not candidates:
            # Verify if content was completely blocked due to safety flags
            prompt_feedback = result.get("promptFeedback", {})
            if prompt_feedback and "blockReason" in prompt_feedback:
                reason = prompt_feedback["blockReason"]
                logger.error(f"❌ Generation blocked by safety filters. Reason: {reason}")
                raise SafetyError(f"Request blocked by Gemini safety filters: {reason}")
            raise APIError("No generation candidates returned from Gemini.")

        candidate = candidates[0]
        
        # Check finish reason for safety block
        finish_reason = candidate.get("finishReason", "STOP")
        if finish_reason == "SAFETY":
            logger.error("❌ Content generation interrupted due to safety violations.")
            raise SafetyError("Content generation blocked by Gemini safety filters.")

        # Extract generated content
        content_parts = candidate.get("content", {}).get("parts", [])
        generated_text = ""
        if content_parts:
            generated_text = "".join(part.get("text", "") for part in content_parts)

        # Resolve usage metrics
        usage_metadata = result.get("usageMetadata", {})
        prompt_tokens = usage_metadata.get("promptTokenCount", est_prompt_tokens)
        completion_tokens = usage_metadata.get("candidatesTokenCount", Tokenizer.count_tokens(generated_text))
        total_tokens = usage_metadata.get("totalTokenCount", prompt_tokens + completion_tokens)

        # Save to Cache if requested
        if request.use_cache and cache_key and generated_text:
            self._cache.set(
                key=cache_key,
                prompt=full_prompt,
                response_text=generated_text,
                model_name=model,
                config_dict=cfg_dict,
                ttl=request.cache_ttl
            )

        return AIResponse(
            text=generated_text,
            model_name=model,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens
            ),
            cached=False,
            finish_reason=finish_reason,
            metadata={"raw_response": result}
        )

    @retry_async()
    async def generate_content_async(self, request: AIRequest) -> AIResponse:
        """Executes an asynchronous non-blocking content generation call to Google Gemini.

        Note: To provide clean async-safe operations in high-concurrency loops,
        this utilizes direct non-blocking worker pools or native threads.
        """
        import asyncio
        # Run synchronous call in a background thread executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_content, request)

    def generate_content_stream(self, request: AIRequest) -> Generator[str, None, None]:
        """Streams content generation chunks synchronously."""
        model = self._get_model_name(request)
        RequestValidator.validate_model_name(model)

        full_prompt = request.prompt or ""
        if request.messages:
            full_prompt += "\n".join(f"{m.role}: {m.content}" for m in request.messages)

        # Enforce rate limits
        est_tokens = Tokenizer.count_tokens(full_prompt)
        limiter = self._rate_limiters.get_limiter(model)
        limiter.acquire(tokens=est_tokens, wait=True)

        payload = self._build_payload(request)
        api_key = self._get_api_key()
        
        # Use streamGenerateContent endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={api_key}"
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "aistudio-build"
            },
            method="POST"
        )

        try:
            logger.info(f"🤖 Opening streaming connection with Google Gemini (Model: {model})")
            with urllib.request.urlopen(req, timeout=60) as response:
                # streamGenerateContent returns a JSON array streamed over HTTP chunked encoding.
                # We can perform buffer-based parsing of the JSON streaming array objects.
                buffer = ""
                for chunk in response:
                    decoded = chunk.decode("utf-8")
                    buffer += decoded
                    
                    # Look for structured JSON objects in the stream
                    # Google REST streams blocks in format: [\n  { ... },\n  { ... }\n]
                    while True:
                        # Extract matches matching any complete { ... } structure
                        # Since chunks can span lines, we can search for brackets
                        # Very simple yet robust SSE-style parser for REST streams:
                        try:
                            # Trim leading comma or bracket characters
                            buffer = buffer.strip()
                            if buffer.startswith("["):
                                buffer = buffer[1:].strip()
                            if buffer.startswith(","):
                                buffer = buffer[1:].strip()
                            
                            if not buffer:
                                break
                                
                            # Locate the first valid closed JSON curly brace block
                            # Counting curly braces is standard and highly reliable for streaming JSON arrays.
                            bracket_count = 0
                            in_string = False
                            escape = False
                            end_index = -1
                            
                            for i, char in enumerate(buffer):
                                if char == '"' and not escape:
                                    in_string = not in_string
                                elif char == '\\' and in_string:
                                    escape = True
                                    continue
                                elif in_string:
                                    escape = False
                                    continue
                                
                                if char == '{':
                                    bracket_count += 1
                                elif char == '}':
                                    bracket_count -= 1
                                    if bracket_count == 0:
                                        end_index = i
                                        break
                                escape = False

                            if end_index != -1:
                                json_str = buffer[:end_index + 1]
                                buffer = buffer[end_index + 1:].strip()
                                
                                # Parse single chunk block
                                data_block = json.loads(json_str)
                                candidates = data_block.get("candidates", [])
                                if candidates:
                                    candidate = candidates[0]
                                    finish_reason = candidate.get("finishReason", "STOP")
                                    if finish_reason == "SAFETY":
                                        raise SafetyError("Generation blocked by safety filters.")
                                        
                                    parts = candidate.get("content", {}).get("parts", [])
                                    for part in parts:
                                        text_val = part.get("text", "")
                                        if text_val:
                                            yield text_val
                            else:
                                # Incomplete block in buffer, wait for next network chunk
                                break
                        except Exception as e:
                            # Parsing anomaly, dump buffer to next chunk or fail softly
                            logger.debug(f"Streaming parse warning: {e}")
                            break
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise APIError(f"Streaming error ({e.code}): {err_body}", status_code=e.code) from e
        except Exception as e:
            if isinstance(e, SafetyError):
                raise e
            raise NetworkError(f"Streaming failed: {e}") from e

    async def generate_content_stream_async(self, request: AIRequest) -> AsyncGenerator[str, None]:
        """Streams content generation chunks asynchronously."""
        # Yield generator values non-blockingly using thread pools
        import asyncio
        from queue import Queue, Empty
        
        loop = asyncio.get_event_loop()
        queue = Queue()
        
        def run_stream():
            try:
                for chunk in self.generate_content_stream(request):
                    queue.put(chunk)
            except Exception as e:
                queue.put(e)
            finally:
                queue.put(None)  # Sentinel value signaling completion

        # Run generator in a separate thread
        await loop.run_in_executor(None, run_stream)
        
        while True:
            # Non-blocking poll from thread-safe Queue
            try:
                item = queue.get_nowait()
                if item is None:
                    break
                if isinstance(item, Exception):
                    raise item
                yield item
            except Empty:
                # Sleep briefly to yield CPU control to other coroutines
                await asyncio.sleep(0.05)

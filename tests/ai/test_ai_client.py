"""Comprehensive Unit Tests for AIMS Pro AI and Gemini Client Layer."""

import os
import time
import json
import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.ai import (
    AIError,
    ConfigurationError,
    ValidationError,
    SafetyError,
    ParseError,
    AIRequest,
    Message,
    GenerationConfig,
    PromptBuilder,
    ResponseParser,
    Tokenizer,
    CacheManager,
    RateLimiter,
    SafetyConfig,
    RequestValidator,
    ProviderFactory,
    AIManager,
    GeminiClient,
)

class TestAIExceptions(unittest.TestCase):
    """Verifies hierarchy of AI client exceptions."""

    def test_exception_inheritance(self):
        """Ensure all custom AI exceptions inherit from AIError."""
        self.assertTrue(issubclass(ConfigurationError, AIError))
        self.assertTrue(issubclass(ValidationError, AIError))
        self.assertTrue(issubclass(SafetyError, AIError))
        self.assertTrue(issubclass(ParseError, AIError))


class TestPromptBuilder(unittest.TestCase):
    """Verifies that PromptBuilder binds variables and compiles templates correctly."""

    def test_template_binding(self):
        """Ensure variables are correctly injected into prompt templates."""
        builder = PromptBuilder("{key1} and {key2}")
        builder.bind("key1", "value1").bind("key2", "value2")
        self.assertEqual(builder.build_prompt(), "value1 and " + "value2")

    def test_missing_key_raises_value_error(self):
        """Ensure missing keys in template format raise ValueError."""
        builder = PromptBuilder("{required_key}")
        with self.assertRaises(ValueError):
            builder.build_prompt()

    def test_preloaded_templates(self):
        """Verify preloaded vertical video templates initialize correctly."""
        builder = PromptBuilder.vertical_video_script()
        builder.bind_dict({
            "product_name": "EcoCase",
            "target_audience": "Tech Enthusiasts",
            "core_benefit": "Zero Carbon Footprint",
            "tone": "Inspiring"
        })
        compiled = builder.build_prompt()
        self.assertIn("EcoCase", compiled)
        self.assertIn("Tech Enthusiasts", compiled)


class TestResponseParser(unittest.TestCase):
    """Verifies markdown stripping and JSON repair parsing capabilities."""

    def test_strip_markdown_json_fences(self):
        """Ensure json code block fences are cleanly removed."""
        raw = "```json\n{\"key\": \"value\"}\n```"
        self.assertEqual(ResponseParser.strip_markdown(raw), "{\"key\": \"value\"}")

        raw_simple = "```\nHello\n```"
        self.assertEqual(ResponseParser.strip_markdown(raw_simple), "Hello")

    def test_parse_json_robustness(self):
        """Ensure standard and repaired JSONs parse correctly."""
        raw_json = "```json\n{\"items\": [1, 2, 3],}\n```"  # Trailing comma
        parsed = ResponseParser.parse_json(raw_json)
        self.assertEqual(parsed, {"items": [1, 2, 3]})


class TestTokenizer(unittest.TestCase):
    """Verifies precision counts and character fallbacks."""

    def test_tokenizer_empty(self):
        """Ensure empty strings yield 0 tokens."""
        self.assertEqual(Tokenizer.count_tokens(""), 0)

    def test_tokenizer_character_fallback(self):
        """Ensure character fallback uses ~4 chars to 1 token division."""
        self.assertEqual(Tokenizer.count_tokens("abcd"), 1)
        self.assertEqual(Tokenizer.count_tokens("abcdefgh"), 2)


class TestCacheManager(unittest.TestCase):
    """Verifies local SQLite caching lifecycle and expiration logic."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = Path(self.temp_dir.name)
        self.cache = CacheManager(cache_dir=self.cache_dir, ttl=1)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_set_and_get_cache(self):
        """Ensure set items are successfully retrieved."""
        key = "test_key"
        self.cache.set(
            key=key,
            prompt="Hello World",
            response_text="How can I help you?",
            model_name="gemini-2.5-flash"
        )
        self.assertEqual(self.cache.get(key), "How can I help you?")

    def test_cache_expiration(self):
        """Ensure cached entries expire after TTL duration."""
        key = "expire_key"
        self.cache.set(
            key=key,
            prompt="Expire Prompt",
            response_text="Soon gone",
            model_name="gemini-2.5-flash",
            ttl=0  # Expire immediately
        )
        self.assertIsNone(self.cache.get(key))


class TestRateLimiter(unittest.TestCase):
    """Verifies thread-safe sliding window rate limits compliance."""

    def test_rate_limiter_allows_under_limits(self):
        """Ensure rate limiter permits requests under the active RPM limit."""
        limiter = RateLimiter(max_rpm=5, max_tpm=1000)
        delay = limiter.acquire(tokens=10, wait=False)
        self.assertEqual(delay, 0.0)

    def test_rate_limiter_blocks_above_limits(self):
        """Ensure rate limiter rejects requests immediately if wait=False and limit exceeded."""
        limiter = RateLimiter(max_rpm=1, max_tpm=100)
        limiter.acquire(tokens=10, wait=False)
        with self.assertRaises(Exception):
            limiter.acquire(tokens=10, wait=False)


class TestAIManager(unittest.TestCase):
    """Verifies Singleton behavior and model routing rules."""

    def test_singleton_behavior(self):
        """Ensure multiple instantiations of AIManager point to the exact same memory address."""
        mgr1 = AIManager()
        mgr2 = AIManager()
        self.assertIs(mgr1, mgr2)


class TestGeminiClient(unittest.TestCase):
    """Verifies payload builders, parameter validations, and direct REST calls."""

    @patch("urllib.request.urlopen")
    def test_generate_content_success(self, mock_urlopen):
        """Ensure GeminiClient constructs correct payload and maps success response."""
        # Setup mock HTTP response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "candidates": [{
                "content": {
                    "parts": [{"text": "Mocked generated output text"}]
                },
                "finishReason": "STOP"
            }],
            "usageMetadata": {
                "promptTokenCount": 10,
                "candidatesTokenCount": 20,
                "totalTokenCount": 30
            }
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = GeminiClient(api_key="test_fake_api_key_value")
        request = AIRequest(
            prompt="Hello Gemini",
            model_name="gemini-2.5-flash",
            use_cache=False
        )
        
        response = client.generate_content(request)
        self.assertEqual(response.text, "Mocked generated output text")
        self.assertEqual(response.usage.total_tokens, 30)
        self.assertFalse(response.cached)

    @patch("urllib.request.urlopen")
    def test_generate_content_safety_blocked(self, mock_urlopen):
        """Ensure safety blocks raise SafetyError."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "candidates": [{
                "finishReason": "SAFETY"
            }]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = GeminiClient(api_key="test_fake_api_key_value")
        request = AIRequest(
            prompt="Trigger safety block",
            model_name="gemini-2.5-flash",
            use_cache=False
        )

        with self.assertRaises(SafetyError):
            client.generate_content(request)

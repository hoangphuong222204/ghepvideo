# Module 04: AI and Gemini Client

The `src/ai` package provides a robust, enterprise-grade, thread-safe AI gateway for **AI Marketing Studio PRO**. 

Designed to act as a unified proxy between the application modules and large language models, it features native direct HTTP REST integration with **Google Gemini API** (using the high-performance Gemini 2.5 and 3.5 series), sliding-window rate limiting, local SQLite response caching, safety configurations, resilient backoff retries, and a plugin-driven provider registration framework.

---

## Directory Structure

```text
src/ai/
├── __init__.py             # Public exports mapping
├── ai_manager.py           # Thread-safe Singleton orchestrator & DB audit logger
├── gemini_client.py        # Direct HTTP REST Gemini protocol client
├── provider_base.py        # Abstract Base Class contract for AI plugins
├── provider_factory.py     # Registry factory mapping provider instances
├── request_models.py       # Dataclass-based Request payloads (AIRequest)
├── response_models.py      # Dataclass-based Response payloads (AIResponse)
├── prompt_builder.py       # Fluent variables mapping dynamic prompt builder
├── prompt_templates.py     # Default industry-proven copywriting templates
├── response_parser.py      # Cleaner utility (markdown code fence stripping, JSON repair)
├── tokenizer.py            # Token estimator (tiktoken with fallback character counts)
├── cache_manager.py        # Thread-safe SQLite prompt & response cache with TTL
├── retry.py                # Exponential backoff retry decorators (sync and async)
├── rate_limiter.py         # Sliding window RPM / TPM rate limiter managers
├── safety.py               # Google Gemini Harm thresholds setting formatters
├── validators.py           # Logical bounds parameter validations
├── exceptions.py           # AI-specific custom exceptions
├── constants.py            # Model parameters and system constants
└── README.md               # Package documentation (this file)
```

---

## Architecture Design

### 1. Robust Zero-Dependency Rest Clients (`gemini_client.py`)
To prevent package installation locking issues in sandboxed container instances, the system integrates with Google Gemini's official REST endpoint natively using standard libraries (`urllib`). It includes custom support for headers, payloads, error code mapping, and streaming chunk parsing.

### 2. Thread-Safe Sliding Window Rate Limiting (`rate_limiter.py`)
Tracks Requests Per Minute (RPM) and Tokens Per Minute (TPM) using atomic lock synchronizations. Under load, it automatically sleeps until a slot opens up, or drops requests instantly with a `RateLimitError` depending on preferences.

### 3. Local SQLite Response Caching (`cache_manager.py`)
Caches identical prompt and configuration requests inside a lightweight, lightning-fast, local SQLite table (`ai_cache.db`). Includes background-ready table index creation, lazy expired cleanup routines, and customizable TTL boundaries.

### 4. Dynamic Provider Factory Framework (`provider_factory.py`)
Enables future plug-and-play scaling for alternative APIs (OpenAI, Claude, DeepSeek, local LLMs) by mapping standard provider hooks back to the `AIProviderBase` interface.

---

## Usage Examples

### 1. Primary Generation (Synchronous)

```python
from src.ai import AIManager, AIRequest, GenerationConfig

ai_manager = AIManager()

request = AIRequest(
    prompt="Write a punchy marketing tagline for a solar-powered smartphone case.",
    model_name="gemini-2.5-flash",
    config=GenerationConfig(
        temperature=0.7,
        max_output_tokens=150,
        system_instruction="You are a professional conversion copywriter."
    )
)

response = ai_manager.generate(request)
print(f"Generated text: {response.text}")
print(f"Tokens consumed: {response.usage.total_tokens} (Prompt: {response.usage.prompt_tokens})")
print(f"Served from Cache? {response.cached}")
```

### 2. Chat Conversation (Asynchronous)

```python
import asyncio
from src.ai import AIManager, AIRequest, Message, GenerationConfig

async def chat_interaction():
    ai_manager = AIManager()
    
    request = AIRequest(
        messages=[
            Message(role="system", content="You are a friendly branding guide."),
            Message(role="user", content="Suggest three color names for an eco-luxury cosmetics line.")
        ],
        model_name="gemini-2.5-pro",
        config=GenerationConfig(temperature=0.5)
    )
    
    response = await ai_manager.generate_async(request)
    print(response.text)

asyncio.run(chat_interaction())
```

### 3. Streaming (Real-Time Chunk Consumption)

```python
from src.ai import AIManager, AIRequest

ai_manager = AIManager()
request = AIRequest(
    prompt="Explain quantum physics in a single vertical video hook paragraph.",
    model_name="gemini-2.5-flash"
)

for chunk in ai_manager.generate_stream(request):
    print(chunk, end="", flush=True)
```

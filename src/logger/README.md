# Logger System Module (Module 02)

The **Logger System** is an enterprise-grade, thread-safe, and asynchronous-friendly logging framework designed specifically for **AI Marketing Studio PRO**. It serves as the unified diagnostics and observability backbone for all modules (FastAPI, NiceGUI, Gemini API, Fish Speech, FFmpeg, and SQLite database).

---

## Project Structure

```text
src/logger/
├── __init__.py             # Public API exports and quick-use convenience functions
├── logger_manager.py       # Thread-safe Singleton orchestrating active log routing
├── logger_factory.py       # Static factory constructing colored/JSON handlers
├── log_formatter.py       # Custom log formatters (Colored Console, UTF-8 Emojis, JSON)
├── log_config.py           # Unified logging dataclass holding configuration options
├── performance_logger.py   # Context manager tracking code timing and memory metrics
├── decorators.py           # Sync/async execution time decorators
├── exceptions.py           # Domain-specific logging exceptions hierarchy
├── constants.py            # Log filenames, ANSI codes, level emojis, and format defaults
└── README.md               # Extensive module documentation and integration guides
```

---

## Core Features

-   **Singleton Orchestrator**: One central, thread-safe, double-checked locking `LoggerManager`.
-   **Multi-File Log Routing**: Dedicated streams automatically output logs to:
    -   `app.log` (General aggregation)
    -   `error.log` (Aggregated `ERROR` and `CRITICAL` warnings)
    -   `gemini.log` (Google Gemini integrations)
    -   `database.log` (SQLite queries & connections)
    -   `fishspeech.log` (TTS audio synthesis metrics)
    -   `ffmpeg.log` (Video/audio compilation outputs)
    -   `ui.log` (NiceGUI interactions & routing)
-   **Daily Log Partitioning**: Group logs into dynamic day-to-day folders (`logs/YYYY-MM-DD/`) automatically with real-time rollover.
-   **Console Diagnostics**: Highly visible ANSI-colored levels with UTF-8 support and contextual emojis (e.g. 🤖 for Gemini, 🗄️ for Database).
-   **Structured JSON Output**: Ideal for ingestion into central log analysis stacks.
-   **Performance Monitoring**: High-precision timers and standard `tracemalloc` memory delta checks.
-   **Sync/Async Decorators**: Non-intrusive metadata tracing with `@log_execution_time`.

---

## Quick Usage Integration Guide

### 1. Basic Logging

```python
from src import logger

# Retrieve logger dynamically by module keyword
db_logger = logger.get_logger("database")
gemini_logger = logger.get_logger("gemini")

db_logger.info("Initializing database schemas...")
gemini_logger.debug("Prompt payload compiled successfully")
```

### 2. Exception Helper

```python
from src import logger

try:
    raise ConnectionError("Database timed out")
except Exception as e:
    logger.log_exception("database", "Failed to retrieve user profile", e)
```

### 3. Execution Time Decoration

```python
from src.logger import log_execution_time

@log_execution_time(logger_name="ffmpeg", monitor_memory=True)
def render_video_clip():
    # Sync operation code
    pass

@log_execution_time(logger_name="gemini")
async def generate_marketing_copy():
    # Async endpoint coroutine code
    pass
```

### 4. Code Block Performance Profiling

```python
from src.logger import PerformanceTimer

with PerformanceTimer("heavy_computation", monitor_memory=True):
    # Performance critical execution block
    total = sum(i * i for i in range(1000000))
```

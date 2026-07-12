"""High-performance decorators for logging and measuring execution times."""

import asyncio
import logging
import functools
import time
from typing import Callable, Any, TypeVar, cast
from src.logger.logger_manager import LoggerManager

F = TypeVar("F", bound=Callable[..., Any])


def log_execution_time(
    logger_name: str = "performance",
    level: int = logging.INFO,
    monitor_memory: bool = False,
) -> Callable[[F], F]:
    """Decorator to measure and log the precise execution time of a function.

    Fully supports both standard synchronous functions and asynchronous coroutine functions.

    Args:
        logger_name: Target logger to dispatch stats to. Defaults to "performance".
        level: Log level (e.g. logging.INFO, logging.DEBUG).
        monitor_memory: If True, tracks memory delta allocated by standard tracemalloc.

    Returns:
        The wrapped callable.
    """
    def decorator(func: F) -> F:
        # Import PerformanceTimer here to avoid circular imports if any
        from src.logger.performance_logger import PerformanceTimer

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            op_name = f"{func.__module__}.{func.__qualname__}"
            with PerformanceTimer(op_name, logger_name, level, monitor_memory):
                return func(*args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            op_name = f"{func.__module__}.{func.__qualname__}"
            with PerformanceTimer(op_name, logger_name, level, monitor_memory):
                return await func(*args, **kwargs)

        # Introspect if target function is a coroutine
        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        return cast(F, sync_wrapper)

    return decorator

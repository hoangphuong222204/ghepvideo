"""Robust sync and async exponential backoff retry mechanism with randomized jitter."""

import time
import random
import asyncio
import logging
from typing import Callable, Any, Type, Tuple, TypeVar, Awaitable, Union
from src.ai.exceptions import (
    APIError,
    NetworkError,
    QuotaError,
)

logger = logging.getLogger("AIMSPro.AI")

T = TypeVar("T")

# Define default retriable exceptions
DEFAULT_RETRIABLE_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    NetworkError,
    QuotaError,
)

def is_retriable_api_error(e: Exception) -> bool:
    """Heuristic helper to check if an APIError is retriable (e.g. 5xx Server Errors)."""
    if isinstance(e, APIError):
        # Retry on standard server-side failures (500, 502, 503, 504) or rate limit (429)
        return e.status_code in {429, 500, 502, 503, 504}
    return False

def calculate_delay(attempt: int, base_delay: float, max_delay: float) -> float:
    """Computes backoff delay with randomized jitter.

    Args:
        attempt: Current iteration (1-indexed).
        base_delay: Initial waiting interval.
        max_delay: Upper interval boundary.
    """
    # Exponential backoff formula: base * 2 ^ attempt
    backoff = base_delay * (2 ** (attempt - 1))
    # Add full random jitter to prevent "thundering herd" issues
    delay = random.uniform(0.1, min(backoff, max_delay))
    return delay

def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    retriable_exceptions: Tuple[Type[Exception], ...] = DEFAULT_RETRIABLE_EXCEPTIONS
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Synchronous retry decorator with exponential backoff and full jitter.

    Args:
        max_retries: Total retry limit.
        base_delay: Initial delay in seconds.
        max_delay: Cap on maximum backoff delay.
        retriable_exceptions: Exceptions that trigger retries.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    is_retriable = (
                        any(isinstance(e, exc) for exc in retriable_exceptions) or
                        is_retriable_api_error(e)
                    )
                    
                    if not is_retriable or attempt > max_retries:
                        logger.debug(f"Retry threshold exceeded or non-retriable exception. Raising: {e}")
                        raise

                    delay = calculate_delay(attempt, base_delay, max_delay)
                    logger.warning(
                        f"Attempt {attempt}/{max_retries} failed for '{func.__name__}': {e}. "
                        f"Retrying in {delay:.2s}s..."
                    )
                    time.sleep(delay)
                    attempt += 1
        return wrapper
    return decorator

def retry_async(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    retriable_exceptions: Tuple[Type[Exception], ...] = DEFAULT_RETRIABLE_EXCEPTIONS
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Asynchronous retry decorator with exponential backoff and full jitter.

    Args:
        max_retries: Total retry limit.
        base_delay: Initial delay in seconds.
        max_delay: Cap on maximum backoff delay.
        retriable_exceptions: Exceptions that trigger retries.
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 1
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    is_retriable = (
                        any(isinstance(e, exc) for exc in retriable_exceptions) or
                        is_retriable_api_error(e)
                    )
                    
                    if not is_retriable or attempt > max_retries:
                        logger.debug(f"Async Retry threshold exceeded or non-retriable exception. Raising: {e}")
                        raise

                    delay = calculate_delay(attempt, base_delay, max_delay)
                    logger.warning(
                        f"Async Attempt {attempt}/{max_retries} failed for '{func.__name__}': {e}. "
                        f"Retrying in {delay:.2s}s..."
                    )
                    await asyncio.sleep(delay)
                    attempt += 1
        return wrapper
    return decorator

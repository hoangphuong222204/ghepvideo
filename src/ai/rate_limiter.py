"""Thread-safe sliding-window Rate Limiter for RPM and TPM rate limit compliance."""

import time
import asyncio
import threading
import logging
from typing import List, Tuple
from src.ai.exceptions import RateLimitError

logger = logging.getLogger("AIMSPro.AI")

class RateLimiter:
    """Thread-safe Sliding Window Rate Limiter managing Request Per Minute (RPM)

    and Token Per Minute (TPM) limits with automatic queue delaying and early
    blocking rejection.
    """

    def __init__(self, max_rpm: int = 15, max_tpm: int = 30000) -> None:
        """Initializes the RateLimiter.

        Args:
            max_rpm: Maximum Requests Per Minute limit.
            max_tpm: Maximum Tokens Per Minute limit.
        """
        self._max_rpm = max_rpm
        self._max_tpm = max_tpm

        # Sliding window history of (timestamp, 1)
        self._request_history: List[float] = []
        # Sliding window history of (timestamp, tokens)
        self._token_history: List[Tuple[float, int]] = []

        self._lock = threading.Lock()

    @property
    def max_rpm(self) -> int:
        return self._max_rpm

    @property
    def max_tpm(self) -> int:
        return self._max_tpm

    def configure(self, max_rpm: int, max_tpm: int) -> None:
        """Dynamically updates the rate limits at runtime."""
        with self._lock:
            self._max_rpm = max_rpm
            self._max_tpm = max_tpm
            logger.info(f"RateLimiter reconfigured: RPM={max_rpm}, TPM={max_tpm}")

    def _prune(self, now: float) -> None:
        """Removes records older than 60 seconds from history."""
        cutoff = now - 60.0
        
        # Prune requests
        self._request_history = [t for t in self._request_history if t > cutoff]
        
        # Prune tokens
        self._token_history = [item for item in self._token_history if item[0] > cutoff]

    def _get_current_metrics(self) -> Tuple[int, int]:
        """Calculates current sliding RPM and TPM."""
        current_rpm = len(self._request_history)
        current_tpm = sum(tokens for _, tokens in self._token_history)
        return current_rpm, current_tpm

    def acquire(self, tokens: int = 1, wait: bool = True) -> float:
        """Acquires permission to make an API call, blocking if necessary.

        Args:
            tokens: Est. token size of the request.
            wait: If True, blocks/sleeps until limits are available. If False,
                  immediately raises RateLimitError.

        Returns:
            The total sleep delay in seconds (0.0 if allowed immediately).
        """
        while True:
            with self._lock:
                now = time.time()
                self._prune(now)

                current_rpm, current_tpm = self._get_current_metrics()

                # Check limit breaches
                rpm_ok = (current_rpm + 1) <= self._max_rpm
                tpm_ok = (current_tpm + tokens) <= self._max_tpm

                if rpm_ok and tpm_ok:
                    # Record the current transaction
                    self._request_history.append(now)
                    self._token_history.append((now, tokens))
                    return 0.0

                # Limits breached!
                if not wait:
                    raise RateLimitError(
                        f"Rate limit exceeded. Max RPM: {self._max_rpm} (Current: {current_rpm}), "
                        f"Max TPM: {self._max_tpm} (Current: {current_tpm} + requested: {tokens})"
                    )

                # Heuristic delay estimate (e.g. sleep 0.5s before retrying)
                delay = 0.5
                logger.info(
                    f"Rate limiter sleeping {delay}s for limit window availability. "
                    f"Current RPM={current_rpm}/{self._max_rpm}, TPM={current_tpm}/{self._max_tpm}"
                )
            
            time.sleep(delay)

    async def acquire_async(self, tokens: int = 1, wait: bool = True) -> float:
        """Asynchronous equivalent of acquire using non-blocking asyncio.sleep.

        Args:
            tokens: Est. token size of the request.
            wait: If True, pauses execution. If False, raises RateLimitError.

        Returns:
            The total sleep delay in seconds (0.0 if allowed immediately).
        """
        while True:
            with self._lock:
                now = time.time()
                self._prune(now)

                current_rpm, current_tpm = self._get_current_metrics()

                rpm_ok = (current_rpm + 1) <= self._max_rpm
                tpm_ok = (current_tpm + tokens) <= self._max_tpm

                if rpm_ok and tpm_ok:
                    self._request_history.append(now)
                    self._token_history.append((now, tokens))
                    return 0.0

                if not wait:
                    raise RateLimitError(
                        f"Rate limit exceeded. Max RPM: {self._max_rpm} (Current: {current_rpm}), "
                        f"Max TPM: {self._max_tpm} (Current: {current_tpm} + requested: {tokens})"
                    )

                delay = 0.5
                logger.info(
                    f"Async Rate limiter sleeping {delay}s for limit window availability. "
                    f"Current RPM={current_rpm}/{self._max_rpm}, TPM={current_tpm}/{self._max_tpm}"
                )

            await asyncio.sleep(delay)
class RateLimiterManager:
    """Manager to hold separate rate limiters for different models or providers."""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls) -> "RateLimiterManager":
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._limiters = {}
        return cls._instance

    def get_limiter(self, name: str, default_rpm: int = 15, default_tpm: int = 30000) -> RateLimiter:
        """Gets or provisions a specific rate limiter by key."""
        with self._lock:
            if name not in self._limiters:
                self._limiters[name] = RateLimiter(max_rpm=default_rpm, max_tpm=default_tpm)
            return self._limiters[name]

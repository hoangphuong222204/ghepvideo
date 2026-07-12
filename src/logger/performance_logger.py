"""Performance Timer and Resource Monitor Context Manager for AIMS Pro."""

import time
import logging
import tracemalloc
from typing import Optional, Union, Any
from src.logger.logger_manager import LoggerManager


class PerformanceTimer:
    """A context manager to monitor performance and execution metrics of code blocks.

    Tracks high-precision elapsed time and memory allocations using standard
    `tracemalloc` capabilities, logging the analytics automatically.
    """

    def __init__(
        self,
        operation_name: str,
        logger_name: str = "performance",
        level: int = logging.INFO,
        monitor_memory: bool = True,
    ) -> None:
        """Initializes the PerformanceTimer.

        Args:
            operation_name: Descriptive name of the code block or query being analyzed.
            logger_name: The name of the logger to dispatch stats to. Defaults to "performance".
            level: The standard logging level (e.g. logging.INFO, logging.DEBUG).
            monitor_memory: If True, tracks memory allocation changes during the block execution.
        """
        self.operation_name = operation_name
        self.logger_name = logger_name
        self.level = level
        self.monitor_memory = monitor_memory
        
        self._logger = LoggerManager().get_logger(self.logger_name)
        self._start_time: float = 0.0
        self._start_mem_size: int = 0

    def __enter__(self) -> "PerformanceTimer":
        """Starts the performance measurements."""
        if self.monitor_memory:
            if not tracemalloc.is_tracing():
                tracemalloc.start()
            # Capture baseline memory size
            self._start_mem_size, _ = tracemalloc.get_traced_memory()

        self._start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stops the timer and memory checks, logging the final results."""
        elapsed_sec = time.perf_counter() - self._start_time
        elapsed_ms = elapsed_sec * 1000.0

        mem_delta_str = ""
        if self.monitor_memory:
            current_mem_size, peak_mem_size = tracemalloc.get_traced_memory()
            mem_delta = current_mem_size - self._start_mem_size
            mem_delta_mb = mem_delta / (1024 * 1024)
            peak_mem_mb = peak_mem_size / (1024 * 1024)
            mem_delta_str = f" | Memory Delta: {mem_delta_mb:+.4f} MB (Peak Traced: {peak_mem_mb:.4f} MB)"

        status = "SUCCESS" if exc_type is None else f"FAILED ({exc_type.__name__})"
        
        log_message = (
            f"[PERF] Operation: '{self.operation_name}' | Status: {status} | "
            f"Elapsed: {elapsed_ms:.2f}ms ({elapsed_sec:.4f}s){mem_delta_str}"
        )

        self._logger.log(self.level, log_message)

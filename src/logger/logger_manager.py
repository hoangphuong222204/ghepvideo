"""Singleton Thread-Safe Logger Manager orchestrating central log routing in AIMS Pro."""

import os
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Set, Callable
from src.logger.log_config import LoggerConfig
from src.logger.logger_factory import LoggerFactory
from src.logger.constants import (
    APP_LOG,
    ERROR_LOG,
    MODULE_TO_FILE,
    DEFAULT_FILE_FORMAT,
)
from src.logger.exceptions import LogDirectoryCreationError


class LoggerManager:
    """Singleton Thread-safe manager for all AIMS Pro application loggers.

    Handles daily log directory partitioning, automated file routing,
    multi-handler configurations (app.log, error.log, module.log),
    and runtime config hot-swapping.
    """

    _instance: Optional["LoggerManager"] = None
    _lock: threading.RLock = threading.RLock()

    def __new__(cls, *args: Any, **kwargs: Any) -> "LoggerManager":
        """Ensures a strict thread-safe Singleton instantiation."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Optional[LoggerConfig] = None) -> None:
        """Initializes the LoggerManager.

        Args:
            config: Optional custom LoggerConfig configuration. If omitted, uses defaults.
        """
        # Ensure initialization only happens once
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            self._config = config or LoggerConfig()
            self._loggers: Dict[str, logging.Logger] = {}
            self._current_date_str = datetime.now().strftime("%Y-%m-%d")
            
            # Shared global handlers to prevent redundant file open locks
            self._shared_handlers: Dict[str, logging.Handler] = {}

            # Create base directories immediately
            self._resolve_and_create_log_dir()
            self._initialized = True

    @property
    def config(self) -> LoggerConfig:
        """Returns the current LoggerConfig."""
        return self._config

    def _resolve_and_create_log_dir(self) -> Path:
        """Determines the active log output directory and ensures it exists.

        If `use_daily_folder` is active, appends a date folder (YYYY-MM-DD).

        Returns:
            The resolved target Path.
        """
        target_dir = Path(self._config.base_log_dir)
        if self._config.use_daily_folder:
            # Check if date has progressed in real-time
            self._current_date_str = datetime.now().strftime("%Y-%m-%d")
            target_dir = target_dir / self._current_date_str

        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            return target_dir
        except Exception as e:
            raise LogDirectoryCreationError(
                f"Failed to create logging directory at {target_dir}: {e}"
            ) from e

    def _get_shared_file_handler(self, filename: str) -> logging.Handler:
        """Gets or builds a shared file handler to avoid redundant descriptor allocation.

        Args:
            filename: The specific log file name (e.g., "app.log", "error.log").

        Returns:
            The logging.Handler instance.
        """
        # Ensure target directory is refreshed and current (handling date transitions)
        active_dir = self._resolve_and_create_log_dir()
        file_path = active_dir / filename
        key = str(file_path)

        if key not in self._shared_handlers:
            handler = LoggerFactory.create_file_handler(self._config, file_path)
            # Special case: error.log should strictly trigger only for ERROR/CRITICAL
            if filename == ERROR_LOG:
                handler.setLevel(logging.ERROR)
            self._shared_handlers[key] = handler

        return self._shared_handlers[key]

    def get_logger(self, name: str) -> logging.Logger:
        """Retrieves or provisions a beautifully-configured thread-safe Logger.

        Args:
            name: The module or specific system logger name (e.g. "gemini", "database", "ffmpeg").

        Returns:
            The fully populated Python Logger.
        """
        # Standardize prefix and check cache
        name = name.lower().strip()
        
        with self._lock:
            # Check if date changed to roll log directories dynamically in real-time
            today = datetime.now().strftime("%Y-%m-%d")
            if self._config.use_daily_folder and today != self._current_date_str:
                self.reset_handlers()

            if name in self._loggers:
                return self._loggers[name]

            logger = logging.getLogger(name)
            logger.setLevel(self._config.level)
            logger.propagate = False

            # Clear any pre-existing handlers
            if logger.handlers:
                for h in list(logger.handlers):
                    logger.removeHandler(h)

            # 1. Console Handler (if active)
            if self._config.enable_console:
                console_handler = LoggerFactory.create_console_handler(self._config)
                logger.addHandler(console_handler)

            # 2. File Handlers (if active)
            if self._config.enable_file:
                # Resolve primary module file route
                module_file = MODULE_TO_FILE.get(name, APP_LOG)
                
                # Fetch shared app.log handler
                app_handler = self._get_shared_file_handler(APP_LOG)
                logger.addHandler(app_handler)

                # Fetch shared error.log handler (level filtered inside handler creation)
                err_handler = self._get_shared_file_handler(ERROR_LOG)
                logger.addHandler(err_handler)

                # If the module has its own dedicated log (e.g. gemini.log, ffmpeg.log), add it
                if module_file != APP_LOG:
                    dedicated_handler = self._get_shared_file_handler(module_file)
                    logger.addHandler(dedicated_handler)

            self._loggers[name] = logger
            return logger

    def update_config(self, new_config: LoggerConfig) -> None:
        """Hot-swaps logging configuration dynamically at runtime.

        Recreates and updates all instantiated loggers and shared handlers instantly.

        Args:
            new_config: The new LoggerConfig target.
        """
        with self._lock:
            self._config = new_config
            self.reset_handlers()

    def reset_handlers(self) -> None:
        """Closes and clears all active file handlers and cached loggers.

        Extremely useful for rotating folders on date transitions or post configuration hot-swaps.
        """
        with self._lock:
            # Safely close shared handlers
            for handler in self._shared_handlers.values():
                try:
                    handler.close()
                except Exception:
                    pass
            self._shared_handlers.clear()

            # Refresh current logger handlers
            cached_names = list(self._loggers.keys())
            self._loggers.clear()
            
            # Recreate critical logs directories
            self._resolve_and_create_log_dir()

            # Repopulate cached loggers
            for name in cached_names:
                self.get_logger(name)

    def log_exception(self, logger_name: str, message: str, exception: Exception) -> None:
        """Centralized helper to log exceptions cleanly with standard traces.

        Args:
            logger_name: Name of target logger (e.g. "ui", "database").
            message: Explicit context message.
            exception: The raw Exception object.
        """
        logger = self.get_logger(logger_name)
        logger.error(f"{message} - Reason: {exception}", exc_info=exception)

"""Comprehensive Unit Tests for AIMS Pro Logger System.

Covers all handlers, formatters, managers, performance timers, and decorators.
"""

import os
import json
import shutil
import unittest
import tempfile
import logging
import asyncio
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.logger import (
    LoggerConfig,
    LoggerManager,
    LoggerFactory,
    PerformanceTimer,
    log_execution_time,
    LoggerException,
    LoggerConfigurationError,
    LogDirectoryCreationError,
    get_logger,
    log_exception,
)
from src.logger.constants import (
    APP_LOG,
    ERROR_LOG,
    GEMINI_LOG,
    DATABASE_LOG,
    COLOR_RESET,
)
from src.logger.log_formatter import ColoredFormatter, JsonFormatter


class TestLoggerExceptions(unittest.TestCase):
    """Verifies hierarchy of logger system exceptions."""

    def test_exception_inheritance(self):
        """Ensure all logger exceptions inherit from LoggerException."""
        self.assertTrue(issubclass(LoggerConfigurationError, LoggerException))
        self.assertTrue(issubclass(LogDirectoryCreationError, LoggerException))


class TestLoggerConfig(unittest.TestCase):
    """Verifies that LoggerConfig handles defaults and raises on invalid inputs."""

    def test_config_defaults(self):
        """Verify standard defaults."""
        config = LoggerConfig()
        self.assertEqual(config.level, "INFO")
        self.assertTrue(config.enable_console)
        self.assertTrue(config.enable_file)
        self.assertFalse(config.use_json)
        self.assertTrue(config.use_daily_folder)

    def test_config_invalid_level(self):
        """Verify invalid log levels trigger LoggerConfigurationError."""
        with self.assertRaises(LoggerConfigurationError):
            LoggerConfig(level="UNKNOWN")

    def test_config_invalid_bounds(self):
        """Verify negative bounds trigger LoggerConfigurationError."""
        with self.assertRaises(LoggerConfigurationError):
            LoggerConfig(max_bytes=0)
        with self.assertRaises(LoggerConfigurationError):
            LoggerConfig(backup_count=-1)

    def test_config_invalid_timed_rotation(self):
        """Verify timed rotation validations function properly."""
        with self.assertRaises(LoggerConfigurationError):
            LoggerConfig(use_timed_rotation=True, timed_when="every_hour")
        with self.assertRaises(LoggerConfigurationError):
            LoggerConfig(use_timed_rotation=True, timed_interval=0)


class TestFormatters(unittest.TestCase):
    """Tests for ColoredFormatter and JsonFormatter."""

    def test_colored_formatter(self):
        """Verify ColoredFormatter decorates records appropriately."""
        formatter = ColoredFormatter(
            fmt="%(levelname)s [%(name)s] %(message)s",
            use_colors=True,
            use_emojis=True
        )
        record = logging.LogRecord(
            name="gemini",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Processing user prompt",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        self.assertIn("🤖", formatted)  # Gemini emoji
        self.assertIn(COLOR_RESET, formatted)  # Color reset present

    def test_colored_formatter_no_color_no_emoji(self):
        """Verify disable flags render plain output."""
        formatter = ColoredFormatter(
            fmt="%(levelname)s [%(name)s] %(message)s",
            use_colors=False,
            use_emojis=False
        )
        record = logging.LogRecord(
            name="app",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Testing simplicity",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        self.assertNotIn("🚀", formatted)
        self.assertNotIn(COLOR_RESET, formatted)

    def test_json_formatter_serializes_cleanly(self):
        """Verify JSON log structures are valid JSON and preserve custom 'extra' elements."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="db",
            level=logging.WARNING,
            pathname="db_manager.py",
            lineno=10,
            msg="Schema mismatch detected",
            args=(),
            exc_info=None,
        )
        # Inject extra dynamic parameter
        record.__dict__["connection_id"] = "CONN_1234"

        formatted = formatter.format(record)
        payload = json.loads(formatted)

        self.assertEqual(payload["level"], "WARNING")
        self.assertEqual(payload["logger_name"], "db")
        self.assertEqual(payload["message"], "Schema mismatch detected")
        self.assertEqual(payload["extra"]["connection_id"], "CONN_1234")


class TestLoggerManager(unittest.TestCase):
    """Comprehensive orchestrated layer testing for LoggerManager."""

    def setUp(self):
        # Establish unique isolated temp directories for log outputs
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Reset LoggerManager Singleton instance cache completely
        LoggerManager._instance = None
        
        self.config = LoggerConfig(
            base_log_dir=self.temp_path,
            use_daily_folder=False,  # Flatten files for deterministic verification
            enable_console=True,
            enable_file=True,
        )
        self.manager = LoggerManager(config=self.config)

    def tearDown(self):
        # Reset Singleton cache to prevent cross-contamination
        self.manager.reset_handlers()
        LoggerManager._instance = None
        self.temp_dir.cleanup()

    def test_singleton_concurrency_isolation(self):
        """Verify strict double-checked thread safety of the manager Singleton."""
        inst_a = LoggerManager()
        inst_b = LoggerManager()
        self.assertIs(inst_a, inst_b)

        instances = []

        def spawn():
            instances.append(LoggerManager())

        threads = [threading.Thread(target=spawn) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        for inst in instances:
            self.assertIs(inst, inst_a)

    def test_logger_routing_to_correct_files(self):
        """Verify logged messages are correctly written to the app, error, and dedicated logs."""
        gemini_logger = self.manager.get_logger("gemini")
        
        gemini_logger.info("Sent user message to Gemini")
        gemini_logger.error("Failed to connect to API endpoint")

        # Flush logger handlers to write to disk
        for handler in gemini_logger.handlers:
            handler.flush()

        # Target expected files
        app_log_path = self.temp_path / APP_LOG
        error_log_path = self.temp_path / ERROR_LOG
        gemini_log_path = self.temp_path / GEMINI_LOG

        self.assertTrue(app_log_path.exists())
        self.assertTrue(error_log_path.exists())
        self.assertTrue(gemini_log_path.exists())

        # Check app.log content
        with open(app_log_path, "r", encoding="utf-8") as f:
            app_content = f.read()
        self.assertIn("Sent user message to Gemini", app_content)
        self.assertIn("Failed to connect to API endpoint", app_content)

        # Check error.log content (should ONLY have the error message)
        with open(error_log_path, "r", encoding="utf-8") as f:
            err_content = f.read()
        self.assertNotIn("Sent user message to Gemini", err_content)
        self.assertIn("Failed to connect to API endpoint", err_content)

        # Check gemini.log content
        with open(gemini_log_path, "r", encoding="utf-8") as f:
            gem_content = f.read()
        self.assertIn("Sent user message to Gemini", gem_content)
        self.assertIn("Failed to connect to API endpoint", gem_content)

    def test_shorthand_functions(self):
        """Verify get_logger and log_exception package-level API shorthand functions."""
        # Setup manager with isolated test config
        LoggerManager._instance = None
        mgr = LoggerManager(config=self.config)

        db_logger = get_logger("database")
        self.assertEqual(db_logger.name, "database")

        try:
            raise KeyError("test_key_missing")
        except Exception as e:
            log_exception("database", "Failed operation", e)

        # Flush
        for handler in db_logger.handlers:
            handler.flush()

        db_log_path = self.temp_path / DATABASE_LOG
        self.assertTrue(db_log_path.exists())
        with open(db_log_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Failed operation", content)
        self.assertIn("KeyError", content)

    def test_dynamic_config_hotswap(self):
        """Verify dynamic configuration hotswapping and reloading."""
        initial_level = self.manager.config.level
        self.assertEqual(initial_level, "INFO")

        # Swap to DEBUG
        new_cfg = LoggerConfig(
            base_log_dir=self.temp_path,
            use_daily_folder=False,
            level="DEBUG",
        )
        self.manager.update_config(new_cfg)
        self.assertEqual(self.manager.config.level, "DEBUG")


class TestPerformanceMetrics(unittest.TestCase):
    """Verifies PerformanceTimer and log_execution_time decorator correctness."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Isolated LoggerManager
        LoggerManager._instance = None
        self.config = LoggerConfig(
            base_log_dir=self.temp_path,
            use_daily_folder=False,
            level="INFO",
        )
        self.manager = LoggerManager(config=self.config)

    def tearDown(self):
        self.manager.reset_handlers()
        LoggerManager._instance = None
        self.temp_dir.cleanup()

    def test_performance_timer_context_manager(self):
        """Verify PerformanceTimer logs duration and memory delta metrics correctly."""
        with PerformanceTimer("heavy_render", logger_name="ffmpeg", monitor_memory=True):
            # Simulated dummy work
            data = [x * x for x in range(10000)]

        # Get logs and verify output
        ffmpeg_logger = self.manager.get_logger("ffmpeg")
        for h in ffmpeg_logger.handlers:
            h.flush()

        ffmpeg_log_path = self.temp_path / "ffmpeg.log"
        self.assertTrue(ffmpeg_log_path.exists())

        with open(ffmpeg_log_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Operation: 'heavy_render'", content)
        self.assertIn("Elapsed:", content)
        self.assertIn("Memory Delta:", content)

    def test_sync_log_execution_time_decorator(self):
        """Verify decorator tracks standard synchronous functions."""
        @log_execution_time(logger_name="ffmpeg")
        def run_sync_calc():
            return sum(i for i in range(1000))

        result = run_sync_calc()
        self.assertEqual(result, 499500)

        # Confirm logged
        ffmpeg_logger = self.manager.get_logger("ffmpeg")
        for h in ffmpeg_logger.handlers:
            h.flush()

        ffmpeg_log_path = self.temp_path / "ffmpeg.log"
        with open(ffmpeg_log_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("run_sync_calc", content)

    def test_async_log_execution_time_decorator(self):
        """Verify decorator tracks asynchronous functions seamlessly."""
        @log_execution_time(logger_name="gemini")
        async def run_async_mock():
            await asyncio.sleep(0.01)
            return "async_done"

        # Execute in async loop
        result = asyncio.run(run_async_mock())
        self.assertEqual(result, "async_done")

        # Confirm logged
        gemini_logger = self.manager.get_logger("gemini")
        for h in gemini_logger.handlers:
            h.flush()

        gemini_log_path = self.temp_path / "gemini.log"
        with open(gemini_log_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("run_async_mock", content)


if __name__ == "__main__":
    unittest.main()

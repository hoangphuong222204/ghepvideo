"""Custom formatters for Colored Console and JSON output in the AIMS Pro Logger."""

import json
import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from src.logger.constants import (
    COLOR_RESET,
    COLOR_BOLD,
    COLOR_DEBUG,
    COLOR_INFO,
    COLOR_WARNING,
    COLOR_ERROR,
    COLOR_CRITICAL,
    COLOR_TIME,
    COLOR_MODULE,
    LEVEL_EMOJIS,
    MODULE_EMOJIS,
)


class ColoredFormatter(logging.Formatter):
    """Custom standard logging Formatter that adds colors and emojis to console logs.

    Ensures highly professional readability with a structured aesthetic.
    """

    # Level color mapping
    LEVEL_COLORS = {
        logging.DEBUG: COLOR_DEBUG,
        logging.INFO: COLOR_INFO,
        logging.WARNING: COLOR_WARNING,
        logging.ERROR: COLOR_ERROR,
        logging.CRITICAL: COLOR_CRITICAL,
    }

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        use_colors: bool = True,
        use_emojis: bool = True,
    ) -> None:
        """Initializes the colored formatter.

        Args:
            fmt: The format string.
            datefmt: The date/time format string.
            use_colors: Whether to colorize console output.
            use_emojis: Whether to prepend emojis to logs based on level and module.
        """
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors
        self.use_emojis = use_emojis

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors, emojis, and high readability.

        Args:
            record: The LogRecord instance to format.

        Returns:
            The beautifully formatted string representation of the record.
        """
        # Capture original attributes to avoid corrupting the record permanently
        orig_msg = record.msg
        orig_levelname = record.levelname
        orig_name = record.name

        # 1. Level Emoji
        emoji = ""
        if self.use_emojis:
            # Check level emoji
            lvl_emoji = LEVEL_EMOJIS.get(record.levelno, "")
            # Check module emoji
            mod_emoji = ""
            for mod_key, mod_val in MODULE_EMOJIS.items():
                if mod_key in record.name.lower():
                    mod_emoji = mod_val
                    break
            
            emoji_part = f"{lvl_emoji} " if lvl_emoji else ""
            if mod_emoji:
                emoji_part += f"{mod_emoji} "
            emoji = emoji_part

        # 2. ANSI Colors
        if self.use_colors:
            color = self.LEVEL_COLORS.get(record.levelno, COLOR_RESET)
            # Standardize names
            record.levelname = f"{color}{record.levelname:<8}{COLOR_RESET}"
            record.name = f"{COLOR_MODULE}{record.name}{COLOR_RESET}"
            
            # Format timestamp manually or let Formatter do it, we'll prefix it with gray
            # Since standard logging.Formatter puts asctime, we can intercept it
            # But simpler to colorize the entire message/levels
            record.msg = f"{emoji}{orig_msg}"
        else:
            record.msg = f"{emoji}{orig_msg}"

        # Run standard formatter
        formatted = super().format(record)

        # Restore original attributes
        record.msg = orig_msg
        record.levelname = orig_levelname
        record.name = orig_name

        return formatted


class JsonFormatter(logging.Formatter):
    """Custom logging Formatter that outputs log records as structured JSON.

    Excellent for enterprise monitoring, log aggregation, and system ingestion.
    """

    def __init__(
        self,
        datefmt: Optional[str] = "%Y-%m-%dT%H:%M:%S.%fZ",
    ) -> None:
        """Initializes the JSON formatter."""
        super().__init__(None, datefmt)

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record into a structured JSON string.

        Args:
            record: The LogRecord instance to format.

        Returns:
            A JSON-serialized string of log attributes.
        """
        # Handle datetime serialization
        timestamp = datetime.fromtimestamp(record.created).strftime(self.datefmt or "%Y-%m-%dT%H:%M:%S.%fZ")

        # Build payload
        log_payload: Dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger_name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "filename": record.filename,
            "lineno": record.lineno,
            "func_name": record.funcName,
            "process": record.process,
            "thread_name": record.threadName,
        }

        # Siphon exception info if present
        if record.exc_info:
            log_payload["exception"] = {
                "type": str(record.exc_info[0].__name__ if record.exc_info[0] else ""),
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Include custom dynamic fields injected via the extra={} dictionary parameter
        # Filter standard record properties
        standard_fields = {
            "args", "asctime", "created", "exc_info", "exc_text", "filename",
            "funcName", "levelname", "levelno", "lineno", "module", "msecs",
            "msg", "name", "pathname", "process", "processName", "relativeCreated",
            "stack_info", "thread", "threadName"
        }
        
        extra_fields = {
            k: v for k, v in record.__dict__.items()
            if k not in standard_fields and not k.startswith("_")
        }
        
        if extra_fields:
            log_payload["extra"] = extra_fields

        # Serialize
        return json.dumps(log_payload, ensure_ascii=False)

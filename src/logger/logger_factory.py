"""Logger Factory for constructing and configuring Python loggers dynamically."""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Union, List, Optional
from src.logger.log_config import LoggerConfig
from src.logger.log_formatter import ColoredFormatter, JsonFormatter
from src.logger.constants import DEFAULT_CONSOLE_FORMAT, DEFAULT_FILE_FORMAT


class LoggerFactory:
    """Enterprise factory class responsible for building configured handlers and loggers."""

    @staticmethod
    def create_console_handler(config: LoggerConfig) -> logging.Handler:
        """Creates a beautifully colorized/emoji-enabled Console Handler.

        Args:
            config: LoggerConfig containing formatting preferences.

        Returns:
            A standard logging.StreamHandler configured for console output.
        """
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(config.level)

        # Set Custom ColoredFormatter
        formatter = ColoredFormatter(
            fmt=DEFAULT_CONSOLE_FORMAT,
            use_colors=config.use_colors,
            use_emojis=config.use_emojis,
        )
        handler.setFormatter(formatter)
        return handler

    @staticmethod
    def create_file_handler(
        config: LoggerConfig,
        file_path: Union[str, Path]
    ) -> logging.Handler:
        """Creates a highly durable, rotating or timed rotating file Handler.

        Args:
            config: LoggerConfig containing backup, rotation and format details.
            file_path: The absolute/relative path of the target log file.

        Returns:
            A logging.Handler instance (either RotatingFileHandler or TimedRotatingFileHandler).
        """
        file_path = Path(file_path)
        
        # Ensure parent directory is fully created
        file_path.parent.mkdir(parents=True, exist_ok=True)

        handler: logging.Handler
        if config.use_timed_rotation:
            handler = TimedRotatingFileHandler(
                filename=str(file_path),
                when=config.timed_when,
                interval=config.timed_interval,
                backupCount=config.backup_count,
                encoding="utf-8",
            )
        else:
            handler = RotatingFileHandler(
                filename=str(file_path),
                maxBytes=config.max_bytes,
                backupCount=config.backup_count,
                encoding="utf-8",
            )

        handler.setLevel(config.level)

        # Format as JSON or Standard
        if config.use_json:
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(DEFAULT_FILE_FORMAT)

        handler.setFormatter(formatter)
        return handler

    @classmethod
    def configure_logger(
        cls,
        name: str,
        config: LoggerConfig,
        file_path: Optional[Union[str, Path]] = None,
    ) -> logging.Logger:
        """Constructs and fully configures a Logger instance with handlers.

        Args:
            name: The dotted module or specific name of the logger (e.g. "gemini", "db").
            config: The unified system LoggerConfig dataclass.
            file_path: Optional dedicated log file path. If omitted, no file writing occurs.

        Returns:
            A customized logging.Logger instance.
        """
        logger = logging.getLogger(name)
        logger.setLevel(config.level)

        # Prevent double handling/propagation issues if already configured
        logger.propagate = False
        
        # Clean existing handlers
        if logger.handlers:
            for h in list(logger.handlers):
                logger.removeHandler(h)

        # Add Console Handler if requested
        if config.enable_console:
            console_handler = cls.create_console_handler(config)
            logger.addHandler(console_handler)

        # Add File Handler if requested and a file path is provided
        if config.enable_file and file_path:
            file_handler = cls.create_file_handler(config, file_path)
            logger.addHandler(file_handler)

        return logger

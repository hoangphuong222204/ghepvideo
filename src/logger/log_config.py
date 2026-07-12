"""Logging Configuration Dataclass for AIMS Pro Logger."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, Optional
from src.logger.exceptions import LoggerConfigurationError


@dataclass
class LoggerConfig:
    """Dataclass holding all configuration parameters for the logging system.

    Attributes:
        base_log_dir: The directory where log files will be saved.
        level: Default log level (e.g., "INFO", "DEBUG").
        enable_console: Whether to print logs to the console.
        enable_file: Whether to save logs to files.
        use_colors: Use ANSI colors in console log formatting.
        use_emojis: Prepend logs with decorative and descriptive emojis.
        use_json: Format file logs as structured JSON objects.
        use_daily_folder: If True, creates and writes logs into a nested folder named by date (YYYY-MM-DD).
        max_bytes: Maximum size per log file before rotating (for RotatingFileHandler).
        backup_count: Number of rotated log files to retain.
        use_timed_rotation: Use TimedRotatingFileHandler instead of RotatingFileHandler.
        timed_when: Time interval type for timed rotation (e.g., "midnight", "D", "H").
        timed_interval: Multiplier for the timed interval.
    """
    base_log_dir: Union[str, Path] = "logs"
    level: str = "INFO"
    enable_console: bool = True
    enable_file: bool = True
    use_colors: bool = True
    use_emojis: bool = True
    use_json: bool = False
    use_daily_folder: bool = True
    max_bytes: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 7
    use_timed_rotation: bool = False
    timed_when: str = "midnight"
    timed_interval: int = 1

    def __post_init__(self) -> None:
        """Performs basic validation and sanitization of the config attributes."""
        # Clean and convert path
        if isinstance(self.base_log_dir, str):
            self.base_log_dir = Path(self.base_log_dir.strip())

        # Validate Level
        self.level = self.level.upper().strip()
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.level not in valid_levels:
            raise LoggerConfigurationError(
                f"Invalid log level: {self.level}. Must be one of {valid_levels}"
            )

        # Validate rotating bounds
        if self.max_bytes <= 0:
            raise LoggerConfigurationError("max_bytes must be a positive integer greater than 0")
        if self.backup_count < 0:
            raise LoggerConfigurationError("backup_count cannot be negative")

        # Validate timed rotation parameters
        if self.use_timed_rotation:
            valid_whens = {"S", "M", "H", "D", "W0", "W1", "W2", "W3", "W4", "W5", "W6", "midnight"}
            if self.timed_when not in valid_whens:
                raise LoggerConfigurationError(
                    f"Invalid timed_when: {self.timed_when}. Must be one of {valid_whens}"
                )
            if self.timed_interval <= 0:
                raise LoggerConfigurationError("timed_interval must be a positive integer greater than 0")

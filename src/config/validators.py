"""Validation rules and utilities for the AI Marketing Studio PRO Configuration System.

This module provides structural and business-level constraints validation for all configuration
parameters. It ensures that any invalid settings are caught early at load or update time.
"""

import re
from pathlib import Path
from typing import Any, List, Set
from src.config.exceptions import ConfigValidationError


class ConfigValidators:
    """Static validation methods for configuration field constraints."""

    # Regex to match resolutions like 1080x1920 or 1920x1080
    RESOLUTION_PATTERN = re.compile(r"^\d+x\d+$")

    # Allowed standard portrait and landscape high-definition resolutions
    STANDARD_RESOLUTIONS: Set[str] = {"720x1280", "1080x1920", "1440x2560", "2160x3840"}

    # Common audio sample rates supported by standard TTS and audio engines
    ALLOWED_SAMPLE_RATES: Set[int] = {8000, 11025, 16000, 22050, 24000, 32000, 44100, 48000}

    @staticmethod
    def validate_non_empty_string(field_name: str, val: Any) -> str:
        """Validates that a field is a non-empty string.

        Args:
            field_name: Name of the field for error context.
            val: The value to validate.

        Returns:
            The validated string.

        Raises:
            ConfigValidationError: If validation fails.
        """
        if not isinstance(val, str):
            raise ConfigValidationError(f"Field '{field_name}' must be a string, got {type(val).__name__}.")
        cleaned = val.strip()
        if not cleaned:
            raise ConfigValidationError(f"Field '{field_name}' cannot be empty or whitespace only.")
        return cleaned

    @staticmethod
    def validate_language(val: Any) -> Any:
        """Validates the application interface language code."""
        from src.config.config_models import AppLanguage
        if isinstance(val, AppLanguage):
            return val
        cleaned = str(val).strip().lower()
        try:
            return AppLanguage(cleaned)
        except ValueError:
            raise ConfigValidationError(
                f"Unsupported language '{cleaned}'. Supported values: {[e.value for e in AppLanguage]}"
            )

    @staticmethod
    def validate_theme(val: Any) -> Any:
        """Validates the application theme."""
        from src.config.config_models import AppTheme
        if isinstance(val, AppTheme):
            return val
        cleaned = str(val).strip()
        try:
            return AppTheme(cleaned)
        except ValueError:
            raise ConfigValidationError(
                f"Unsupported theme '{cleaned}'. Supported values: {[e.value for e in AppTheme]}"
            )

    @staticmethod
    def validate_temperature(val: float) -> float:
        """Validates that the Gemini LLM temperature is within safe bounds [0.0, 2.0]."""
        try:
            val_float = float(val)
        except (ValueError, TypeError):
            raise ConfigValidationError(f"Temperature must be a number, got {val}.")
        
        if not (0.0 <= val_float <= 2.0):
            raise ConfigValidationError(f"Temperature must be between 0.0 and 2.0, got {val_float}.")
        return val_float

    @staticmethod
    def validate_top_p(val: float) -> float:
        """Validates that top_p parameter is within standard boundaries [0.0, 1.0]."""
        try:
            val_float = float(val)
        except (ValueError, TypeError):
            raise ConfigValidationError(f"Top P must be a float, got {val}.")
        
        if not (0.0 <= val_float <= 1.0):
            raise ConfigValidationError(f"Top P must be between 0.0 and 1.0, got {val_float}.")
        return val_float

    @staticmethod
    def validate_max_tokens(val: int) -> int:
        """Validates that the LLM max tokens value is a positive integer."""
        try:
            val_int = int(val)
        except (ValueError, TypeError):
            raise ConfigValidationError(f"Max tokens must be an integer, got {val}.")
        
        if val_int <= 0:
            raise ConfigValidationError(f"Max tokens must be a positive integer, got {val_int}.")
        return val_int

    @staticmethod
    def validate_device(val: Any) -> Any:
        """Validates execution device settings."""
        from src.config.config_models import DeviceType
        if isinstance(val, DeviceType):
            return val
        cleaned = str(val).strip().lower()
        try:
            return DeviceType(cleaned)
        except ValueError:
            raise ConfigValidationError(
                f"Unsupported execution device '{cleaned}'. Supported values: {[e.value for e in DeviceType]}"
            )

    @staticmethod
    def validate_sample_rate(val: int) -> int:
        """Validates that the Fish Speech output sample rate is mathematically standard."""
        try:
            val_int = int(val)
        except (ValueError, TypeError):
            raise ConfigValidationError(f"Sample rate must be an integer, got {val}.")
        
        if val_int not in ConfigValidators.ALLOWED_SAMPLE_RATES:
            raise ConfigValidationError(
                f"Invalid sample rate {val_int}Hz. Supported: {sorted(list(ConfigValidators.ALLOWED_SAMPLE_RATES))}"
            )
        return val_int

    @staticmethod
    def validate_threads(val: int) -> int:
        """Validates that the CPU processing thread allotment is positive and reasonable."""
        try:
            val_int = int(val)
        except (ValueError, TypeError):
            raise ConfigValidationError(f"Thread count must be an integer, got {val}.")
        
        if not (1 <= val_int <= 128):
            raise ConfigValidationError(f"FFmpeg threads must be between 1 and 128, got {val_int}.")
        return val_int

    @staticmethod
    def validate_resolution(val: str, allow_custom: bool = False) -> str:
        """Validates resolution values. Asserts 720x1280, 1080x1920, 1440x2560, or 2160x3840 unless custom mode enabled."""
        cleaned = ConfigValidators.validate_non_empty_string("resolution", val)
        if not ConfigValidators.RESOLUTION_PATTERN.match(cleaned):
            raise ConfigValidationError(
                f"Resolution must follow 'WIDTHxHEIGHT' pattern (e.g., '1080x1920'), got '{cleaned}'."
            )
        if not allow_custom and cleaned not in ConfigValidators.STANDARD_RESOLUTIONS:
            raise ConfigValidationError(
                f"Resolution '{cleaned}' is not supported. Standard: {sorted(list(ConfigValidators.STANDARD_RESOLUTIONS))}. "
                f"Set custom resolution mode to bypass this constraint."
            )
        return cleaned

    @staticmethod
    def validate_fps(val: int) -> int:
        """Validates frame rate configuration limits."""
        try:
            val_int = int(val)
        except (ValueError, TypeError):
            raise ConfigValidationError(f"FPS must be an integer, got {val}.")
        
        if not (1 <= val_int <= 120):
            raise ConfigValidationError(f"Video FPS must be between 1 and 120 frames per second, got {val_int}.")
        return val_int

    @staticmethod
    def validate_codec(val: Any) -> Any:
        """Validates video format codec configurations."""
        from src.config.config_models import VideoCodec
        if isinstance(val, VideoCodec):
            return val
        cleaned = str(val).strip().lower()
        try:
            return VideoCodec(cleaned)
        except ValueError:
            raise ConfigValidationError(
                f"Unsupported video codec '{cleaned}'. Supported values: {[e.value for e in VideoCodec]}"
            )

    @staticmethod
    def validate_crf(val: int) -> int:
        """Validates the Constant Rate Factor (CRF) quality metric [0, 51]."""
        try:
            val_int = int(val)
        except (ValueError, TypeError):
            raise ConfigValidationError(f"CRF must be an integer, got {val}.")
        
        if not (0 <= val_int <= 51):
            raise ConfigValidationError(f"CRF quality factor must be between 0 (lossless) and 51, got {val_int}.")
        return val_int

    @staticmethod
    def validate_volume(val: float) -> float:
        """Validates standard gain multiplier ranges [0.0, 2.0]."""
        try:
            val_float = float(val)
        except (ValueError, TypeError):
            raise ConfigValidationError(f"Volume must be a decimal value, got {val}.")
        
        if not (0.0 <= val_float <= 2.0):
            raise ConfigValidationError(f"Volume scale factor must be between 0.0 (muted) and 2.0, got {val_float}.")
        return val_float

    @staticmethod
    def validate_sqlite_path(val: str) -> str:
        """Validates that the database path expression represents a valid name."""
        cleaned = ConfigValidators.validate_non_empty_string("sqlite_path", val)
        if cleaned == ":memory:":
            return cleaned
        
        # Ensure it has a database-like extension
        path = Path(cleaned)
        if path.suffix not in {".db", ".sqlite", ".sqlite3"}:
            raise ConfigValidationError(
                f"SQLite database file should have a '.db' or '.sqlite' suffix, got '{cleaned}'."
            )
        return cleaned


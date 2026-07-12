"""Constants and default configurations for the AIMS Pro Logger System."""

import logging
from typing import Dict

# Log File Names as required
APP_LOG = "app.log"
ERROR_LOG = "error.log"
GEMINI_LOG = "gemini.log"
DATABASE_LOG = "database.log"
FISHSPEECH_LOG = "fishspeech.log"
FFMPEG_LOG = "ffmpeg.log"
UI_LOG = "ui.log"

# Log Module Mapper to files
MODULE_TO_FILE: Dict[str, str] = {
    "app": APP_LOG,
    "gemini": GEMINI_LOG,
    "database": DATABASE_LOG,
    "db": DATABASE_LOG,
    "fishspeech": FISHSPEECH_LOG,
    "ffmpeg": FFMPEG_LOG,
    "ui": UI_LOG,
}

# ANSI Color Codes for Console Logging
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"

COLOR_DEBUG = "\033[36m"      # Cyan
COLOR_INFO = "\033[32m"       # Green
COLOR_WARNING = "\033[33m"    # Yellow
COLOR_ERROR = "\033[31m"      # Red
COLOR_CRITICAL = "\033[1;31m" # Bold Red
COLOR_TIME = "\033[90m"       # Grey
COLOR_MODULE = "\033[35m"     # Magenta

# Level Emojis
LEVEL_EMOJIS: Dict[int, str] = {
    logging.DEBUG: "🔍",
    logging.INFO: "ℹ️",
    logging.WARNING: "⚠️",
    logging.ERROR: "❌",
    logging.CRITICAL: "🚨",
}

# Module-specific Emojis
MODULE_EMOJIS: Dict[str, str] = {
    "app": "🚀",
    "gemini": "🤖",
    "database": "🗄️",
    "db": "🗄️",
    "fishspeech": "🗣️",
    "ffmpeg": "🎬",
    "ui": "🖥️",
    "performance": "⏱️",
}

# Default Format Patterns
DEFAULT_CONSOLE_FORMAT = (
    "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
DEFAULT_FILE_FORMAT = (
    "%(asctime)s [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
)

"""System-wide constants and configuration boundaries for the AI layer."""

# Default Models
DEFAULT_TEXT_MODEL = "gemini-2.5-flash"
DEFAULT_PRO_MODEL = "gemini-2.5-pro"

# Model Capabilities Map (Max Input and Output Tokens)
MODEL_CAPABILITIES = {
    "gemini-2.5-flash": {
        "max_input_tokens": 1000000,
        "max_output_tokens": 8192,
        "supports_system_instruction": True,
        "supports_json_mode": True,
        "supports_tools": True,
    },
    "gemini-2.5-pro": {
        "max_input_tokens": 2000000,
        "max_output_tokens": 8192,
        "supports_system_instruction": True,
        "supports_json_mode": True,
        "supports_tools": True,
    },
    "gemini-2.5-flash-lite": {
        "max_input_tokens": 1000000,
        "max_output_tokens": 8192,
        "supports_system_instruction": True,
        "supports_json_mode": True,
        "supports_tools": True,
    },
    "gemini-3.5-flash": {
        "max_input_tokens": 1000000,
        "max_output_tokens": 8192,
        "supports_system_instruction": True,
        "supports_json_mode": True,
        "supports_tools": True,
    },
}

# Parameter Validation Ranges
TEMP_MIN = 0.0
TEMP_MAX = 2.0
TOP_P_MIN = 0.0
TOP_P_MAX = 1.0
TOP_K_MIN = 1
TOP_K_MAX = 100

# Rate Limiter Settings
DEFAULT_RPM = 15
DEFAULT_TPM = 30000

# Cache Constants
CACHE_DB_NAME = "ai_cache.db"
DEFAULT_CACHE_TTL = 86400  # 24 hours in seconds

# Safety Categories and Thresholds (Gemini-specific representation)
SAFETY_HARM_CATEGORIES = [
    "HARM_CATEGORY_HARASSMENT",
    "HARM_CATEGORY_HATE_SPEECH",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "HARM_CATEGORY_DANGEROUS_CONTENT",
]

SAFETY_THRESHOLD_BLOCK_NONE = "BLOCK_NONE"
SAFETY_THRESHOLD_BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE"
SAFETY_THRESHOLD_BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE"

# Standard Roles
ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_ASSISTANT = "model"

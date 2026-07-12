"""Input and configuration parameter validation layer."""

from typing import Dict, Any, Optional
from src.ai.exceptions import ValidationError
from src.ai.constants import (
    MODEL_CAPABILITIES,
    TEMP_MIN,
    TEMP_MAX,
    TOP_P_MIN,
    TOP_P_MAX,
    TOP_K_MIN,
    TOP_K_MAX,
)

class RequestValidator:
    """Validator class ensuring payload and configuration inputs conform to system specifications."""

    @staticmethod
    def validate_model_name(model_name: str) -> None:
        """Validates that the selected model is supported."""
        if not model_name:
            raise ValidationError("Model name cannot be empty.")
        
        if model_name not in MODEL_CAPABILITIES:
            allowed = list(MODEL_CAPABILITIES.keys())
            raise ValidationError(
                f"Model '{model_name}' is not supported by this application. Supported models: {allowed}"
            )

    @staticmethod
    def validate_generation_config(
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        max_output_tokens: Optional[int] = None,
        model_name: Optional[str] = None,
    ) -> None:
        """Validates that parameters fall within standard logical boundaries."""
        
        # Temperature
        if temperature is not None:
            if not (TEMP_MIN <= temperature <= TEMP_MAX):
                raise ValidationError(f"Temperature must be between {TEMP_MIN} and {TEMP_MAX}. Received: {temperature}")

        # Top_p
        if top_p is not None:
            if not (TOP_P_MIN <= top_p <= TOP_P_MAX):
                raise ValidationError(f"Top_p must be between {TOP_P_MIN} and {TOP_P_MAX}. Received: {top_p}")

        # Top_k
        if top_k is not None:
            if not (TOP_K_MIN <= top_k <= TOP_K_MAX):
                raise ValidationError(f"Top_k must be between {TOP_K_MIN} and {TOP_K_MAX}. Received: {top_k}")

        # Max Output Tokens
        if max_output_tokens is not None:
            if max_output_tokens <= 0:
                raise ValidationError(f"max_output_tokens must be positive. Received: {max_output_tokens}")
            
            if model_name and model_name in MODEL_CAPABILITIES:
                max_allowed = MODEL_CAPABILITIES[model_name]["max_output_tokens"]
                if max_output_tokens > max_allowed:
                    raise ValidationError(
                        f"max_output_tokens {max_output_tokens} exceeds max allowed limits of {max_allowed} for model '{model_name}'."
                    )

"""Request and parameter validation layer for the Script Engine."""

from typing import Optional
from src.script_engine.exceptions import ValidationError
from src.script_engine.models import ScriptRequest
from src.script_engine.constants import SUPPORTED_STYLES, SUPPORTED_PLATFORMS


class ScriptRequestValidator:
    """Validator class ensuring payload and configuration inputs conform to system specifications."""

    @staticmethod
    def validate_request(request: ScriptRequest) -> None:
        """Validates all attributes of a ScriptRequest object.

        Raises:
            ValidationError: If any attribute is outside of accepted bounds.
        """
        # Validate product_name
        if not request.product_name or not request.product_name.strip():
            raise ValidationError("Product name cannot be empty.")

        # Validate product_description
        if not request.product_description or not request.product_description.strip():
            raise ValidationError("Product description cannot be empty.")

        # Validate quantity (1-50)
        if not (1 <= request.quantity <= 50):
            raise ValidationError(
                f"Requested quantity must be between 1 and 50. Received: {request.quantity}"
            )

        # Validate duration_seconds (positive reasonable range, say 5 to 600)
        if not (5 <= request.duration_seconds <= 600):
            raise ValidationError(
                f"Target duration must be between 5 and 600 seconds. Received: {request.duration_seconds}"
            )

        # Validate style if specified
        if request.style and request.style not in SUPPORTED_STYLES:
            raise ValidationError(
                f"Style '{request.style}' is not supported. Supported: {SUPPORTED_STYLES}"
            )

        # Validate platform if specified
        if request.platform and request.platform not in SUPPORTED_PLATFORMS:
            # We allow it for future-ready custom, but let's log a warning or support standard ones
            pass

        # Validate min_quality_score
        if not (0.0 <= request.min_quality_score <= 100.0):
            raise ValidationError(
                f"Minimum quality score must be between 0.0 and 100.0. Received: {request.min_quality_score}"
            )

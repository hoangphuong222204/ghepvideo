"""ABTesting manager enabling comparative split evaluation of prompts in production."""

import random
from typing import Dict, Any, Tuple
from src.prompt_engine.models import ABTestConfig


class ABTestingManager:
    """Orchestrates traffic routing and conversion logging to identify the most performant prompt variants."""

    def __init__(self) -> None:
        """Initializes the manager."""
        # Memory-backed repository for tracking session configs in development/testing
        self._tests: Dict[str, ABTestConfig] = {}

    def create_test(
        self,
        test_id: str,
        name: str,
        template_name: str,
        version_a: str,
        version_b: str,
        allocation_ratio_a: float = 0.5,
    ) -> ABTestConfig:
        """Registers a new A/B testing experiment configuration."""
        config = ABTestConfig(
            test_id=test_id,
            name=name,
            template_name=template_name,
            version_a=version_a,
            version_b=version_b,
            allocation_ratio_a=allocation_ratio_a,
        )
        self._tests[test_id] = config
        return config

    def select_version(self, config: ABTestConfig) -> Tuple[str, str]:
        """Routes traffic to variant A or B according to the configured split allocation ratio.

        Returns:
            Tuple containing:
            - selected_version (str): Either version_a or version_b
            - label (str): "A" or "B" for auditing
        """
        if not config.is_active:
            # Fallback to A if test is inactive
            return config.version_a, "A"

        rand_val = random.random()
        if rand_val < config.allocation_ratio_a:
            config.impressions_a += 1
            return config.version_a, "A"
        else:
            config.impressions_b += 1
            return config.version_b, "B"

    def record_conversion(self, config: ABTestConfig, variant: str) -> None:
        """Records a successful business goal achievement (conversion) for a given variant ("A" or "B")."""
        variant_upper = variant.strip().upper()
        if variant_upper == "A":
            config.conversions_a += 1
        elif variant_upper == "B":
            config.conversions_b += 1

    def get_test_stats(self, config: ABTestConfig) -> Dict[str, Any]:
        """Calculates conversion rates and metrics for both variants."""
        rate_a = (
            (config.conversions_a / config.impressions_a)
            if config.impressions_a > 0
            else 0.0
        )
        rate_b = (
            (config.conversions_b / config.impressions_b)
            if config.impressions_b > 0
            else 0.0
        )

        improvement = 0.0
        if rate_a > 0:
            improvement = ((rate_b - rate_a) / rate_a) * 100.0

        # Simple recommendation engine
        winner = "Draw"
        if config.impressions_a >= 10 and config.impressions_b >= 10:
            if rate_a > rate_b * 1.1:
                winner = "Variant A"
            elif rate_b > rate_a * 1.1:
                winner = "Variant B"

        return {
            "test_id": config.test_id,
            "name": config.name,
            "template_name": config.template_name,
            "variant_a": {
                "version": config.version_a,
                "impressions": config.impressions_a,
                "conversions": config.conversions_a,
                "conversion_rate": round(rate_a, 4),
            },
            "variant_b": {
                "version": config.version_b,
                "impressions": config.impressions_b,
                "conversions": config.conversions_b,
                "conversion_rate": round(rate_b, 4),
            },
            "improvement_b_vs_a_percent": round(improvement, 2),
            "leading_variant": winner,
        }

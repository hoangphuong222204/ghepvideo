"""Orchestrates AI-driven analysis of marketing products, extracting key selling and behavioral metrics."""

import logging
from typing import Optional
from src.ai import AIManager, AIRequest, GenerationConfig
from src.script_engine.models import ProductAnalysis
from src.script_engine.prompt_generator import PromptGenerator
from src.script_engine.json_parser import JSONParser
from src.logger.logger_manager import LoggerManager

logger = LoggerManager().get_logger("script_engine.product_analyzer")


class ProductAnalyzer:
    """Uses advanced AI capabilities via AI Gateway to perform detailed strategic product reviews."""

    def __init__(self, ai_manager: Optional[AIManager] = None) -> None:
        """Initializes ProductAnalyzer with specified AI gateway manager."""
        self._ai_manager = ai_manager or AIManager()

    def analyze(self, product_name: str, product_description: str) -> ProductAnalysis:
        """Analyzes product details synchronously and returns structured behavioral attributes."""
        logger.info(f"Analyzing product: {product_name}")
        
        system_prompt = PromptGenerator.get_product_analysis_system_prompt()
        user_prompt = PromptGenerator.get_product_analysis_user_prompt(product_name, product_description)

        # Dispatch via Module 04 AI Gateway
        request = AIRequest(
            prompt=user_prompt,
            model_name="gemini-2.5-flash",
            config=GenerationConfig(
                temperature=0.2,
                system_instruction=system_prompt,
                json_mode=True,
            )
        )

        response = self._ai_manager.generate(request)
        return JSONParser.parse_product_analysis(response.text)

    async def analyze_async(self, product_name: str, product_description: str) -> ProductAnalysis:
        """Analyzes product details asynchronously and returns structured behavioral attributes."""
        logger.info(f"Analyzing product (async): {product_name}")
        
        system_prompt = PromptGenerator.get_product_analysis_system_prompt()
        user_prompt = PromptGenerator.get_product_analysis_user_prompt(product_name, product_description)

        # Dispatch via Module 04 AI Gateway
        request = AIRequest(
            prompt=user_prompt,
            model_name="gemini-2.5-flash",
            config=GenerationConfig(
                temperature=0.2,
                system_instruction=system_prompt,
                json_mode=True,
            )
        )

        response = await self._ai_manager.generate_async(request)
        return JSONParser.parse_product_analysis(response.text)

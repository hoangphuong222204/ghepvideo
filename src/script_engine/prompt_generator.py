"""Assembles and validates system and user prompts for script generation and product analysis."""

from typing import Dict, Any, Optional
from src.script_engine.exceptions import ValidationError


class PromptGenerator:
    """Enterprise Prompt Engine composing strict-structured prompts for AI marketing assets."""

    @staticmethod
    def get_product_analysis_system_prompt() -> str:
        """Returns the system instruction for analyzing products."""
        return (
            "You are a professional product marketing analyst. "
            "Analyze the provided product name and description and extract structured marketing assets. "
            "Your output MUST be a valid JSON object matching the following schema exactly, with no additional text or markdown wrappers:\n"
            "{\n"
            "  \"category\": \"Brief categorized product vertical\",\n"
            "  \"selling_points\": [\"Unique selling proposition 1\", \"Unique selling proposition 2\"],\n"
            "  \"target_audience\": [\"Specific target demographic buyer persona 1\", \"Buyer persona 2\"],\n"
            "  \"buying_motivations\": [\"Why they buy 1\", \"Why they buy 2\"],\n"
            "  \"usage_scenarios\": [\"In what exact context they use this product 1\", \"Context 2\"]\n"
            "}"
        )

    @staticmethod
    def get_product_analysis_user_prompt(product_name: str, product_description: str) -> str:
        """Assembles user prompt for product analysis."""
        if not product_name or not product_description:
            raise ValidationError("Product name and description are required for prompt generation.")
        return (
            f"Product Name: {product_name}\n"
            f"Product Description: {product_description}\n\n"
            "Analyze the product and generate the JSON payload matching the requested format."
        )

    @staticmethod
    def get_script_generation_system_prompt() -> str:
        """Returns the system instruction for script generation."""
        return (
            "You are an elite conversion copywriting specialist and short-form video creator for platforms like TikTok, Shopee, Reels, and Shorts.\n"
            "Your goal is to generate high-converting, natural-sounding video scripts in Vietnamese.\n\n"
            "CRITICAL GUIDELINES FOR VIETNAMESE SPEECH OPTIMIZATION:\n"
            "1. ENGLISH WORDS: Adapt any English technical/brand terms (like TikTok, sale, cream) into Vietnamese phonetic equivalents (e.g. tíc-tóc, seo, cờ-rim) or append pronunciation cues, so it sounds perfectly natural when read out loud.\n"
            "2. NUMBER EXPANSION: Expand ALL digits/numbers (like 100, 2026, 5) into spelled-out Vietnamese words (e.g., một trăm, hai nghìn không trăm hai mươi sáu, năm) so the speaker reads them with correct cadence.\n"
            "3. PACING: Write with natural, conversational, energetic rhythm. Avoid overly long sentences. Ensure there is a strong hook in the first 3 seconds.\n\n"
            "Your output MUST be a valid JSON object matching this schema exactly, with no additional text or markdown wrappers:\n"
            "{\n"
            "  \"scripts\": [\n"
            "    {\n"
            "      \"title\": \"Creative Title for Script\",\n"
            "      \"style\": \"Specific Style Name\",\n"
            "      \"platform\": \"Target Platform\",\n"
            "      \"estimated_duration\": 45.0,\n"
            "      \"word_count\": 110,\n"
            "      \"scenes\": [\n"
            "        {\n"
            "          \"scene_number\": 1,\n"
            "          \"visual_description\": \"Camera angle and visual action description (Vietnamese)\",\n"
            "          \"spoken_text\": \"Spoken voiceover text with phonetic English and expanded numbers (Vietnamese)\",\n"
            "          \"duration_seconds\": 8.0\n"
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}"
        )

    @staticmethod
    def get_script_generation_user_prompt(
        product_name: str,
        product_description: str,
        style: str,
        style_guideline: str,
        platform: str,
        duration_seconds: int,
        brand_name: Optional[str] = None,
        target_audience: Optional[str] = None,
        core_benefit: Optional[str] = None,
        quantity: int = 1,
    ) -> str:
        """Compiles user prompt injected with concrete parameters for generating unique marketing scripts."""
        if not product_name or not product_description:
            raise ValidationError("Product name and description are required for prompt generation.")

        user_prompt = (
            f"Generate exactly {quantity} unique video marketing script(s) matching the requested JSON format.\n\n"
            f"PRODUCT INFO:\n"
            f"- Product Name: {product_name}\n"
            f"- Brand: {brand_name or 'N/A'}\n"
            f"- Description: {product_description}\n"
            f"- Core Benefit: {core_benefit or 'N/A'}\n"
            f"- Target Audience: {target_audience or 'N/A'}\n\n"
            f"SPECIFICATIONS:\n"
            f"- Target Style: {style}\n"
            f"- Style Guidelines: {style_guideline}\n"
            f"- Platform: {platform}\n"
            f"- Desired Speech Duration: {duration_seconds} seconds\n\n"
            "Make sure the script flows nicely, highlights unique selling arguments, has a strong opening hook, and uses phonetic terms and expanded numbers."
        )

        return user_prompt

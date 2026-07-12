"""High-level facade class exposing AI Script Engine APIs for FastAPI and NiceGUI applications."""

from typing import List, Optional
from src.ai import AIManager
from src.script_engine.models import ScriptRequest, VideoScript, ProductAnalysis
from src.script_engine.script_manager import ScriptManager
from src.script_engine.product_analyzer import ProductAnalyzer
from src.script_engine.constants import SUPPORTED_STYLES, SUPPORTED_PLATFORMS


class ScriptEngine:
    """The central business intelligence gateway for short-form marketing script assets."""

    def __init__(self, ai_manager: Optional[AIManager] = None) -> None:
        """Initializes ScriptEngine with optional specified AIManager instance."""
        self._ai_manager = ai_manager or AIManager()
        self._script_manager = ScriptManager(self._ai_manager)
        self._product_analyzer = ProductAnalyzer(self._ai_manager)

    def generate_scripts(self, request: ScriptRequest) -> List[VideoScript]:
        """Generates a batch of high-converting, fully-optimized marketing scripts synchronously.

        Optimized for direct integration with synchronous FastAPI handlers or background jobs.
        """
        return self._script_manager.generate_scripts(request)

    async def generate_scripts_async(self, request: ScriptRequest) -> List[VideoScript]:
        """Generates a batch of high-converting, fully-optimized marketing scripts asynchronously.

        Ideal for responsive multi-user web environments like NiceGUI or live WebSockets.
        """
        return await self._script_manager.generate_scripts_async(request)

    def analyze_product(self, product_name: str, product_description: str) -> ProductAnalysis:
        """Analyzes product characteristics and extracts core personas and selling targets synchronously."""
        return self._product_analyzer.analyze(product_name, product_description)

    async def analyze_product_async(self, product_name: str, product_description: str) -> ProductAnalysis:
        """Analyzes product characteristics and extracts core personas and selling targets asynchronously."""
        return await self._product_analyzer.analyze_async(product_name, product_description)

    @staticmethod
    def get_supported_styles() -> List[str]:
        """Returns the list of 14 supported short-form video copywriting styles."""
        return SUPPORTED_STYLES

    @staticmethod
    def get_supported_platforms() -> List[str]:
        """Returns the list of supported delivery channels (e.g. TikTok, Shorts, Shopee)."""
        return SUPPORTED_PLATFORMS

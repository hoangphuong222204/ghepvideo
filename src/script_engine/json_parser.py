"""Parsing layer mapping cleaned AI responses to typed dataclass models."""

import json
from typing import Any, Dict, List, Optional
from src.ai.response_parser import ResponseParser
from src.script_engine.exceptions import JSONParseError
from src.script_engine.models import ProductAnalysis, VideoScript, ScriptScene


class JSONParser:
    """Enterprise-grade JSON Parser mapping clean structured dict outputs to typed script engine models."""

    @classmethod
    def parse_product_analysis(cls, text: str) -> ProductAnalysis:
        """Parses LLM json response into a structured ProductAnalysis instance."""
        try:
            data = ResponseParser.parse_json(text)
            if not isinstance(data, dict):
                raise JSONParseError("Product analysis output must be a JSON dictionary.")

            return ProductAnalysis(
                category=data.get("category", "Uncategorized"),
                selling_points=cls._ensure_list(data.get("selling_points")),
                target_audience=cls._ensure_list(data.get("target_audience")),
                buying_motivations=cls._ensure_list(data.get("buying_motivations")),
                usage_scenarios=cls._ensure_list(data.get("usage_scenarios")),
            )
        except Exception as e:
            if isinstance(e, JSONParseError):
                raise e
            raise JSONParseError(f"Failed to parse product analysis: {e}") from e

    @classmethod
    def parse_video_scripts(cls, text: str, fallback_style: str = "Standard", fallback_platform: str = "TikTok") -> List[VideoScript]:
        """Parses LLM json response containing a list of video scripts or a single script."""
        try:
            parsed = ResponseParser.parse_json(text)
            scripts_data = []

            # Normalize to list of dictionaries
            if isinstance(parsed, list):
                scripts_data = parsed
            elif isinstance(parsed, dict):
                # Check if it has a nested "scripts" array
                if "scripts" in parsed and isinstance(parsed["scripts"], list):
                    scripts_data = parsed["scripts"]
                else:
                    scripts_data = [parsed]
            else:
                raise JSONParseError("Response parsed was not an array or a JSON dictionary.")

            scripts = []
            for item in scripts_data:
                if not isinstance(item, dict):
                    continue

                scenes_data = item.get("scenes", [])
                scenes = []
                for idx, sc in enumerate(scenes_data):
                    if not isinstance(sc, dict):
                        continue
                    scenes.append(
                        ScriptScene(
                            scene_number=sc.get("scene_number", idx + 1),
                            visual_description=sc.get("visual_description", "Cảnh quay cận cảnh sản phẩm."),
                            spoken_text=sc.get("spoken_text", ""),
                            duration_seconds=float(sc.get("duration_seconds", 5.0)),
                        )
                    )

                style = item.get("style", fallback_style)
                platform = item.get("platform", fallback_platform)
                title = item.get("title", f"Kịch bản {style} - {platform}")

                # Construct plain spoken text
                spoken_parts = [sc.spoken_text for sc in scenes if sc.spoken_text]
                content_text = " ".join(spoken_parts)

                # Collect scores if present, fallback to 0.0
                scripts.append(
                    VideoScript(
                        title=title,
                        style=style,
                        platform=platform,
                        scenes=scenes,
                        estimated_duration=float(item.get("estimated_duration", 0.0)),
                        word_count=int(item.get("word_count", 0)),
                        hook_score=float(item.get("hook_score", 0.0)),
                        selling_score=float(item.get("selling_score", 0.0)),
                        natural_speech_score=float(item.get("natural_speech_score", 0.0)),
                        policy_score=float(item.get("policy_score", 0.0)),
                        originality_score=float(item.get("originality_score", 0.0)),
                        overall_score=float(item.get("overall_score", 0.0)),
                        content_text=content_text,
                    )
                )

            return scripts
        except Exception as e:
            if isinstance(e, JSONParseError):
                raise e
            raise JSONParseError(f"Failed to parse video scripts JSON: {e}") from e

    @staticmethod
    def _ensure_list(val: Any) -> List[str]:
        """Utility to safely transform strings, lists or None into a list of strings."""
        if not val:
            return []
        if isinstance(val, str):
            return [val.strip()]
        if isinstance(val, list):
            return [str(v).strip() for v in val if v]
        return [str(val)]

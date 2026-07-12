"""ScriptManager coordinates the entire pipeline from style selection to AI generation, optimization, and DB persistence."""

import os
import json
import logging
from typing import List, Optional
from src.ai import AIManager, AIRequest, GenerationConfig
from src.logger.logger_manager import LoggerManager
from src.script_engine.models import ScriptRequest, VideoScript, QualityScore
from src.script_engine.validators import ScriptRequestValidator
from src.script_engine.style_selector import StyleSelector
from src.script_engine.prompt_generator import PromptGenerator
from src.script_engine.json_parser import JSONParser
from src.script_engine.number_converter import NumberConverter
from src.script_engine.pronunciation_adapter import PronunciationAdapter
from src.script_engine.policy_checker import PolicyChecker
from src.script_engine.duration_estimator import DurationEstimator
from src.script_engine.quality_checker import QualityChecker
from src.script_engine.exceptions import QualityError, ScriptEngineError

# Optional database layer integration
try:
    from src.database.database_manager import DatabaseManager
    _has_db = True
except ImportError:
    _has_db = False

logger = LoggerManager().get_logger("script_engine.manager")


class ScriptManager:
    """Enterprise Script Pipeline Orchestrator."""

    def __init__(self, ai_manager: Optional[AIManager] = None) -> None:
        """Initializes the ScriptManager with standard AI and Database managers."""
        self._ai_manager = ai_manager or AIManager()

    def generate_scripts(self, request: ScriptRequest) -> List[VideoScript]:
        """Generates a batch of high-quality marketing scripts synchronously."""
        # 1. Input Validation
        ScriptRequestValidator.validate_request(request)
        logger.info(f"🚀 Starting script generation batch of {request.quantity} style(s) for: {request.product_name}")

        # 2. Resolve Styles (Ensure "No Duplicate Style")
        selected_styles = StyleSelector.select_unique_styles(request.quantity, request.style)
        logger.info(f"Resolved unique style sequence: {selected_styles}")

        generated_scripts: List[VideoScript] = []

        # 3. Compile and Execute for each style
        for style in selected_styles:
            style_guideline = StyleSelector.get_guideline(style)
            
            # Use retry block for quality self-correction (up to 2 retry attempts)
            attempts = 3
            current_script: Optional[VideoScript] = None
            retry_instruction = ""

            for attempt in range(attempts):
                try:
                    system_prompt = PromptGenerator.get_script_generation_system_prompt()
                    user_prompt = PromptGenerator.get_script_generation_user_prompt(
                        product_name=request.product_name,
                        product_description=request.product_description,
                        style=style,
                        style_guideline=style_guideline,
                        platform=request.platform,
                        duration_seconds=request.duration_seconds,
                        brand_name=request.brand_name,
                        target_audience=request.target_audience,
                        core_benefit=request.core_benefit,
                        quantity=1,
                    )

                    if retry_instruction:
                        user_prompt += f"\n\nREWRITE CORRECTION FEEDBACK:\n{retry_instruction}"

                    # Dispatch request to AI Gateway (Module 04)
                    ai_req = AIRequest(
                        prompt=user_prompt,
                        model_name="gemini-2.5-flash",
                        config=GenerationConfig(
                            temperature=0.7 + (attempt * 0.1), # Increase temperature slightly for variety
                            system_instruction=system_prompt,
                            json_mode=True,
                        )
                    )
                    ai_resp = self._ai_manager.generate(ai_req)
                    
                    # Parse scripts from response
                    parsed_batch = JSONParser.parse_video_scripts(ai_resp.text, style, request.platform)
                    if not parsed_batch:
                        raise ScriptEngineError("AI Gateway returned no valid script structures.")

                    candidate = parsed_batch[0]

                    # 4. Vietnamese Speech Optimization
                    self._optimize_script_speech(candidate)

                    # 5. Quality Checking
                    eval_score = QualityChecker.evaluate_script(
                        script=candidate,
                        target_duration_seconds=request.duration_seconds,
                        previous_scripts=generated_scripts,
                        min_quality_score=request.min_quality_score,
                    )

                    self._apply_score_metrics(candidate, eval_score)

                    if eval_score.is_approved:
                        logger.info(f"✅ Approved Script (Style: {style}, Attempt: {attempt+1}, Score: {eval_score.overall_score})")
                        current_script = candidate
                        break
                    else:
                        logger.warning(
                            f"⚠️ Low Quality Script (Style: {style}, Attempt: {attempt+1}, Score: {eval_score.overall_score}). "
                            f"Rejection: {eval_score.rejection_reason}"
                        )
                        # Prepare instructions for rewrite
                        retry_instruction = (
                            f"Your previous attempt scored only {eval_score.overall_score}/100. "
                            f"Issues to improve: {eval_score.rejection_reason}. "
                            "Please focus heavily on strong opening hooks, natural flow, "
                            "and keeping the speaking speed perfectly aligned to the requested duration."
                        )
                        # Keep candidate as fallback if all attempts fail
                        current_script = candidate

                except Exception as e:
                    logger.error(f"Error during script generation attempt {attempt+1} (Style: {style}): {e}")
                    retry_instruction = f"An execution error occurred: {e}. Please regenerate a clean structured script."

            if current_script:
                generated_scripts.append(current_script)

        # 6. Database Persistence & Audit Logging
        self._persist_and_audit(request, generated_scripts)

        return generated_scripts

    async def generate_scripts_async(self, request: ScriptRequest) -> List[VideoScript]:
        """Generates a batch of high-quality marketing scripts asynchronously."""
        ScriptRequestValidator.validate_request(request)
        logger.info(f"🚀 Starting script generation batch (async) of {request.quantity} style(s) for: {request.product_name}")

        selected_styles = StyleSelector.select_unique_styles(request.quantity, request.style)
        generated_scripts: List[VideoScript] = []

        for style in selected_styles:
            style_guideline = StyleSelector.get_guideline(style)
            
            attempts = 3
            current_script: Optional[VideoScript] = None
            retry_instruction = ""

            for attempt in range(attempts):
                try:
                    system_prompt = PromptGenerator.get_script_generation_system_prompt()
                    user_prompt = PromptGenerator.get_script_generation_user_prompt(
                        product_name=request.product_name,
                        product_description=request.product_description,
                        style=style,
                        style_guideline=style_guideline,
                        platform=request.platform,
                        duration_seconds=request.duration_seconds,
                        brand_name=request.brand_name,
                        target_audience=request.target_audience,
                        core_benefit=request.core_benefit,
                        quantity=1,
                    )

                    if retry_instruction:
                        user_prompt += f"\n\nREWRITE CORRECTION FEEDBACK:\n{retry_instruction}"

                    # Dispatch request to AI Gateway (Module 04)
                    ai_req = AIRequest(
                        prompt=user_prompt,
                        model_name="gemini-2.5-flash",
                        config=GenerationConfig(
                            temperature=0.7 + (attempt * 0.1),
                            system_instruction=system_prompt,
                            json_mode=True,
                        )
                    )
                    ai_resp = await self._ai_manager.generate_async(ai_req)
                    
                    parsed_batch = JSONParser.parse_video_scripts(ai_resp.text, style, request.platform)
                    if not parsed_batch:
                        raise ScriptEngineError("AI Gateway returned no valid script structures.")

                    candidate = parsed_batch[0]

                    # Vietnamese Speech Optimization
                    self._optimize_script_speech(candidate)

                    # Quality Checking
                    eval_score = QualityChecker.evaluate_script(
                        script=candidate,
                        target_duration_seconds=request.duration_seconds,
                        previous_scripts=generated_scripts,
                        min_quality_score=request.min_quality_score,
                    )

                    self._apply_score_metrics(candidate, eval_score)

                    if eval_score.is_approved:
                        logger.info(f"✅ Approved Script (Style: {style}, Attempt: {attempt+1}, Score: {eval_score.overall_score})")
                        current_script = candidate
                        break
                    else:
                        logger.warning(
                            f"⚠️ Low Quality Script (Style: {style}, Attempt: {attempt+1}, Score: {eval_score.overall_score}). "
                            f"Rejection: {eval_score.rejection_reason}"
                        )
                        retry_instruction = (
                            f"Your previous attempt scored only {eval_score.overall_score}/100. "
                            f"Issues to improve: {eval_score.rejection_reason}. "
                            "Please focus heavily on strong opening hooks, natural flow, "
                            "and keeping the speaking speed perfectly aligned to the requested duration."
                        )
                        current_script = candidate

                except Exception as e:
                    logger.error(f"Error during async script generation attempt {attempt+1} (Style: {style}): {e}")
                    retry_instruction = f"An execution error occurred: {e}. Please regenerate a clean structured script."

            if current_script:
                generated_scripts.append(current_script)

        # Database Persistence & Audit Logging
        self._persist_and_audit(request, generated_scripts)

        return generated_scripts

    def _optimize_script_speech(self, script: VideoScript) -> None:
        """Applies number expansion, English phonetics adaptation, and duration calculation to all scenes."""
        full_text_parts = []
        for scene in script.scenes:
            # 1. Expand numbers: "100" -> "một trăm"
            scene.spoken_text = NumberConverter.expand_numbers(scene.spoken_text)
            
            # 2. English phonetic translation: "sale" -> "seo"
            scene.spoken_text = PronunciationAdapter.adapt_text(scene.spoken_text)
            
            # 3. Calculate exact scene duration based on words
            scene.duration_seconds = DurationEstimator.estimate_duration(scene.spoken_text)
            full_text_parts.append(scene.spoken_text)

        # 4. Compute overall metrics
        script.content_text = " ".join(full_text_parts)
        script.word_count = DurationEstimator.count_words(script.content_text)
        script.estimated_duration = DurationEstimator.estimate_duration(script.content_text)

    def _apply_score_metrics(self, script: VideoScript, score: QualityScore) -> None:
        """Helper to bind granular evaluation quality metrics to the script object."""
        script.hook_score = score.hook_score
        script.selling_score = score.selling_score
        script.natural_speech_score = score.natural_speech_score
        script.policy_score = score.policy_score
        script.originality_score = score.originality_score
        script.overall_score = score.overall_score
        script.is_approved = score.is_approved
        script.rejection_reason = score.rejection_reason

    def _persist_and_audit(self, request: ScriptRequest, scripts: List[VideoScript]) -> None:
        """Saves generated script metrics into relational database and logs audit records on completion."""
        if not _has_db:
            logger.debug("Database manager is not available. Skipping SQL persistence.")
            return

        # Audit events string
        approved_count = sum(1 for s in scripts if s.is_approved)
        audit_desc = (
            f"Script Batch Generated | Campaign: {request.campaign_id or 'None'} | "
            f"Product: {request.product_name} | Total scripts: {len(scripts)} | Approved: {approved_count}"
        )

        try:
            db_manager = DatabaseManager()
            with db_manager.unit_of_work() as uow:
                # 1. Write Audit Log
                uow.logs.log_event(
                    event_type="SCRIPT_GENERATION",
                    description=audit_desc,
                    user_ref="script_engine_system"
                )

                # 2. If campaign_id is provided, save as MarketingAsset records
                if request.campaign_id:
                    for script in scripts:
                        # Define directory for local JSON storage
                        assets_dir = "/app/assets/scripts"
                        os.makedirs(assets_dir, exist_ok=True)
                        
                        # Serialize script object to file
                        filename = f"script_{request.campaign_id}_{style_to_slug(script.style)}_{int(time_nano())}.json"
                        file_path = os.path.join(assets_dir, filename)
                        
                        with open(file_path, "w", encoding="utf-8") as f:
                            # Convert scenes to dict lists for serialization
                            scenes_dict = [
                                {
                                    "scene_number": s.scene_number,
                                    "visual_description": s.visual_description,
                                    "spoken_text": s.spoken_text,
                                    "duration_seconds": s.duration_seconds
                                }
                                for s in script.scenes
                            ]
                            json.dump({
                                "title": script.title,
                                "style": script.style,
                                "platform": script.platform,
                                "estimated_duration": script.estimated_duration,
                                "word_count": script.word_count,
                                "hook_score": script.hook_score,
                                "selling_score": script.selling_score,
                                "natural_speech_score": script.natural_speech_score,
                                "policy_score": script.policy_score,
                                "overall_score": script.overall_score,
                                "scenes": scenes_dict
                            }, f, ensure_ascii=False, indent=2)

                        # Save asset metadata to DB
                        uow.assets.create({
                            "campaign_id": request.campaign_id,
                            "title": script.title,
                            "asset_type": "text",
                            "file_path": file_path,
                            "gemini_prompt": request.product_description,
                            "is_exported": False
                        })
                        
            logger.info("Successfully persisted scripts metadata and logged audit events to SQL layer.")
        except Exception as e:
            logger.warning(f"Failed to record scripts persistence / audits in database: {e}")


def style_to_slug(style: str) -> str:
    """Converts a styling name to a filesystem friendly lowercase slug."""
    return style.lower().replace(" ", "_")


def time_nano() -> int:
    """Helper returning high resolution nanosecond float converted to int."""
    import time
    return int(time.time_ns())

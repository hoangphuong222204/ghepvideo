"""Evaluation and scoring engine assessing quality metrics of generated marketing scripts."""

import re
from typing import List, Optional
from src.script_engine.models import VideoScript, QualityScore
from src.script_engine.policy_checker import PolicyChecker
from src.script_engine.duration_estimator import DurationEstimator


class QualityChecker:
    """Evaluates video scripts against rigorous content, platform compliance, and speech metrics."""

    @classmethod
    def evaluate_script(
        cls,
        script: VideoScript,
        target_duration_seconds: float,
        previous_scripts: Optional[List[VideoScript]] = None,
        min_quality_score: float = 70.0,
    ) -> QualityScore:
        """Runs full suite of semantic and compliance checks to calculate granular scores.

        Args:
            script: The VideoScript instance to evaluate.
            target_duration_seconds: The desired length of the script in seconds.
            previous_scripts: List of previously generated scripts in the batch to assess uniqueness.
            min_quality_score: Threshold below which a script is flagged as rejected.

        Returns:
            QualityScore instance.
        """
        # 1. Hook Score: evaluated from the first scene (Scene 1)
        hook_score = cls._evaluate_hook(script)

        # 2. Selling Score: checks if selling points are integrated in spoken text
        selling_score = cls._evaluate_selling(script)

        # 3. Natural Speech Score: assesses rhythm, punctuation, and flow
        natural_speech_score = cls._evaluate_natural_speech(script)

        # 4. Policy Score: checks for forbidden claims and phrases via PolicyChecker
        _, _, _, policy_score = PolicyChecker.analyze_text(script.content_text)

        # 5. Duration Score: evaluates closeness to target duration
        duration_score = cls._evaluate_duration(script, target_duration_seconds)

        # 6. Originality Score: compares text similarity with other scripts
        originality_score = cls._evaluate_originality(script, previous_scripts or [])

        # 7. Overall Score: weighted average
        # Focus weights: Policy compliance (25%), Selling quality (20%), Hook (20%),
        # Natural Speech (15%), Duration fit (10%), Originality (10%).
        overall_score = (
            (policy_score * 0.25)
            + (selling_score * 0.20)
            + (hook_score * 0.20)
            + (natural_speech_score * 0.15)
            + (duration_score * 0.10)
            + (originality_score * 0.10)
        )
        overall_score = round(overall_score, 1)

        is_approved = overall_score >= min_quality_score
        rejection_reason = None
        if not is_approved:
            rejection_reason = (
                f"Overall score {overall_score} is below the required {min_quality_score}. "
                f"Breakdowns - Hook: {hook_score}, Policy: {policy_score}, Selling: {selling_score}, "
                f"Speech: {natural_speech_score}, Duration: {duration_score}."
            )

        return QualityScore(
            hook_score=hook_score,
            selling_score=selling_score,
            natural_speech_score=natural_speech_score,
            policy_score=policy_score,
            originality_score=originality_score,
            duration_score=duration_score,
            overall_score=overall_score,
            is_approved=is_approved,
            rejection_reason=rejection_reason,
        )

    @staticmethod
    def _evaluate_hook(script: VideoScript) -> float:
        """Evaluates opening segment of the script."""
        if not script.scenes:
            return 0.0
        
        first_scene = script.scenes[0]
        spoken = first_scene.spoken_text.strip()
        if not spoken:
            return 10.0  # Extremely low if no speech at start
            
        word_count = DurationEstimator.count_words(spoken)
        
        score = 100.0
        # Hook should be punchy and short (typically 5 to 15 words)
        if word_count < 4:
            score -= 30.0  # Too short to be meaningful
        elif word_count > 20:
            score -= 25.0  # Too long/boring for a quick hook

        # Check for attention-grabbing words or syntax (e.g. "bạn có biết", "đừng", "bí quyết", "?", "!")
        hook_triggers = ["bạn có", "đừng", "bí quyết", "lý do", "tại sao", "cảnh báo", "sự thật", "mẹo", "thử"]
        has_trigger = any(trig in spoken.lower() for trig in hook_triggers)
        if not has_trigger and not any(char in spoken for char in ["?", "!"]):
            score -= 15.0

        return max(0.0, score)

    @staticmethod
    def _evaluate_selling(script: VideoScript) -> float:
        """Evaluates how effectively selling arguments are embedded in text."""
        spoken = script.content_text.lower()
        if not spoken:
            return 0.0

        score = 60.0  # Base selling score
        # Benefit / selling terms
        benefits_terms = [
            "giúp", "mang lại", "tiết kiệm", "giải quyết", "hiệu quả",
            "sở hữu", "vượt trội", "đặc biệt", "tự nhiên", "an toàn",
            "tiện lợi", "nhanh chóng", "cải thiện", "chính hãng"
        ]
        matches = sum(1 for term in benefits_terms if term in spoken)
        score += min(30.0, matches * 5.0)

        # Call to Action (CTA) check at final scenes
        cta_terms = ["mua ngay", "click vào", "giỏ hàng", "đăng ký", "sở hữu ngay", "thử ngay", "bình luận", "liên hệ"]
        has_cta = any(term in spoken for term in cta_terms)
        if has_cta:
            score += 10.0
        else:
            score -= 15.0

        return min(100.0, max(0.0, score))

    @staticmethod
    def _evaluate_natural_speech(script: VideoScript) -> float:
        """Evaluates rhythmic smoothness and formatting of spoken segments."""
        if not script.scenes:
            return 0.0

        score = 100.0
        # 1. Check scene count (too few scenes makes pacing boring)
        if len(script.scenes) < 3:
            score -= 20.0

        for sc in script.scenes:
            txt = sc.spoken_text.strip()
            if not txt:
                continue
                
            # 2. Check for overly long sentences without punctuation (difficult to breathe)
            if len(txt) > 120 and not any(char in txt for char in [",", ".", ";"]):
                score -= 10.0

            # 3. Check for repetitive/duplicate terms
            words = txt.lower().split()
            unique_words = set(words)
            if len(words) > 15 and len(unique_words) / len(words) < 0.5:
                score -= 15.0

        return max(0.0, score)

    @staticmethod
    def _evaluate_duration(script: VideoScript, target_duration_seconds: float) -> float:
        """Scores duration accuracy compared to target."""
        if target_duration_seconds <= 0:
            return 100.0

        # Validate using DurationEstimator
        _, _, deviation_pct = DurationEstimator.validate_duration_fit(
            script.word_count, target_duration_seconds
        )

        # Ideal: 100 score if deviation is 0. Deduct 1.5 points per % deviation
        score = 100.0 - (deviation_pct * 1.5)
        return min(100.0, max(0.0, score))

    @staticmethod
    def _evaluate_originality(script: VideoScript, previous_scripts: List[VideoScript]) -> float:
        """Determines the uniqueness of the script text compared to others generated in the batch."""
        if not previous_scripts:
            return 100.0

        current_text = script.content_text.lower().strip()
        if not current_text:
            return 0.0

        max_similarity = 0.0
        for prev in previous_scripts:
            prev_text = prev.content_text.lower().strip()
            if not prev_text:
                continue

            # Simple Jaccard similarity of word sets to measure duplication
            words_curr = set(current_text.split())
            words_prev = set(prev_text.split())
            
            if not words_curr or not words_prev:
                continue

            intersection = words_curr.intersection(words_prev)
            union = words_curr.union(words_prev)
            similarity = len(intersection) / len(union)
            if similarity > max_similarity:
                max_similarity = similarity

        # Originality is the inverse of maximum similarity
        # E.g., if similarity is 80%, originality score is 20
        originality_score = (1.0 - max_similarity) * 100.0
        return round(originality_score, 1)

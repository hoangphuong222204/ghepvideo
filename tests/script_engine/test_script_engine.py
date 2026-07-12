"""Comprehensive Unit Tests for the AI Script Engine (Module 05)."""

import json
import unittest
from unittest.mock import patch, MagicMock

from src.script_engine import (
    ScriptEngineError,
    ValidationError,
    PolicyError,
    JSONParseError,
    QualityError,
    ProductAnalysis,
    ScriptRequest,
    ScriptScene,
    VideoScript,
    QualityScore,
    NumberConverter,
    PronunciationAdapter,
    PolicyChecker,
    DurationEstimator,
    StyleSelector,
    QualityChecker,
    JSONParser,
    TextAnalyzer,
    ProductAnalyzer,
    ScriptManager,
    ScriptEngine,
    SUPPORTED_STYLES,
    SUPPORTED_PLATFORMS,
)


class TestNumberConverter(unittest.TestCase):
    """Verifies Vietnamese number expansion correctness."""

    def test_single_digits(self):
        self.assertEqual(NumberConverter.expand_numbers("0"), "không")
        self.assertEqual(NumberConverter.expand_numbers("5"), "năm")
        self.assertEqual(NumberConverter.expand_numbers("9"), "chín")

    def test_multi_digits(self):
        self.assertEqual(NumberConverter.expand_numbers("10"), "mười")
        self.assertEqual(NumberConverter.expand_numbers("21"), "hai mươi mốt")
        self.assertEqual(NumberConverter.expand_numbers("105"), "một trăm linh năm")
        self.assertEqual(NumberConverter.expand_numbers("1000"), "một nghìn")

    def test_expand_in_sentence(self):
        sentence = "Sản phẩm 100 cam kết hiệu quả trong 5 ngày."
        expected = "Sản phẩm một trăm cam kết hiệu quả trong năm ngày."
        self.assertEqual(NumberConverter.expand_numbers(sentence), expected)


class TestPronunciationAdapter(unittest.TestCase):
    """Verifies English technical/brand term phonetics adaptation."""

    def test_exact_matches(self):
        self.assertEqual(PronunciationAdapter.adapt_text("tiktok"), "tíc-tóc")
        self.assertEqual(PronunciationAdapter.adapt_text("iPhone"), "Ai-phôn")
        self.assertEqual(PronunciationAdapter.adapt_text("cream"), "cờ-rim")

    def test_adaptation_in_sentence(self):
        sentence = "Xem ngay review cực hot trên TikTok về serum này."
        expected = "Xem ngay ri-viu cực hót trên Tíc-tóc về xi-rum này."
        self.assertEqual(PronunciationAdapter.adapt_text(sentence), expected)


class TestPolicyChecker(unittest.TestCase):
    """Verifies TikTok policy scanning and automatic claim rewrite rules."""

    def test_clean_text(self):
        clean = "Sản phẩm dưỡng da vượt trội này rất an toàn cho người dùng."
        is_violating, terms, sanitized, score = PolicyChecker.analyze_text(clean)
        self.assertFalse(is_violating)
        self.assertEqual(len(terms), 0)
        self.assertEqual(sanitized, clean)
        self.assertEqual(score, 100.0)

    def test_violating_claims_trigger_and_rewrite(self):
        dirty = "Chúng tôi cam kết 100% trị dứt điểm mọi thâm mụn hiệu quả tức thì."
        is_violating, terms, sanitized, score = PolicyChecker.analyze_text(dirty)
        self.assertTrue(is_violating)
        self.assertIn("cam kết 100%", terms)
        self.assertIn("trị dứt điểm", terms)
        self.assertIn("hiệu quả tức thì", terms)
        # Verify score deductions (3 violations -> score drops by 75 to 25)
        self.assertEqual(score, 25.0)
        # Check replacement keywords
        self.assertIn("mang lại trải nghiệm tối ưu", sanitized)
        self.assertIn("hỗ trợ cải thiện rõ rệt", sanitized)
        self.assertIn("hiệu quả nhanh chóng", sanitized)


class TestDurationEstimator(unittest.TestCase):
    """Verifies word counts and estimated speech durations."""

    def test_word_counts(self):
        self.assertEqual(DurationEstimator.count_words(""), 0)
        self.assertEqual(DurationEstimator.count_words("Một hai ba bốn."), 4)

    def test_estimate_duration(self):
        # 150 WPM = 2.5 words per second
        # 25 words = 10.0 seconds
        self.assertEqual(DurationEstimator.estimate_duration("ba " * 25), 10.0)

    def test_validate_duration_fit(self):
        # Target: 10s. Words: 25 (exactly 10s speech). Fits perfectly.
        fits, est, dev = DurationEstimator.validate_duration_fit(25, 10.0)
        self.assertTrue(fits)
        self.assertEqual(est, 10.0)
        self.assertEqual(dev, 0.0)


class TestStyleSelector(unittest.TestCase):
    """Verifies style mappings and the unique selector list."""

    def test_unique_styles_selector(self):
        # 1. No preferred style
        styles = StyleSelector.select_unique_styles(5)
        self.assertEqual(len(styles), 5)
        self.assertEqual(len(set(styles)), 5)  # No duplicate style

        # 2. Preferred style first
        styles_pref = StyleSelector.select_unique_styles(3, "POV")
        self.assertEqual(styles_pref[0], "POV")
        self.assertEqual(len(styles_pref), 3)
        self.assertEqual(len(set(styles_pref)), 3)

    def test_unique_styles_oversized_quantity(self):
        # Requesting more than the 14 available styles wraps around safely
        styles = StyleSelector.select_unique_styles(20)
        self.assertEqual(len(styles), 20)


class TestJSONParser(unittest.TestCase):
    """Verifies decoding structures and JSON mappings."""

    def test_parse_product_analysis_success(self):
        raw_json = json.dumps({
            "category": "Mỹ phẩm",
            "selling_points": ["Trắng da", "Mờ thâm"],
            "target_audience": "Nữ từ 18-30 tuổi",
            "buying_motivations": ["Muốn đẹp", "Tự tin"],
            "usage_scenarios": ["Trước khi đi ngủ"]
        })
        analysis = JSONParser.parse_product_analysis(raw_json)
        self.assertEqual(analysis.category, "Mỹ phẩm")
        self.assertEqual(analysis.selling_points, ["Trắng da", "Mờ thâm"])
        self.assertEqual(analysis.target_audience, ["Nữ từ 18-30 tuổi"])

    def test_parse_video_scripts_success(self):
        raw_json = json.dumps({
            "scripts": [
                {
                    "title": "Kịch bản mẫu",
                    "style": "Problem Solution",
                    "platform": "TikTok",
                    "estimated_duration": 15.0,
                    "word_count": 35,
                    "scenes": [
                        {
                            "scene_number": 1,
                            "visual_description": "Cận cảnh serum",
                            "spoken_text": "Bạn bị thâm mụn lâu ngày?",
                            "duration_seconds": 5.0
                        }
                    ]
                }
            ]
        })
        scripts = JSONParser.parse_video_scripts(raw_json)
        self.assertEqual(len(scripts), 1)
        self.assertEqual(scripts[0].title, "Kịch bản mẫu")
        self.assertEqual(scripts[0].scenes[0].spoken_text, "Bạn bị thâm mụn lâu ngày?")


class TestQualityChecker(unittest.TestCase):
    """Verifies individual score evaluations and low-quality rejections."""

    def test_quality_checker_high_score(self):
        script = VideoScript(
            title="Serum diệu kỳ",
            style="Problem Solution",
            platform="TikTok",
            scenes=[
                ScriptScene(1, "Visual 1", "Bạn có mụn đầu đen đáng ghét?", 5.0),
                ScriptScene(2, "Visual 2", "Hãy dùng serum dưỡng ẩm giúp tái tạo làn da vượt trội này.", 10.0),
                ScriptScene(3, "Visual 3", "Mua ngay tại giỏ hàng phía dưới.", 5.0)
            ],
            estimated_duration=20.0,
            word_count=23,
            content_text="Bạn có mụn đầu đen đáng ghét? Hãy dùng serum dưỡng ẩm giúp tái tạo làn da vượt trội này. Mua ngay tại giỏ hàng phía dưới."
        )
        
        # Target duration match is close (20s vs 20s target)
        score = QualityChecker.evaluate_script(script, target_duration_seconds=20.0, min_quality_score=70.0)
        self.assertTrue(score.is_approved)
        self.assertGreaterEqual(score.overall_score, 70.0)


class TestProductAnalyzer(unittest.TestCase):
    """Verifies AI gateway interaction for product analysis."""

    @patch("src.ai.AIManager")
    def test_product_analyzer_calls_gateway(self, mock_ai_manager_cls):
        # Mock AI Manager response
        mock_ai_manager = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "category": "Thời trang",
            "selling_points": ["Thấm hút mồ hôi tốt"],
            "target_audience": ["Người tập thể thao"],
            "buying_motivations": ["Thoải mái"],
            "usage_scenarios": ["Chạy bộ buổi sáng"]
        })
        mock_ai_manager.generate.return_value = mock_response
        mock_ai_manager_cls.return_value = mock_ai_manager

        analyzer = ProductAnalyzer(ai_manager=mock_ai_manager)
        result = analyzer.analyze("Áo thun", "Áo thun thể thao cao cấp")

        self.assertEqual(result.category, "Thời trang")
        self.assertEqual(result.selling_points, ["Thấm hút mồ hôi tốt"])


class TestScriptEngine(unittest.TestCase):
    """Verifies core script engine integration orchestration and multiple script generations."""

    @patch("src.ai.AIManager")
    def test_engine_generates_scripts_successfully(self, mock_ai_manager_cls):
        mock_ai_manager = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "scripts": [
                {
                    "title": "Kịch bản mẫu",
                    "style": "Problem Solution",
                    "platform": "TikTok",
                    "scenes": [
                        {
                            "scene_number": 1,
                            "visual_description": "Cận cảnh chai serum HA",
                            "spoken_text": "Làn da khô sạm bong tróc vào mùa đông 2026?",
                            "duration_seconds": 6.0
                        },
                        {
                            "scene_number": 2,
                            "visual_description": "Thoa sản phẩm lên mặt",
                            "spoken_text": "Giải pháp là tinh chất phục hồi giúp căng bóng nhanh chóng.",
                            "duration_seconds": 12.0
                        }
                    ]
                }
            ]
        })
        mock_ai_manager.generate.return_value = mock_response
        mock_ai_manager_cls.return_value = mock_ai_manager

        engine = ScriptEngine(ai_manager=mock_ai_manager)
        request = ScriptRequest(
            product_name="Serum HA",
            product_description="Serum dưỡng ẩm sâu",
            style="Problem Solution",
            quantity=1
        )
        
        scripts = engine.generate_scripts(request)
        self.assertEqual(len(scripts), 1)
        script = scripts[0]
        self.assertEqual(script.style, "Problem Solution")
        
        # Verify Vietnamese Speech Optimization was applied (e.g., "2026" expanded to words)
        self.assertIn("hai nghìn không trăm hai mươi sáu", script.scenes[0].spoken_text)

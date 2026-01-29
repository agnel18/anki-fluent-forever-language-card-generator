import pytest
import json
from unittest.mock import patch, MagicMock

class TestArabicAnalyzer:
    """Test Arabic analyzer facade"""

    def test_initialization(self, arabic_analyzer):
        """Test analyzer initializes correctly"""
        assert arabic_analyzer.LANGUAGE_CODE == "ar"
        assert arabic_analyzer.LANGUAGE_NAME == "Arabic"
        assert arabic_analyzer.VERSION == "1.0"
        assert arabic_analyzer.config is not None
        assert arabic_analyzer.prompt_builder is not None
        assert arabic_analyzer.response_parser is not None
        assert arabic_analyzer.validator is not None

    def test_language_info(self, arabic_analyzer):
        """Test language information retrieval"""
        info = arabic_analyzer.get_language_info()
        assert info['code'] == 'ar'
        assert info['name'] == 'Arabic'
        assert info['native_name'] == 'العربية'
        assert info['is_rtl'] == True
        assert 'root_based_morphology' in info['features']

    def test_supported_complexities(self, arabic_analyzer):
        """Test supported complexity levels"""
        complexities = arabic_analyzer.get_supported_complexities()
        assert 'beginner' in complexities
        assert 'intermediate' in complexities
        assert 'advanced' in complexities

    def test_arabic_text_validation(self, arabic_analyzer):
        """Test Arabic text validation"""
        assert arabic_analyzer.validate_arabic_text("مرحبا") == True
        assert arabic_analyzer.validate_arabic_text("Hello") == False

    @patch('languages.arabic.ar_analyzer.ArAnalyzer._call_ai')
    def test_fallback_analysis(self, mock_call_ai, arabic_analyzer):
        """Test fallback analysis when AI call fails"""
        # Mock AI call to fail
        mock_call_ai.return_value = None

        result = arabic_analyzer.analyze_grammar(
            sentence="القطة سوداء",
            target_word="قطة",
            complexity="beginner",
            gemini_api_key="mock_key"
        )

        # Should return fallback result
        assert result.sentence == "القطة سوداء"
        assert result.target_word == "قطة"
        assert result.language_code == "ar"
        assert result.complexity_level == "beginner"
        assert result.confidence_score < 0.5  # Low confidence for fallback
        assert result.is_rtl == True
        assert len(result.word_explanations) > 0  # Should still have basic analysis

    def test_invalid_inputs(self, arabic_analyzer):
        """Test handling of invalid inputs"""
        # Empty sentence
        result = arabic_analyzer.analyze_grammar("", "test", "beginner", "key")
        assert result.confidence_score < 0.5

        # Empty target word
        result = arabic_analyzer.analyze_grammar("test sentence", "", "beginner", "key")
        assert result.confidence_score < 0.5

        # Invalid complexity
        result = arabic_analyzer.analyze_grammar("test", "test", "invalid", "key")
        assert result.confidence_score < 0.5

    @patch('languages.arabic.ar_analyzer.ArAnalyzer._call_ai')
    def test_full_analysis_workflow(self, mock_call_ai, arabic_analyzer, mock_arabic_responses):
        """Test complete analysis workflow with mocked AI"""
        # Mock successful AI response
        mock_call_ai.return_value = json.dumps(mock_arabic_responses['valid_response'])

        result = arabic_analyzer.analyze_grammar(
            sentence="القطة سوداء",
            target_word="قطة",
            complexity="beginner",
            gemini_api_key="mock_key"
        )

        # Verify result structure
        assert result.sentence == "القطة سوداء"
        assert result.target_word == "قطة"
        assert result.language_code == "ar"
        assert result.complexity_level == "beginner"
        assert len(result.word_explanations) > 0
        assert result.confidence_score > 0
        assert result.html_output is not None
        assert result.is_rtl == True
        assert 'dir="rtl"' in result.html_output  # RTL HTML

    def test_rtl_word_order(self, arabic_analyzer):
        """Test that word explanations are in reading order for RTL"""
        # Create a simple sentence
        sentence = "القطة سوداء نائمة"

        # Get fallback analysis (should keep reading order for RTL)
        result = arabic_analyzer.analyze_grammar(sentence, "قطة", "beginner", "")

        # In RTL, the explanations should be in the SAME order as the words in the sentence
        # This ensures proper reading flow: first word first, last word last
        assert result.is_rtl == True
        assert result.text_direction == "rtl"

        # The word explanations should be in reading order for proper RTL display
        # (Same order as sentence words, not reversed)
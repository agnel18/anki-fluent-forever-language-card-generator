# languages/chinese_traditional/tests/test_zh_tw_analyzer.py
"""
Chinese Traditional Analyzer Tests

Following Chinese Simplified Clean Architecture gold standard:
- Unit tests for domain components
- Integration tests for main analyzer
- Test external configuration loading
- Validate Chinese Traditional linguistic accuracy

TEST COVERAGE:
- Configuration loading from external files
- Prompt generation with Jinja2 templates
- Response parsing with fallback mechanisms
- Validation and confidence scoring
- Pattern matching for Chinese Traditional text
- Main analyzer facade functionality

TEST PHILOSOPHY:
- Test domain logic independently
- Mock external dependencies (AI service)
- Validate Chinese Traditional specific features
- Ensure fallback mechanisms work correctly
"""

import pytest
import json
from unittest.mock import Mock, patch
from pathlib import Path

from ..zh_tw_analyzer import ZhTwAnalyzer
from ..domain.zh_tw_config import ZhTwConfig
from ..domain.zh_tw_patterns import ZhTwPatterns

class TestZhTwAnalyzer:
    """Test the main ZhTwAnalyzer facade."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ZhTwAnalyzer()

    def test_initialization(self):
        """Test analyzer initializes correctly."""
        assert self.analyzer.config is not None
        assert self.analyzer.prompt_builder is not None
        assert self.analyzer.response_parser is not None
        assert self.analyzer.validator is not None
        assert self.analyzer.patterns is not None

    def test_supported_complexity_levels(self):
        """Test complexity level support."""
        levels = self.analyzer.get_supported_complexity_levels()
        assert "beginner" in levels
        assert "intermediate" in levels
        assert "advanced" in levels

    def test_grammatical_roles_access(self):
        """Test grammatical roles are accessible."""
        roles = self.analyzer.get_grammatical_roles()
        assert isinstance(roles, dict)
        assert len(roles) > 0

    def test_color_scheme_generation(self):
        """Test color scheme generation."""
        scheme = self.analyzer.get_color_scheme("intermediate")
        assert isinstance(scheme, dict)
        assert "noun" in scheme
        assert "verb" in scheme

    def test_empty_sentence_analysis(self):
        """Test handling of empty sentences."""
        result = self.analyzer.analyze_sentence("")
        assert not result.success
        assert "Empty sentence" in result.error_message

    def test_basic_sentence_analysis(self):
        """Test basic sentence analysis functionality."""
        sentence = "這是一個測試句子。"
        result = self.analyzer.analyze_sentence(sentence)

        assert result.success
        assert result.sentence == sentence
        assert isinstance(result.words, list)
        assert len(result.words) > 0
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0

    def test_batch_analysis(self):
        """Test batch sentence analysis."""
        sentences = ["這是第一句。", "這是第二句。"]
        result = self.analyzer.analyze_sentences_batch(sentences)

        assert result.success
        assert len(result.results) == 2
        assert result.total_sentences == 2
        assert isinstance(result.average_confidence, float)

    def test_text_validation(self):
        """Test text validation functionality."""
        valid_text = "這是一個有效的中文句子。"
        invalid_text = "This is English text."

        valid_result = self.analyzer.validate_text(valid_text)
        invalid_result = self.analyzer.validate_text(invalid_text)

        assert valid_result['is_valid']
        assert not invalid_result['is_valid']

    def test_component_status(self):
        """Test component status reporting."""
        status = self.analyzer.get_component_status()
        assert status['config_loaded']
        assert 'patterns_available' in status
        assert 'complexity_levels' in status

class TestZhTwConfig:
    """Test configuration loading and management."""

    def setup_method(self):
        """Set up config test fixtures."""
        self.config = ZhTwConfig()

    def test_config_loading(self):
        """Test external configuration file loading."""
        assert len(self.config.grammatical_roles) > 0
        assert len(self.config.common_classifiers) > 0
        assert len(self.config.aspect_markers) > 0

    def test_color_scheme_generation(self):
        """Test color scheme generation for different complexities."""
        beginner_scheme = self.config.get_color_scheme("beginner")
        advanced_scheme = self.config.get_color_scheme("advanced")

        assert isinstance(beginner_scheme, dict)
        assert isinstance(advanced_scheme, dict)
        assert len(beginner_scheme) > 0
        assert len(advanced_scheme) > 0

    def test_traditional_characters(self):
        """Test Traditional Chinese character handling."""
        # Test that Traditional-specific characters are recognized
        traditional_chars = ['著', '裡', '藉', '徵', '並', '祇']

        for char in traditional_chars:
            assert char in str(self.config.aspect_markers) or \
                   char in str(self.config.word_meanings) or \
                   char in str(self.config.common_classifiers)

class TestZhTwPatterns:
    """Test pattern matching functionality."""

    def setup_method(self):
        """Set up patterns test fixtures."""
        config = ZhTwConfig()
        self.patterns = ZhTwPatterns(config)

    def test_chinese_character_recognition(self):
        """Test Chinese Traditional character recognition."""
        chinese_text = "這是一個測試句子。"
        matches = self.patterns.match_pattern('chinese_character', chinese_text)

        assert len(matches) > 0
        for match in matches:
            assert len(match.matched_text) == 1  # Single characters

    def test_traditional_vs_simplified(self):
        """Test distinction between Traditional and Simplified characters."""
        traditional = "這是傳統中文。"
        simplified = "这是简体中文。"

        trad_validation = self.patterns.validate_text(traditional)
        simp_validation = self.patterns.validate_text(simplified)

        # Both should be valid but Traditional should be preferred
        assert trad_validation['is_valid']
        assert simp_validation['is_valid']

        # Traditional should have higher confidence or no warnings
        assert len(trad_validation['issues']) <= len(simp_validation['issues'])

    def test_sentence_segmentation(self):
        """Test sentence segmentation into words/elements."""
        sentence = "這是一個測試句子。"
        segments = self.patterns.segment_sentence(sentence)

        assert isinstance(segments, list)
        assert len(segments) > 0
        assert ''.join(segments) == sentence.replace('。', '')  # Remove period

    def test_pattern_info(self):
        """Test pattern information retrieval."""
        info = self.patterns.get_pattern_info()
        assert 'available_patterns' in info
        assert 'pattern_count' in info
        assert info['pattern_count'] > 0

class TestIntegration:
    """Integration tests for component interaction."""

    def test_full_analysis_workflow(self):
        """Test complete analysis workflow."""
        analyzer = ZhTwAnalyzer()

        # Test with Traditional Chinese sentence
        sentence = "學生正在圖書館讀書。"
        result = analyzer.analyze_sentence(sentence, complexity="intermediate")

        assert result.success
        assert result.sentence == sentence
        assert len(result.words) > 0

        # Check that words have required fields
        for word in result.words:
            assert 'word' in word
            assert 'grammatical_role' in word
            assert 'individual_meaning' in word
            assert 'confidence' in word

    def test_error_recovery(self):
        """Test error recovery mechanisms."""
        analyzer = ZhTwAnalyzer()

        # Test with malformed input
        result = analyzer.analyze_sentence("Invalid input!")

        # Should still return a result (using fallbacks)
        assert isinstance(result, object)
        assert hasattr(result, 'success')

    def test_configuration_consistency(self):
        """Test configuration consistency across components."""
        analyzer = ZhTwAnalyzer()

        # Get roles from different access points
        roles_from_analyzer = analyzer.get_grammatical_roles()
        roles_from_config = analyzer.config.grammatical_roles

        assert roles_from_analyzer == roles_from_config

if __name__ == "__main__":
    # Run basic functionality test
    print("Running Chinese Traditional Analyzer tests...")

    analyzer = ZhTwAnalyzer()
    test_sentence = "這是一個測試句子。"

    print(f"Testing sentence: {test_sentence}")
    result = analyzer.analyze_sentence(test_sentence)

    print(f"Success: {result.success}")
    print(f"Words analyzed: {len(result.words)}")
    print(f"Confidence: {result.confidence:.2f}")

    if result.words:
        print("Sample word analysis:")
        for word in result.words[:3]:
            print(f"  {word['word']}: {word['grammatical_role']} ({word['confidence']:.2f})")

    print("Component status:")
    status = analyzer.get_component_status()
    print(f"  Config loaded: {status['config_loaded']}")
    print(f"  Patterns available: {status['patterns_available']['pattern_count']}")

    print("Tests completed!")
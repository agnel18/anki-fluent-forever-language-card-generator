# languages/zh/tests/test_zh_analyzer.py
"""
Tests for Chinese Simplified Grammar Analyzer

GOLD STANDARD TESTING:
This file demonstrates comprehensive testing for a language analyzer.
It covers unit tests, integration tests, and edge cases.

TEST CATEGORIES:
- Unit tests: Individual component testing
- Integration tests: Full analyzer workflow
- Edge cases: Error handling and boundary conditions
- Performance tests: Response time validation
- Accuracy tests: Grammar analysis quality

TESTING PRINCIPLES:
- Isolation: Test components independently
- Coverage: Test all code paths and edge cases
- Automation: Tests run in CI/CD pipeline
- Documentation: Tests serve as usage examples
- Maintenance: Tests catch regressions

USAGE FOR NEW LANGUAGES:
1. Copy test structure and adapt for target language
2. Test all components individually and integrated
3. Include realistic test data from target language
4. Test error conditions and edge cases
5. Validate performance requirements
"""

import pytest
import time
from unittest.mock import Mock, patch
from languages.zh.zh_analyzer import ZhAnalyzer
from languages.zh.domain.zh_config import ZhConfig
from languages.zh.domain.zh_prompt_builder import ZhPromptBuilder
from languages.zh.domain.zh_response_parser import ZhResponseParser
from languages.zh.domain.zh_validator import ZhValidator
from languages.zh.domain.zh_fallbacks import ZhFallbacks
from languages.zh.domain.zh_patterns import ZhPatterns


class TestZhAnalyzer:
    """Test Chinese Simplified analyzer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ZhAnalyzer()
        self.test_api_key = "test-key"

    def test_initialization(self):
        """Test analyzer initializes correctly."""
        assert self.analyzer is not None
        assert self.analyzer.language_code == "zh"
        assert self.analyzer.language_name == "Chinese Simplified"
        assert hasattr(self.analyzer, 'zh_config')
        assert hasattr(self.analyzer, 'prompt_builder')
        assert hasattr(self.analyzer, 'response_parser')
        assert hasattr(self.analyzer, 'validator')

    def test_single_sentence_analysis(self):
        """Test single sentence grammar analysis."""
        sentence = "我吃了一个苹果"
        target_word = "苹果"

        # Mock the AI call
        with patch.object(self.analyzer, '_call_ai') as mock_ai:
            mock_ai.return_value = '''
            {
              "sentence": "我吃了一个苹果",
              "words": [
                {"word": "我", "grammatical_role": "pronoun", "individual_meaning": "I, the speaker"},
                {"word": "吃", "grammatical_role": "verb", "individual_meaning": "to eat, consume"},
                {"word": "了", "grammatical_role": "aspect_marker", "individual_meaning": "perfective aspect, completed action"},
                {"word": "一个", "grammatical_role": "classifier", "individual_meaning": "one (with general classifier 个)"},
                {"word": "苹果", "grammatical_role": "noun", "individual_meaning": "apple, a type of fruit"}
              ],
              "explanations": {
                "overall_structure": "Subject-Verb-Object sentence with aspect marker and classifier",
                "key_features": "Uses perfective aspect 了 and classifier construction 一个"
              }
            }
            '''

            result = self.analyzer.analyze_grammar(sentence, target_word, "intermediate", self.test_api_key)

            assert result is not None
            assert result.sentence == sentence
            assert result.target_word == target_word
            assert result.language_code == "zh"
            assert len(result.word_explanations) > 0
            assert result.confidence_score >= 0.0

    def test_batch_analysis(self):
        """Test batch sentence analysis."""
        sentences = ["我吃饭", "你喝水", "他睡觉"]
        target_word = ""

        with patch.object(self.analyzer, '_call_ai') as mock_ai:
            mock_ai.return_value = '''
            {
              "batch_results": [
                {
                  "sentence": "我吃饭",
                  "words": [
                    {"word": "我", "grammatical_role": "pronoun", "individual_meaning": "I"},
                    {"word": "吃饭", "grammatical_role": "verb", "individual_meaning": "to eat (rice/meal)"}
                  ],
                  "explanations": {"overall_structure": "Simple SVO sentence"}
                },
                {
                  "sentence": "你喝水",
                  "words": [
                    {"word": "你", "grammatical_role": "pronoun", "individual_meaning": "you"},
                    {"word": "喝水", "grammatical_role": "verb", "individual_meaning": "to drink water"}
                  ],
                  "explanations": {"overall_structure": "Simple SVO sentence"}
                },
                {
                  "sentence": "他睡觉",
                  "words": [
                    {"word": "他", "grammatical_role": "pronoun", "individual_meaning": "he"},
                    {"word": "睡觉", "grammatical_role": "verb", "individual_meaning": "to sleep"}
                  ],
                  "explanations": {"overall_structure": "Simple SVO sentence"}
                }
              ]
            }
            '''

            results = self.analyzer.batch_analyze_grammar(sentences, target_word, "intermediate", self.test_api_key)

            assert len(results) == len(sentences)
            for result in results:
                assert result.language_code == "zh"
                assert len(result.word_explanations) > 0

    def test_fallback_analysis(self):
        """Test fallback analysis when AI fails."""
        sentence = "测试句子"
        target_word = ""

        # Mock AI to fail
        with patch.object(self.analyzer, '_call_ai') as mock_ai:
            mock_ai.side_effect = Exception("AI Error")

            result = self.analyzer.analyze_grammar(sentence, target_word, "intermediate", self.test_api_key)

            # Should still return a result via fallback
            assert result is not None
            assert result.confidence_score < 0.5  # Low confidence for fallback
            assert len(result.word_explanations) > 0

    def test_color_schemes(self):
        """Test color scheme generation."""
        beginner_colors = self.analyzer.get_color_scheme("beginner")
        intermediate_colors = self.analyzer.get_color_scheme("intermediate")
        advanced_colors = self.analyzer.get_color_scheme("advanced")

        # Check that all schemes have expected roles
        expected_roles = ["noun", "verb", "adjective", "particle", "classifier"]
        for role in expected_roles:
            assert role in beginner_colors
            assert role in intermediate_colors
            assert role in advanced_colors

        # Check that colors are valid hex codes
        import re
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        for scheme in [beginner_colors, intermediate_colors, advanced_colors]:
            for color in scheme.values():
                assert hex_pattern.match(color), f"Invalid color: {color}"

    def test_performance(self):
        """Test performance requirements."""
        sentence = "这是一个测试句子"

        with patch.object(self.analyzer, '_call_ai') as mock_ai:
            mock_ai.return_value = '''
            {
              "sentence": "这是一个测试句子",
              "words": [
                {"word": "这", "grammatical_role": "pronoun", "individual_meaning": "this"},
                {"word": "是", "grammatical_role": "verb", "individual_meaning": "to be"},
                {"word": "一个", "grammatical_role": "classifier", "individual_meaning": "one (with classifier)"},
                {"word": "测试", "grammatical_role": "noun", "individual_meaning": "test"},
                {"word": "句子", "grammatical_role": "noun", "individual_meaning": "sentence"}
              ],
              "explanations": {"overall_structure": "Topic-comment sentence"}
            }
            '''

            start_time = time.time()
            result = self.analyzer.analyze_grammar(sentence, "", "intermediate", self.test_api_key)
            end_time = time.time()

            # Should complete within reasonable time (allowing for mock)
            assert end_time - start_time < 5.0  # 5 seconds max


class TestZhConfig:
    """Test Chinese configuration."""

    def test_config_loading(self):
        """Test configuration loads correctly."""
        config = ZhConfig()

        # Check that required attributes exist
        assert hasattr(config, 'grammatical_roles')
        assert hasattr(config, 'common_classifiers')
        assert hasattr(config, 'aspect_markers')
        assert hasattr(config, 'word_meanings')
        assert hasattr(config, 'prompt_templates')

        # Check that classifiers loaded
        assert isinstance(config.common_classifiers, list)
        assert len(config.common_classifiers) > 0

    def test_color_schemes(self):
        """Test color scheme generation."""
        config = ZhConfig()

        schemes = ["beginner", "intermediate", "advanced"]
        for scheme_name in schemes:
            colors = config.get_color_scheme(scheme_name)
            assert isinstance(colors, dict)
            assert len(colors) > 0
            # Should have Chinese-specific roles
            assert "classifier" in colors
            assert "aspect_marker" in colors


class TestZhPatterns:
    """Test Chinese pattern recognition."""

    def test_particle_recognition(self):
        """Test particle pattern matching."""
        config = ZhConfig()
        patterns = ZhPatterns(config)

        # Test aspect markers
        assert patterns.is_aspect_marker("了")
        assert patterns.is_aspect_marker("着")
        assert patterns.is_aspect_marker("过")
        assert not patterns.is_aspect_marker("的")

        # Test particles
        assert patterns.is_particle("吗")
        assert patterns.is_particle("呢")
        assert patterns.is_particle("的")
        assert not patterns.is_particle("苹果")

    def test_classifier_recognition(self):
        """Test classifier pattern matching."""
        config = ZhConfig()
        patterns = ZhPatterns(config)

        assert patterns.is_classifier("个")
        assert patterns.is_classifier("本")
        assert patterns.is_classifier("杯")
        assert not patterns.is_classifier("苹果")

    def test_han_character_validation(self):
        """Test Han character detection."""
        config = ZhConfig()
        patterns = ZhPatterns(config)

        assert patterns.is_han_character("苹果")
        assert patterns.is_han_character("你好")
        assert not patterns.is_han_character("hello")
        assert patterns.is_han_character("hello世界")  # Mixed


class TestZhFallbacks:
    """Test Chinese fallback system."""

    def test_fallback_generation(self):
        """Test fallback analysis generation."""
        config = ZhConfig()
        fallbacks = ZhFallbacks(config)

        sentence = "我吃苹果"
        result = fallbacks.create_fallback(sentence, "intermediate")

        assert result is not None
        assert result['sentence'] == sentence
        assert len(result['word_explanations']) > 0
        assert result['confidence'] == 0.3
        assert result['is_fallback'] is True

    def test_role_guessing(self):
        """Test grammatical role guessing."""
        config = ZhConfig()
        fallbacks = ZhFallbacks(config)

        # Test various words
        assert fallbacks._guess_role("我") == "pronoun"
        assert fallbacks._guess_role("了") == "aspect_marker"
        assert fallbacks._guess_role("个") == "classifier"
        assert fallbacks._guess_role("吗") == "modal_particle"
        assert fallbacks._guess_role("苹果") == "noun"  # Default


if __name__ == "__main__":
    pytest.main([__file__])
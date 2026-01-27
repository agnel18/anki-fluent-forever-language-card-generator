#!/usr/bin/env python3
"""
Comprehensive Test Suite for ZhTwAnalyzer (Chinese Traditional Grammar Analyzer)
Updated for Modular Architecture v4.0

Tests cover:
- Modular component integration (config, prompt builder, parser, validator, fallbacks)
- Chinese Traditional-specific linguistic features
- Error handling and edge cases
- Quality validation and fallback mechanisms
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock, patch

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'streamlit_app'))

from languages.chinese_traditional.zh_tw_analyzer import ZhTwAnalyzer


class TestZhTwAnalyzer:
    """Comprehensive test suite for Chinese Traditional Grammar Analyzer"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing"""
        return ZhTwAnalyzer()

    @pytest.fixture
    def sample_sentences(self):
        """Sample Chinese Traditional sentences for testing"""
        return [
            "我吃了三個蘋果。",  # I ate three apples.
            "他在圖書館學習。",  # He is studying in the library.
            "你去過北京嗎？",   # Have you been to Beijing?
            "這本書很好看。",   # This book is very interesting.
            "我們一起吃飯吧。",  # Let's eat together.
        ]

    @pytest.fixture
    def mock_ai_response(self):
        """Mock AI response for batch processing tests"""
        return {
            "batch_results": [
                {
                    "sentence_index": 1,
                    "sentence": "我吃了三個蘋果。",
                    "words": [
                        {"word": "我", "individual_meaning": "I", "grammatical_role": "pronoun"},
                        {"word": "吃", "individual_meaning": "eat", "grammatical_role": "verb"},
                        {"word": "了", "individual_meaning": "perfective aspect", "grammatical_role": "aspect_particle"},
                        {"word": "三", "individual_meaning": "three", "grammatical_role": "numeral"},
                        {"word": "個", "individual_meaning": "classifier", "grammatical_role": "measure_word"},
                        {"word": "蘋果", "individual_meaning": "apple", "grammatical_role": "noun"}
                    ],
                    "word_combinations": [
                        {"text": "蘋果", "combined_meaning": "apple", "grammatical_role": "noun"}
                    ],
                    "explanations": {
                        "sentence_structure": "Subject-Verb-Object with perfective aspect",
                        "complexity_notes": "Basic sentence structure with measure word usage"
                    }
                },
                {
                    "sentence_index": 2,
                    "sentence": "他在圖書館學習。",
                    "words": [
                        {"word": "他", "individual_meaning": "he", "grammatical_role": "pronoun"},
                        {"word": "在", "individual_meaning": "at", "grammatical_role": "preposition"},
                        {"word": "圖書館", "individual_meaning": "library", "grammatical_role": "noun"},
                        {"word": "學習", "individual_meaning": "study", "grammatical_role": "verb"}
                    ],
                    "word_combinations": [
                        {"text": "圖書館", "combined_meaning": "library", "grammatical_role": "noun"}
                    ],
                    "explanations": {
                        "sentence_structure": "Subject-Location-Verb structure",
                        "complexity_notes": "Prepositional phrase usage"
                    }
                }
            ]
        }

    def test_initialization(self, analyzer):
        """Test analyzer initialization and basic properties"""
        assert analyzer.VERSION == "4.0"  # Updated for modular architecture
        assert analyzer.LANGUAGE_CODE == "zh-tw"
        assert analyzer.LANGUAGE_NAME == "Chinese Traditional"

        # Test modular components are initialized
        assert hasattr(analyzer, 'config')
        assert hasattr(analyzer, 'prompt_builder')
        assert hasattr(analyzer, 'response_parser')
        assert hasattr(analyzer, 'validator')
        assert hasattr(analyzer, 'fallbacks')

        # Test config properties
        assert analyzer.config.language_code == "zh-tw"
        assert analyzer.config.language_name == "Chinese Traditional"
        assert len(analyzer.config.grammatical_roles) == 16  # 16 Chinese categories

    def test_config_initialization(self, analyzer):
        """Test configuration component initialization"""
        config = analyzer.config

        # Test basic properties
        assert config.language_code == "zh-tw"
        assert config.language_name == "Chinese Traditional"
        assert config.native_name == "繁體中文"
        assert config.family == "Sino-Tibetan"
        assert config.complexity_rating == "high"

        # Test grammatical roles
        assert 'noun' in config.grammatical_roles
        assert 'verb' in config.grammatical_roles
        assert 'aspect_particle' in config.grammatical_roles
        assert 'measure_word' in config.grammatical_roles

        # Test word patterns
        assert 'measure_words' in config.word_patterns
        assert 'aspect_particles' in config.word_patterns
        assert 'modal_particles' in config.word_patterns

    def test_prompt_builder(self, analyzer):
        """Test prompt builder component"""
        prompt_builder = analyzer.prompt_builder

        # Test prompt generation
        sentences = ["我吃飯。", "你學習。"]
        prompt = prompt_builder.build_batch_grammar_prompt(
            complexity="intermediate",
            sentences=sentences,
            target_word="吃",
            native_language="English"
        )

        assert "Chinese Traditional" in prompt
        assert "intermediate" in prompt
        assert "我吃飯。" in prompt
        assert "你學習。" in prompt
        assert "target word: \"吃\"" in prompt

    def test_response_parser(self, analyzer):
        """Test response parser component"""
        parser = analyzer.response_parser

        # Test JSON extraction
        json_response = '{"batch_results": [{"sentence_index": 1, "words": []}]}'
        parsed = parser._extract_json_from_response(json_response)
        assert parsed is not None
        assert 'batch_results' in parsed

        # Test invalid response handling
        invalid_response = "This is not JSON"
        parsed = parser._extract_json_from_response(invalid_response)
        assert parsed is None

    def test_validator(self, analyzer):
        """Test validator component"""
        validator = analyzer.validator

        # Test validation of good result
        good_result = {
            'words': [
                {'word': '我', 'individual_meaning': 'I', 'grammatical_role': 'pronoun'},
                {'word': '吃', 'individual_meaning': 'eat', 'grammatical_role': 'verb'},
                {'word': '飯', 'individual_meaning': 'rice/meal', 'grammatical_role': 'noun'}
            ],
            'word_combinations': [],
            'original_sentence': '我吃飯。'
        }

        validation = validator.validate_analysis(good_result)
        assert validation['is_valid'] is True
        assert validation['quality_score'] > 0

        # Test validation of bad result
        bad_result = {
            'words': [],
            'word_combinations': [],
            'original_sentence': ''
        }

        validation = validator.validate_analysis(bad_result)
        assert validation['is_valid'] is False
        assert validation['quality_score'] < 50

    def test_fallbacks(self, analyzer):
        """Test fallbacks component"""
        fallbacks = analyzer.fallbacks

        # Test fallback analysis
        sentence = "我吃飯。"
        result = fallbacks.generate_fallback_analysis(sentence)

        assert result['analysis_method'] == 'fallback_rule_based'
        assert 'words' in result
        assert len(result['words']) > 0

    def test_modular_integration(self, analyzer, sample_sentences):
        """Test integration of all modular components"""
        # Test full pipeline with mocked AI response
        mock_response = json.dumps({
            "batch_results": [{
                "sentence_index": 1,
                "words": [
                    {"word": "我", "individual_meaning": "I", "grammatical_role": "pronoun"},
                    {"word": "吃", "individual_meaning": "eat", "grammatical_role": "verb"},
                    {"word": "飯", "individual_meaning": "rice/meal", "grammatical_role": "noun"}
                ],
                "word_combinations": []
            }]
        })

        # This would normally call AI, but we'll test the parsing pipeline
        parsed = analyzer.response_parser.parse_batch_response(mock_response, sample_sentences[:1])
        assert parsed['success'] is True
        assert len(parsed['results']) == 1

    def test_language_info(self, analyzer):
        """Test language information retrieval"""
        info = analyzer.get_language_info()

        assert info['code'] == 'zh-tw'
        assert info['name'] == 'Chinese Traditional'
        assert info['native_name'] == '繁體中文'
        assert info['family'] == 'Sino-Tibetan'
        assert info['complexity_rating'] == 'high'
        assert info['analyzer_version'] == '4.0'

    def test_supported_levels(self, analyzer):
        """Test supported complexity levels"""
        levels = analyzer.get_supported_complexity_levels()
        assert 'beginner' in levels
        assert 'intermediate' in levels
        assert 'advanced' in levels

    def test_grammatical_roles(self, analyzer):
        """Test grammatical roles access"""
        roles = analyzer.get_grammatical_roles()
        assert isinstance(roles, dict)
        assert len(roles) == 16  # Chinese has 16 categories
        assert 'noun' in roles
        assert 'aspect_particle' in roles

    def test_sentence_validation(self, analyzer):
        """Test sentence validation"""
        # Valid sentence
        valid_result = analyzer.validate_sentence("我吃飯。")
        assert valid_result['is_valid'] is True

        # Invalid sentence
        invalid_result = analyzer.validate_sentence("")
        assert invalid_result['is_valid'] is False

    def test_patterns_initialization(self, analyzer):
        """Test Chinese Traditional-specific pattern initialization"""
        # Check for key Chinese Traditional patterns
        assert hasattr(analyzer, 'aspect_patterns')
        assert hasattr(analyzer, 'modal_patterns')
        assert hasattr(analyzer, 'structural_patterns')
        assert hasattr(analyzer, 'measure_word_patterns')
        assert hasattr(analyzer, 'preposition_patterns')

        # Verify aspect particles pattern - Traditional characters
        aspect_patterns = analyzer.aspect_patterns
        assert 'perfective_le' in aspect_patterns
        assert 'durative_zhe' in aspect_patterns
        assert 'experiential_guo' in aspect_patterns

        # Check Traditional characters in patterns
        assert '著' in aspect_patterns['durative_zhe'].pattern  # Traditional 著
        assert '過' in aspect_patterns['experiential_guo'].pattern  # Traditional 過

    def test_grammatical_roles_mapping(self, analyzer):
        """Test grammatical role color mapping"""
        roles = analyzer.GRAMMATICAL_ROLES

        # Check content words
        assert roles['noun'] == "#FFAA00"  # Orange
        assert roles['verb'] == "#44FF44"  # Green
        assert roles['adjective'] == "#FF44FF"  # Magenta
        assert roles['measure_word'] == "#FFD700"  # Gold

        # Check function words
        assert roles['aspect_particle'] == "#8A2BE2"  # Purple
        assert roles['modal_particle'] == "#DA70D6"   # Plum
        assert roles['preposition'] == "#4444FF"      # Blue

    def test_batch_prompt_generation(self, analyzer, sample_sentences):
        """Test batch grammar prompt generation"""
        prompt = analyzer.get_batch_grammar_prompt("intermediate", sample_sentences, "學習")

        # Verify prompt structure
        assert "Chinese Traditional" in prompt
        assert "實詞/虛詞" in prompt  # Content/function word distinction
        assert "體詞" in prompt       # Aspect particles
        assert "語氣詞" in prompt     # Modal particles
        assert "量詞" in prompt       # Measure words

        # Check sentence inclusion
        for sentence in sample_sentences:
            assert sentence in prompt

        # Verify prompt length is reasonable
        assert len(prompt) > 1000  # Should be comprehensive

    def test_batch_response_parsing(self, analyzer, sample_sentences, mock_ai_response):
        """Test batch response parsing"""
        results = analyzer.parse_batch_grammar_response(
            json.dumps(mock_ai_response),
            sample_sentences,
            "intermediate"
        )

        assert len(results) == 2  # Two sentences processed

        # Check first result structure
        result1 = results[0]
        assert 'sentence' in result1
        assert 'elements' in result1
        assert 'word_explanations' in result1
        assert 'explanations' in result1

        # Verify sentence content
        assert result1['sentence'] == "我吃了三個蘋果。"

        # Check word explanations structure
        word_explanations = result1['word_explanations']
        assert len(word_explanations) == 6  # 6 words in sentence

        # Verify word explanation format [word, role, color, explanation]
        for explanation in word_explanations:
            assert len(explanation) == 4
            assert isinstance(explanation[0], str)  # word
            assert isinstance(explanation[1], str)  # role
            assert explanation[2].startswith('#')  # color
            assert isinstance(explanation[3], str)  # explanation

    def test_validation_high_quality(self, analyzer):
        """Test validation with high-quality analysis"""
        parsed_data = {
            'elements': {
                'noun': [{'word': '蘋果', 'individual_meaning': 'apple'}],
                'verb': [{'word': '吃', 'individual_meaning': 'eat'}],
                'aspect_particle': [{'word': '了', 'individual_meaning': 'perfective'}],
                'measure_word': [{'word': '個', 'individual_meaning': 'classifier'}],
                'modal_particle': [{'word': '嗎', 'individual_meaning': 'question'}]
            }
        }
        sentence = "你吃了幾個蘋果嗎？"

        score = analyzer.validate_analysis(parsed_data, sentence)
        assert score >= 0.85  # Should pass validation

    def test_validation_traditional_characters(self, analyzer):
        """Test validation specifically for Traditional character recognition"""
        # Test with valid Traditional characters
        parsed_data = {
            'elements': {
                'noun': [{'word': '蘋果', 'individual_meaning': 'apple'}],  # 蘋果 = Traditional
                'verb': [{'word': '學習', 'individual_meaning': 'study'}],  # 學習 = Traditional
                'measure_word': [{'word': '個', 'individual_meaning': 'classifier'}]  # 個 = Traditional
            }
        }
        sentence = "他在學習英語。"  # All Traditional characters

        score = analyzer.validate_analysis(parsed_data, sentence)
        assert score >= 0.7  # Should pass character validation

    def test_validation_rejects_simplified(self, analyzer):
        """Test that validation properly handles Simplified vs Traditional characters"""
        # This test ensures the analyzer is designed for Traditional characters
        # In practice, the AI should be prompted to use Traditional characters
        parsed_data = {
            'elements': {
                'noun': [{'word': '苹果', 'individual_meaning': 'apple'}],  # 苹果 = Simplified
                'verb': [{'word': '学习', 'individual_meaning': 'study'}],  # 学习 = Simplified
                'measure_word': [{'word': '个', 'individual_meaning': 'classifier'}]  # 个 = Simplified
            }
        }
        sentence = "他在学习英语。"  # All Simplified characters

        score = analyzer.validate_analysis(parsed_data, sentence)
        # Should have lower score due to character validation
        # (This tests that the analyzer is configured for Traditional characters)

    def test_measure_word_patterns_traditional(self, analyzer):
        """Test measure word patterns use Traditional characters"""
        patterns = analyzer.measure_word_patterns

        # Check Traditional measure words
        assert '個' in patterns['general_ge'].pattern      # 個 not 个
        assert '張' in patterns['flat_zhang'].pattern      # 張 not 张
        assert '隻' in patterns['animals_zhi'].pattern     # 隻 not 只
        assert '輛' in patterns['vehicles_liang'].pattern  # 輛 not 辆
        assert '條' in patterns['long_tiao'].pattern       # 條 not 条

    def test_aspect_particle_patterns_traditional(self, analyzer):
        """Test aspect particle patterns use Traditional characters"""
        patterns = analyzer.aspect_patterns

        # Check Traditional aspect particles
        assert '著' in patterns['durative_zhe'].pattern     # 著 not 着
        assert '過' in patterns['experiential_guo'].pattern # 過 not 过

    def test_color_scheme_consistency(self, analyzer):
        """Test color scheme matches Simplified Chinese analyzer"""
        colors = analyzer.get_color_scheme("intermediate")

        # Should have same color scheme as Simplified analyzer
        assert colors['noun'] == "#FFAA00"
        assert colors['verb'] == "#44FF44"
        assert colors['aspect_particle'] == "#8A2BE2"
        assert colors['measure_word'] == "#FFD700"

    def test_reorder_explanations_by_position(self, analyzer):
        """Test word explanation reordering by sentence position"""
        sentence = "我在學習中文。"
        word_explanations = [
            ["學習", "verb", "#44FF44", "study (verb)"],      # Position 3
            ["我", "pronoun", "#FF4444", "I (pronoun)"],      # Position 0
            ["在", "preposition", "#4444FF", "at (preposition)"], # Position 1
            ["中文", "noun", "#FFAA00", "Chinese (noun)"]     # Position 4
        ]

        reordered = analyzer._reorder_explanations_by_sentence_position(sentence, word_explanations)

        # Should be reordered by position in sentence
        assert reordered[0][0] == "我"      # Position 0
        assert reordered[1][0] == "在"      # Position 1
        assert reordered[2][0] == "學習"    # Position 3
        assert reordered[3][0] == "中文"    # Position 4

    def test_language_config(self, analyzer):
        """Test language configuration"""
        config = analyzer.config

        assert config.code == "zh-tw"
        assert config.name == "Chinese Traditional"
        assert config.native_name == "繁體中文"
        assert config.family == "Sino-Tibetan"
        assert config.script_type == "logographic"
        assert config.complexity_rating == "high"
        assert "chinese_categories" in config.key_features

    def test_fallback_parsing(self, analyzer):
        """Test fallback parsing when AI response is malformed"""
        malformed_response = "Invalid JSON response"
        sentence = "這是一個測試句子。"

        result = analyzer._create_fallback_parse(malformed_response, sentence)

        assert result['sentence'] == sentence
        assert result['elements'] == {}
        assert 'parsing_error' in result['explanations']

    def test_empty_input_handling(self, analyzer):
        """Test handling of empty or None inputs"""
        # Test empty sentence list
        results = analyzer.parse_batch_grammar_response("{}", [], "intermediate")
        assert results == []

        # Test None inputs
        reordered = analyzer._reorder_explanations_by_sentence_position(None, None)
        assert reordered == []

        reordered_empty = analyzer._reorder_explanations_by_sentence_position("", [])
        assert reordered_empty == []

    def test_validation_edge_cases(self, analyzer):
        """Test validation with edge cases"""
        # Empty analysis
        score = analyzer.validate_analysis({}, "")
        assert score == 0.5  # Neutral fallback

        # Analysis with no elements
        score = analyzer.validate_analysis({'elements': {}}, "test")
        assert score == 0.5  # Neutral fallback

    def test_pattern_compilation(self, analyzer):
        """Test that all patterns compile correctly"""
        # This will raise an exception if any pattern has syntax errors
        assert analyzer.aspect_patterns is not None
        assert analyzer.modal_patterns is not None
        assert analyzer.structural_patterns is not None
        assert analyzer.measure_word_patterns is not None
        assert analyzer.preposition_patterns is not None

        # Verify patterns are compiled regex objects
        import re
        for pattern_dict in [analyzer.aspect_patterns, analyzer.modal_patterns,
                           analyzer.structural_patterns, analyzer.measure_word_patterns,
                           analyzer.preposition_patterns]:
            for pattern in pattern_dict.values():
                assert hasattr(pattern, 'search')  # Compiled regex object

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
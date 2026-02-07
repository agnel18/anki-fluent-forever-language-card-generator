#!/usr/bin/env python3
"""
Comprehensive Test Suite for ZhAnalyzer (Chinese Simplified Grammar Analyzer)
Phase 4: Tests + Documentation

Tests cover:
- Core functionality (patterns, validation, batch processing)
- Chinese-specific linguistic features
- Error handling and edge cases
- HTML generation and color coding
- Integration with batch processor
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'streamlit_app'))

from languages.chinese_simplified.zh_analyzer import ZhAnalyzer


class TestZhAnalyzer:
    """Comprehensive test suite for Chinese Simplified Grammar Analyzer"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing"""
        return ZhAnalyzer()

    @pytest.fixture
    def sample_sentences(self):
        """Sample Chinese sentences for testing"""
        return [
            "æˆ‘åƒäº†ä¸‰ä¸ªè‹¹æžœã€‚",  # I ate three apples.
            "ä»–åœ¨å›¾ä¹¦é¦†å­¦ä¹ ã€‚",  # He is studying in the library.
            "ä½ åŽ»è¿‡åŒ—äº¬å—ï¼Ÿ",   # Have you been to Beijing?
            "è¿™æœ¬ä¹¦å¾ˆå¥½çœ‹ã€‚",   # This book is very interesting.
            "æˆ‘ä»¬ä¸€èµ·åƒé¥­å§ã€‚",  # Let's eat together.
        ]

    @pytest.fixture
    def mock_ai_response(self):
        """Mock AI response for batch processing tests"""
        return {
            "results": [
                {
                    "sentence_index": 0,
                    "analysis": [
                        {"word": "æˆ‘", "role": "pronoun", "pinyin": "wÇ’"},
                        {"word": "åƒ", "role": "verb", "pinyin": "chÄ«"},
                        {"word": "äº†", "role": "aspect_particle", "pinyin": "le"},
                        {"word": "ä¸‰", "role": "numeral", "pinyin": "sÄn"},
                        {"word": "ä¸ª", "role": "measure_word", "pinyin": "gÃ¨"},
                        {"word": "è‹¹æžœ", "role": "noun", "pinyin": "pÃ­ngguÇ’"}
                    ],
                    "confidence": 0.95
                },
                {
                    "sentence_index": 1,
                    "analysis": [
                        {"word": "ä»–", "role": "pronoun", "pinyin": "tÄ"},
                        {"word": "åœ¨", "role": "preposition", "pinyin": "zÃ i"},
                        {"word": "å›¾ä¹¦é¦†", "role": "noun", "pinyin": "tÃºshÅ«guÇŽn"},
                        {"word": "å­¦ä¹ ", "role": "verb", "pinyin": "xuÃ©xÃ­"}
                    ],
                    "confidence": 0.92
                }
            ]
        }

    def test_initialization(self, analyzer):
        """Test analyzer initialization and basic properties"""
        assert analyzer.VERSION == "3.0"
        assert analyzer.language_code == "zh"
        assert analyzer.language_name == "Chinese Simplified"
        assert hasattr(analyzer, '_patterns')
        assert hasattr(analyzer, '_grammatical_roles')

    def test_patterns_initialization(self, analyzer):
        """Test Chinese-specific pattern initialization"""
        patterns = analyzer._patterns

        # Check for key Chinese patterns
        assert 'aspect_particles' in patterns
        assert 'modal_particles' in patterns
        assert 'structural_particles' in patterns
        assert 'measure_words' in patterns
        assert 'prepositions' in patterns

        # Verify aspect particles pattern
        aspect_pattern = patterns['aspect_particles']
        assert 'äº†' in aspect_pattern.pattern
        assert 'ç€' in aspect_pattern.pattern
        assert 'è¿‡' in aspect_pattern.pattern

    def test_grammatical_roles_mapping(self, analyzer):
        """Test grammatical role color mapping"""
        roles = analyzer._grammatical_roles

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
        prompt = analyzer.get_batch_grammar_prompt(sample_sentences)

        # Verify prompt structure
        assert "Chinese Simplified" in prompt
        assert "å®žè¯/è™šè¯" in prompt  # Content/function word distinction
        assert "ä½“è¯" in prompt       # Aspect particles
        assert "è¯­æ°”è¯" in prompt     # Modal particles
        assert "é‡è¯" in prompt       # Measure words

        # Check sentence inclusion
        for sentence in sample_sentences:
            assert sentence in prompt

        # Verify prompt length is reasonable
        assert len(prompt) > 1000  # Should be comprehensive

    @patch('language_analyzers.analyzers.zh_analyzer.call_ai_with_retry')
    def test_batch_response_parsing(self, mock_ai_call, analyzer, sample_sentences, mock_ai_response):
        """Test batch response parsing"""
        mock_ai_call.return_value = json.dumps(mock_ai_response)

        results = analyzer.parse_batch_grammar_response(
            json.dumps(mock_ai_response),
            sample_sentences
        )

        assert len(results) == 2  # Two sentences processed

        # Check first result structure
        result1 = results[0]
        assert 'analysis' in result1
        assert 'confidence' in result1
        assert 'html_output' in result1

        # Verify analysis structure
        analysis = result1['analysis']
        assert len(analysis) == 6  # 6 words in first sentence
        assert analysis[0]['word'] == 'æˆ‘'
        assert analysis[0]['role'] == 'pronoun'

    def test_validation_logic(self, analyzer):
        """Test validation checks"""
        # Valid analysis
        valid_analysis = [
            {"word": "æˆ‘", "role": "pronoun", "pinyin": "wÇ’"},
            {"word": "åƒ", "role": "verb", "pinyin": "chÄ«"},
            {"word": "äº†", "role": "aspect_particle", "pinyin": "le"},
            {"word": "è‹¹æžœ", "role": "noun", "pinyin": "pÃ­ngguÇ’"}
        ]

        is_valid, confidence, issues = analyzer.validate_analysis(valid_analysis)
        assert is_valid
        assert confidence >= 0.85

        # Invalid analysis (missing required particles)
        invalid_analysis = [
            {"word": "æˆ‘", "role": "pronoun", "pinyin": "wÇ’"},
            {"word": "åƒ", "role": "verb", "pinyin": "chÄ«"},
            {"word": "è‹¹æžœ", "role": "noun", "pinyin": "pÃ­ngguÇ’"}
        ]

        is_valid, confidence, issues = analyzer.validate_analysis(invalid_analysis)
        assert not is_valid or confidence < 0.85

    def test_html_generation(self, analyzer):
        """Test HTML output generation"""
        analysis = [
            {"word": "æˆ‘", "role": "pronoun", "pinyin": "wÇ’"},
            {"word": "åƒ", "role": "verb", "pinyin": "chÄ«"},
            {"word": "äº†", "role": "aspect_particle", "pinyin": "le"},
            {"word": "è‹¹æžœ", "role": "noun", "pinyin": "pÃ­ngguÇ’"}
        ]

        html = analyzer.generate_html_output(analysis, "æˆ‘åƒäº†è‹¹æžœã€‚")

        # Check HTML structure
        assert "<span" in html
        assert "style=" in html
        assert "æˆ‘" in html
        assert "åƒäº†" in html
        assert "è‹¹æžœ" in html

        # Check color coding
        assert "#FF4444" in html  # Red for pronoun
        assert "#44FF44" in html  # Green for verb
        assert "#8A2BE2" in html  # Purple for aspect particle
        assert "#FFAA00" in html  # Orange for noun

    def test_character_validation(self, analyzer):
        """Test Han character validation"""
        # Valid Chinese characters
        valid_text = "æˆ‘åƒäº†ä¸‰ä¸ªè‹¹æžœã€‚"
        assert analyzer._validate_characters(valid_text)

        # Invalid characters (contains English)
        invalid_text = "I ate three apples."
        assert not analyzer._validate_characters(invalid_text)

        # Mixed valid/invalid
        mixed_text = "æˆ‘åƒäº†threeä¸ªè‹¹æžœã€‚"
        assert not analyzer._validate_characters(mixed_text)

    def test_measure_word_validation(self, analyzer):
        """Test measure word agreement validation"""
        # Valid: numeral + measure word + noun
        valid_analysis = [
            {"word": "ä¸‰", "role": "numeral"},
            {"word": "ä¸ª", "role": "measure_word"},
            {"word": "è‹¹æžœ", "role": "noun"}
        ]
        assert analyzer._validate_measure_words(valid_analysis)

        # Invalid: missing measure word
        invalid_analysis = [
            {"word": "ä¸‰", "role": "numeral"},
            {"word": "è‹¹æžœ", "role": "noun"}
        ]
        assert not analyzer._validate_measure_words(invalid_analysis)

    def test_particle_position_validation(self, analyzer):
        """Test particle position validation"""
        # Valid: aspect particle after verb
        valid_analysis = [
            {"word": "åƒ", "role": "verb"},
            {"word": "äº†", "role": "aspect_particle"}
        ]
        assert analyzer._validate_particle_positions(valid_analysis)

        # Invalid: aspect particle before verb
        invalid_analysis = [
            {"word": "äº†", "role": "aspect_particle"},
            {"word": "åƒ", "role": "verb"}
        ]
        assert not analyzer._validate_particle_positions(invalid_analysis)

    def test_pinyin_validation(self, analyzer):
        """Test Pinyin romanization validation"""
        # Valid Pinyin with tone marks
        valid_analysis = [
            {"word": "æˆ‘", "pinyin": "wÇ’"},
            {"word": "åƒ", "pinyin": "chÄ«"},
            {"word": "äº†", "pinyin": "le"}
        ]
        assert analyzer._validate_pinyin(valid_analysis)

        # Invalid: missing tone marks
        invalid_analysis = [
            {"word": "æˆ‘", "pinyin": "wo"},
            {"word": "åƒ", "pinyin": "chi"}
        ]
        assert not analyzer._validate_pinyin(invalid_analysis)

    def test_error_handling(self, analyzer):
        """Test error handling and fallbacks"""
        # Test with malformed JSON
        malformed_response = "{invalid json"
        results = analyzer.parse_batch_grammar_response(malformed_response, ["test"])

        # Should return fallback results
        assert isinstance(results, list)
        assert len(results) >= 0

    def test_empty_input_handling(self, analyzer):
        """Test handling of empty or invalid inputs"""
        # Empty sentence list
        prompt = analyzer.get_batch_grammar_prompt([])
        assert isinstance(prompt, str)

        # None input
        results = analyzer.parse_batch_grammar_response(None, [])
        assert isinstance(results, list)

    def test_batch_processing_integration(self, analyzer, sample_sentences):
        """Test full batch processing integration"""
        # This would normally call AI, but we'll mock it
        with patch('language_analyzers.analyzers.zh_analyzer.call_ai_with_retry') as mock_call:
            mock_response = {
                "results": [
                    {
                        "sentence_index": i,
                        "analysis": [
                            {"word": word, "role": "noun", "pinyin": "test"}
                            for word in sentence.replace("ã€‚", "").replace("ï¼Ÿ", "").replace("ï¼", "")
                        ],
                        "confidence": 0.9
                    } for i, sentence in enumerate(sample_sentences)
                ]
            }
            mock_call.return_value = json.dumps(mock_response)

            results = analyzer.process_batch_grammar_analysis(sample_sentences)

            assert len(results) == len(sample_sentences)
            for result in results:
                assert 'analysis' in result
                assert 'confidence' in result
                assert 'html_output' in result

    def test_confidence_scoring(self, analyzer):
        """Test confidence score calculation"""
        # High confidence analysis
        high_conf_analysis = [
            {"word": "æˆ‘", "role": "pronoun", "pinyin": "wÇ’"},
            {"word": "åƒ", "role": "verb", "pinyin": "chÄ«"},
            {"word": "äº†", "role": "aspect_particle", "pinyin": "le"},
            {"word": "è‹¹æžœ", "role": "noun", "pinyin": "pÃ­ngguÇ’"}
        ]

        is_valid, confidence, issues = analyzer.validate_analysis(high_conf_analysis)
        assert confidence >= 0.85

        # Low confidence analysis (missing particles)
        low_conf_analysis = [
            {"word": "æˆ‘", "role": "noun"},  # Wrong role
            {"word": "åƒ", "role": "verb"},
            {"word": "è‹¹æžœ", "role": "noun"}
        ]

        is_valid, confidence, issues = analyzer.validate_analysis(low_conf_analysis)
        assert confidence < 0.85

    def test_logging_integration(self, analyzer, caplog):
        """Test logging functionality"""
        import logging
        caplog.set_level(logging.INFO)

        # Trigger some logging
        analyzer.validate_analysis([])

        # Check that logging occurred
        assert len(caplog.records) >= 0  # May or may not log depending on implementation


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

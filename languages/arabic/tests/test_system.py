# Arabic System Tests
# End-to-end testing for Arabic grammar analyzer
# Tests complete workflows from input to output

import pytest
import json
import time
from unittest.mock import patch, MagicMock


class TestArabicSystem:
    """System-level tests for Arabic analyzer end-to-end functionality"""

    @pytest.fixture
    def mock_gemini_api(self):
        """Mock Gemini API for system tests"""
        with patch('languages.arabic.ar_analyzer.ArAnalyzer._call_ai') as mock_call_ai:
            mock_call_ai.return_value = '''{
                "words": [
                    {"word": "القطة", "grammatical_role": "noun", "meaning": "The cat (subject)"},
                    {"word": "سوداء", "grammatical_role": "adjective", "meaning": "black (description)"}
                ],
                "explanations": {
                    "overall_structure": "Simple nominal sentence with subject-predicate structure",
                    "key_features": "Definite article assimilation, adjective agreement"
                }
            }'''
            yield mock_call_ai

    def test_complete_arabic_analysis_workflow(self, arabic_analyzer, mock_gemini_api):
        """Test complete analysis workflow from sentence to HTML output"""
        sentence = "القطة سوداء"
        target_word = "قطة"
        complexity = "intermediate"

        # Execute complete analysis
        result = arabic_analyzer.analyze_grammar(sentence, target_word, complexity, "mock_key")

        # Verify result structure
        assert result.sentence == sentence
        assert result.target_word == target_word
        assert result.complexity_level == complexity
        assert result.language_code == "ar"
        assert hasattr(result, 'is_rtl') and result.is_rtl == True
        assert hasattr(result, 'text_direction') and result.text_direction == "rtl"

        # Verify word explanations
        assert len(result.word_explanations) > 0
        for explanation in result.word_explanations:
            assert len(explanation) >= 3  # word, role, color, [meaning]

        # Verify explanations
        assert 'overall_structure' in result.explanations
        assert 'key_features' in result.explanations

        # Verify HTML output
        assert result.html_output is not None
        assert 'dir="rtl"' in result.html_output  # RTL HTML attribute
        # Check that individual words from the sentence appear in the HTML
        for word in sentence.split():
            assert word in result.html_output

        # Verify color scheme
        assert isinstance(result.color_scheme, dict)
        assert len(result.color_scheme) > 0

        # Verify confidence score
        assert 0.0 <= result.confidence_score <= 1.0

    def test_arabic_batch_processing_system(self, arabic_analyzer, mock_gemini_api):
        """Test batch processing system for multiple Arabic sentences"""
        sentences = [
            "القطة سوداء",
            "أنا أدرس العربية",
            "الطالب يقرأ الكتاب"
        ]
        target_word = "قطة"
        complexity = "intermediate"

        # Execute batch analysis
        results = arabic_analyzer.batch_analyze_grammar(sentences, target_word, complexity, "mock_key")

        # Verify batch results
        assert len(results) == len(sentences)
        for i, result in enumerate(results):
            assert result.sentence == sentences[i]
            assert result.target_word == target_word
            assert result.complexity_level == complexity
            assert result.language_code == "ar"
            assert hasattr(result, 'is_rtl') and result.is_rtl == True
            assert len(result.word_explanations) > 0
            assert result.html_output is not None
            assert 0.0 <= result.confidence_score <= 1.0

    def test_arabic_error_recovery_system(self, arabic_analyzer):
        """Test error recovery and fallback systems"""
        # Test with invalid API key
        result = arabic_analyzer.analyze_grammar("القطة سوداء", "قطة", "intermediate", "")

        # Should return fallback analysis
        assert result.sentence == "القطة سوداء"
        assert result.confidence_score < 0.5  # Low confidence for fallback
        assert len(result.word_explanations) > 0
        assert result.html_output is not None
        assert 'dir="rtl"' in result.html_output

    def test_arabic_complexity_levels_system(self, arabic_analyzer, mock_gemini_api):
        """Test all complexity levels in system context"""
        sentence = "الطالب الذي يدرس بجد سيحصل على درجة عالية"
        target_word = "يدرس"

        for complexity in ["beginner", "intermediate", "advanced"]:
            result = arabic_analyzer.analyze_grammar(sentence, target_word, complexity, "mock_key")

            assert result.complexity_level == complexity
            assert result.sentence == sentence
            assert result.target_word == target_word
            assert len(result.word_explanations) > 0
            assert result.html_output is not None

            # Verify color scheme matches complexity
            expected_colors = arabic_analyzer.config.get_color_scheme(complexity)
            assert result.color_scheme == expected_colors

    def test_arabic_rtl_text_processing_system(self, arabic_analyzer, mock_gemini_api):
        """Test RTL text processing in complete system"""
        # Arabic sentence with mixed script (should still be RTL)
        sentence = "Hello world مرحبا بالعالم"
        target_word = "مرحبا"

        result = arabic_analyzer.analyze_grammar(sentence, target_word, "intermediate", "mock_key")

        # Should maintain RTL properties
        assert hasattr(result, 'is_rtl') and result.is_rtl == True
        assert hasattr(result, 'text_direction') and result.text_direction == "rtl"
        assert 'dir="rtl"' in result.html_output

        # Should process all words including non-Arabic
        assert len(result.word_explanations) >= 2  # At least Arabic and non-Arabic words

    def test_arabic_api_integration_system(self, arabic_analyzer):
        """Test API integration and response handling"""
        with patch.object(arabic_analyzer, '_call_ai') as mock_call_ai:
            # Mock successful API call - _call_ai returns JSON string directly
            mock_response = '''{
                "words": [
                    {"word": "مرحبا", "grammatical_role": "interjection", "meaning": "hello (greeting)"},
                    {"word": "بالعالم", "grammatical_role": "noun", "meaning": "the world (object)"}
                ],
                "explanations": {
                    "overall_structure": "Greeting phrase with direct object",
                    "key_features": "Prepositional phrase, definite article assimilation"
                }
            }'''
            mock_call_ai.return_value = mock_response

            result = arabic_analyzer.analyze_grammar("مرحبا بالعالم", "مرحبا", "intermediate", "test_key")

            # Verify API was called correctly
            mock_call_ai.assert_called_once()

            # Verify result processing
            assert result.confidence_score > 0.5
            assert len(result.word_explanations) == 2
            assert result.explanations['overall_structure'] == "Greeting phrase with direct object"

    def test_arabic_performance_requirements_system(self, arabic_analyzer, mock_gemini_api):
        """Test performance requirements for Arabic analysis"""
        sentence = "الطالب الذي يدرس بجد سيحصل على درجة عالية"
        target_word = "يدرس"

        # Measure analysis time
        start_time = time.time()
        result = arabic_analyzer.analyze_grammar(sentence, target_word, "intermediate", "mock_key")
        end_time = time.time()

        analysis_time = end_time - start_time

        # Should complete within reasonable time (30 seconds max as per guide)
        assert analysis_time < 30.0, f"Analysis took {analysis_time:.2f} seconds"

        # Should produce valid result
        assert result is not None
        assert result.confidence_score > 0

    def test_arabic_memory_usage_system(self, arabic_analyzer, mock_gemini_api):
        """Test memory usage stability during multiple analyses"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Perform multiple analyses
        sentences = [
            "القطة سوداء",
            "أنا أدرس العربية",
            "الطالب يقرأ الكتاب",
            "المعلم يكتب الدرس",
            "الطالبة تكتب الواجب"
        ]

        for sentence in sentences:
            result = arabic_analyzer.analyze_grammar(sentence, sentence.split()[0], "intermediate", "mock_key")
            assert result is not None

        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory

        # Memory growth should be reasonable (less than 50MB as per guide)
        assert memory_growth < 50 * 1024 * 1024, f"Memory grew by {memory_growth / 1024 / 1024:.2f} MB"

    def test_arabic_output_format_consistency_system(self, arabic_analyzer, mock_gemini_api):
        """Test output format consistency across different inputs"""
        test_cases = [
            ("القطة", "قطة", "beginner"),
            ("أنا أدرس", "أدرس", "intermediate"),
            ("الطالب الذي يدرس بجد", "يدرس", "advanced")
        ]

        for sentence, target_word, complexity in test_cases:
            result = arabic_analyzer.analyze_grammar(sentence, target_word, complexity, "mock_key")

            # Verify consistent output structure
            assert hasattr(result, 'sentence')
            assert hasattr(result, 'target_word')
            assert hasattr(result, 'complexity_level')
            assert hasattr(result, 'language_code')
            assert hasattr(result, 'word_explanations')
            assert hasattr(result, 'explanations')
            assert hasattr(result, 'color_scheme')
            assert hasattr(result, 'html_output')
            assert hasattr(result, 'confidence_score')

            # Verify Arabic-specific attributes
            assert hasattr(result, 'is_rtl')
            assert hasattr(result, 'text_direction')

            # Verify data types
            assert isinstance(result.word_explanations, list)
            assert isinstance(result.explanations, dict)
            assert isinstance(result.color_scheme, dict)
            assert isinstance(result.html_output, str)
            assert isinstance(result.confidence_score, (int, float))
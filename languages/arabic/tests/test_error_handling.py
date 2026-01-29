# Arabic Error Handling Tests
# Comprehensive error handling and recovery tests for Arabic analyzer
# Tests API failures, invalid inputs, network issues, and recovery mechanisms

import pytest
import json
from unittest.mock import patch, MagicMock
from languages.arabic.ar_analyzer import ArAnalyzer


class TestArabicErrorHandling:
    """Error handling tests for Arabic analyzer"""

    @pytest.fixture
    def mock_gemini_api_failure(self):
        """Mock Gemini API that always fails"""
        with patch('languages.arabic.ar_analyzer.ArAnalyzer._call_ai') as mock_call_ai:
            mock_call_ai.return_value = None
            yield mock_call_ai

    @pytest.fixture
    def mock_gemini_api_timeout(self):
        """Mock Gemini API that times out"""
        with patch('languages.arabic.ar_analyzer.ArAnalyzer._call_ai') as mock_call_ai:
            mock_call_ai.side_effect = TimeoutError("Request timeout")
            yield mock_call_ai

    @pytest.fixture
    def mock_gemini_api_invalid_response(self):
        """Mock Gemini API that returns invalid JSON"""
        with patch('languages.arabic.ar_analyzer.ArAnalyzer._call_ai') as mock_call_ai:
            mock_call_ai.return_value = "Invalid JSON response {"
            yield mock_call_ai

    @pytest.fixture
    def mock_gemini_api_empty_response(self):
        """Mock Gemini API that returns empty response"""
        with patch('languages.arabic.ar_analyzer.ArAnalyzer._call_ai') as mock_call_ai:
            mock_call_ai.return_value = ""
            yield mock_call_ai

    def test_arabic_api_failure_graceful_degradation(self, arabic_analyzer, mock_gemini_api_failure):
        """Test graceful degradation when API fails"""
        sentence = "القطة سوداء"
        target_word = "قطة"

        # Should not raise exception, should return fallback result
        result = arabic_analyzer.analyze_grammar(sentence, target_word, "intermediate", "invalid_key")

        # Should still return a result (fallback)
        assert result is not None
        assert hasattr(result, 'confidence_score')
        assert result.confidence_score < 0.5  # Low confidence for failed analysis

    def test_arabic_timeout_recovery(self, arabic_analyzer, mock_gemini_api_timeout):
        """Test recovery from API timeouts"""
        sentence = "أنا أدرس العربية"
        target_word = "أدرس"

        # Should handle timeout gracefully
        result = arabic_analyzer.analyze_grammar(sentence, target_word, "intermediate", "mock_key")

        assert result is not None
        assert result.confidence_score < 0.5  # Low confidence for timeout

    def test_arabic_invalid_json_response_handling(self, arabic_analyzer, mock_gemini_api_invalid_response):
        """Test handling of invalid JSON responses"""
        sentence = "الطالب يقرأ"
        target_word = "يقرأ"

        # Should handle invalid JSON gracefully
        result = arabic_analyzer.analyze_grammar(sentence, target_word, "intermediate", "mock_key")

        assert result is not None
        assert result.confidence_score < 0.5  # Low confidence for invalid response

    def test_arabic_empty_response_handling(self, arabic_analyzer, mock_gemini_api_empty_response):
        """Test handling of empty API responses"""
        sentence = "المعلم يكتب"
        target_word = "يكتب"

        result = arabic_analyzer.analyze_grammar(sentence, target_word, "intermediate", "mock_key")

        assert result is not None
        assert result.confidence_score < 0.5  # Low confidence for empty response

    def test_arabic_invalid_input_validation(self, arabic_analyzer):
        """Test validation of invalid inputs"""
        # Test with non-Arabic text
        assert arabic_analyzer.validate_arabic_text("Hello world") == False

        # Test with empty string
        assert arabic_analyzer.validate_arabic_text("") == False

        # Test with None
        assert arabic_analyzer.validate_arabic_text(None) == False

        # Test with numbers only
        assert arabic_analyzer.validate_arabic_text("12345") == False

    def test_arabic_malformed_sentence_handling(self, arabic_analyzer):
        """Test handling of malformed Arabic sentences"""
        # Test with mixed scripts
        mixed_sentence = "القطة Hello world سوداء"
        target_word = "القطة"

        # Should handle mixed scripts gracefully
        result = arabic_analyzer.analyze_grammar(mixed_sentence, target_word, "intermediate", "mock_key")
        assert result is not None
        # Confidence might be low due to mixed scripts

    def test_arabic_target_word_not_found(self, arabic_analyzer):
        """Test when target word is not in sentence"""
        sentence = "القطة سوداء"
        target_word = "كلب"  # Dog - not in sentence

        # Should handle gracefully
        result = arabic_analyzer.analyze_grammar(sentence, target_word, "intermediate", "mock_key")
        assert result is not None
        # Confidence should be low since target word not found

    def test_arabic_batch_error_recovery(self, arabic_analyzer, mock_gemini_api_failure):
        """Test batch analysis error recovery"""
        sentences = [
            "القطة سوداء",
            "أنا أدرس",
            "الطالب يقرأ"
        ]
        target_word = "قطة"

        # Should handle batch errors gracefully
        results = arabic_analyzer.batch_analyze_grammar(sentences, target_word, "intermediate", "invalid_key")

        # Should return results for all sentences (even if failed)
        assert len(results) == len(sentences)
        for result in results:
            assert result is not None
            assert result.confidence_score < 0.5  # Low confidence for failed analyses

    def test_arabic_network_error_recovery(self, arabic_analyzer):
        """Test recovery from network errors"""
        with patch('languages.arabic.ar_analyzer.ArAnalyzer._call_ai') as mock_call_ai:
            mock_call_ai.side_effect = ConnectionError("Network is unreachable")

            sentence = "القطة سوداء"
            target_word = "قطة"

            result = arabic_analyzer.analyze_grammar(sentence, target_word, "intermediate", "mock_key")

            assert result is not None
            assert result.confidence_score < 0.5

    def test_arabic_rate_limit_handling(self, arabic_analyzer):
        """Test handling of API rate limits"""
        with patch('languages.arabic.ar_analyzer.ArAnalyzer._call_ai') as mock_call_ai:
            # Simulate rate limit error
            mock_call_ai.return_value = None

            sentence = "الطالب يقرأ الكتاب"
            target_word = "يقرأ"

            result = arabic_analyzer.analyze_grammar(sentence, target_word, "intermediate", "mock_key")

            assert result is not None
            assert result.confidence_score < 0.5

    def test_arabic_partial_response_handling(self, arabic_analyzer):
        """Test handling of partial API responses"""
        with patch('languages.arabic.ar_analyzer.ArAnalyzer._call_ai') as mock_call_ai:
            # Partial JSON response
            mock_call_ai.return_value = '{"words": [{"word": "القطة", "grammatical_role": "noun"'

            sentence = "القطة سوداء"
            target_word = "قطة"

            result = arabic_analyzer.analyze_grammar(sentence, target_word, "intermediate", "mock_key")

            assert result is not None
            assert result.confidence_score < 0.5

    def test_arabic_unicode_encoding_errors(self, arabic_analyzer):
        """Test handling of Unicode encoding errors"""
        # Test with Arabic text that might cause encoding issues
        sentence = "القطة 🐱 سوداء"  # Arabic with emoji
        target_word = "القطة"

        # Should handle Unicode gracefully
        result = arabic_analyzer.analyze_grammar(sentence, target_word, "intermediate", "mock_key")
        assert result is not None

    def test_arabic_memory_error_handling(self, arabic_analyzer):
        """Test handling of memory errors during analysis"""
        with patch('languages.arabic.ar_analyzer.ArAnalyzer._call_ai') as mock_call_ai:
            mock_call_ai.side_effect = MemoryError("Out of memory")

            sentence = "القطة سوداء"
            target_word = "قطة"

            result = arabic_analyzer.analyze_grammar(sentence, target_word, "intermediate", "mock_key")

            assert result is not None
            assert result.confidence_score < 0.5

    def test_arabic_invalid_complexity_level(self, arabic_analyzer):
        """Test handling of invalid complexity levels"""
        sentence = "القطة سوداء"
        target_word = "قطة"

        # Test with invalid complexity
        result = arabic_analyzer.analyze_grammar(sentence, target_word, "invalid_level", "mock_key")

        # Should handle gracefully, perhaps defaulting to intermediate
        assert result is not None

    def test_arabic_extremely_long_input_error(self, arabic_analyzer):
        """Test handling of extremely long inputs that might cause issues"""
        # Create an extremely long sentence
        long_sentence = "القطة " * 1000  # Very long sentence
        target_word = "القطة"

        # Should handle gracefully without crashing
        result = arabic_analyzer.analyze_grammar(long_sentence, target_word, "intermediate", "mock_key")
        assert result is not None

    def test_arabic_concurrent_error_handling(self, arabic_analyzer, mock_gemini_api_failure):
        """Test error handling under concurrent load"""
        import threading

        results = []
        errors = []

        def analyze_with_error(sentence, index):
            try:
                result = arabic_analyzer.analyze_grammar(sentence, sentence.split()[0], "intermediate", "invalid_key")
                results.append((index, result))
            except Exception as e:
                errors.append((index, str(e)))

        sentences = [
            "القطة سوداء",
            "أنا أدرس",
            "الطالب يقرأ",
            "المعلم يكتب"
        ]

        # Start concurrent analyses that will fail
        threads = []
        for i, sentence in enumerate(sentences):
            thread = threading.Thread(target=analyze_with_error, args=(sentence, i))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)

        # Should handle all errors gracefully
        assert len(results) == len(sentences), f"Expected {len(sentences)} results, got {len(results)}. Errors: {errors}"
        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # All results should be fallback results
        for index, result in results:
            assert result is not None
            assert result.confidence_score < 0.5

    def test_arabic_error_logging(self, arabic_analyzer, mock_gemini_api_failure, caplog):
        """Test that errors are properly logged"""
        import logging

        sentence = "القطة سوداء"
        target_word = "قطة"

        with caplog.at_level(logging.WARNING):
            result = arabic_analyzer.analyze_grammar(sentence, target_word, "intermediate", "invalid_key")
        
        # Should log errors
        assert any("AI API call failed" in record.message for record in caplog.records), "API errors should be logged"

    def test_arabic_fallback_mechanism_completeness(self, arabic_analyzer, mock_gemini_api_failure):
        """Test that fallback mechanism provides complete results"""
        sentence = "القطة سوداء نائمة"
        target_word = "قطة"

        result = arabic_analyzer.analyze_grammar(sentence, target_word, "intermediate", "invalid_key")

        # Fallback should still provide basic structure
        assert result is not None
        assert hasattr(result, 'confidence_score')
        assert hasattr(result, 'word_explanations')  # Fallback uses word_explanations
        assert hasattr(result, 'explanations')

        # Even fallback should have some basic analysis
        assert len(result.word_explanations) > 0 or result.confidence_score < 0.1
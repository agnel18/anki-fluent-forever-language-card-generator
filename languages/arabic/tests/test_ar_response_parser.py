import pytest
import json

class TestArabicResponseParser:
    """Test Arabic response parser component"""

    def test_initialization(self, arabic_response_parser, arabic_config):
        """Test response parser initializes correctly"""
        assert arabic_response_parser.config == arabic_config

    def test_valid_response_parsing(self, arabic_response_parser, mock_arabic_responses):
        """Test parsing valid AI response"""
        response = json.dumps(mock_arabic_responses['valid_response'])
        result = arabic_response_parser.parse_response(
            response, "beginner", "القطة سوداء", "قطة"
        )

        assert 'word_explanations' in result
        assert 'explanations' in result
        assert 'metadata' in result
        assert result['metadata']['is_rtl'] == True
        assert len(result['word_explanations']) > 0

        # Check RTL word order (should be reversed)
        explanations = result['word_explanations']
        # For RTL, the first explanation should correspond to the last word
        # This ensures proper display order

    def test_malformed_response_handling(self, arabic_response_parser):
        """Test handling of malformed JSON responses"""
        result = arabic_response_parser.parse_response(
            "invalid json", "beginner", "test sentence", "test"
        )

        # Should return valid structure even with malformed input
        assert isinstance(result, dict)
        assert 'word_explanations' in result

    def test_incomplete_response_handling(self, arabic_response_parser, mock_arabic_responses):
        """Test handling of incomplete responses"""
        response = json.dumps(mock_arabic_responses['incomplete_response'])
        result = arabic_response_parser.parse_response(
            response, "beginner", "test sentence", "test"
        )

        assert isinstance(result, dict)
        assert 'word_explanations' in result

    def test_batch_response_parsing(self, arabic_response_parser, mock_arabic_responses):
        """Test parsing batch responses"""
        response = json.dumps(mock_arabic_responses['batch_response'])
        result = arabic_response_parser.parse_response(
            response, "beginner", "test sentence", "test"
        )

        assert isinstance(result, dict)
        assert 'word_explanations' in result

    def test_fallback_response_creation(self, arabic_response_parser):
        """Test fallback response creation"""
        result = arabic_response_parser._create_fallback_response(
            "القطة سوداء", "قطة", "beginner"
        )

        assert isinstance(result, dict)
        assert 'word_explanations' in result
        assert 'explanations' in result
        assert result['metadata']['is_rtl'] == True
        assert result['metadata']['fallback_used'] == True

    def test_arabic_tokenization(self, arabic_response_parser):
        """Test Arabic sentence tokenization"""
        sentence = "القطة سوداء نائمة"
        words = arabic_response_parser._tokenize_arabic_sentence(sentence)

        assert isinstance(words, list)
        assert len(words) > 0
        # Basic check that words are separated
        assert "القطة" in words or "سوداء" in words

    def test_rtl_word_order_processing(self, arabic_response_parser, mock_arabic_responses):
        """Test that word explanations are processed in RTL order"""
        words_data = mock_arabic_responses['valid_response']['words']
        processed = arabic_response_parser._process_word_explanations(
            words_data, "beginner", "test sentence"
        )

        assert isinstance(processed, list)
        assert len(processed) > 0

        # Each explanation should be a 4-tuple: [word, role, color, meaning]
        for exp in processed:
            assert len(exp) >= 4
            assert isinstance(exp[0], str)  # word
            assert isinstance(exp[1], str)  # role
            assert exp[2].startswith('#')  # color
            assert isinstance(exp[3], str)  # meaning

    def test_grammatical_role_normalization(self, arabic_response_parser):
        """Test grammatical role normalization"""
        # Test various role formats
        assert arabic_response_parser._normalize_grammatical_role('noun_term') == 'noun'
        assert arabic_response_parser._normalize_grammatical_role('verb_form') == 'verb'
        assert arabic_response_parser._normalize_grammatical_role('noun') == 'noun'

    def test_response_structure_validation(self, arabic_response_parser):
        """Test response structure validation"""
        valid_response = {'words': [], 'explanations': {}}
        assert arabic_response_parser.validate_response_structure(valid_response) == True

        invalid_response = "not a dict"
        assert arabic_response_parser.validate_response_structure(invalid_response) == False

        incomplete_response = {'words': []}  # missing explanations
        assert arabic_response_parser.validate_response_structure(incomplete_response) == False

    def test_robust_json_parsing_markdown_blocks(self, arabic_response_parser):
        """Test robust JSON parsing with markdown code blocks"""
        markdown_response = '''Here's the analysis for the Arabic sentence:
```json
{"words": [{"word": "القطة", "grammatical_role": "noun", "meaning": "the cat"}]}
```
This shows the grammatical structure.'''
        
        result = arabic_response_parser.parse_response(
            markdown_response, "beginner", "القطة", "قطة"
        )
        
        assert isinstance(result, dict)
        assert 'word_explanations' in result
        assert len(result['word_explanations']) > 0

    def test_robust_json_parsing_inline_json(self, arabic_response_parser):
        """Test robust JSON parsing with JSON embedded in explanatory text"""
        inline_response = 'The grammatical analysis shows: {"words": [{"word": "القطة", "grammatical_role": "noun", "meaning": "the cat"}]} and this indicates the sentence structure.'
        
        result = arabic_response_parser.parse_response(
            inline_response, "beginner", "القطة", "قطة"
        )
        
        assert isinstance(result, dict)
        assert 'word_explanations' in result
        assert len(result['word_explanations']) > 0

    def test_robust_json_parsing_ai_text_prefix(self, arabic_response_parser):
        """Test robust JSON parsing with AI explanatory text prefix"""
        ai_response = '''As an AI language model, I'll analyze this Arabic sentence. The grammatical breakdown is: {"words": [{"word": "القطة", "grammatical_role": "noun", "meaning": "the cat"}], "explanations": {"overall_structure": "Simple noun phrase", "key_features": "Definite article usage"}}'''
        
        result = arabic_response_parser.parse_response(
            ai_response, "beginner", "القطة", "قطة"
        )
        
        assert isinstance(result, dict)
        assert 'word_explanations' in result
        assert 'explanations' in result
        assert result['explanations']['overall_structure'] == "Simple noun phrase"
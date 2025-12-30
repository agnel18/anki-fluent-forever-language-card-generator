import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the streamlit_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'streamlit_app'))

from sentence_generator import generate_sentences

def test_generate_sentences_success():
    """Test successful sentence generation."""
    with patch('sentence_generator.generate_word_meaning_sentences_and_keywords') as mock_combined:
        mock_combined.return_value = {
            'meaning': 'hello',
            'sentences': ['Hello, how are you?', 'I say hello to my friends.'],
            'ipa': ['həˈloʊ', 'həˈloʊ'],
            'keywords': ['greeting, friend', 'hello, conversation']
        }

        with patch('sentence_generator._validate_and_enrich_batch_pass2') as mock_validate, \
             patch('sentence_generator._batch_analyze_grammar_and_color') as mock_analyze:

            mock_validate.return_value = [
                {'sentence': 'Hello, how are you?', 'english_translation': 'Hello, how are you?', 'context': 'Greeting', 'ipa': 'həˈloʊ', 'role_of_word': 'greeting'},
                {'sentence': 'I say hello to my friends.', 'english_translation': 'I say hello to my friends.', 'context': 'Social', 'ipa': 'həˈloʊ', 'role_of_word': 'verb'}
            ]
            mock_analyze.return_value = [
                {'colored_sentence': 'Hello, how are you?', 'word_explanations': [], 'grammar_summary': 'Simple greeting'},
                {'colored_sentence': 'I say hello to my friends.', 'word_explanations': [], 'grammar_summary': 'Present tense'}
            ]

            result = generate_sentences('hello', 'English', 2, 5, 20, 'intermediate', 'test_key')

            assert result[0] == 'hello'
            assert len(result[1]) == 2
            assert result[1][0]['sentence'] == 'Hello, how are you?'

def test_generate_sentences_api_failure():
    """Test sentence generation when API fails."""
    with patch('sentence_generator.generate_word_meaning_sentences_and_keywords') as mock_combined:
        mock_combined.side_effect = Exception("API Error")

        result = generate_sentences('hello', 'English', 2, 5, 20, 'intermediate', 'test_key')

        assert result == ("hello", [])
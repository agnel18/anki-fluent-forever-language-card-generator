import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the streamlit_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'streamlit_app'))

from sentence_generator import generate_sentences

def test_generate_sentences_success():
    """Test successful sentence generation."""
    with patch('sentence_generator.get_content_generator') as mock_get_generator:
        mock_content_generator = MagicMock()
        mock_get_generator.return_value = mock_content_generator

        mock_content_generator.generate_word_meaning_sentences_and_keywords.return_value = {
            'meaning': 'hello',
            'sentences': ['Hello, how are you?', 'I say hello to my friends.'],
            'ipa': ['həˈloʊ', 'həˈloʊ'],
            'keywords': ['greeting, friend', 'hello, conversation']
        }

        result = generate_sentences('hello', 'English', 2, 5, 20, 'intermediate', 'test_key')

        assert result[0] == 'hello'
        assert len(result[1]) == 2
        assert result[1][0]['sentence'] == 'Hello, how are you?'
        assert result[1][0]['ipa'] == 'həˈloʊ'
        assert result[1][0]['image_keywords'] == 'greeting, friend'

def test_generate_sentences_api_failure():
    """Test sentence generation when API fails."""
    with patch('sentence_generator.get_content_generator') as mock_get_generator:
        mock_content_generator = MagicMock()
        mock_get_generator.return_value = mock_content_generator

        mock_content_generator.generate_word_meaning_sentences_and_keywords.side_effect = Exception("API Error")

        result = generate_sentences('hello', 'English', 2, 5, 20, 'intermediate', 'test_key')

        assert result == ("hello", [])
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the streamlit_app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'streamlit_app'))

from streamlit_app.core_functions import generate_complete_deck

def test_generate_complete_deck_success():
    """Test successful deck generation with mocked dependencies."""
    # Mock the dependencies
    with patch('streamlit_app.core_functions.generate_sentences') as mock_generate_sentences, \
         patch('streamlit_app.core_functions.generate_audio') as mock_generate_audio, \
         patch('streamlit_app.core_functions.generate_images_google') as mock_generate_images, \
         patch('streamlit_app.core_functions.create_apkg_export') as mock_create_apkg:

        # Setup mocks
        mock_generate_sentences.return_value = ("test meaning", [
            {'sentence': 'Test sentence 1', 'image_keywords': 'keyword1'},
            {'sentence': 'Test sentence 2', 'image_keywords': 'keyword2'}
        ])
        mock_generate_audio.return_value = ['audio1.mp3', 'audio2.mp3']
        mock_generate_images.return_value = (['image1.jpg', 'image2.jpg'], set())
        mock_create_apkg.return_value = True

        # Test parameters
        words = ['test']
        language = 'English'
        gemini_api_key = 'test_key'
        output_dir = 'test_output'

        result = generate_complete_deck(
            words=words,
            language=language,
            gemini_api_key=gemini_api_key,
            output_dir=output_dir
        )

        assert result['success'] == True
        assert 'apkg_path' in result
        assert result['apkg_path'].endswith('.apkg')

def test_generate_complete_deck_sentence_failure():
    """Test deck generation when sentence generation fails."""
    with patch('streamlit_app.core_functions.generate_sentences') as mock_generate_sentences:
        mock_generate_sentences.return_value = ("test meaning", None)  # Sentences is None

        result = generate_complete_deck(
            words=['test'],
            language='English',
            gemini_api_key='test_key',
            output_dir='test_output'
        )

        assert result['success'] == False
        assert 'error' in result

def test_generate_complete_deck_apkg_failure():
    """Test deck generation when APKG creation fails."""
    with patch('streamlit_app.core_functions.generate_sentences') as mock_generate_sentences, \
         patch('streamlit_app.core_functions.generate_audio') as mock_generate_audio, \
         patch('streamlit_app.core_functions.generate_images_google') as mock_generate_images, \
         patch('streamlit_app.core_functions.create_apkg_export') as mock_create_apkg:

        mock_generate_sentences.return_value = ("test meaning", [
            {'sentence': 'Test sentence 1', 'image_keywords': 'keyword1'}
        ])
        mock_generate_audio.return_value = ['audio1.mp3']
        mock_generate_images.return_value = (['image1.jpg'], set())
        mock_create_apkg.return_value = False  # APKG creation fails

        result = generate_complete_deck(
            words=['test'],
            language='English',
            gemini_api_key='test_key',
            output_dir='test_output'
        )

        assert result['success'] == False
        assert 'Failed to create APKG file' in result['error']
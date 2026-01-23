import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile
import shutil

# Add the streamlit_app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'streamlit_app'))

from streamlit_app.core_functions import generate_deck_progressive, create_apkg_from_word_data, _generate_unique_id

class TestFilenameUniqueness:
    """Test that filenames are unique across deck generations."""

    def test_unique_id_generation(self):
        """Test that unique IDs are generated correctly."""
        unique_id1 = _generate_unique_id()
        unique_id2 = _generate_unique_id()

        # Unique IDs should be different (now includes milliseconds and counter)
        assert unique_id1 != unique_id2

        # Should be in format YYYYMMDD_HHMMSS_MMM_CCC
        assert len(unique_id1) == 23  # 8 date + 1 + 6 time + 1 + 3 ms + 1 + 3 counter
        assert unique_id1.count('_') == 3
        assert unique_id1.replace('_', '').isdigit()

    def test_progressive_generation_includes_unique_id(self):
        """Test that generate_deck_progressive includes unique_id in word_data."""
        with patch('streamlit_app.core_functions.generate_sentences') as mock_generate_sentences, \
             patch('streamlit_app.core_functions.generate_audio') as mock_generate_audio, \
             patch('streamlit_app.core_functions.generate_images_google') as mock_generate_images:

            # Setup mocks
            mock_generate_sentences.return_value = ("test meaning", [
                {'sentence': 'Test sentence 1', 'image_keywords': 'keyword1'},
                {'sentence': 'Test sentence 2', 'image_keywords': 'keyword2'}
            ])
            mock_generate_audio.return_value = ['audio1.mp3', 'audio2.mp3']
            mock_generate_images.return_value = (['image1.jpg', 'image2.jpg'], set())

            with tempfile.TemporaryDirectory() as temp_dir:
                result = generate_deck_progressive(
                    word='test',
                    language='English',
                    gemini_api_key='test_key',
                    google_custom_search_engine_id='test_cx',
                    output_dir=temp_dir,
                    num_sentences=2
                )

                assert result['success'] == True
                assert 'unique_id' in result['word_data']
                assert result['word_data']['unique_id'] is not None
                assert len(result['word_data']['unique_id']) == 23

    def test_create_apkg_from_word_data_uses_unique_id(self):
        """Test that create_apkg_from_word_data uses unique_id for filenames."""
        with patch('streamlit_app.core_functions.create_apkg_export') as mock_create_apkg:

            mock_create_apkg.return_value = True

            # Test data with unique_id
            test_unique_id = '20260105_120000_123_001'
            words_data = [{
                'word': 'test',
                'meaning': 'test meaning',
                'sentences': [
                    {'sentence': 'Test sentence 1', 'image_keywords': 'keyword1'},
                    {'sentence': 'Test sentence 2', 'image_keywords': 'keyword2'}
                ],
                'audio_files': [f'test_01_{test_unique_id}.mp3', f'test_02_{test_unique_id}.mp3'],
                'image_files': [f'test_01_{test_unique_id}.jpg', f'test_02_{test_unique_id}.jpg'],
                'unique_id': test_unique_id
            }]

            with tempfile.TemporaryDirectory() as temp_dir:
                success = create_apkg_from_word_data(
                    words_data=words_data,
                    media_dir=temp_dir,
                    output_apkg_path=os.path.join(temp_dir, 'test.apkg'),
                    language='English'
                )

                assert success == True

                # Check that create_apkg_export was called with correct file_name
                call_args = mock_create_apkg.call_args
                cards_data = call_args[0][0]  # First positional argument

                # Should have 2 cards
                assert len(cards_data) == 2

                # Check filenames include unique_id
                assert cards_data[0]['file_name'] == f'test_01_{test_unique_id}'
                assert cards_data[1]['file_name'] == f'test_02_{test_unique_id}'

                # Check audio and image fields also use unique filenames
                assert test_unique_id in cards_data[0]['audio']
                assert test_unique_id in cards_data[0]['image']

    def test_create_apkg_from_word_data_without_unique_id(self):
        """Test backward compatibility when unique_id is not provided."""
        with patch('streamlit_app.core_functions.create_apkg_export') as mock_create_apkg:

            mock_create_apkg.return_value = True

            # Test data without unique_id (backward compatibility)
            words_data = [{
                'word': 'test',
                'meaning': 'test meaning',
                'sentences': [
                    {'sentence': 'Test sentence 1', 'image_keywords': 'keyword1'}
                ],
                'audio_files': ['test_01.mp3'],
                'image_files': ['test_01.jpg']
                # No unique_id provided
            }]

            with tempfile.TemporaryDirectory() as temp_dir:
                success = create_apkg_from_word_data(
                    words_data=words_data,
                    media_dir=temp_dir,
                    output_apkg_path=os.path.join(temp_dir, 'test.apkg'),
                    language='English'
                )

                assert success == True

                # Check that create_apkg_export was called with correct file_name
                call_args = mock_create_apkg.call_args
                cards_data = call_args[0][0]

                # Should have 1 card
                assert len(cards_data) == 1

                # Check filename does NOT include unique_id (backward compatibility)
                assert cards_data[0]['file_name'] == 'test_01'

    def test_filename_consistency_across_multiple_generations(self):
        """Test that multiple deck generations produce different unique IDs."""
        with patch('streamlit_app.core_functions.generate_sentences') as mock_generate_sentences, \
             patch('streamlit_app.core_functions.generate_audio') as mock_generate_audio, \
             patch('streamlit_app.core_functions.generate_images_google') as mock_generate_images:

            # Setup mocks
            mock_generate_sentences.return_value = ("test meaning", [
                {'sentence': 'Test sentence 1', 'image_keywords': 'keyword1'}
            ])
            mock_generate_audio.return_value = ['audio1.mp3']
            mock_generate_images.return_value = (['image1.jpg'], set())

            with tempfile.TemporaryDirectory() as temp_dir:
                # Generate first deck
                result1 = generate_deck_progressive(
                    word='test',
                    language='English',
                    gemini_api_key='test_key',
                    google_custom_search_engine_id='test_cx',
                    output_dir=temp_dir,
                    num_sentences=1
                )

                # Generate second deck
                result2 = generate_deck_progressive(
                    word='test',
                    language='English',
                    gemini_api_key='test_key',
                    google_custom_search_engine_id='test_cx',
                    output_dir=temp_dir,
                    num_sentences=1
                )

                # Unique IDs should be different
                assert result1['word_data']['unique_id'] != result2['word_data']['unique_id']

                # Both should have successfully generated unique IDs
                assert len(result1['word_data']['unique_id']) == 23
                assert len(result2['word_data']['unique_id']) == 23
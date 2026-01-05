import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile

# Add the streamlit_app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'streamlit_app'))

from streamlit_app.core_functions import generate_deck_progressive, create_apkg_from_word_data

class TestWordFieldConsistency:
    """Test that the 'What is the Word?' field always contains the correct selected word."""

    def test_progressive_generation_word_field_consistency(self):
        """Test that generate_deck_progressive always sets word field to selected word."""
        with patch('streamlit_app.core_functions.generate_sentences') as mock_generate_sentences, \
             patch('streamlit_app.core_functions.generate_audio') as mock_generate_audio, \
             patch('streamlit_app.core_functions.generate_images_pixabay') as mock_generate_images:

            # Setup mocks
            mock_generate_sentences.return_value = ("test meaning", [
                {'sentence': 'Test sentence with word है', 'image_keywords': 'keyword1'},
                {'sentence': 'Another sentence with कहो', 'image_keywords': 'keyword2'}
            ])
            mock_generate_audio.return_value = ['audio1.mp3', 'audio2.mp3']
            mock_generate_images.return_value = (['image1.jpg', 'image2.jpg'], set())

            with tempfile.TemporaryDirectory() as temp_dir:
                result = generate_deck_progressive(
                    word='कहो',  # Selected word
                    language='Hindi',
                    groq_api_key='test_key',
                    pixabay_api_key='test_key',
                    output_dir=temp_dir,
                    num_sentences=2
                )

                assert result['success'] == True
                assert result['word_data']['word'] == 'कहो'  # Should be the selected word

    def test_create_apkg_word_field_uses_selected_word(self):
        """Test that create_apkg_from_word_data sets word field to selected word, not sentence words."""
        with patch('streamlit_app.core_functions.create_apkg_export') as mock_create_apkg:

            mock_create_apkg.return_value = True

            # Test data with sentences containing different words
            words_data = [{
                'word': 'कहो',  # Selected word
                'meaning': 'say, tell',
                'sentences': [
                    {
                        'sentence': 'कलाकार से पूछो कि वह अपनी कला के बारे में क्या कहता है।',
                        'word_explanations': [
                            ['कलाकार', 'noun', '#FFAA00', 'artist'],
                            ['से', 'postposition', '#4444FF', 'from'],
                            ['पूछो', 'verb', '#44FF44', 'ask'],
                            ['कि', 'conjunction', '#888888', 'that'],
                            ['वह', 'pronoun', '#FF4444', 'he'],
                            ['अपनी', 'adjective', '#FF44FF', 'his own'],
                            ['कला', 'noun', '#FFAA00', 'art'],
                            ['के', 'postposition', '#4444FF', 'of'],
                            ['बारे', 'noun', '#FFAA00', 'about'],
                            ['में', 'postposition', '#4444FF', 'in'],
                            ['क्या', 'pronoun', '#FF4444', 'what'],
                            ['कहता', 'verb', '#44FF44', 'says'],
                            ['है', 'auxiliary_verb', '#44FF44', 'is']  # This word appears in sentence
                        ]
                    }
                ],
                'audio_files': ['कहो_01_20260105_120000.mp3'],
                'image_files': ['कहो_01_20260105_120000.jpg'],
                'unique_id': '20260105_120000_123_001'
            }]

            with tempfile.TemporaryDirectory() as temp_dir:
                success = create_apkg_from_word_data(
                    words_data=words_data,
                    media_dir=temp_dir,
                    output_apkg_path=os.path.join(temp_dir, 'test.apkg'),
                    language='Hindi'
                )

                assert success == True

                # Check that create_apkg_export was called with correct word field
                call_args = mock_create_apkg.call_args
                cards_data = call_args[0][0]

                assert len(cards_data) == 1
                # Word field should be the SELECTED word, not any word from the sentence
                assert cards_data[0]['word'] == 'कहो'
                # Meaning should match
                assert cards_data[0]['meaning'] == 'say, tell'
                # File name should include unique ID
                assert '20260105_120000_123_001' in cards_data[0]['file_name']

    def test_multiple_words_generate_consistent_word_fields(self):
        """Test that multiple selected words each get their own correct word field."""
        with patch('streamlit_app.core_functions.create_apkg_export') as mock_create_apkg:

            mock_create_apkg.return_value = True

            # Test data for multiple words
            words_data = [
                {
                    'word': 'कहो',  # First selected word
                    'meaning': 'say, tell',
                    'sentences': [{'sentence': 'Sentence 1', 'word_explanations': []}],
                    'audio_files': ['कहो_01_20260105_120000.mp3'],
                    'image_files': ['कहो_01_20260105_120000.jpg'],
                    'unique_id': '20260105_120000_001'
                },
                {
                    'word': 'खाना',  # Second selected word
                    'meaning': 'food, eat',
                    'sentences': [{'sentence': 'Sentence 2', 'word_explanations': []}],
                    'audio_files': ['खाना_01_20260105_120001.mp3'],
                    'image_files': ['खाना_01_20260105_120001.jpg'],
                    'unique_id': '20260105_120001_002'
                }
            ]

            with tempfile.TemporaryDirectory() as temp_dir:
                success = create_apkg_from_word_data(
                    words_data=words_data,
                    media_dir=temp_dir,
                    output_apkg_path=os.path.join(temp_dir, 'test.apkg'),
                    language='Hindi'
                )

                assert success == True

                call_args = mock_create_apkg.call_args
                cards_data = call_args[0][0]

                assert len(cards_data) == 2
                # Each card should have the correct selected word
                assert cards_data[0]['word'] == 'कहो'
                assert cards_data[1]['word'] == 'खाना'
                # Meanings should be different
                assert cards_data[0]['meaning'] == 'say, tell'
                assert cards_data[1]['meaning'] == 'food, eat'

    def test_word_field_not_overridden_by_sentence_content(self):
        """Test that word field is never overridden by words appearing in sentences."""
        with patch('streamlit_app.core_functions.create_apkg_export') as mock_create_apkg:

            mock_create_apkg.return_value = True

            # Test with a sentence that contains many different words
            words_data = [{
                'word': 'नमस्ते',  # Selected word: hello
                'meaning': 'hello, greetings',
                'sentences': [{
                    'sentence': 'नमस्ते, मैं आपसे मिलकर बहुत खुश हूं।',  # Contains words like मैं, आपसे, मिलकर, बहुत, खुश, हूं
                    'word_explanations': [
                        ['नमस्ते', 'interjection', '#FFA07A', 'hello'],
                        ['मैं', 'pronoun', '#FF4444', 'I'],
                        ['आपसे', 'pronoun', '#FF4444', 'with you'],
                        ['मिलकर', 'verb', '#44FF44', 'meeting'],
                        ['बहुत', 'adverb', '#44FFFF', 'very'],
                        ['खुश', 'adjective', '#FF44FF', 'happy'],
                        ['हूं', 'auxiliary_verb', '#44FF44', 'am']
                    ]
                }],
                'audio_files': ['नमस्ते_01_20260105_120000.mp3'],
                'image_files': ['नमस्ते_01_20260105_120000.jpg'],
                'unique_id': '20260105_120000_123_001'
            }]

            with tempfile.TemporaryDirectory() as temp_dir:
                success = create_apkg_from_word_data(
                    words_data=words_data,
                    media_dir=temp_dir,
                    output_apkg_path=os.path.join(temp_dir, 'test.apkg'),
                    language='Hindi'
                )

                assert success == True

                call_args = mock_create_apkg.call_args
                cards_data = call_args[0][0]

                assert len(cards_data) == 1
                # Word field should ALWAYS be the selected word, never any word from sentence
                assert cards_data[0]['word'] == 'नमस्ते'  # Selected word
                # Should NOT be any of the words from the sentence explanations
                assert cards_data[0]['word'] != 'मैं'
                assert cards_data[0]['word'] != 'आपसे'
                assert cards_data[0]['word'] != 'मिलकर'
                assert cards_data[0]['word'] != 'बहुत'
                assert cards_data[0]['word'] != 'खुश'
                assert cards_data[0]['word'] != 'हूं'
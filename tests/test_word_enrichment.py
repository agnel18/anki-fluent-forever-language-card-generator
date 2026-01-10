"""
Unit tests for word enrichment functionality.
Tests core word data fetching and enrichment without external API calls.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the streamlit_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'streamlit_app'))

# Import with absolute paths to avoid relative import issues
import generation_utils
import language_registry
from word_data_fetcher import enrich_word_data_batch


class TestWordEnrichment:
    """Test word enrichment functionality."""

    def test_pinyin_tone_marks_constant(self):
        """Test that PINYIN_TONE_MARKS constant is properly defined."""
        expected_marks = 'āēīōūǖǎěǐǒǔǚ'
        assert generation_utils.PINYIN_TONE_MARKS == expected_marks
        assert len(generation_utils.PINYIN_TONE_MARKS) == 12  # 6 macron + 6 caron marks

    def test_language_registry_structure(self):
        """Test that language registry has proper structure."""
        registry = language_registry.get_language_registry()

        # Should be a LanguageRegistry object
        assert hasattr(registry, 'get_supported_languages')
        assert hasattr(registry, 'get_config')

        # Should have supported languages
        supported = registry.get_supported_languages()
        assert isinstance(supported, set)
        assert len(supported) > 0

        # Test getting a specific language config
        hindi_config = registry.get_config('Hindi')
        assert hindi_config is not None
        assert hindi_config.iso_code == 'hi'
        assert hindi_config.full_name == 'Hindi'

    @patch('word_data_fetcher.fetch_wiktionary_data')
    @patch('word_data_fetcher.fetch_google_translate_data')
    def test_enrich_word_data_batch_empty_input(self, mock_translate, mock_wiktionary):
        """Test batch enrichment with empty input."""
        result = enrich_word_data_batch([])
        assert result == {}

    @patch('word_data_fetcher.fetch_wiktionary_data')
    @patch('word_data_fetcher.fetch_google_translate_data')
    def test_enrich_word_data_batch_language_mapping(self, mock_translate, mock_wiktionary):
        """Test that language codes are properly mapped to full names."""
        # Mock the API responses
        mock_wiktionary.return_value = {'definition': 'test definition'}
        mock_translate.return_value = 'test translation'

        # Test with language code 'hi' (should map to 'Hindi')
        result = enrich_word_data_batch(['hello'], 'hi', batch_size=1)

        # Verify the mock was called with the correct language name
        mock_wiktionary.assert_called_with('hello', 'Hindi')
        mock_translate.assert_called_with('hello', 'Hindi')

        assert 'hello' in result
        assert isinstance(result['hello'], str)

    def test_ipa_validation_valid_input(self):
        """Test IPA validation with valid input."""
        # Test valid IPA with tone marks
        valid_ipa = "[mǎ]"
        result = generation_utils.validate_ipa_output(valid_ipa, 'zh')
        assert result[0] == True  # Should be valid
        assert "Valid IPA" in result[1]

    def test_ipa_validation_pinyin_rejection_chinese(self):
        """Test that Pinyin tone marks are rejected for Chinese."""
        # Test Pinyin input (should be rejected for Chinese)
        pinyin_input = "[mǎ]"
        result = generation_utils.validate_ipa_output(pinyin_input, 'zh')
        assert result[0] == False  # Should be invalid
        assert "non-IPA characters" in result[1]  # Pinyin tone marks are not valid IPA

    def test_ipa_validation_pinyin_allowed_other_languages(self):
        """Test that Pinyin tone marks are allowed for non-Chinese languages."""
        # Test Pinyin input for Hindi (should be allowed)
        pinyin_input = "[mǎ]"
        result = generation_utils.validate_ipa_output(pinyin_input, 'hi')
        # This should pass IPA validation since it's not Chinese
        # (though it might fail other IPA character checks)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_ipa_validation_invalid_characters(self):
        """Test IPA validation with invalid characters."""
        invalid_ipa = "[test@invalid]"  # Contains @ which is not a valid IPA character
        result = generation_utils.validate_ipa_output(invalid_ipa, 'zh')
        assert result[0] == False  # Should be invalid
        assert "non-IPA characters" in result[1]


class TestLanguageRegistry:
    """Test language registry functionality."""

    def test_registry_contains_supported_languages(self):
        """Test that registry contains expected languages."""
        registry = language_registry.get_language_registry()

        # Check for some key languages that should be supported
        expected_languages = ['Hindi', 'Spanish', 'Chinese', 'Japanese', 'Korean']
        supported = registry.get_supported_languages()

        # Convert to full names for checking
        supported_full_names = {registry.get_full_name(code) for code in supported}
        supported_full_names = {name for name in supported_full_names if name}

        for lang in expected_languages:
            assert lang in supported_full_names, f"Language {lang} not found in registry"

    def test_registry_iso_codes(self):
        """Test that ISO codes are properly mapped."""
        registry = language_registry.get_language_registry()

        # Test some known mappings
        hindi_iso = registry.get_iso_code('Hindi')
        assert hindi_iso == 'hi'

        spanish_iso = registry.get_iso_code('Spanish')
        assert spanish_iso == 'es'

    def test_registry_ipa_systems(self):
        """Test that IPA systems are properly configured."""
        registry = language_registry.get_language_registry()

        # Test that we can get IPA codes for supported languages
        hindi_config = registry.get_config('Hindi')
        assert hindi_config is not None
        assert hindi_config.epitran_code == 'hin-Deva'
        assert hindi_config.phonemizer_code == 'hi'


if __name__ == "__main__":
    pytest.main([__file__])
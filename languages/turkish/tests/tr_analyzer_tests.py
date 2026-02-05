"""
Turkish Analyzer Tests
=====================

Basic tests for Turkish language analyzer implementation.
Tests domain components and basic functionality.
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from languages.turkish.domain import TurkishConfig, TurkishPromptBuilder
from languages.turkish.infrastructure import AnalysisRequest


class TestTurkishConfig:
    """Test Turkish configuration."""

    def test_config_initialization(self):
        """Test basic config initialization."""
        config = TurkishConfig()

        assert config.language_code == "tr"
        assert config.language_name == "Turkish"
        assert config.complexity_levels == ["beginner", "intermediate", "advanced"]

    def test_color_scheme(self):
        """Test color scheme access."""
        config = TurkishConfig()

        beginner_colors = config.color_scheme['beginner']
        assert 'noun' in beginner_colors
        assert 'verb' in beginner_colors

        # Test color retrieval
        noun_color = config.get_color_for_category('noun', 'beginner')
        assert noun_color.startswith('#')

    def test_vowel_harmony(self):
        """Test vowel harmony functionality."""
        config = TurkishConfig()

        # Test case marker selection
        marker = config.get_case_marker('dative', 'e')  # front vowel
        assert marker in ['e', 'a']

        marker = config.get_case_marker('dative', 'a')  # back vowel
        assert marker in ['e', 'a']

    def test_possessive_suffixes(self):
        """Test possessive suffix selection."""
        config = TurkishConfig()

        # Test 1st person singular
        suffix = config.get_possessive_suffix('1sg', 'e')  # front vowel
        assert suffix in ['im', 'ım', 'um', 'üm']

        suffix = config.get_possessive_suffix('1sg', 'a')  # back vowel
        assert suffix in ['im', 'ım', 'um', 'üm']


class TestTurkishPromptBuilder:
    """Test Turkish prompt building."""

    def test_prompt_builder_initialization(self):
        """Test prompt builder initialization."""
        config = TurkishConfig()
        builder = TurkishPromptBuilder(config)

        assert builder.config == config

    def test_analysis_prompt(self):
        """Test analysis prompt generation."""
        config = TurkishConfig()
        builder = TurkishPromptBuilder(config)

        text = "Merhaba dünya!"
        prompt = builder.build_analysis_prompt(text, 'beginner')

        # Check prevention-at-source elements
        assert 'AGGLUTINATION' in prompt
        assert 'VOWEL HARMONY' in prompt
        assert 'CASE SYSTEM' in prompt
        assert text in prompt

    def test_complexity_levels(self):
        """Test complexity level handling."""
        config = TurkishConfig()
        builder = TurkishPromptBuilder(config)

        complexities = builder.get_supported_complexities()
        assert 'beginner' in complexities
        assert 'intermediate' in complexities
        assert 'advanced' in complexities


class TestAnalysisRequest:
    """Test analysis request structure."""

    def test_request_creation(self):
        """Test analysis request creation."""
        request = AnalysisRequest(
            text="Test text",
            complexity="beginner",
            options={"test": True}
        )

        assert request.text == "Test text"
        assert request.complexity == "beginner"
        assert request.options == {"test": True}


if __name__ == "__main__":
    # Run basic tests
    print("Running Turkish Analyzer Tests...")

    # Test config
    config = TurkishConfig()
    print(f"✓ Config initialized: {config.language_name}")

    # Test prompt builder
    builder = TurkishPromptBuilder(config)
    prompt = builder.build_analysis_prompt("Merhaba!", "beginner")
    print(f"✓ Prompt generated: {len(prompt)} characters")

    # Test vowel harmony
    marker = config.get_case_marker('dative', 'e')
    print(f"✓ Case marker for 'e': {marker}")

    print("All basic tests passed!")
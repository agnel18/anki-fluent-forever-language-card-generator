# Test Spanish Configuration
# Tests for EsConfig class

import pytest
from ..domain.es_config import EsConfig

class TestEsConfig:
    """Tests for Spanish configuration"""

    @pytest.fixture
    def config(self):
        return EsConfig()

    def test_initialization(self, config):
        """Test config initializes correctly"""
        assert config.language_code == "es"
        assert config.language_name == "Spanish"
        assert config.language_name_native == "Español"
        assert not config.is_rtl
        assert config.text_direction == "ltr"
        assert config.script_type == "alphabetic"

    def test_grammatical_roles(self, config):
        """Test grammatical roles for different complexity levels"""
        beginner_roles = config.get_grammatical_roles("beginner")
        assert isinstance(beginner_roles, dict)
        assert 'noun' in beginner_roles
        assert 'verb' in beginner_roles

        intermediate_roles = config.get_grammatical_roles("intermediate")
        assert len(intermediate_roles) >= len(beginner_roles)  # Should have more roles

        advanced_roles = config.get_grammatical_roles("advanced")
        assert len(advanced_roles) >= len(intermediate_roles)  # Should have even more roles

    def test_color_schemes(self, config):
        """Test color schemes for different complexity levels"""
        beginner_colors = config.get_color_scheme("beginner")
        assert isinstance(beginner_colors, dict)
        assert 'noun' in beginner_colors
        assert isinstance(beginner_colors['noun'], str)

        # Check that colors are valid hex codes
        for role, color in beginner_colors.items():
            assert color.startswith('#'), f"Invalid color format for {role}: {color}"

    def test_linguistic_features(self, config):
        """Test linguistic features configuration"""
        features = config.linguistic_features
        assert features['gender_agreement'] is True
        assert features['verb_conjugation'] is True
        assert features['ser_estar_distinction'] is True
        assert features['differential_object_marking'] is True

    def test_spanish_text_validation(self, config):
        """Test Spanish text validation"""
        assert config.is_spanish_text("Hola, ¿cómo estás?") == True  # Contains Spanish characters
        assert config.is_spanish_text("Hello world") == False  # No Spanish characters
        assert config.is_spanish_text("café") == True  # Contains accented characters

    def test_prompt_templates(self, config):
        """Test prompt templates are loaded"""
        templates = config.prompt_templates
        assert 'single' in templates
        assert 'batch' in templates
        assert isinstance(templates['single'], str)
        assert len(templates['single']) > 0
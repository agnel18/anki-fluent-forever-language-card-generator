import pytest

class TestArabicConfig:
    """Test Arabic configuration component"""

    def test_initialization(self, arabic_config):
        """Test config initializes with required attributes"""
        assert hasattr(arabic_config, 'language_code')
        assert hasattr(arabic_config, 'language_name')
        assert hasattr(arabic_config, 'grammatical_roles')
        assert isinstance(arabic_config.grammatical_roles, dict)

    def test_arabic_specific_properties(self, arabic_config):
        """Test Arabic-specific configuration properties"""
        assert arabic_config.is_rtl == True
        assert arabic_config.text_direction == "rtl"
        assert arabic_config.script_type == "abjad"
        assert arabic_config.language_code == "ar"
        assert arabic_config.language_name_native == "العربية"

    def test_grammatical_roles_mapping(self, arabic_config):
        """Test grammatical roles are properly mapped"""
        roles = arabic_config.grammatical_roles

        # Should have basic universal roles
        assert 'beginner' in roles
        assert 'intermediate' in roles
        assert 'advanced' in roles

        # Beginner should have basic roles
        beginner_roles = roles['beginner']
        assert 'noun' in [k.split()[0] for k in beginner_roles.keys()]

    @pytest.mark.parametrize("complexity", ["beginner", "intermediate", "advanced"])
    def test_color_scheme_generation(self, arabic_config, complexity):
        """Test color scheme for different complexity levels"""
        colors = arabic_config.get_color_scheme(complexity)

        assert isinstance(colors, dict)
        assert len(colors) > 0

        # All colors should be valid hex codes
        for role, color in colors.items():
            assert color.startswith('#')
            assert len(color) == 7  # #RRGGBB format

    def test_complexity_progression(self, arabic_config):
        """Test that complexity levels build upon each other"""
        beginner = arabic_config.get_color_scheme('beginner')
        intermediate = arabic_config.get_color_scheme('intermediate')
        advanced = arabic_config.get_color_scheme('advanced')

        # Intermediate should have at least as many roles as beginner
        assert len(intermediate) >= len(beginner)

        # Advanced should have at least as many roles as intermediate
        assert len(advanced) >= len(intermediate)

    def test_arabic_text_detection(self, arabic_config):
        """Test Arabic text detection"""
        assert arabic_config.is_arabic_text("مرحبا") == True
        assert arabic_config.is_arabic_text("Hello") == False
        assert arabic_config.is_arabic_text("مرحبا Hello") == True

    def test_linguistic_features(self, arabic_config):
        """Test Arabic linguistic features configuration"""
        features = arabic_config.linguistic_features
        assert features['root_based_morphology'] == True
        assert features['case_marking_i3rab'] == True
        assert features['definite_article_al'] == True
        assert features['article_assimilation'] == True
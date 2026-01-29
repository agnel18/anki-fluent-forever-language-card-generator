import pytest
from unittest.mock import patch, MagicMock

class TestArabicIntegration:
    """Integration tests for Arabic analyzer components"""

    def test_config_and_prompt_builder_integration(self, arabic_config, arabic_prompt_builder):
        """Test config and prompt builder work together"""
        # Get grammatical roles from config
        roles = arabic_config.get_grammatical_roles('beginner')

        # Use in prompt builder
        prompt = arabic_prompt_builder.build_single_prompt(
            "القطة سوداء", "قطة", "beginner"
        )

        # Prompt should contain role information
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "القطة سوداء" in prompt

    def test_response_parser_and_validator_integration(self, arabic_response_parser, arabic_validator, mock_arabic_responses):
        """Test response parser and validator work together"""
        import json

        # Parse response
        response = json.dumps(mock_arabic_responses['valid_response'])
        parsed = arabic_response_parser.parse_response(
            response, "beginner", "القطة سوداء", "قطة"
        )

        # Validate result
        validated = arabic_validator.validate_result(parsed, "القطة سوداء")

        # Should have validation metadata
        assert 'validation_metadata' in validated
        assert 'confidence_score' in validated
        assert validated['validation_metadata']['is_rtl_validated'] == True

    @patch('languages.arabic.ar_analyzer.ArAnalyzer._call_ai')
    def test_full_analyzer_workflow(self, mock_call_ai, arabic_analyzer, mock_arabic_responses):
        """Test complete analyzer workflow with mocked AI"""
        import json

        # Mock successful AI response
        mock_call_ai.return_value = json.dumps(mock_arabic_responses['valid_response'])

        result = arabic_analyzer.analyze_grammar(
            sentence="القطة سوداء",
            target_word="قطة",
            complexity="beginner",
            gemini_api_key="mock_key"
        )

        # Verify complete workflow
        assert result.sentence == "القطة سوداء"
        assert result.target_word == "قطة"
        assert result.language_code == "ar"
        assert result.complexity_level == "beginner"
        assert result.is_rtl == True
        assert result.text_direction == "rtl"
        assert len(result.word_explanations) > 0
        assert result.confidence_score > 0
        assert result.html_output is not None
        assert 'dir="rtl"' in result.html_output

    def test_component_dependency_injection(self):
        """Test that components can be injected for testing"""
        from ..domain.ar_config import ArConfig
        from ..domain.ar_prompt_builder import ArPromptBuilder
        from ..domain.ar_response_parser import ArResponseParser
        from ..domain.ar_validator import ArValidator
        from ..ar_analyzer import ArAnalyzer

        # Create components
        config = ArConfig()
        prompt_builder = ArPromptBuilder(config)
        response_parser = ArResponseParser(config)
        validator = ArValidator(config)

        # Inject into analyzer
        analyzer = ArAnalyzer(
            config=config,
            prompt_builder=prompt_builder,
            response_parser=response_parser,
            validator=validator
        )

        # Verify injection worked
        assert analyzer.config == config
        assert analyzer.prompt_builder == prompt_builder
        assert analyzer.response_parser == response_parser
        assert analyzer.validator == validator

    def test_error_recovery_integration(self, arabic_analyzer):
        """Test error recovery across components"""
        # Test with invalid inputs
        result = arabic_analyzer.analyze_grammar("", "", "invalid", "")

        # Should still return valid result structure
        assert hasattr(result, 'sentence')
        assert hasattr(result, 'confidence_score')
        assert result.confidence_score < 0.5  # Low confidence for error case

    def test_rtl_text_processing_integration(self, arabic_analyzer):
        """Test RTL text processing across all components"""
        # Arabic text should be properly handled
        assert arabic_analyzer.validate_arabic_text("مرحبا") == True

        # Config should identify RTL
        assert arabic_analyzer.config.is_rtl == True

        # Results should be marked as RTL
        result = arabic_analyzer.analyze_grammar("test", "test", "beginner", "")
        assert result.is_rtl == True
        assert result.text_direction == "rtl"

    @pytest.mark.parametrize("complexity", ["beginner", "intermediate", "advanced"])
    def test_complexity_level_integration(self, arabic_analyzer, complexity, mock_arabic_responses):
        """Test complexity level handling across components"""
        import json
        from unittest.mock import patch

        with patch.object(arabic_analyzer, '_call_ai', return_value=json.dumps(mock_arabic_responses['valid_response'])):
            result = arabic_analyzer.analyze_grammar(
                "test sentence", "test", complexity, "mock_key"
            )

            assert result.complexity_level == complexity

            # Color scheme should match complexity
            expected_colors = arabic_analyzer.config.get_color_scheme(complexity)
            assert result.color_scheme == expected_colors

    def test_fallback_system_integration(self, arabic_analyzer):
        """Test fallback system integration"""
        # Force fallback by providing empty API key
        result = arabic_analyzer.analyze_grammar(
            "القطة سوداء نائمة", "قطة", "beginner", ""
        )

        # Should return fallback result
        assert result.confidence_score < 0.5
        assert result.is_rtl == True
        assert len(result.word_explanations) > 0

        # Fallback should still provide basic analysis
        assert all(len(exp) >= 4 for exp in result.word_explanations)
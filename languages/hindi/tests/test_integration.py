"""
Integration tests for Hindi analyzer components.
"""

import pytest

from ..hi_analyzer import HiAnalyzer


class TestHiIntegration:
    """Integration tests for Hindi analyzer."""

    @pytest.fixture
    def analyzer(self):
        return HiAnalyzer()

    def test_full_analysis_workflow_simulation(self, analyzer):
        """Test complete analysis workflow without API calls."""
        sentence = "यह एक परीक्षण वाक्य है"
        target_word = "परीक्षण"
        complexity = "beginner"

        prompt = analyzer.get_grammar_prompt(complexity, sentence, target_word)
        assert isinstance(prompt, str)
        assert sentence in prompt

        fallback_result = analyzer.response_parser.fallbacks.create_fallback(sentence, complexity)
        assert "word_explanations" in fallback_result
        assert "explanations" in fallback_result
        assert len(fallback_result["word_explanations"]) > 0

        validated = analyzer.validator.validate_result(fallback_result, sentence)
        assert "confidence" in validated
        assert 0.0 <= validated["confidence"] <= 1.0
        assert validated.get("is_fallback", False) is True

    def test_component_integration(self, analyzer):
        """Test that all components are initialized."""
        assert analyzer.hi_config is not None
        assert analyzer.prompt_builder is not None
        assert analyzer.response_parser is not None
        assert analyzer.validator is not None

    def test_prompt_to_parser_integration(self, analyzer):
        """Test prompt builder and response parser interoperability."""
        sentence = "मैं किताब पढ़ता हूँ"
        target_word = "किताब"
        complexity = "beginner"

        prompt = analyzer.prompt_builder.build_single_prompt(sentence, target_word, complexity)
        assert isinstance(prompt, str)

        mock_response = '''{
            "words": [
                {"word": "मैं", "grammatical_role": "pronoun", "individual_meaning": "first person"},
                {"word": "किताब", "grammatical_role": "noun", "individual_meaning": "book"},
                {"word": "पढ़ता", "grammatical_role": "verb", "individual_meaning": "read"}
            ],
            "explanations": {"overall_structure": "simple SOV", "key_features": "present tense"}
        }'''

        parsed = analyzer.response_parser.parse_response(mock_response, complexity, sentence, target_word)
        validated = analyzer.validator.validate_result(parsed, sentence)

        assert "word_explanations" in validated
        assert len(validated["word_explanations"]) > 0

    def test_fallback_integration(self, analyzer):
        """Test fallback system produces valid structure."""
        sentence = "नमस्ते दुनिया"
        complexity = "beginner"

        fallback = analyzer.response_parser.fallbacks.create_fallback(sentence, complexity)
        assert "word_explanations" in fallback
        assert "explanations" in fallback
        assert "confidence" in fallback

    def test_color_scheme_integration(self, analyzer):
        """Test color scheme coverage across roles."""
        complexity = "intermediate"

        colors = analyzer.get_color_scheme(complexity)
        roles = analyzer.hi_config.grammatical_roles.get("grammatical_roles", {})

        for role in roles.keys():
            assert role in colors, f"Missing color for role: {role}"

    @pytest.mark.parametrize("sentence,target,complexity", [
        ("वह घर गया", "घर", "beginner"),
        ("मैंने किताब पढ़ी", "किताब", "intermediate"),
        ("वे तेजी से दौड़ रहे हैं", "दौड़", "advanced"),
    ])
    def test_various_sentences_fallback(self, analyzer, sentence, target, complexity):
        """Test fallback analysis on varied sentences."""
        fallback = analyzer.response_parser.fallbacks.create_fallback(sentence, complexity)

        assert "word_explanations" in fallback
        assert len(fallback["word_explanations"]) > 0

        for word_data in fallback["word_explanations"]:
            assert len(word_data) >= 4

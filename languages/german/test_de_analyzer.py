# German Analyzer Test Suite
# Comprehensive testing for German grammar analysis
# Tests case system, gender agreement, and linguistic accuracy

import pytest
import sys
import os
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add the languages directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import German analyzer components
from languages.german.de_analyzer import DeAnalyzer
from languages.german.domain.de_config import DeConfig
from languages.german.domain.de_prompt_builder import DePromptBuilder
from languages.german.domain.de_response_parser import DeResponseParser
from languages.german.domain.de_validator import DeValidator
from languages.german.infrastructure.de_fallbacks import DeFallbacks

class TestDeAnalyzer:
    """Test suite for German analyzer"""

    @pytest.fixture
    def de_config(self):
        """Create German configuration"""
        return DeConfig()

    @pytest.fixture
    def de_prompt_builder(self, de_config):
        """Create German prompt builder"""
        return DePromptBuilder(de_config)

    @pytest.fixture
    def de_response_parser(self, de_config):
        """Create German response parser"""
        return DeResponseParser(de_config)

    @pytest.fixture
    def de_validator(self, de_config):
        """Create German validator"""
        return DeValidator(de_config)

    @pytest.fixture
    def de_fallbacks(self, de_config):
        """Create German fallbacks"""
        return DeFallbacks(de_config)

    @pytest.fixture
    def analyzer(self, de_config, de_prompt_builder, de_response_parser, de_validator, de_fallbacks):
        """Create German analyzer with mocked dependencies"""
        return DeAnalyzer(
            config=de_config,
            prompt_builder=de_prompt_builder,
            response_parser=de_response_parser,
            validator=de_validator,
            fallbacks=de_fallbacks
        )

    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer.LANGUAGE_CODE == "de"
        assert analyzer.LANGUAGE_NAME == "German"
        assert analyzer.VERSION == "1.0"
        assert analyzer.de_config is not None
        assert analyzer.prompt_builder is not None
        assert analyzer.response_parser is not None
        assert analyzer.validator is not None
        assert analyzer.fallbacks is not None

    def test_case_name_mapping(self, de_config):
        """Test German case name mapping"""
        assert de_config.get_case_name("nominativ") == "Nominativ"
        assert de_config.get_case_name("akkusativ") == "Akkusativ"
        assert de_config.get_case_name("dativ") == "Dativ"
        assert de_config.get_case_name("genitiv") == "Genitiv"
        assert de_config.get_case_name("unknown") == "unknown"

    def test_gender_name_mapping(self, de_config):
        """Test German gender name mapping"""
        assert de_config.get_gender_name("maskulin") == "Maskulinum"
        assert de_config.get_gender_name("feminin") == "Femininum"
        assert de_config.get_gender_name("neutrum") == "Neutrum"
        assert de_config.get_gender_name("unknown") == "unknown"

    def test_color_scheme_generation(self, de_config):
        """Test color scheme generation for different complexity levels"""
        beginner_scheme = de_config.get_color_scheme("beginner")
        assert "noun" in beginner_scheme
        assert "verb" in beginner_scheme
        assert "article" in beginner_scheme

        advanced_scheme = de_config.get_color_scheme("advanced")
        assert "noun" in advanced_scheme
        assert "verb" in advanced_scheme
        assert "preposition" in advanced_scheme

    def test_prompt_builder_single_prompt(self, de_prompt_builder):
        """Test single prompt generation"""
        sentence = "Der Mann isst einen Apfel."
        target_word = "Mann"
        complexity = "intermediate"

        prompt = de_prompt_builder.build_single_prompt(sentence, target_word, complexity)

        assert "German" in prompt
        assert sentence in prompt
        assert target_word in prompt
        assert "case" in prompt.lower()
        assert "gender" in prompt.lower()

    def test_prompt_builder_batch_prompt(self, de_prompt_builder):
        """Test batch prompt generation"""
        sentences = ["Der Mann isst.", "Die Frau trinkt."]
        target_word = "Mann"
        complexity = "intermediate"

        prompt = de_prompt_builder.build_batch_prompt(sentences, target_word, complexity)

        assert "German" in prompt
        assert "sentences" in prompt.lower()
        assert "Der Mann isst." in prompt
        assert "Die Frau trinkt." in prompt

    def test_response_parser_valid_json(self, de_response_parser):
        """Test parsing valid JSON response"""
        json_response = '''
        {
            "words": [
                {
                    "word": "Der",
                    "grammatical_role": "article",
                    "grammatical_case": "nominativ",
                    "gender": "maskulin",
                    "individual_meaning": "The (masculine nominative)"
                },
                {
                    "word": "Mann",
                    "grammatical_role": "noun",
                    "grammatical_case": "nominativ",
                    "gender": "maskulin",
                    "individual_meaning": "man"
                }
            ],
            "overall_analysis": {
                "sentence_structure": "Subject-verb-object with definite article",
                "key_features": "Nominative case, masculine gender agreement"
            }
        }
        '''

        result = de_response_parser.parse_response(json_response, "intermediate", "Der Mann isst.", "Mann")

        assert "words" in result
        assert len(result["words"]) == 2
        assert result["words"][0]["word"] == "Der"
        assert result["words"][0]["grammatical_case"] == "nominative"
        assert result["words"][0]["gender"] == "masculine"

    def test_response_parser_malformed_json(self, de_response_parser):
        """Test parsing malformed JSON response"""
        malformed_response = '''
        {
            "words": [
                {
                    "word": "Der",
                    "grammatical_role": "article",
                    "grammatical_case": "nominativ",
                    "gender": "maskulin",
                    "individual_meaning": "The (masculine nominative)"
                },
                {
                    "word": "Mann",
                    "grammatical_role": "noun",
                    "grammatical_case": "nominativ",
                    "gender": "maskulin",
                    "individual_meaning": "man"
                }
            ],
            "overall_analysis": {
                "sentence_structure": "Subject-verb-object with definite article",
                "key_features": "Nominative case, masculine gender agreement"
            }
        '''
        # Missing closing brace

        result = de_response_parser.parse_response(malformed_response, "intermediate", "Der Mann isst.", "Mann")

        # Should still parse successfully due to error handling
        assert "words" in result
        assert len(result["words"]) == 3

    def test_validator_case_consistency(self, de_validator):
        """Test case consistency validation"""
        # Valid case consistency
        valid_result = {
            "words": [
                {"word": "Der", "grammatical_role": "article", "grammatical_case": "nominativ", "gender": "maskulin"},
                {"word": "Mann", "grammatical_role": "noun", "grammatical_case": "nominativ", "gender": "maskulin"}
            ],
            "overall_analysis": {
                "sentence_structure": "Subject-verb-object with definite article",
                "key_features": "Nominative case, masculine gender agreement"
            }
        }

        validated = de_validator.validate_result(valid_result, "Der Mann isst.")
        assert validated["confidence"] > 0.6  # Should be reasonably high confidence

        # Invalid case inconsistency
        invalid_result = {
            "words": [
                {"word": "Der", "grammatical_role": "article", "grammatical_case": "nominativ", "gender": "maskulin"},
                {"word": "Mann", "grammatical_role": "noun", "grammatical_case": "akkusativ", "gender": "maskulin"}
            ]
        }

        validated = de_validator.validate_result(invalid_result, "Der Mann isst.")
        assert validated["confidence"] < 0.7  # Should be lower confidence

    def test_validator_gender_agreement(self, de_validator):
        """Test gender agreement validation"""
        # Valid gender agreement
        valid_result = {
            "words": [
                {"word": "Der", "grammatical_role": "article", "grammatical_case": "nominativ", "gender": "maskulin"},
                {"word": "Mann", "grammatical_role": "noun", "grammatical_case": "nominativ", "gender": "maskulin"}
            ],
            "overall_analysis": {
                "sentence_structure": "Subject-verb-object with definite article",
                "key_features": "Nominative case, masculine gender agreement"
            }
        }

        validated = de_validator.validate_result(valid_result, "Der Mann isst.")
        assert validated["confidence"] > 0.6

        # Invalid gender disagreement
        invalid_result = {
            "words": [
                {"word": "Der", "grammatical_role": "article", "grammatical_case": "nominativ", "gender": "maskulin"},
                {"word": "Mann", "grammatical_role": "noun", "grammatical_case": "nominativ", "gender": "feminin"}
            ]
        }

        validated = de_validator.validate_result(invalid_result, "Der Mann isst.")
        assert validated["confidence"] < 0.7

    def test_fallbacks_basic_analysis(self, de_fallbacks):
        """Test fallback analysis for basic German sentence"""
        sentence = "Der Mann isst einen Apfel."
        complexity = "intermediate"
        target_word = "Mann"

        result = de_fallbacks.create_fallback(sentence, complexity, target_word)

        assert "words" in result
        assert len(result["words"]) > 0
        assert result["words"][0]["word"] in sentence

    def test_fallbacks_case_detection(self, de_fallbacks):
        """Test fallback case detection"""
        # Test nominative case
        result = de_fallbacks._analyze_german_word("Der", "Der Mann")
        assert result["grammatical_case"] == "nominative"
        assert result["gender"] == "maskulin"

        # Test akkusative case
        result = de_fallbacks._analyze_german_word("einen", "isst einen Apfel")
        assert result["grammatical_case"] == "accusative"
        assert result["gender"] == "maskulin"

    def test_analyzer_fallback_on_ai_failure(self, analyzer):
        """Test analyzer falls back when AI call fails"""
        with patch.object(analyzer, '_call_ai', return_value=None):
            result = analyzer.analyze_grammar("Der Mann isst.", "Mann", "intermediate", "fake_key")

            assert result is not None
            assert result.sentence == "Der Mann isst."
            assert result.target_word == "Mann"
            assert result.language_code == "de"

    @patch('languages.german.de_analyzer.get_gemini_model')
    def test_analyzer_ai_call_success(self, mock_get_model, analyzer):
        """Test analyzer with successful AI call"""
        # Mock AI response
        mock_response = Mock()
        mock_response.text = '''
        {
            "words": [
                {
                    "word": "Der",
                    "grammatical_role": "article",
                    "grammatical_case": "nominativ",
                    "gender": "maskulin",
                    "individual_meaning": "The (masculine nominative definite article)"
                },
                {
                    "word": "Mann",
                    "grammatical_role": "noun",
                    "grammatical_case": "nominativ",
                    "gender": "maskulin",
                    "individual_meaning": "man, male person"
                }
            ],
            "overall_analysis": {
                "sentence_structure": "Subject-verb-object with definite article",
                "key_features": "Nominative case, masculine gender agreement, V2 word order"
            }
        }
        '''
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model

        result = analyzer.analyze_grammar("Der Mann isst.", "Mann", "intermediate", "fake_key")

        assert result is not None
        assert result.sentence == "Der Mann isst."
        assert result.language_code == "de"
        assert len(result.word_explanations) == 2
        assert result.word_explanations[0][0] == "Der"  # word
        assert result.word_explanations[0][1] == "article"  # role

    def test_batch_analysis(self, analyzer):
        """Test batch analysis functionality"""
        sentences = ["Der Mann isst.", "Die Frau trinkt."]
        target_word = "Mann"
        complexity = "intermediate"

        with patch.object(analyzer, '_call_ai', return_value=None):
            results = analyzer.batch_analyze_grammar(sentences, target_word, complexity, "fake_key")

            assert len(results) == 2
            assert results[0].sentence == "Der Mann isst."
            assert results[1].sentence == "Die Frau trinkt."
            assert all(r.language_code == "de" for r in results)

    def test_html_output_generation(self, analyzer):
        """Test HTML output generation with German features"""
        sentence = "Der Mann isst einen Apfel."
        words = [
            {"word": "Der", "grammatical_role": "article", "grammatical_case": "nominativ", "gender": "maskulin", "individual_meaning": "The"},
            {"word": "Mann", "grammatical_role": "noun", "grammatical_case": "nominativ", "gender": "maskulin", "individual_meaning": "man"},
            {"word": "isst", "grammatical_role": "verb", "grammatical_case": "", "gender": "", "individual_meaning": "eats"},
            {"word": "einen", "grammatical_role": "article", "grammatical_case": "akkusativ", "gender": "maskulin", "individual_meaning": "a"},
            {"word": "Apfel", "grammatical_role": "noun", "grammatical_case": "akkusativ", "gender": "maskulin", "individual_meaning": "apple"}
        ]

        color_scheme = analyzer.de_config.get_color_scheme("intermediate")
        html_output = analyzer._generate_html_output(sentence, words, color_scheme)

        assert '<div dir="ltr" lang="de">' in html_output
        assert 'title=' in html_output  # Tooltips present
        assert 'style="color:' in html_output  # Colors applied

    def test_german_color_logic(self, analyzer):
        """Test German-specific color logic"""
        color_scheme = analyzer.de_config.get_color_scheme("intermediate")

        # Test article colors based on case/gender
        color = analyzer._get_german_color("article", "nominativ", "maskulin", color_scheme)
        assert color != color_scheme.get("default", "#000000")  # Should be different from default

        color = analyzer._get_german_color("article", "akkusativ", "maskulin", color_scheme)
        assert color != color_scheme.get("default", "#000000")

        # Test regular role colors
        color = analyzer._get_german_color("noun", "", "", color_scheme)
        assert color == color_scheme.get("noun", color_scheme.get("default", "#000000"))

    def test_legacy_methods(self, analyzer):
        """Test legacy compatibility methods"""
        # Test prompt generation
        prompt = analyzer.get_grammar_prompt("intermediate", "Der Mann isst.", "Mann")
        assert "German" in prompt
        assert "Der Mann isst." in prompt

        # Test response parsing
        json_response = '{"words": [], "overall_analysis": {}}'
        parsed = analyzer.parse_grammar_response(json_response, "intermediate", "Der Mann isst.")
        assert "words" in parsed

        # Test validation
        test_data = {"words": []}
        confidence = analyzer.validate_analysis(test_data, "Der Mann isst.")
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

if __name__ == "__main__":
    pytest.main([__file__])
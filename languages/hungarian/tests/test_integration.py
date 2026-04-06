"""Hungarian integration tests — full pipeline without AI."""

import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.hungarian.hu_analyzer import HuAnalyzer
from languages.hungarian.domain.hu_config import HuConfig
from languages.hungarian.domain.hu_prompt_builder import HuPromptBuilder
from languages.hungarian.domain.hu_response_parser import HuResponseParser
from languages.hungarian.domain.hu_validator import HuValidator
from languages.hungarian.infrastructure.hu_fallbacks import HuFallbacks


class TestFullPipeline:
    """Test the full prompt → parse → validate → HTML pipeline."""

    def setup_method(self):
        self.analyzer = HuAnalyzer()
        self.config = HuConfig()

    def test_prompt_to_parse_to_validate(self):
        """Simulate the full pipeline with a mock AI response."""
        sentence = "A fiú almát eszik."
        target_word = "eszik"
        complexity = "beginner"

        # Step 1: Generate prompt
        prompt = self.analyzer.get_grammar_prompt(complexity, sentence, target_word)
        assert isinstance(prompt, str)
        assert sentence in prompt

        # Step 2: Simulate AI response (mock)
        mock_response = json.dumps({
            "sentence": sentence,
            "words": [
                {"word": "A", "grammatical_role": "definite_article", "individual_meaning": "the (definite article before consonants)"},
                {"word": "fiú", "grammatical_role": "noun", "case": "nominative", "individual_meaning": "boy (nominative, subject)"},
                {"word": "almát", "grammatical_role": "noun", "case": "accusative", "individual_meaning": "apple with accusative suffix -t"},
                {"word": "eszik", "grammatical_role": "verb", "conjugation_type": "indefinite", "tense": "present", "individual_meaning": "eats (3rd person singular, indefinite conjugation, present)"}
            ],
            "explanations": {
                "overall_structure": "SVO sentence: Subject + Object-ACC + Verb (indefinite conjugation for indefinite object without article)",
                "key_features": "Accusative -t suffix on alma → almát, indefinite verb conjugation because 'alma' has no definite article",
                "complexity_notes": "Beginner level — basic SVO with accusative case"
            }
        })

        # Step 3: Parse
        parsed = self.analyzer.parse_grammar_response(mock_response, complexity, sentence)
        assert 'word_explanations' in parsed
        assert len(parsed['word_explanations']) == 4

        # Step 4: Validate
        confidence = self.analyzer.validate_analysis(parsed, sentence)
        assert isinstance(confidence, float)
        assert confidence >= 0.85

        # Step 5: Generate HTML
        html = self.analyzer._generate_html_output(parsed, sentence, complexity)
        assert '<span' in html
        assert 'fiú' in html

    def test_intermediate_pipeline(self):
        """Test intermediate complexity with case markers and conjugation types."""
        sentence = "Megírtam a levelet tegnap."
        mock_response = json.dumps({
            "sentence": sentence,
            "words": [
                {"word": "Megírtam", "grammatical_role": "verb", "conjugation_type": "definite", "tense": "past", "preverb": "meg", "individual_meaning": "I finished writing (it) — meg- (completion preverb) + ír (write) + past + 1sg definite"},
                {"word": "a", "grammatical_role": "definite_article", "individual_meaning": "the (definite article)"},
                {"word": "levelet", "grammatical_role": "noun", "case": "accusative", "individual_meaning": "letter with accusative suffix -et"},
                {"word": "tegnap", "grammatical_role": "adverb", "individual_meaning": "yesterday (time adverb)"}
            ],
            "explanations": {
                "overall_structure": "Verb-first with preverb meg-, definite conjugation because 'a levelet' is definite object",
                "key_features": "Preverb meg- (completion), definite conjugation, past tense, accusative case",
                "complexity_notes": "Intermediate — preverb + definite conjugation + past tense"
            }
        })

        parsed = self.analyzer.parse_grammar_response(mock_response, "intermediate", sentence)
        assert len(parsed['word_explanations']) == 4

        confidence = self.analyzer.validate_analysis(parsed, sentence)
        assert confidence >= 0.85

        html = self.analyzer._generate_html_output(parsed, sentence, "intermediate")
        assert '<span' in html
        assert 'Megírtam' in html

    def test_fallback_pipeline(self):
        """Test that fallback produces valid output for any sentence."""
        fallbacks = HuFallbacks(self.config)
        result = fallbacks.create_fallback("A gyerek az iskolában tanul.", "beginner")

        assert 'word_explanations' in result
        assert len(result['word_explanations']) > 0
        assert result['confidence'] == 0.3
        assert result['is_fallback'] is True

        # Verify fallback produces valid HTML
        html = self.analyzer._generate_html_output(result, "A gyerek az iskolában tanul.", "beginner")
        assert isinstance(html, str)

    def test_batch_parse_pipeline(self):
        """Test batch parsing."""
        sentences = [
            "A fiú almát eszik.",
            "Olvasok egy könyvet."
        ]

        mock_batch = json.dumps({
            "batch_results": [
                {
                    "sentence": "A fiú almát eszik.",
                    "words": [
                        {"word": "A", "grammatical_role": "definite_article", "individual_meaning": "the"},
                        {"word": "fiú", "grammatical_role": "noun", "individual_meaning": "boy"},
                        {"word": "almát", "grammatical_role": "noun", "case": "accusative", "individual_meaning": "apple (accusative)"},
                        {"word": "eszik", "grammatical_role": "verb", "individual_meaning": "eats (indefinite conjugation)"}
                    ],
                    "explanations": {"overall_structure": "SVO", "key_features": "Accusative"}
                },
                {
                    "sentence": "Olvasok egy könyvet.",
                    "words": [
                        {"word": "Olvasok", "grammatical_role": "verb", "conjugation_type": "indefinite", "individual_meaning": "I read (indefinite)"},
                        {"word": "egy", "grammatical_role": "indefinite_article", "individual_meaning": "a/an"},
                        {"word": "könyvet", "grammatical_role": "noun", "case": "accusative", "individual_meaning": "book (accusative)"}
                    ],
                    "explanations": {"overall_structure": "VO", "key_features": "Indefinite conjugation"}
                }
            ]
        })

        parser = HuResponseParser(self.config, HuFallbacks(self.config))
        results = parser.parse_batch_response(mock_batch, sentences, "beginner")
        assert len(results) == 2
        assert len(results[0]['word_explanations']) == 4
        assert len(results[1]['word_explanations']) == 3

    def test_color_schemes_across_levels(self):
        """Verify color schemes are well-defined across all complexity levels."""
        for level in ['beginner', 'intermediate', 'advanced']:
            scheme = self.analyzer.get_color_scheme(level)
            assert isinstance(scheme, dict)
            assert 'noun' in scheme
            assert 'verb' in scheme
            # All colors should be valid hex codes
            for role, color in scheme.items():
                assert color.startswith('#'), f"Invalid color for {role}: {color}"
                assert len(color) == 7, f"Invalid color length for {role}: {color}"

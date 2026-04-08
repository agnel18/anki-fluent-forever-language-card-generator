"""Malayalam analyzer tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.malayalam.ml_analyzer import MlAnalyzer


def test_analyzer_creation():
    analyzer = MlAnalyzer()
    assert analyzer is not None
    assert analyzer.language_code == "ml"


def test_analyzer_has_required_methods():
    analyzer = MlAnalyzer()
    required_methods = [
        'analyze_grammar',
        'batch_analyze_grammar',
        'get_grammar_prompt',
        'parse_grammar_response',
        'get_color_scheme',
        'validate_analysis',
    ]

    for method in required_methods:
        assert hasattr(analyzer, method), f"Missing method: {method}"


def test_analyzer_version():
    analyzer = MlAnalyzer()
    assert analyzer.VERSION == "1.0"
    assert analyzer.LANGUAGE_CODE == "ml"
    assert analyzer.LANGUAGE_NAME == "Malayalam"


def test_color_scheme_returns_dict():
    analyzer = MlAnalyzer()
    for level in ['beginner', 'intermediate', 'advanced']:
        scheme = analyzer.get_color_scheme(level)
        assert isinstance(scheme, dict)
        assert len(scheme) > 0


def test_get_grammar_prompt_returns_string():
    analyzer = MlAnalyzer()
    prompt = analyzer.get_grammar_prompt("beginner", "ഞാൻ വെള്ളം കുടിക്കുന്നു", "കുടിക്കുക")
    assert isinstance(prompt, str)
    assert len(prompt) > 50
    assert "ഞാൻ വെള്ളം കുടിക്കുന്നു" in prompt


def test_html_output_generation():
    analyzer = MlAnalyzer()
    parsed_data = {
        'word_explanations': [
            ["ഞാൻ", "pronoun", "#4FC3F7", "I (first person singular)"],
            ["വെള്ളം", "noun", "#FFAA00", "water"],
            ["കുടിക്കുന്നു", "verb", "#44FF44", "drink (present tense)"],
        ],
        'elements': {},
        'explanations': {},
        'confidence': 0.8
    }
    html = analyzer._generate_html_output(parsed_data, "ഞാൻ വെള്ളം കുടിക്കുന്നു", "beginner")
    assert isinstance(html, str)
    assert "<span" in html
    assert "ഞാൻ" in html
    assert "കുടിക്കുന്നു" in html


def test_html_handles_empty_explanations():
    analyzer = MlAnalyzer()
    parsed_data = {'word_explanations': [], 'elements': {}, 'explanations': {}}
    html = analyzer._generate_html_output(parsed_data, "ടെസ്റ്റ്", "beginner")
    assert html == "ടെസ്റ്റ്"


def test_map_grammatical_role():
    analyzer = MlAnalyzer()
    category = analyzer._map_grammatical_role_to_category("auxiliary_verb")
    assert isinstance(category, str)

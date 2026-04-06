"""Hungarian analyzer tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.hungarian.hu_analyzer import HuAnalyzer


def test_analyzer_creation():
    analyzer = HuAnalyzer()
    assert analyzer is not None
    assert analyzer.language_code == "hu"


def test_analyzer_has_required_methods():
    analyzer = HuAnalyzer()
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
    analyzer = HuAnalyzer()
    assert analyzer.VERSION == "1.0"
    assert analyzer.LANGUAGE_CODE == "hu"
    assert analyzer.LANGUAGE_NAME == "Hungarian"


def test_color_scheme_returns_dict():
    analyzer = HuAnalyzer()
    for level in ['beginner', 'intermediate', 'advanced']:
        scheme = analyzer.get_color_scheme(level)
        assert isinstance(scheme, dict)
        assert len(scheme) > 0


def test_get_grammar_prompt_returns_string():
    analyzer = HuAnalyzer()
    prompt = analyzer.get_grammar_prompt("beginner", "A fiú almát eszik.", "eszik")
    assert isinstance(prompt, str)
    assert len(prompt) > 50
    assert "A fiú almát eszik." in prompt


def test_html_output_generation():
    analyzer = HuAnalyzer()
    parsed_data = {
        'word_explanations': [
            ['A', 'definite_article', '#87CEEB', 'the (definite article)'],
            ['fiú', 'noun', '#FFAA00', 'boy (nominative)'],
            ['almát', 'noun', '#FFAA00', 'apple (accusative case, -t suffix)'],
            ['eszik', 'verb', '#44FF44', 'eats (3rd person singular, indefinite conjugation)'],
        ],
        'elements': {},
        'explanations': {}
    }

    html = analyzer._generate_html_output(parsed_data, "A fiú almát eszik.", "beginner")
    assert '<span' in html
    assert 'fiú' in html
    assert 'almát' in html
    assert 'eszik' in html


def test_parse_grammar_response_valid_json():
    analyzer = HuAnalyzer()
    valid_json = '''{
        "sentence": "A fiú almát eszik.",
        "words": [
            {"word": "A", "grammatical_role": "definite_article", "individual_meaning": "the"},
            {"word": "fiú", "grammatical_role": "noun", "individual_meaning": "boy"},
            {"word": "almát", "grammatical_role": "noun", "case": "accusative", "individual_meaning": "apple (accusative)"},
            {"word": "eszik", "grammatical_role": "verb", "conjugation_type": "indefinite", "individual_meaning": "eats"}
        ],
        "explanations": {
            "overall_structure": "SVO sentence with accusative object",
            "key_features": "Accusative -t suffix on alma, indefinite conjugation",
            "complexity_notes": "Beginner level"
        }
    }'''

    result = analyzer.parse_grammar_response(valid_json, "beginner", "A fiú almát eszik.")
    assert isinstance(result, dict)
    assert 'word_explanations' in result
    assert len(result['word_explanations']) == 4


def test_validate_analysis_returns_float():
    analyzer = HuAnalyzer()
    parsed_data = {
        'word_explanations': [
            ['A', 'definite_article', '#87CEEB', 'the (definite article)'],
            ['fiú', 'noun', '#FFAA00', 'boy (nominative)'],
            ['almát', 'accusative', '#4169E1', 'apple with accusative -t suffix'],
            ['eszik', 'verb', '#44FF44', 'eats (3rd person, indefinite conjugation)'],
        ],
        'elements': {
            'definite_article': [{'word': 'A'}],
            'noun': [{'word': 'fiú'}],
            'accusative': [{'word': 'almát'}],
            'verb': [{'word': 'eszik'}],
        },
        'explanations': {
            'overall_structure': 'SVO with accusative',
            'key_features': 'Basic Hungarian sentence',
            'complexity_notes': 'Beginner level'
        }
    }

    score = analyzer.validate_analysis(parsed_data, "A fiú almát eszik.")
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_fallback_on_invalid_json():
    analyzer = HuAnalyzer()
    result = analyzer.parse_grammar_response("invalid json data", "beginner", "A fiú almát eszik.")
    assert isinstance(result, dict)
    assert 'word_explanations' in result
    # Fallback should still produce some analysis
    assert result.get('is_fallback', False) is True


def test_hungarian_specific_colors():
    """Verify Hungarian-specific color categories exist."""
    analyzer = HuAnalyzer()

    # Intermediate should have case marker colors
    intermediate = analyzer.get_color_scheme("intermediate")
    assert "accusative" in intermediate
    assert "dative" in intermediate
    assert "instrumental" in intermediate
    assert "preverb" in intermediate
    assert "postposition" in intermediate
    assert "possessive_suffix" in intermediate
    assert "definite_conjugation" in intermediate
    assert "indefinite_conjugation" in intermediate

    # Advanced should have all 18 cases
    advanced = analyzer.get_color_scheme("advanced")
    case_roles = [
        "accusative", "dative", "instrumental", "causal_final",
        "translative", "inessive", "superessive", "adessive",
        "sublative", "delative", "elative", "illative",
        "allative", "ablative", "terminative", "essive_formal", "distributive"
    ]
    for case in case_roles:
        assert case in advanced, f"Missing case color: {case}"

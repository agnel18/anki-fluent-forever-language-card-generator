"""Japanese analyzer tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.japanese.ja_analyzer import JaAnalyzer


def test_analyzer_creation():
    analyzer = JaAnalyzer()
    assert analyzer is not None
    assert analyzer.language_code == "ja"


def test_analyzer_has_required_methods():
    analyzer = JaAnalyzer()
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
    analyzer = JaAnalyzer()
    assert analyzer.VERSION == "1.0"
    assert analyzer.LANGUAGE_CODE == "ja"
    assert analyzer.LANGUAGE_NAME == "Japanese"


def test_color_scheme_returns_dict():
    analyzer = JaAnalyzer()
    for level in ['beginner', 'intermediate', 'advanced']:
        scheme = analyzer.get_color_scheme(level)
        assert isinstance(scheme, dict)
        assert len(scheme) > 0


def test_get_grammar_prompt_returns_string():
    analyzer = JaAnalyzer()
    prompt = analyzer.get_grammar_prompt("beginner", "私は本を読む", "読む")
    assert isinstance(prompt, str)
    assert len(prompt) > 50
    assert "私は本を読む" in prompt


def test_html_output_generation():
    analyzer = JaAnalyzer()
    parsed_data = {
        'word_explanations': [
            ["私", "pronoun", "#4FC3F7", "I/me"],
            ["は", "topic_particle", "#81C784", "(topic marker)"],
            ["本", "noun", "#4FC3F7", "book"],
            ["を", "object_particle", "#81C784", "(object marker)"],
            ["読む", "verb", "#FF8A65", "read"],
        ],
        'elements': {},
        'explanations': {},
        'confidence': 0.8
    }
    html = analyzer._generate_html_output(parsed_data, "私は本を読む", "beginner")
    assert isinstance(html, str)
    assert "<span" in html
    assert "私" in html
    assert "読む" in html


def test_html_handles_empty_explanations():
    analyzer = JaAnalyzer()
    parsed_data = {'word_explanations': [], 'elements': {}, 'explanations': {}}
    html = analyzer._generate_html_output(parsed_data, "テスト", "beginner")
    assert html == "テスト"


def test_map_grammatical_role():
    analyzer = JaAnalyzer()
    # Roles defined in role_hierarchy should map to parent categories
    category = analyzer._map_grammatical_role_to_category("topic_particle")
    assert isinstance(category, str)

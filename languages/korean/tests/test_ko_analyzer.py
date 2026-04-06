"""Korean analyzer tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.korean.ko_analyzer import KoAnalyzer


def test_analyzer_creation():
    analyzer = KoAnalyzer()
    assert analyzer is not None
    assert analyzer.language_code == "ko"


def test_analyzer_has_required_methods():
    analyzer = KoAnalyzer()
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
    analyzer = KoAnalyzer()
    assert analyzer.VERSION == "1.0"
    assert analyzer.LANGUAGE_CODE == "ko"
    assert analyzer.LANGUAGE_NAME == "Korean"


def test_color_scheme_returns_dict():
    analyzer = KoAnalyzer()
    for level in ['beginner', 'intermediate', 'advanced']:
        scheme = analyzer.get_color_scheme(level)
        assert isinstance(scheme, dict)
        assert len(scheme) > 0


def test_get_grammar_prompt_returns_string():
    analyzer = KoAnalyzer()
    prompt = analyzer.get_grammar_prompt("beginner", "저는 학생입니다.", "학생")
    assert isinstance(prompt, str)
    assert len(prompt) > 50
    assert "저는 학생입니다." in prompt


def test_html_output_generation():
    analyzer = KoAnalyzer()
    parsed_data = {
        'word_explanations': [
            ["저", "pronoun", "#FF4444", "I (humble)"],
            ["는", "topic_marker", "#1E90FF", "topic marker"],
            ["학생", "noun", "#FFAA00", "student"],
            ["입니다", "copula", "#AA44FF", "is (formal polite)"],
        ],
        'elements': {},
        'explanations': {},
        'confidence': 0.8
    }
    html = analyzer._generate_html_output(parsed_data, "저는 학생입니다.", "beginner")
    assert isinstance(html, str)
    assert "<span" in html
    assert "저" in html
    assert "학생" in html


def test_html_handles_empty_explanations():
    analyzer = KoAnalyzer()
    parsed_data = {'word_explanations': [], 'elements': {}, 'explanations': {}}
    html = analyzer._generate_html_output(parsed_data, "테스트", "beginner")
    assert html == "테스트"


def test_map_grammatical_role():
    analyzer = KoAnalyzer()
    category = analyzer._map_grammatical_role_to_category("topic_marker")
    assert isinstance(category, str)

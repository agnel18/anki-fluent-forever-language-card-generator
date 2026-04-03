"""Japanese analyzer integration tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.japanese.ja_analyzer import JaAnalyzer


def test_analyzer_integration():
    """Test that all components work together."""
    analyzer = JaAnalyzer()

    # Test that all components are properly initialized
    assert analyzer.ja_config is not None
    assert analyzer.prompt_builder is not None
    assert analyzer.response_parser is not None
    assert analyzer.validator is not None

    # Test that config has required attributes
    assert hasattr(analyzer, 'language_code')
    assert analyzer.language_code == "ja"


def test_config_data_files_loaded():
    """Test that all external data files are loaded."""
    analyzer = JaAnalyzer()
    config = analyzer.ja_config

    assert isinstance(config.grammatical_roles, dict)
    assert isinstance(config.particle_patterns, dict)
    assert isinstance(config.verb_conjugations, dict)
    assert isinstance(config.adjective_patterns, dict)
    assert isinstance(config.honorific_patterns, dict)
    assert isinstance(config.counter_patterns, dict)
    assert isinstance(config.word_meanings, dict)
    assert isinstance(config.patterns, dict)


def test_fallback_produces_valid_result():
    """Test that fallback analysis produces a valid structure."""
    analyzer = JaAnalyzer()
    fallback = analyzer.ja_fallbacks.create_fallback("猫が好きです", "beginner")

    assert isinstance(fallback, dict)
    assert 'word_explanations' in fallback
    assert 'confidence' in fallback
    assert isinstance(fallback['word_explanations'], list)
    assert len(fallback['word_explanations']) > 0


def test_prompt_to_html_pipeline():
    """Test the prompt → parse → validate → HTML pipeline (without AI)."""
    analyzer = JaAnalyzer()

    # Step 1: Build a prompt
    prompt = analyzer.get_grammar_prompt("beginner", "私は猫が好きです", "猫")
    assert isinstance(prompt, str)
    assert len(prompt) > 50

    # Step 2: Simulate a parsed result (as if AI returned it)
    mock_result = {
        'word_explanations': [
            ["私", "pronoun", "#4FC3F7", "I/me"],
            ["は", "topic_particle", "#81C784", "(topic marker)"],
            ["猫", "noun", "#4FC3F7", "cat"],
            ["が", "subject_particle", "#81C784", "(subject marker)"],
            ["好き", "na_adjective", "#FFD54F", "liked"],
            ["です", "copula", "#F48FB1", "is (polite)"],
        ],
        'elements': {},
        'explanations': {},
        'confidence': 0.8
    }

    # Step 3: Validate the result
    validated = analyzer.validator.validate_result(mock_result, "私は猫が好きです")
    assert validated['confidence'] > 0

    # Step 4: Generate HTML
    html = analyzer._generate_html_output(validated, "私は猫が好きです", "beginner")
    assert isinstance(html, str)
    assert "猫" in html
    assert "<span" in html


def test_complexity_levels_consistency():
    """Test that all complexity levels are consistent across components."""
    analyzer = JaAnalyzer()

    for level in ['beginner', 'intermediate', 'advanced']:
        # Color scheme should exist
        colors = analyzer.get_color_scheme(level)
        assert isinstance(colors, dict)

        # Prompt should build
        prompt = analyzer.get_grammar_prompt(level, "テスト", "テスト")
        assert isinstance(prompt, str)

        # Fallback should work
        fallback = analyzer.ja_fallbacks.create_fallback("テスト文です", level)
        assert isinstance(fallback, dict)

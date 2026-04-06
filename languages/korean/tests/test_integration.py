"""Korean analyzer integration tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.korean.ko_analyzer import KoAnalyzer


def test_analyzer_integration():
    """Test that all components work together."""
    analyzer = KoAnalyzer()

    # Test that all components are properly initialized
    assert analyzer.ko_config is not None
    assert analyzer.prompt_builder is not None
    assert analyzer.response_parser is not None
    assert analyzer.validator is not None

    # Test that config has required attributes
    assert hasattr(analyzer, 'language_code')
    assert analyzer.language_code == "ko"


def test_config_data_files_loaded():
    """Test that all external data files are loaded."""
    analyzer = KoAnalyzer()
    config = analyzer.ko_config

    assert isinstance(config.grammatical_roles, dict)
    assert isinstance(config.particle_patterns, dict)
    assert isinstance(config.verb_conjugations, dict)
    assert isinstance(config.honorific_patterns, dict)
    assert isinstance(config.word_meanings, dict)
    assert isinstance(config.patterns, dict)


def test_fallback_produces_valid_result():
    """Test that fallback analysis produces a valid structure."""
    analyzer = KoAnalyzer()
    fallback = analyzer.ko_fallbacks.create_fallback("저는 학생입니다.", "beginner")

    assert isinstance(fallback, dict)
    assert 'word_explanations' in fallback
    assert 'confidence' in fallback
    assert isinstance(fallback['word_explanations'], list)
    assert len(fallback['word_explanations']) > 0


def test_prompt_to_html_pipeline():
    """Test the prompt → parse → validate → HTML pipeline (without AI)."""
    analyzer = KoAnalyzer()

    # Step 1: Build a prompt
    prompt = analyzer.get_grammar_prompt("beginner", "저는 한국어를 배워요.", "한국어")
    assert isinstance(prompt, str)
    assert len(prompt) > 50

    # Step 2: Simulate a parsed result (as if AI returned it)
    mock_result = {
        'word_explanations': [
            ["저", "pronoun", "#FF4444", "I (humble)"],
            ["는", "topic_marker", "#1E90FF", "topic marker"],
            ["한국어", "noun", "#FFAA00", "Korean language"],
            ["를", "object_marker", "#6495ED", "object marker"],
            ["배워요", "verb", "#44FF44", "learn (polite present)"],
        ],
        'elements': {},
        'explanations': {},
        'confidence': 0.8
    }

    # Step 3: Validate the result
    validated = analyzer.validator.validate_result(mock_result, "저는 한국어를 배워요.")
    assert validated['confidence'] > 0

    # Step 4: Generate HTML
    html = analyzer._generate_html_output(validated, "저는 한국어를 배워요.", "beginner")
    assert isinstance(html, str)
    assert "한국어" in html
    assert "<span" in html


def test_complexity_levels_consistency():
    """Test that all complexity levels are consistent across components."""
    analyzer = KoAnalyzer()

    for level in ['beginner', 'intermediate', 'advanced']:
        # Color scheme should exist
        colors = analyzer.get_color_scheme(level)
        assert isinstance(colors, dict)

        # Prompt should build
        prompt = analyzer.get_grammar_prompt(level, "밥을 먹어요.", "밥")
        assert isinstance(prompt, str)
        assert len(prompt) > 0


def test_fallback_tokenization():
    """Test that Korean fallback tokenizer handles spaces and particles."""
    analyzer = KoAnalyzer()
    fallback = analyzer.ko_fallbacks.create_fallback("오늘 날씨가 좋아요.", "beginner")

    words = [exp[0] for exp in fallback['word_explanations']]
    # Should have tokenized the sentence into meaningful units
    assert len(words) >= 2
    # Should have recognized common words
    assert any('오늘' in w for w in words) or any('날씨' in w for w in words)

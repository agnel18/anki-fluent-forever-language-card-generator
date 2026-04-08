"""Malayalam analyzer integration tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.malayalam.ml_analyzer import MlAnalyzer


def test_analyzer_integration():
    """Test that all components work together."""
    analyzer = MlAnalyzer()

    assert analyzer.ml_config is not None
    assert analyzer.prompt_builder is not None
    assert analyzer.response_parser is not None
    assert analyzer.validator is not None

    assert hasattr(analyzer, 'language_code')
    assert analyzer.language_code == "ml"


def test_config_data_files_loaded():
    """Test that all external data files are loaded."""
    analyzer = MlAnalyzer()
    config = analyzer.ml_config

    assert isinstance(config.grammatical_roles, dict)
    assert isinstance(config.case_patterns, dict)
    assert isinstance(config.verb_conjugations, dict)
    assert isinstance(config.postposition_patterns, dict)
    assert isinstance(config.sandhi_rules, dict)
    assert isinstance(config.honorific_patterns, dict)
    assert isinstance(config.word_meanings, dict)
    assert isinstance(config.patterns, dict)


def test_fallback_produces_valid_result():
    """Test that fallback analysis produces a valid structure."""
    analyzer = MlAnalyzer()
    fallback = analyzer.ml_fallbacks.create_fallback("ഞാൻ വെള്ളം കുടിക്കുന്നു", "beginner")

    assert isinstance(fallback, dict)
    assert 'word_explanations' in fallback
    assert 'confidence' in fallback
    assert isinstance(fallback['word_explanations'], list)
    assert len(fallback['word_explanations']) > 0


def test_prompt_to_html_pipeline():
    """Test the prompt → parse → validate → HTML pipeline (without AI)."""
    analyzer = MlAnalyzer()

    # Step 1: Build a prompt
    prompt = analyzer.get_grammar_prompt("beginner", "ഞാൻ വെള്ളം കുടിക്കുന്നു", "കുടിക്കുക")
    assert isinstance(prompt, str)
    assert len(prompt) > 50

    # Step 2: Simulate a parsed result
    mock_result = {
        'word_explanations': [
            ["ഞാൻ", "pronoun", "#4FC3F7", "I (first person singular)"],
            ["വെള്ളം", "noun", "#FFAA00", "water (direct object)"],
            ["കുടിക്കുന്നു", "verb", "#44FF44", "drink (present tense)"],
        ],
        'elements': {},
        'explanations': {},
        'confidence': 0.8
    }

    # Step 3: Validate the result
    validated = analyzer.validator.validate_result(mock_result, "ഞാൻ വെള്ളം കുടിക്കുന്നു")
    assert validated['confidence'] > 0

    # Step 4: Generate HTML
    html = analyzer._generate_html_output(validated, "ഞാൻ വെള്ളം കുടിക്കുന്നു", "beginner")
    assert isinstance(html, str)
    assert "ഞാൻ" in html
    assert "<span" in html


def test_complexity_levels_consistency():
    """Test that all complexity levels are consistent across components."""
    analyzer = MlAnalyzer()

    for level in ['beginner', 'intermediate', 'advanced']:
        colors = analyzer.get_color_scheme(level)
        assert isinstance(colors, dict)

        prompt = analyzer.get_grammar_prompt(level, "ഞാൻ വെള്ളം കുടിക്കുന്നു", "കുടിക്കുക")
        assert isinstance(prompt, str)
        assert len(prompt) > 50


def test_language_config():
    """Test language config properties."""
    analyzer = MlAnalyzer()

    assert analyzer.config.code == "ml"
    assert analyzer.config.name == "Malayalam"
    assert analyzer.config.native_name == "മലയാളം"
    assert analyzer.config.family == "Dravidian"
    assert 'agglutinative_morphology' in analyzer.config.key_features
    assert 'sov_word_order' in analyzer.config.key_features
    assert 'case_system' in analyzer.config.key_features
    assert 'postpositions' in analyzer.config.key_features


def test_fallback_recognizes_pronouns():
    """Test that fallback correctly identifies Malayalam pronouns."""
    analyzer = MlAnalyzer()
    fallback = analyzer.ml_fallbacks.create_fallback("ഞാൻ നിങ്ങൾ അവൻ", "beginner")

    roles = [exp[1] for exp in fallback['word_explanations']]
    assert roles.count('pronoun') >= 2


def test_fallback_recognizes_verb_patterns():
    """Test that fallback correctly identifies Malayalam verb endings."""
    analyzer = MlAnalyzer()
    fallback = analyzer.ml_fallbacks.create_fallback("കുടിക്കുന്നു", "beginner")

    assert len(fallback['word_explanations']) > 0
    assert fallback['word_explanations'][0][1] == 'verb'

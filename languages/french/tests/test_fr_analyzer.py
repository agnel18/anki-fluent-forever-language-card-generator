"""French analyzer tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.french.fr_analyzer import FrAnalyzer


def test_analyzer_creation():
    analyzer = FrAnalyzer()
    assert analyzer is not None
    assert analyzer.language_code == "fr"


def test_analyzer_has_required_methods():
    analyzer = FrAnalyzer()
    required_methods = [
        'analyze_grammar',
        'batch_analyze_grammar',
        'get_sentence_generation_prompt'
    ]

    for method in required_methods:
        assert hasattr(analyzer, method), f"Missing method: {method}"


def test_sentence_generation_prompt():
    analyzer = FrAnalyzer()
    prompt = analyzer.get_sentence_generation_prompt("maison", "fr", 4)
    assert isinstance(prompt, str)
    assert len(prompt) > 100
    assert "maison" in prompt
"""Basic German analyzer tests."""

from ..de_analyzer import DeAnalyzer


def test_analyzer_instantiation():
    analyzer = DeAnalyzer()
    assert analyzer.language_code == "de"


def test_sentence_generation_prompt():
    analyzer = DeAnalyzer()
    prompt = analyzer.get_sentence_generation_prompt("Haus", "German", 2)
    assert isinstance(prompt, str)
    assert "German" in prompt

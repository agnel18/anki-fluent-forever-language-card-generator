"""Basic Hindi analyzer tests."""

from ..hi_analyzer import HiAnalyzer


def test_analyzer_instantiation():
    analyzer = HiAnalyzer()
    assert analyzer.language_code == "hi"


def test_sentence_generation_prompt():
    analyzer = HiAnalyzer()
    prompt = analyzer.get_sentence_generation_prompt("परीक्षण", "Hindi", 2)
    assert isinstance(prompt, str)
    assert "Hindi" in prompt

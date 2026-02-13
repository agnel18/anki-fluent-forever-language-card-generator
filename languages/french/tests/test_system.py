"""French analyzer system tests."""

import pytest
import os
from dotenv import load_dotenv
from languages.french.fr_analyzer import FrAnalyzer

# Load environment variables
load_dotenv()


def test_full_pipeline_integration():
    """Test complete analysis pipeline from input to output."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test complete workflow
    sentence = "Les étudiants lisent attentivement leurs livres intéressants."
    target_word = "lisent"

    result = analyzer.analyze_grammar(sentence, target_word, "intermediate", api_key)

    # Verify complete result structure
    required_keys = ['sentence', 'target_word', 'language_code', 'complexity_level', 'grammatical_elements', 'explanations', 'color_scheme', 'html_output', 'confidence_score', 'word_explanations']
    for key in required_keys:
        assert hasattr(result, key), f"Missing required attribute: {key}"

    # Verify word explanations structure
    word_explanations = result.word_explanations
    assert isinstance(word_explanations, list), "word_explanations should be a list"
    assert len(word_explanations) > 0, "Should have word explanations"

    # Each explanation should be a 4-tuple
    for exp in word_explanations:
        assert len(exp) == 4, f"Word explanation should be 4-tuple: {exp}"
        word, role, color, meaning = exp
        assert isinstance(word, str), f"Word should be string: {word}"
        assert isinstance(role, str), f"Role should be string: {role}"
        assert isinstance(color, str), f"Color should be string: {color}"
        assert isinstance(meaning, str), f"Meaning should be string: {meaning}"


def test_batch_processing_consistency():
    """Test that batch processing produces consistent results."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    sentences = [
        "Le chat dort.",
        "La fille lit un livre.",
        "Nous mangeons du pain.",
        "Ils jouent au football."
    ]

    results = analyzer.batch_analyze_grammar(sentences, "intermediate", "le", api_key)

    # Should return results for all sentences
    assert len(results) == len(sentences), f"Expected {len(sentences)} results, got {len(results)}"

    # Each result should have proper structure
    for i, result in enumerate(results):
        assert hasattr(result, 'word_explanations'), f"Result {i} missing word_explanations"
        assert hasattr(result, 'sentence'), f"Result {i} missing sentence"
        assert result.sentence == sentences[i], f"Result {i} sentence mismatch"


def test_error_handling_system():
    """Test system-level error handling and recovery."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test with various problematic inputs
    test_cases = [
        ("", "intermediate", "test"),  # Empty sentence
        ("   ", "intermediate", "test"),  # Whitespace only
        ("Le chat.", "intermediate", ""),  # Empty target word
        ("Le chat dort.", "invalid_complexity", "chat"),  # Invalid complexity
    ]

    for sentence, complexity, target_word in test_cases:
        # Should not crash, should return some result
        try:
            result = analyzer.analyze_grammar(sentence, target_word, complexity, api_key)
            assert hasattr(result, 'word_explanations'), f"Should handle problematic input gracefully: {sentence}"
        except Exception as e:
            # If it does crash, error should be meaningful
            assert "word_explanations" not in str(e).lower(), f"Error should not mention internal structure: {e}"


def test_configuration_loading():
    """Test that configuration loads properly."""
    analyzer = FrAnalyzer()

    # Should have loaded configuration
    assert hasattr(analyzer, 'hi_config'), "Should have config attribute"
    config = analyzer.hi_config

    # Should have required configuration sections
    assert hasattr(config, 'grammatical_roles'), "Should have grammatical roles"
    assert hasattr(config, 'prompt_templates'), "Should have prompt templates"
    assert hasattr(config, 'patterns'), "Should have patterns"

    # Grammatical roles should be loaded
    assert isinstance(config.grammatical_roles, dict), "Grammatical roles should be dict"
    assert len(config.grammatical_roles) > 0, "Should have grammatical roles loaded"


def test_memory_management():
    """Test that analyzer manages memory properly."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Run multiple analyses
    sentences = [
        "Le chat noir dort paisiblement.",
        "La belle fille danse gracieusement.",
        "Les enfants jouent joyeusement.",
        "Nous lisons attentivement nos livres."
    ]

    # Process each sentence multiple times
    for _ in range(3):
        for sentence in sentences:
            result = analyzer.analyze_grammar(sentence, "le", "intermediate", api_key)
            assert result is not None
            assert hasattr(result, 'word_explanations'), f"Result should have word_explanations: {result}"

    # Should still work after multiple runs (no memory corruption)
    final_result = analyzer.analyze_grammar("Le test final.", "test", "beginner", api_key)
    assert final_result is not None


def test_concurrent_access():
    """Test that analyzer handles concurrent access properly."""
    import threading
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    results = []
    errors = []

    def analyze_sentence(sentence, index):
        try:
            result = analyzer.analyze_grammar(sentence, "le", "intermediate", api_key)
            results.append((index, result))
        except Exception as e:
            errors.append((index, e))

    # Create multiple threads
    threads = []
    sentences = [
        "Le premier chat dort.",
        "La deuxième fille lit.",
        "Le troisième garçon joue.",
        "La quatrième femme chante."
    ]

    for i, sentence in enumerate(sentences):
        thread = threading.Thread(target=analyze_sentence, args=(sentence, i))
        threads.append(thread)

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads
    for thread in threads:
        thread.join()

    # Should have results for all sentences
    assert len(results) == len(sentences), f"Expected {len(sentences)} results, got {len(results)}"
    assert len(errors) == 0, f"Should have no errors: {errors}"

    # Results should be properly structured
    for index, result in results:
        assert hasattr(result, 'word_explanations'), f"Result {index} should have word_explanations"
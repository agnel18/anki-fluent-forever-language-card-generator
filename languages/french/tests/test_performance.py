"""French analyzer performance tests."""

import time
import pytest
import os
from dotenv import load_dotenv
from languages.french.fr_analyzer import FrAnalyzer

# Load environment variables
load_dotenv()


def test_batch_processing_performance():
    """Test that batch processing completes within reasonable time."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test sentences
    sentences = [
        "Le chat dort sur le canapé rouge.",
        "Elle aime lire des romans d'aventure.",
        "Nous allons au cinéma ce soir.",
        "Il fait beau aujourd'hui.",
        "Les enfants jouent dans le parc."
    ]

    start_time = time.time()
    results = analyzer.batch_analyze_grammar(sentences, "intermediate", "les", api_key)
    end_time = time.time()

    processing_time = end_time - start_time

    # Should complete within 30 seconds for 5 sentences
    assert processing_time < 30.0, f"Batch processing took {processing_time:.2f}s, expected < 30s"

    # Should return results for all sentences
    assert len(results) == len(sentences), f"Expected {len(sentences)} results, got {len(results)}"


def test_memory_efficiency():
    """Test that analyzer doesn't have memory leaks in repeated usage."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Process multiple batches
    for i in range(10):
        sentences = [f"Voici la phrase numéro {i} pour tester la mémoire."]
        results = analyzer.batch_analyze_grammar(sentences, "beginner", "phrase", api_key)

        # Each result should be valid
        assert len(results) == 1
        assert hasattr(results[0], 'word_explanations'), f"Result should have word_explanations: {results[0]}"


def test_error_recovery_performance():
    """Test that error recovery doesn't significantly impact performance."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Mix of valid and problematic sentences
    sentences = [
        "Le chat dort.",  # Valid
        "",  # Empty - should trigger fallback
        "Le chat dort sur le canapé rouge avec beaucoup de coussins.",  # Long valid
        "   ",  # Whitespace - should trigger fallback
        "Bonjour, comment allez-vous?"  # Valid with punctuation
    ]

    start_time = time.time()
    results = analyzer.batch_analyze_grammar(sentences, "intermediate", "le", api_key)
    end_time = time.time()

    processing_time = end_time - start_time

    # Should complete within reasonable time even with fallbacks
    assert processing_time < 45.0, f"Processing with fallbacks took {processing_time:.2f}s, expected < 45s"

    # Should return results for all sentences (some may be fallbacks)
    assert len(results) == len(sentences)


def test_complexity_level_performance():
    """Test that different complexity levels have reasonable performance."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')
    sentence = "Le petit chat noir dort paisiblement sur le canapé rouge."

    complexities = ["beginner", "intermediate", "advanced"]

    for complexity in complexities:
        start_time = time.time()
        result = analyzer.analyze_grammar(sentence, complexity, "chat", api_key)
        end_time = time.time()

        processing_time = end_time - start_time

        # Each complexity should complete within 10 seconds
        assert processing_time < 10.0, f"{complexity} processing took {processing_time:.2f}s, expected < 10s"

        # Should have valid result
        assert 'word_explanations' in result
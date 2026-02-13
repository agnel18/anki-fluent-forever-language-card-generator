"""French analyzer gold standard comparison tests."""

import pytest
import os
from dotenv import load_dotenv
from languages.french.fr_analyzer import FrAnalyzer
from languages.hindi.hi_analyzer import HiAnalyzer

# Load environment variables
load_dotenv()


def test_gold_standard_parity():
    """Test that French analyzer matches Hindi gold standard quality."""
    fr_analyzer = FrAnalyzer()
    hi_analyzer = HiAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test sentences with similar grammatical structures
    test_cases = [
        {
            'french': "Le chat noir dort.",
            'hindi': "काला बिल्ली सोता है।",
            'target': "chat",
            'complexity': "beginner"
        },
        {
            'french': "Les étudiants lisent attentivement leurs livres.",
            'hindi': "छात्र ध्यान से अपनी किताबें पढ़ते हैं।",
            'target': "lisent",
            'complexity': "intermediate"
        }
    ]

    for case in test_cases:
        fr_result = fr_analyzer.analyze_grammar(
            case['french'], case['target'], case['complexity'], api_key
        )
        hi_result = hi_analyzer.analyze_grammar(
            case['hindi'], case['target'], case['complexity'], api_key
        )

        # Both should produce valid results
        assert hasattr(fr_result, 'word_explanations'), f"French result should have word_explanations: {fr_result}"
        assert hasattr(hi_result, 'word_explanations'), f"Hindi result should have word_explanations: {hi_result}"

        # Both should have similar structure
        assert len(fr_result.word_explanations) > 0, f"French should have word explanations: {fr_result.word_explanations}"
        assert len(hi_result.word_explanations) > 0, f"Hindi should have word explanations: {hi_result.word_explanations}"

        # Each explanation should be a 4-tuple
        for exp in fr_result.word_explanations:
            assert len(exp) == 4, f"French explanation should be 4-tuple: {exp}"
        for exp in hi_result.word_explanations:
            assert len(exp) == 4, f"Hindi explanation should be 4-tuple: {exp}"


def test_grammatical_coverage_comparison():
    """Compare grammatical coverage between French and Hindi analyzers."""
    fr_analyzer = FrAnalyzer()
    hi_analyzer = HiAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test comprehensive grammatical structures
    test_sentences = {
        'french': [
            "Le garçon mange une pomme.",  # Gender agreement
            "Nous avons mangé hier.",      # Past tense
            "Il faut que tu viennes.",     # Subjunctive
            "C'est le livre que j'ai lu.", # Relative clause
        ],
        'hindi': [
            "लड़का एक सेब खा रहा है।",     # Continuous aspect
            "हमने कल खाया।",             # Past tense
            "तुम्हें आना चाहिए।",          # Modal
            "यह वह किताब है जो मैंने पढ़ी।", # Relative clause
        ]
    }

    for lang, sentences in test_sentences.items():
        analyzer = fr_analyzer if lang == 'french' else hi_analyzer

        for sentence in sentences:
            result = analyzer.analyze_grammar(sentence, "intermediate", "le", api_key)

            # Should provide detailed analysis
            assert hasattr(result, 'word_explanations'), f"Result should have word_explanations: {result}"
            assert len(result.word_explanations) > 0

            # Should have grammatical role information
            roles = [exp[1] for exp in result.word_explanations]
            assert len(roles) > 0, f"Should have grammatical roles for {lang} sentence: {sentence}"


def test_error_recovery_comparison():
    """Test error recovery mechanisms match gold standard."""
    fr_analyzer = FrAnalyzer()
    hi_analyzer = HiAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test with problematic inputs
    problematic_inputs = [
        ("", "intermediate", "test"),           # Empty sentence
        ("Le chat.", "intermediate", ""),       # Empty target
        ("Invalid sentence structure", "intermediate", "invalid"),
    ]

    for sentence, complexity, target in problematic_inputs:
        fr_result = fr_analyzer.analyze_grammar(sentence, complexity, target, api_key)
        hi_result = hi_analyzer.analyze_grammar(sentence, complexity, target, api_key)

        # Both should handle gracefully
        assert hasattr(fr_result, 'word_explanations') or hasattr(fr_result, 'error'), f"French should handle gracefully: {fr_result}"
        assert hasattr(hi_result, 'word_explanations') or hasattr(hi_result, 'error'), f"Hindi should handle gracefully: {hi_result}"


def test_performance_benchmarks():
    """Compare performance benchmarks with gold standard."""
    import time
    fr_analyzer = FrAnalyzer()
    hi_analyzer = HiAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    test_sentence_fr = "Les étudiants français lisent attentivement leurs livres intéressants dans la bibliothèque universitaire."
    test_sentence_hi = "फ्रांसीसी छात्र विश्वविद्यालय पुस्तकालय में अपनी दिलचस्प किताबें ध्यान से पढ़ते हैं।"

    # Benchmark French analyzer
    start_time = time.time()
    for _ in range(10):
        fr_result = fr_analyzer.analyze_grammar(test_sentence_fr, "advanced", "lisent", api_key)
    fr_time = time.time() - start_time

    # Benchmark Hindi analyzer
    start_time = time.time()
    for _ in range(10):
        hi_result = hi_analyzer.analyze_grammar(test_sentence_hi, "advanced", "पढ़ते", api_key)
    hi_time = time.time() - start_time

    # Both should complete within reasonable time (Hindi is gold standard)
    assert fr_time < 30.0, f"French analyzer too slow: {fr_time}s"
    assert hi_time < 30.0, f"Hindi analyzer too slow: {hi_time}s"

    # French should be reasonably close to Hindi performance
    ratio = fr_time / hi_time if hi_time > 0 else 1.0
    assert ratio < 5.0, f"French analyzer significantly slower than gold standard: {ratio}x"


def test_configuration_completeness():
    """Test that French configuration matches Hindi completeness."""
    fr_analyzer = FrAnalyzer()
    hi_analyzer = HiAnalyzer()

    fr_config = fr_analyzer.hi_config
    hi_config = hi_analyzer.hi_config

    # Both should have similar configuration structure
    fr_attrs = [attr for attr in dir(fr_config) if not attr.startswith('_')]
    hi_attrs = [attr for attr in dir(hi_config) if not attr.startswith('_')]

    # French should have at least the core configuration attributes
    core_attrs = ['grammatical_roles', 'prompt_templates', 'patterns']
    for attr in core_attrs:
        assert hasattr(fr_config, attr), f"French config missing {attr}"
        assert hasattr(hi_config, attr), f"Hindi config missing {attr}"

    # Grammatical roles should be comprehensive
    fr_roles = fr_config.grammatical_roles
    hi_roles = hi_config.grammatical_roles

    assert isinstance(fr_roles, dict), "French grammatical roles should be dict"
    assert isinstance(hi_roles, dict), "Hindi grammatical roles should be dict"
    assert len(fr_roles) > 0, "French should have grammatical roles"
    assert len(hi_roles) > 0, "Hindi should have grammatical roles"


def test_batch_processing_efficiency():
    """Test batch processing efficiency compared to gold standard."""
    fr_analyzer = FrAnalyzer()
    hi_analyzer = HiAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test batch processing
    fr_sentences = [
        "Le chat dort.",
        "La fille lit.",
        "Nous mangeons.",
        "Ils jouent."
    ]

    hi_sentences = [
        "बिल्ली सोती है।",
        "लड़की पढ़ती है।",
        "हम खाते हैं।",
        "वे खेलते हैं।"
    ]

    # Both should handle batch processing
    fr_results = fr_analyzer.batch_analyze_grammar(fr_sentences, "intermediate", "le", api_key)
    hi_results = hi_analyzer.batch_analyze_grammar(hi_sentences, "intermediate", "बिल्ली", api_key)

    assert len(fr_results) == len(fr_sentences)
    assert len(hi_results) == len(hi_sentences)

    # All results should be valid
    for result in fr_results + hi_results:
        assert hasattr(result, 'word_explanations'), f"Result should have word_explanations: {result}"
        assert len(result.word_explanations) > 0
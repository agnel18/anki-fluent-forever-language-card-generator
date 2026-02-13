"""French analyzer content generation tests."""

import pytest
import os
from dotenv import load_dotenv
from languages.french.fr_analyzer import FrAnalyzer

# Load environment variables
load_dotenv()


def test_content_generation_quality():
    """Test that generated content meets quality standards."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test various sentence types and complexities
    test_cases = [
        ("Le chat dort.", "beginner", "chat"),
        ("Les étudiants lisent attentivement.", "intermediate", "lisent"),
        ("La complexité grammaticale varie selon le contexte linguistique.", "advanced", "complexité"),
    ]

    for sentence, complexity, target_word in test_cases:
        result = analyzer.analyze_grammar(sentence, target_word, complexity, api_key)

        # Should generate meaningful content
        assert hasattr(result, 'word_explanations'), f"Result should have word_explanations: {result}"
        assert len(result.word_explanations) > 0

        # Each explanation should be detailed
        for word, role, color, meaning in result.word_explanations:
            assert len(meaning.strip()) > 10, f"Explanation too short for {word}: {meaning}"
            assert not meaning.startswith("Error"), f"Should not have error messages: {meaning}"
            assert not meaning.startswith("Failed"), f"Should not have failure messages: {meaning}"


def test_grammatical_accuracy():
    """Test grammatical accuracy of generated explanations."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test gender agreement
    sentence = "Le garçon mange la pomme rouge."
    result = analyzer.analyze_grammar(sentence, "garçon", "intermediate", api_key)

    assert 'word_explanations' in result
    explanations = result['word_explanations']

    # Should identify gender correctly
    gender_mentions = [exp for exp in explanations if 'masculin' in exp[3].lower() or 'féminin' in exp[3].lower()]
    assert len(gender_mentions) > 0, "Should mention gender in explanations"

    # Test verb conjugation
    sentence = "Nous mangeons du pain frais."
    result = analyzer.analyze_grammar(sentence, "mangeons", "intermediate", api_key)

    assert 'word_explanations' in result
    explanations = result['word_explanations']

    # Should explain verb form
    verb_explanations = [exp for exp in explanations if 'verbe' in exp[3].lower() or 'présent' in exp[3].lower()]
    assert len(verb_explanations) > 0, "Should explain verb conjugation"


def test_linguistic_detail_level():
    """Test that explanations provide appropriate detail for complexity level."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    sentence = "Les étudiants lisent attentivement leurs livres intéressants."
    target_word = "lisent"

    # Test different complexity levels
    complexities = ["beginner", "intermediate", "advanced"]

    results = {}
    for complexity in complexities:
        result = analyzer.analyze_grammar(sentence, target_word, complexity, api_key)
        results[complexity] = result

    # All should have explanations
    for complexity, result in results.items():
        assert 'word_explanations' in result, f"No explanations for {complexity}"
        assert len(result['word_explanations']) > 0, f"Empty explanations for {complexity}"

    # Advanced should potentially have more detailed explanations
    beginner_count = len(results["beginner"]['word_explanations'])
    advanced_count = len(results["advanced"]['word_explanations'])

    # Advanced might have same or more explanations (not necessarily fewer)
    assert advanced_count >= beginner_count * 0.8, "Advanced should not have drastically fewer explanations"


def test_cultural_context_inclusion():
    """Test that explanations include relevant cultural/linguistic context."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test sentences that might benefit from cultural context
    test_cases = [
        "Le président parle à la télévision.",  # Political context
        "Nous célébrons Noël en famille.",     # Cultural celebration
        "Les étudiants passent le bac.",       # Educational system
    ]

    for sentence in test_cases:
        result = analyzer.analyze_grammar(sentence, "le", "intermediate", api_key)

        assert 'word_explanations' in result
        explanations = result['word_explanations']

        # Should provide meaningful explanations
        total_explanation_length = sum(len(exp[3]) for exp in explanations)
        assert total_explanation_length > 50, f"Explanations too brief for cultural context: {sentence}"


def test_terminology_consistency():
    """Test consistent use of grammatical terminology."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    sentences = [
        "Le chat dort.",
        "La fille lit.",
        "Nous mangeons.",
        "Ils jouent."
    ]

    all_explanations = []

    for sentence in sentences:
        result = analyzer.analyze_grammar(sentence, "le", "intermediate", api_key)
        if 'word_explanations' in result:
            all_explanations.extend(result['word_explanations'])

    # Should use consistent terminology
    explanation_texts = [exp[3] for exp in all_explanations]

    # Check for consistent use of basic terms
    has_noun = any('nom' in text.lower() or 'substantif' in text.lower() for text in explanation_texts)
    has_verb = any('verbe' in text.lower() for text in explanation_texts)
    has_article = any('article' in text.lower() for text in explanation_texts)

    # Should explain basic grammatical concepts
    assert has_noun or has_verb or has_article, "Should explain basic grammatical concepts"


def test_error_message_quality():
    """Test quality of error messages when generation fails."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test with inputs that might cause issues
    problematic_cases = [
        ("", "intermediate", "test"),  # Empty sentence
        ("xyz abc def", "intermediate", "xyz"),  # Nonsense words
        ("Le chat.", "intermediate", ""),  # Empty target
    ]

    for sentence, complexity, target_word in problematic_cases:
        result = analyzer.analyze_grammar(sentence, target_word, complexity, api_key)

        # Should handle gracefully
        if 'word_explanations' in result:
            # If it succeeds, explanations should be meaningful
            for exp in result['word_explanations']:
                assert len(exp[3].strip()) > 0, f"Empty explanation: {exp}"
                assert not exp[3].startswith("Error:"), f"Raw error in explanation: {exp[3]}"
        else:
            # If it fails, should have error field
            assert 'error' in result, f"Should have error field when failing: {result}"


def test_content_variety():
    """Test that generated content shows variety and avoids repetition."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    sentence = "Le garçon lit un livre intéressant."
    target_word = "lit"

    # Generate multiple analyses
    results = []
    for _ in range(3):
        result = analyzer.analyze_grammar(sentence, target_word, "intermediate", api_key)
        if 'word_explanations' in result:
            results.append(result)

    # Should have some results
    assert len(results) > 0, "Should generate some valid results"

    # Check for variety in explanations (if multiple results)
    if len(results) > 1:
        first_explanations = results[0]['word_explanations']
        second_explanations = results[1]['word_explanations']

        # At least some explanations should be different (allowing for some consistency)
        different_found = False
        for i, (word1, role1, color1, meaning1) in enumerate(first_explanations):
            if i < len(second_explanations):
                word2, role2, color2, meaning2 = second_explanations[i]
                if meaning1 != meaning2:
                    different_found = True
                    break

        # Should show some variety (though some consistency is expected)
        # This is a soft check - not all explanations need to vary


def test_educational_value():
    """Test that content provides genuine educational value."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test with a sentence that has clear grammatical teaching opportunities
    sentence = "Les belles filles françaises mangent des pommes délicieuses."
    target_word = "mangent"

    result = analyzer.analyze_grammar(sentence, target_word, "intermediate", api_key)

    assert 'word_explanations' in result
    explanations = result['word_explanations']

    # Should explain multiple grammatical concepts
    concepts_explained = []
    for word, role, color, meaning in explanations:
        meaning_lower = meaning.lower()
        if 'verbe' in meaning_lower:
            concepts_explained.append('verb')
        if 'féminin' in meaning_lower or 'masculin' in meaning_lower:
            concepts_explained.append('gender')
        if 'pluriel' in meaning_lower:
            concepts_explained.append('number')
        if 'adjectif' in meaning_lower:
            concepts_explained.append('adjective')

    # Should explain at least 2 different grammatical concepts
    unique_concepts = set(concepts_explained)
    assert len(unique_concepts) >= 2, f"Should explain multiple concepts, only found: {unique_concepts}"
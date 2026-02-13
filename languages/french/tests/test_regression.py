"""French analyzer regression tests."""

import pytest
import os
from dotenv import load_dotenv
from languages.french.fr_analyzer import FrAnalyzer

# Load environment variables
load_dotenv()


def test_gender_agreement_regression():
    """Regression test for gender agreement analysis."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test sentence with clear gender agreement
    sentence = "Le chat noir dort sur la chaise rouge."
    result = analyzer.analyze_grammar(sentence, "chat", "intermediate", api_key)

    # Should identify gender agreement patterns
    word_explanations = result.word_explanations

    # Find words with gender information
    gendered_words = [exp for exp in word_explanations if 'masculine' in exp[3] or 'feminine' in exp[3]]

    # Should have at least some gender-marked words
    assert len(gendered_words) > 0, "Should identify gender in French sentence"


def test_verb_conjugation_regression():
    """Regression test for verb conjugation analysis."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test sentence with conjugated verb
    sentence = "Nous mangeons des pommes délicieuses."
    result = analyzer.analyze_grammar(sentence, "mangeons", "intermediate", api_key)

    word_explanations = result.word_explanations

    # Find verb explanations
    verb_explanations = [exp for exp in word_explanations if 'verb' in exp[1] and 'mangeons' in exp[0]]

    # Should have detailed conjugation info
    assert len(verb_explanations) > 0, "Should analyze verb conjugation"

    verb_exp = verb_explanations[0][3]
    # Should mention person, number, or tense
    conjugation_keywords = ['person', 'plural', 'present', '1st person', 'nous']
    has_conjugation_info = any(keyword in verb_exp.lower() for keyword in conjugation_keywords)
    assert has_conjugation_info, f"Verb explanation should include conjugation details: {verb_exp}"


def test_preposition_usage_regression():
    """Regression test for preposition usage analysis."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test sentence with preposition
    sentence = "Le livre est sur la table."
    result = analyzer.analyze_grammar(sentence, "sur", "intermediate", api_key)

    word_explanations = result.word_explanations

    # Find preposition explanation
    prep_explanations = [exp for exp in word_explanations if exp[1] == 'preposition']

    assert len(prep_explanations) > 0, "Should identify preposition"

    prep_exp = prep_explanations[0][3]
    # Should explain preposition function
    assert len(prep_exp) > 10, f"Preposition explanation should be detailed: {prep_exp}"


def test_pronoun_agreement_regression():
    """Regression test for pronoun agreement."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test sentence with pronoun
    sentence = "Il aime sa nouvelle voiture."
    result = analyzer.analyze_grammar(sentence, "sa", "intermediate", api_key)

    word_explanations = result.word_explanations

    # Should identify possessive adjective agreement
    possessive_explanations = [exp for exp in word_explanations if 'possessive' in exp[1] or 'possessive' in exp[3]]

    # Should have some possessive analysis
    assert len(possessive_explanations) > 0, "Should analyze possessive agreement"


def test_article_gender_regression():
    """Regression test for article gender agreement."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test with definite articles
    sentence = "La petite fille lit le livre intéressant."
    result = analyzer.analyze_grammar(sentence, "la", "intermediate", api_key)

    word_explanations = result.word_explanations

    # Should identify definite article
    article_explanations = [exp for exp in word_explanations if 'article' in exp[3] or exp[1] == 'determiner']

    assert len(article_explanations) > 0, "Should identify articles"

    # At least one should mention gender
    gender_mentions = [exp for exp in article_explanations if 'feminine' in exp[3] or 'masculine' in exp[3]]
    assert len(gender_mentions) > 0, "Articles should specify gender agreement"


def test_negation_construction_regression():
    """Regression test for negation constructions."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test ne...pas construction
    sentence = "Je ne comprends pas cette leçon."
    result = analyzer.analyze_grammar(sentence, "ne", "intermediate", api_key)

    word_explanations = result.word_explanations

    # Should identify negation elements
    negation_words = ['ne', 'pas']
    negation_explanations = [exp for exp in word_explanations if exp[0] in negation_words]

    # Should analyze both parts of negation
    assert len(negation_explanations) >= 1, "Should analyze negation construction"


def test_question_formation_regression():
    """Regression test for question formation."""
    analyzer = FrAnalyzer()
    api_key = os.getenv('GEMINI_API_KEY', 'test_key')

    # Test inversion question
    sentence = "Aime-t-il les pommes?"
    result = analyzer.analyze_grammar(sentence, "Aime", "intermediate", api_key)

    word_explanations = result.word_explanations

    # Should identify verb-subject inversion
    verb_explanations = [exp for exp in word_explanations if 'verb' in exp[1]]

    assert len(verb_explanations) > 0, "Should analyze question formation"
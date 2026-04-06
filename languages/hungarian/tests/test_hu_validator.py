"""Hungarian validator tests."""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.hungarian.domain.hu_config import HuConfig
from languages.hungarian.domain.hu_validator import HuValidator


def _make_validator():
    config = HuConfig()
    return HuValidator(config)


def test_validator_creation():
    v = _make_validator()
    assert v is not None


def test_good_result_high_confidence():
    v = _make_validator()
    result = {
        'word_explanations': [
            ['A', 'definite_article', '#87CEEB', 'the (definite article)'],
            ['fiú', 'noun', '#FFAA00', 'boy (nominative)'],
            ['almát', 'accusative', '#4169E1', 'apple with accusative -t suffix'],
            ['eszik', 'verb', '#44FF44', 'eats (3rd person singular, indefinite conjugation, present tense)'],
        ],
        'elements': {
            'definite_article': [{'word': 'A'}],
            'noun': [{'word': 'fiú'}],
            'accusative': [{'word': 'almát'}],
            'verb': [{'word': 'eszik'}],
        },
        'explanations': {}
    }
    validated = v.validate_result(result, "A fiú almát eszik.")
    assert validated['confidence'] >= 0.85


def test_empty_result_zero_confidence():
    v = _make_validator()
    result = {
        'word_explanations': [],
        'elements': {},
        'explanations': {}
    }
    validated = v.validate_result(result, "A fiú almát eszik.")
    assert validated['confidence'] == 0.0


def test_low_coverage_penalty():
    v = _make_validator()
    result = {
        'word_explanations': [
            ['A', 'definite_article', '#87CEEB', 'the'],
        ],
        'elements': {'definite_article': [{'word': 'A'}]},
        'explanations': {}
    }
    validated = v.validate_result(result, "A fiú almát eszik a kertben.")
    assert validated['confidence'] < 0.7


def test_many_other_roles_penalty():
    v = _make_validator()
    result = {
        'word_explanations': [
            ['A', 'other', '#AAAAAA', 'unknown'],
            ['fiú', 'other', '#AAAAAA', 'unknown'],
            ['almát', 'other', '#AAAAAA', 'unknown'],
            ['eszik', 'verb', '#44FF44', 'eats'],
        ],
        'elements': {},
        'explanations': {}
    }
    validated = v.validate_result(result, "A fiú almát eszik.")
    # More than 40% "other" → significant penalty
    assert validated['confidence'] < 0.7


def test_bonus_for_case_markers():
    v = _make_validator()
    result = {
        'word_explanations': [
            ['A', 'definite_article', '#87CEEB', 'the (definite article)'],
            ['házban', 'inessive', '#4682B4', 'in the house (inessive case -ban)'],
            ['lakom', 'verb', '#44FF44', 'I live (1st person singular, indefinite conjugation)'],
        ],
        'elements': {
            'definite_article': [{'word': 'A'}],
            'inessive': [{'word': 'házban'}],
            'verb': [{'word': 'lakom'}],
        },
        'explanations': {}
    }
    validated = v.validate_result(result, "A házban lakom.")
    assert validated['confidence'] >= 0.85


def test_missing_article_penalty():
    v = _make_validator()
    # Sentence has "A" (definite article) but analysis doesn't identify it
    result = {
        'word_explanations': [
            ['A', 'other', '#AAAAAA', 'unknown'],
            ['macska', 'noun', '#FFAA00', 'cat'],
            ['alszik', 'verb', '#44FF44', 'sleeps'],
        ],
        'elements': {},
        'explanations': {}
    }
    validated = v.validate_result(result, "A macska alszik.")
    # Should be penalized for missing article detection
    assert validated['confidence'] < 0.9


def test_explanation_quality_check():
    v = _make_validator()
    result = {
        'word_explanations': [
            ['A', 'definite_article', '#87CEEB', 'the (definite article before consonants)'],
            ['házban', 'inessive', '#4682B4', 'in house — inessive case suffix -ban (back vowel harmony)'],
            ['lakom', 'verb', '#44FF44', 'I live — 1st person singular, indefinite conjugation, present tense'],
        ],
        'elements': {},
        'explanations': {}
    }
    quality = v.validate_explanation_quality(result)
    assert quality['quality_score'] >= 0.9
    assert quality['total_words'] == 3


def test_brief_explanations_penalized():
    v = _make_validator()
    result = {
        'word_explanations': [
            ['A', 'definite_article', '#87CEEB', 'the'],
            ['ház', 'noun', '#FFAA00', 'h'],   # too brief
            ['szép', 'adjective', '#FF44FF', 'nice'],
        ],
        'elements': {},
        'explanations': {}
    }
    quality = v.validate_explanation_quality(result)
    assert quality['quality_score'] < 1.0
    assert len(quality['issues']) > 0


def test_confidence_capped_at_1():
    v = _make_validator()
    result = {
        'word_explanations': [
            ['A', 'definite_article', '#87CEEB', 'the (definite article, used before consonant-initial nouns)'],
            ['nagy', 'adjective', '#FF44FF', 'big/large (attributive adjective before noun)'],
            ['házban', 'inessive', '#4682B4', 'in the house (inessive case suffix -ban, back vowel harmony)'],
            ['lakom', 'verb', '#44FF44', 'I live here (1st person singular, indefinite conjugation, present tense)'],
            ['a', 'definite_article', '#87CEEB', 'the (definite article)'],
            ['barátommal', 'instrumental', '#7B68EE', 'with my friend (instrumental -val assimilated to -mal, possessive 1sg)'],
        ],
        'elements': {
            'definite_article': [{'word': 'A'}, {'word': 'a'}],
            'adjective': [{'word': 'nagy'}],
            'inessive': [{'word': 'házban'}],
            'verb': [{'word': 'lakom'}],
            'instrumental': [{'word': 'barátommal'}],
        },
        'explanations': {}
    }
    validated = v.validate_result(result, "A nagy házban lakom a barátommal.")
    assert validated['confidence'] <= 1.0

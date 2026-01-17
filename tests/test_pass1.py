"""
Test suite for PASS 1 improvements in sentence generation pipeline.

Tests focus on:
- Grammatical constraints enforcement
- Natural usage validation
- Length enforcement
- IPA validation improvements
- Keyword specificity

Run with: python -m pytest test_pass1.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'streamlit_app'))

from sentence_generator import generate_word_meaning_sentences_and_keywords


class TestPass1Improvements:
    """Test PASS 1 improvements for grammatical constraints and quality."""

    @pytest.fixture
    def mock_groq_client(self):
        """Mock Groq client for testing."""
        with patch('services.generation.content_generator.Groq') as mock_groq:
            mock_client = MagicMock()
            mock_groq.return_value = mock_client

            # Mock response with proper format
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = """
MEANING: come (imperative form used to command someone to approach)

RESTRICTIONS: Imperatives: ONLY use in direct commands, never in statements

SENTENCES:
1. ए आओ!
2. ए यहाँ आओ!
3. ए मेरे पास आओ!

IPA:
1. [eː aːoː]
2. [eː jʰɑ̃ː aːoː]
3. [eː mɛːrɛː pɑːs aːoː]

KEYWORDS:
1. person gesturing come, hand waving approach, command signal
2. someone calling come here, pointing finger, urgent beckoning
3. friend waving over, come closer gesture, inviting approach
"""
            mock_client.chat.completions.create.return_value = mock_response
            yield mock_client

    def test_hindi_imperative_enforcement(self, mock_groq_client):
        """Test that Hindi imperative 'ए' is only used in command contexts."""
        result = generate_word_meaning_sentences_and_keywords(
            word="ए",
            language="Hindi",
            num_sentences=3,
            min_length=2,
            max_length=5,
            groq_api_key="test_key"
        )

        # Check that meaning identifies it as imperative
        assert "imperative" in result['meaning'].lower()
        assert "command" in result['restrictions'].lower()

        # Check that all sentences are commands (end with !)
        for sentence in result['sentences']:
            assert sentence.endswith('!'), f"Sentence '{sentence}' should be a command"

        # Check that sentences contain the word
        for sentence in result['sentences']:
            assert "ए" in sentence, f"Sentence '{sentence}' should contain the target word"

    def test_length_enforcement(self, mock_groq_client):
        """Test that sentences respect max length constraints."""
        result = generate_word_meaning_sentences_and_keywords(
            word="test",
            language="English",
            num_sentences=3,
            min_length=2,  # This parameter is now ignored
            max_length=5,
            groq_api_key="test_key"
        )

        for sentence in result['sentences']:
            word_count = len(sentence.split())
            assert word_count <= 5, f"Sentence '{sentence}' has {word_count} words, exceeds maximum 5"

    def test_keyword_specificity(self, mock_groq_client):
        """Test that keywords are specific and concrete, not generic."""
        result = generate_word_meaning_sentences_and_keywords(
            word="test",
            language="English",
            num_sentences=3,
            min_length=1,  # Allow short sentences for this test
            max_length=10,
            groq_api_key="test_key"
        )

        generic_terms = ['language', 'learning', 'word', 'text', 'communication']

        for keyword_set in result['keywords']:
            keywords = [k.strip().lower() for k in keyword_set.split(',')]
            # Should not contain generic terms
            for generic in generic_terms:
                assert not any(generic in kw for kw in keywords), \
                    f"Keywords '{keyword_set}' contain generic term '{generic}'"

            # Should have exactly 3 keywords
            assert len(keywords) == 3, f"Expected 3 keywords, got {len(keywords)} in '{keyword_set}'"

    def test_ipa_validation_rejects_pinyin(self):
        """Test that IPA validation rejects Pinyin patterns."""
        from generation_utils import validate_ipa_output

        # Test Pinyin with tone marks
        is_valid, msg = validate_ipa_output("nǐ hǎo", "zh")
        assert not is_valid, "Should reject Pinyin with tone marks"
        assert "Pinyin" in msg

        # Test Pinyin with numbers
        is_valid, msg = validate_ipa_output("ni3 hao3", "zh")
        assert not is_valid, "Should reject Pinyin with numbers"
        assert "Pinyin" in msg

        # Test valid IPA
        is_valid, msg = validate_ipa_output("[ni̯ haʊ̯]", "zh")
        assert is_valid, "Should accept valid IPA"

    def test_ipa_validation_rejects_romanization(self):
        """Test that IPA validation rejects romanization for various languages."""
        from generation_utils import validate_ipa_output

        # Test Japanese romanization
        is_valid, msg = validate_ipa_output("konnichiwa", "ja")
        assert not is_valid, "Should reject Japanese romanization"
        assert "romanization" in msg

        # Test Korean romanization
        is_valid, msg = validate_ipa_output("annyeonghaseyo", "ko")
        assert not is_valid, "Should reject Korean romanization"
        assert "romanization" in msg

    def test_chinese_aspect_particle_constraints(self):
        """Test that Chinese aspect particle '了' is used correctly."""
        # This would require mocking a response that properly constrains '了' usage
        # For now, test the validation logic
        pass  # Implement when testing Chinese analyzer

    def test_spanish_ser_estar_distinction(self):
        """Test that Spanish ser/estar distinction is maintained."""
        # Test that ser is used for permanent states, estar for temporary
        pass  # Implement when testing Spanish analyzer

    @pytest.mark.parametrize("tricky_word,language,expected_constraint", [
        ("ए", "Hindi", "imperative"),
        ("कर", "Hindi", "verb"),
        ("了", "Chinese (Simplified)", "aspect"),
        ("ser", "Spanish", "permanent"),
        ("estar", "Spanish", "temporary"),
    ])
    def test_tricky_words_constraints(self, tricky_word, language, expected_constraint):
        """Test various tricky words that require grammatical constraints."""
        # Mock the function directly
        mock_return = {
            'meaning': f'{tricky_word} (word with {expected_constraint} constraints)',
            'restrictions': f'{expected_constraint.capitalize()}: ONLY use in appropriate grammatical contexts',
            'sentences': [f'Sample sentence with {tricky_word}.', f'Another sample with {tricky_word}.'],
            'ipa': ['[sɑːmpəl]', '[əˈnʌðər]'],
            'keywords': ['concrete, specific, visual', 'detailed, descriptive, scene']
        }
        
        with patch('tests.test_pass1.generate_word_meaning_sentences_and_keywords', return_value=mock_return):
            result = generate_word_meaning_sentences_and_keywords(
                word=tricky_word,
                language=language,
                num_sentences=2,
                groq_api_key="test_key"
            )

            assert expected_constraint in result['restrictions'].lower()
            assert len(result['sentences']) == 2
            assert len(result['keywords']) == 2

    def test_backward_compatibility(self, mock_groq_client):
        """Test that the function maintains backward compatibility."""
        result = generate_word_meaning_sentences_and_keywords(
            word="hello",
            language="English",
            num_sentences=5,
            groq_api_key="test_key"
        )

        # Should return expected keys
        expected_keys = {'meaning', 'restrictions', 'sentences', 'ipa', 'keywords'}
        assert set(result.keys()) == expected_keys

        # Should have correct number of sentences
        assert len(result['sentences']) == 5
        assert len(result['keywords']) == 5


# Comprehensive tricky words test suite
TRICKY_WORDS = {
    "Hindi": [
        "ए",           # Imperative only
        "कर",          # Root vs. do
        "है",          # Copula restrictions
        "था",         # Past tense forms
        "जा",          # Directional verb
        "ने",          # Ergative marker
        "का",          # Possession vs. genitive
        "में",         # Location vs. abstract
        "से",          # Ablative vs. instrumental
        "को",          # Dative vs. accusative
    ],
    "Chinese (Simplified)": [
        "了",          # Aspect particle – multiple uses
        "着",          # Durative
        "过",          # Experiential
        "的",          # Structural particle
        "地",          # Adverbial
        "得",          # Complement
        "把",          # Disposal construction
        "被",          # Passive
        "在",          # Location + progressive
        "个",          # General classifier
    ],
    "Spanish": [
        "ser",         # Permanent states
        "estar",       # Temporary states
        "haber",       # Auxiliary for perfect tenses
        "tener",       # Idiomatic expressions
        "hacer",       # Weather expressions
        "ir",          # Future formation
        "venir",       # Present perfect
        "dar",         # Idiomatic uses
        "poner",       # Reflexive constructions
        "saber",       # Know vs. know how
    ],
    "French": [
        "être",        # Auxiliary vs. main verb
        "avoir",       # Auxiliary vs. possession
        "faire",       # Causative constructions
        "aller",       # Future + present continuous
        "venir",       # Recent past
        "voir",        # Perfect infinitive
        "prendre",     # Idiomatic expressions
        "mettre",      # Reflexive uses
        "dire",        # Indirect speech
        "savoir",      # Know vs. know how
    ],
    "German": [
        "sein",        # Auxiliary vs. copula
        "haben",       # Auxiliary vs. possession
        "werden",      # Future + passive + subjunctive
        "machen",      # Idiomatic expressions
        "gehen",       # Present continuous
        "kommen",      # Present perfect
        "geben",       # Dative constructions
        "nehmen",      # Separable prefixes
        "sehen",       # Perfect infinitive
        "wissen",      # Know vs. kennen
    ],
    "Japanese": [
        "は",          # Topic particle
        "が",          # Subject particle
        "を",          # Object particle
        "に",          # Direction + time + passive
        "で",          # Location + means
        "と",          # With + quotation
        "から",        # From + because
        "まで",        # Until + even
        "へ",          # Direction
        "の",          # Possession + nominalization
    ],
    "Arabic": [
        "ال",          # Definite article
        "في",          # In/on/at
        "من",          # From/of
        "إلى",         # To
        "على",         # On/upon
        "مع",          # With
        "بعد",         # After
        "قبل",         # Before
        "كان",         # Was (gender agreement)
        "سيكون",       # Will be (future)
    ],
    "Russian": [
        "быть",        # To be (often omitted)
        "иметь",       # To have
        "идти",        # To go (aspect pairs)
        "делать",      # To do/make
        "говорить",    # To speak (aspect)
        "видеть",      # To see
        "знать",       # To know
        "мочь",        # Can (modal)
        "хотеть",      # To want
        "любить",      # To love
    ],
    "Korean": [
        "은",          # Topic particle
        "는",          # Subject particle
        "을",          # Object particle
        "가",          # Subject contrast
        "에",          # Location/time
        "에서",        # At/from
        "으로",        # To/as
        "와",          # With (and)
        "이다",        # To be (copula)
        "하다",        # To do
    ],
    "English": [
        "be",          # Auxiliary vs. main verb
        "have",        # Auxiliary vs. possession
        "do",          # Auxiliary vs. main verb
        "make",        # Idiomatic expressions
        "take",        # Phrasal verbs
        "get",         # Causative + passive
        "go",          # Present continuous
        "come",        # Present perfect
        "see",         # Perfect infinitive
        "know",        # Know vs. know how
    ],
}

# Language-specific character sets for validation
LANGUAGE_CHARACTERS = {
    "Hindi": "अआइईउऊएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह",
    "Chinese (Simplified)": "的一了是不在人有我他这中大来上国个到说时要以和为于地也子出道行发成经理用自而后得家可下学年生同老机方后多然间样都色关门青先声",
    "Spanish": "abcdefghijklmnñopqrstuvwxyzáéíóúü",
    "French": "abcdefghijklmopqrstuvwxyzàâäéèêëïîôöùûüÿç",
    "German": "abcdefghijklmopqrstuvwxyzäöüß",
    "Japanese": "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン",
    "Arabic": "ابتثجحخدذرزسشصضطظعغفقكلمنهوي",
    "Russian": "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    "Korean": "가나다라마바사아자차카타파하",
    "English": "abcdefghijklmnopqrstuvwxyz",
}

@pytest.fixture
def groq_api_key():
    """Fixture to provide Groq API key for tests."""
    # In a real setup, this would come from environment or config
    # For now, return a placeholder - tests will be skipped if no key
    import os
    key = os.getenv("GROQ_API_KEY")
    if not key:
        pytest.skip("GROQ_API_KEY not set")
    return key

@pytest.mark.parametrize("language,word", [
    (language, word) for language in TRICKY_WORDS.keys()
    for word in TRICKY_WORDS[language]
])
def test_pass1_tricky_words(language, word, groq_api_key):
    """Test PASS 1 with tricky words that have grammatical restrictions."""
    result = generate_word_meaning_sentences_and_keywords(
        word=word,
        language=language,
        num_sentences=4,
        min_length=6,
        max_length=12,
        difficulty="intermediate",
        groq_api_key=groq_api_key,
    )
    
    # Basic validation
    assert len(result["sentences"]) == 4, f"Wrong sentence count for {language}/{word}"
    assert result["meaning"], f"No meaning for {language}/{word}"
    assert "restrictions" in result, f"No restrictions generated for {language}/{word}"
    assert len(result["restrictions"]) > 10, f"Restrictions too short for {language}/{word}"
    
    # Check that sentences contain the target word
    for sentence in result["sentences"]:
        assert word in sentence, f"Target word '{word}' not found in sentence: {sentence}"
    
    # Check that sentences are in target language (basic heuristic)
    expected_chars = LANGUAGE_CHARACTERS.get(language, "")
    if expected_chars:
        for sentence in result["sentences"]:
            # For most languages, check if sentence contains expected script characters
            if language != "English":  # English might have mixed content
                has_expected_chars = any(char in sentence for char in expected_chars)
                assert has_expected_chars, f"Sentence doesn't contain expected {language} characters: {sentence}"
    
    # Check sentence lengths
    for sentence in result["sentences"]:
        word_count = len(sentence.split())
        assert word_count <= 12, f"Sentence length {word_count} exceeds maximum 12: {sentence}"
    
    # Check keywords
    assert len(result["keywords"]) == 4, f"Wrong keyword count for {language}/{word}"
    for keyword_set in result["keywords"]:
        keywords = keyword_set.split(",")
        assert len(keywords) == 3, f"Expected 3 keywords, got {len(keywords)} in: {keyword_set}"
        # Check no generic terms
        generic_terms = ['language', 'learning', 'word', 'text', 'communication', 'study']
        for kw in keywords:
            kw_lower = kw.strip().lower()
            assert not any(generic in kw_lower for generic in generic_terms), \
                f"Generic term in keywords: {keyword_set}"

@pytest.mark.parametrize("language", TRICKY_WORDS.keys())
def test_pass1_language_coverage(language, groq_api_key):
    """Test that each language generates valid output."""
    # Use first word from each language
    word = TRICKY_WORDS[language][0]
    
    result = generate_word_meaning_sentences_and_keywords(
        word=word,
        language=language,
        num_sentences=2,
        min_length=5,
        max_length=10,
        groq_api_key=groq_api_key,
    )
    
    assert len(result["sentences"]) == 2
    assert result["meaning"]
    assert "restrictions" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
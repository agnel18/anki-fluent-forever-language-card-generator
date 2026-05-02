# languages/latvian/tests/conftest.py
"""
Pytest fixtures for Latvian analyzer tests.
"""
import pytest
from unittest.mock import MagicMock, patch

from languages.latvian.domain.lv_config import LvConfig
from languages.latvian.domain.lv_fallbacks import LvFallbacks
from languages.latvian.domain.lv_prompt_builder import LvPromptBuilder
from languages.latvian.domain.lv_response_parser import LvResponseParser
from languages.latvian.domain.lv_validator import LvValidator


@pytest.fixture
def config():
    return LvConfig()


@pytest.fixture
def fallbacks(config):
    return LvFallbacks(config)


@pytest.fixture
def prompt_builder(config):
    return LvPromptBuilder(config)


@pytest.fixture
def response_parser(config, fallbacks):
    return LvResponseParser(config, fallbacks)


@pytest.fixture
def validator(config):
    return LvValidator(config)


# ---------------------------------------------------------------------------
# Sample AI responses
# ---------------------------------------------------------------------------

SAMPLE_BEGINNER_RESPONSE = """{
  "sentence": "Es runāju latviski.",
  "overall_structure": "Subject-Verb-Adverb",
  "sentence_structure": "Subject-Verb-Adverb",
  "word_explanations": [
    {"word": "Es", "role": "personal_pronoun", "color": "#9370DB",
     "meaning": "I (1st person singular)", "case": "nominative", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
    {"word": "runāju", "role": "verb", "color": "#4ECDC4",
     "meaning": "speak/spoke (1sg present/past of runāt)", "case": "", "gender": "", "number": "singular", "tense": "present", "definite_form": ""},
    {"word": "latviski.", "role": "adverb", "color": "#FF6347",
     "meaning": "in Latvian (manner adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""}
  ],
  "grammar_notes": "Simple SVO sentence. runāju is the 1st person singular present/past form.",
  "confidence": 0.92
}"""

SAMPLE_INTERMEDIATE_RESPONSE = """{
  "sentence": "Man jāmācās latviešu valoda.",
  "overall_structure": "Debitive construction — beneficiary-Debitive-Object",
  "sentence_structure": "Debitive construction",
  "word_explanations": [
    {"word": "Man", "role": "personal_pronoun", "color": "#9370DB",
     "meaning": "to me / for me (dative of es)", "case": "dative", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
    {"word": "jāmācās", "role": "debitive", "color": "#FF1493",
     "meaning": "must learn/study (debitive of mācīties)", "case": "", "gender": "", "number": "", "tense": "present", "definite_form": ""},
    {"word": "latviešu", "role": "noun", "color": "#FFAA00",
     "meaning": "Latvian — genitive plural (of Latvians)", "case": "genitive", "gender": "masculine", "number": "plural", "tense": "", "definite_form": ""},
    {"word": "valoda.", "role": "noun", "color": "#FFAA00",
     "meaning": "language (nom sg fem)", "case": "nominative", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""}
  ],
  "grammar_notes": "Debitive construction: Man jā- expresses obligation.",
  "confidence": 0.90
}"""

SAMPLE_ADVANCED_RESPONSE = """{
  "sentence": "Uzrakstītā vēstule tika nosūtīta vakar.",
  "overall_structure": "Definite past-passive-participle noun — passive auxiliary — past-passive-participle — adverb",
  "sentence_structure": "Passive sentence with past passive participles",
  "word_explanations": [
    {"word": "Uzrakstītā", "role": "participle", "color": "#FF8C00",
     "meaning": "the written (past passive participle, definite, feminine nominative)", "case": "nominative", "gender": "feminine", "number": "singular", "tense": "", "definite_form": "true"},
    {"word": "vēstule", "role": "noun", "color": "#FFAA00",
     "meaning": "letter (nom sg fem)", "case": "nominative", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""},
    {"word": "tika", "role": "auxiliary", "color": "#00CED1",
     "meaning": "was (past passive auxiliary of tikt)", "case": "", "gender": "", "number": "singular", "tense": "past", "definite_form": ""},
    {"word": "nosūtīta", "role": "participle", "color": "#FF8C00",
     "meaning": "sent (past passive participle, feminine)", "case": "", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""},
    {"word": "vakar.", "role": "adverb", "color": "#FF6347",
     "meaning": "yesterday (time adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""}
  ],
  "grammar_notes": "Passive construction with tika + past passive participle. Uzrakstītā is a definite adjective form.",
  "confidence": 0.88
}"""

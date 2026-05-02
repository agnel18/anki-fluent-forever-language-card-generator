# languages/portuguese/tests/conftest.py
"""
Pytest configuration and shared fixtures for Portuguese analyzer tests.

Path setup: ensures project root is on sys.path so that imports like
    from languages.portuguese.pt_analyzer import PtAnalyzer
work regardless of where pytest is invoked from.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# sys.path setup — project root must be importable
# ---------------------------------------------------------------------------
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Domain component imports
# ---------------------------------------------------------------------------
from languages.portuguese.domain.pt_config import PtConfig
from languages.portuguese.domain.pt_fallbacks import PtFallbacks
from languages.portuguese.domain.pt_prompt_builder import PtPromptBuilder
from languages.portuguese.domain.pt_response_parser import PtResponseParser
from languages.portuguese.domain.pt_validator import PtValidator


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def config():
    return PtConfig()


@pytest.fixture
def fallbacks(config):
    return PtFallbacks(config)


@pytest.fixture
def prompt_builder(config):
    return PtPromptBuilder(config)


@pytest.fixture
def response_parser(config, fallbacks):
    return PtResponseParser(config, fallbacks)


@pytest.fixture
def validator(config):
    return PtValidator(config)


# ---------------------------------------------------------------------------
# Canned AI responses (re-used across test modules)
# ---------------------------------------------------------------------------

SAMPLE_BEGINNER_RESPONSE = """{
  "sentence": "O gato bebe leite.",
  "register": "neutral",
  "overall_structure": "SVO declarative",
  "sentence_structure": "SVO declarative",
  "word_explanations": [
    {
      "word": "O",
      "grammatical_role": "article",
      "color": "#AA44FF",
      "meaning": "the (definite article, masculine singular)",
      "gender": "masculine",
      "number": "singular",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "gato",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "meaning": "cat (masculine noun)",
      "gender": "masculine",
      "number": "singular",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "bebe",
      "grammatical_role": "verb",
      "color": "#44FF44",
      "meaning": "drinks (3rd person singular present of beber)",
      "gender": "",
      "number": "singular",
      "person": "3",
      "tense": "present",
      "mood": "indicative",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "leite",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "meaning": "milk (masculine noun)",
      "gender": "masculine",
      "number": "singular",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": ".",
      "grammatical_role": "other",
      "color": "#AAAAAA",
      "meaning": "sentence-final punctuation",
      "gender": "",
      "number": "",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    }
  ],
  "grammar_notes": "Simple SVO present-tense sentence. 'O' is the masculine singular definite article.",
  "confidence": 0.92
}"""

SAMPLE_INTERMEDIATE_RESPONSE = """{
  "sentence": "Ela vai ao mercado comprar pão.",
  "register": "neutral",
  "overall_structure": "SVO with contraction 'ao' and infinitive complement",
  "sentence_structure": "SVO with contraction and purpose infinitive",
  "word_explanations": [
    {
      "word": "Ela",
      "grammatical_role": "personal_pronoun",
      "color": "#FF4444",
      "meaning": "she (3rd person singular feminine pronoun)",
      "gender": "feminine",
      "number": "singular",
      "person": "3",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "vai",
      "grammatical_role": "auxiliary_verb",
      "color": "#228B22",
      "meaning": "goes/is going (3sg present of ir — periphrastic future aux)",
      "gender": "",
      "number": "singular",
      "person": "3",
      "tense": "present",
      "mood": "indicative",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "ao",
      "grammatical_role": "contraction",
      "color": "#FF7F50",
      "meaning": "to the (contraction: a + o)",
      "gender": "",
      "number": "",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": ["a", "o"]
    },
    {
      "word": "mercado",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "meaning": "market (masculine noun)",
      "gender": "masculine",
      "number": "singular",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "comprar",
      "grammatical_role": "verb",
      "color": "#44FF44",
      "meaning": "to buy (infinitive)",
      "gender": "",
      "number": "",
      "person": "",
      "tense": "",
      "mood": "indicative",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "pão",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "meaning": "bread (masculine noun)",
      "gender": "masculine",
      "number": "singular",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": ".",
      "grammatical_role": "other",
      "color": "#AAAAAA",
      "meaning": "punctuation",
      "gender": "",
      "number": "",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    }
  ],
  "grammar_notes": "'ao' is an obligatory contraction of 'a + o'. 'vai' is a periphrastic future auxiliary.",
  "confidence": 0.91
}"""

SAMPLE_ADVANCED_RESPONSE = """{
  "sentence": "Disse-me a verdade que precisava de saber.",
  "register": "PT",
  "overall_structure": "Enclitic clitic with relative clause",
  "sentence_structure": "SVO with enclitic pronoun and relative clause",
  "word_explanations": [
    {
      "word": "Disse",
      "grammatical_role": "verb",
      "color": "#44FF44",
      "meaning": "said (3sg preterite of dizer)",
      "gender": "",
      "number": "singular",
      "person": "3",
      "tense": "preterite",
      "mood": "indicative",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "me",
      "grammatical_role": "clitic_pronoun",
      "color": "#E91E63",
      "meaning": "me (1sg indirect object clitic — enclitic after verb)",
      "gender": "",
      "number": "singular",
      "person": "1",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "enclitic",
      "contraction_parts": []
    },
    {
      "word": "a",
      "grammatical_role": "definite_article",
      "color": "#AA44FF",
      "meaning": "the (feminine singular definite article)",
      "gender": "feminine",
      "number": "singular",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "verdade",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "meaning": "truth (feminine noun)",
      "gender": "feminine",
      "number": "singular",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "que",
      "grammatical_role": "relative_pronoun",
      "color": "#FF4500",
      "meaning": "that/which (relative pronoun introducing relative clause)",
      "gender": "",
      "number": "",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "precisava",
      "grammatical_role": "verb",
      "color": "#44FF44",
      "meaning": "needed (1sg imperfect of precisar)",
      "gender": "",
      "number": "singular",
      "person": "1",
      "tense": "imperfect",
      "mood": "indicative",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "de",
      "grammatical_role": "preposition",
      "color": "#4444FF",
      "meaning": "of/to (preposition in 'precisar de')",
      "gender": "",
      "number": "",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "saber",
      "grammatical_role": "verb",
      "color": "#44FF44",
      "meaning": "to know (infinitive)",
      "gender": "",
      "number": "",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": ".",
      "grammatical_role": "other",
      "color": "#AAAAAA",
      "meaning": "punctuation",
      "gender": "",
      "number": "",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    }
  ],
  "grammar_notes": "Enclitic clitic 'me' attaches to 'Disse' after the verb (PT standard). Relative clause introduced by 'que'.",
  "confidence": 0.90
}"""

# Second advanced sentence (CLAUDE.md requires 2 for E2E coverage)
SAMPLE_ADVANCED_RESPONSE_2 = """{
  "sentence": "Não me disse a verdade.",
  "register": "neutral",
  "overall_structure": "Negative sentence with proclitic clitic",
  "sentence_structure": "Negation — proclitic clitic placement",
  "word_explanations": [
    {
      "word": "Não",
      "grammatical_role": "particle",
      "color": "#A1887F",
      "meaning": "not (negation particle — triggers proclisis)",
      "gender": "",
      "number": "",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "me",
      "grammatical_role": "clitic_pronoun",
      "color": "#E91E63",
      "meaning": "me (1sg indirect object clitic — proclitic after 'não')",
      "gender": "",
      "number": "singular",
      "person": "1",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "proclitic",
      "contraction_parts": []
    },
    {
      "word": "disse",
      "grammatical_role": "verb",
      "color": "#44FF44",
      "meaning": "said (3sg preterite of dizer)",
      "gender": "",
      "number": "singular",
      "person": "3",
      "tense": "preterite",
      "mood": "indicative",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "a",
      "grammatical_role": "definite_article",
      "color": "#AA44FF",
      "meaning": "the (feminine singular definite article)",
      "gender": "feminine",
      "number": "singular",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "verdade",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "meaning": "truth (feminine noun)",
      "gender": "feminine",
      "number": "singular",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": ".",
      "grammatical_role": "other",
      "color": "#AAAAAA",
      "meaning": "punctuation",
      "gender": "",
      "number": "",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    }
  ],
  "grammar_notes": "Negation 'Não' triggers proclisis — clitic 'me' precedes the verb.",
  "confidence": 0.91
}"""

# Copula responses — ser vs estar
SAMPLE_SER_RESPONSE = """{
  "sentence": "Ela é triste.",
  "register": "neutral",
  "overall_structure": "SVC with ser copula (inherent quality)",
  "sentence_structure": "Subject — copula(ser) — predicate adjective",
  "word_explanations": [
    {
      "word": "Ela",
      "grammatical_role": "personal_pronoun",
      "color": "#FF4444",
      "meaning": "she",
      "gender": "feminine",
      "number": "singular",
      "person": "3",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "é",
      "grammatical_role": "copula",
      "color": "#00B894",
      "meaning": "is (ser — inherent/identity copula: she is inherently sad)",
      "gender": "",
      "number": "singular",
      "person": "3",
      "tense": "present",
      "mood": "indicative",
      "copula_type": "ser",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "triste",
      "grammatical_role": "adjective",
      "color": "#FF44FF",
      "meaning": "sad (adjective)",
      "gender": "",
      "number": "singular",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": ".",
      "grammatical_role": "other",
      "color": "#AAAAAA",
      "meaning": "punctuation",
      "gender": "",
      "number": "",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    }
  ],
  "grammar_notes": "SER indicates inherent quality. 'É triste' = she is (characteristically) sad.",
  "confidence": 0.93
}"""

SAMPLE_ESTAR_RESPONSE = """{
  "sentence": "Ela está triste.",
  "register": "neutral",
  "overall_structure": "SVC with estar copula (transient state)",
  "sentence_structure": "Subject — copula(estar) — predicate adjective",
  "word_explanations": [
    {
      "word": "Ela",
      "grammatical_role": "personal_pronoun",
      "color": "#FF4444",
      "meaning": "she",
      "gender": "feminine",
      "number": "singular",
      "person": "3",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "está",
      "grammatical_role": "copula",
      "color": "#00B894",
      "meaning": "is (estar — transient state copula: she is sad right now)",
      "gender": "",
      "number": "singular",
      "person": "3",
      "tense": "present",
      "mood": "indicative",
      "copula_type": "estar",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "triste",
      "grammatical_role": "adjective",
      "color": "#FF44FF",
      "meaning": "sad (adjective)",
      "gender": "",
      "number": "singular",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": ".",
      "grammatical_role": "other",
      "color": "#AAAAAA",
      "meaning": "punctuation",
      "gender": "",
      "number": "",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    }
  ],
  "grammar_notes": "ESTAR indicates transient state. 'Está triste' = she is (currently/temporarily) sad.",
  "confidence": 0.93
}"""

# Contraction response
SAMPLE_CONTRACTION_RESPONSE = """{
  "sentence": "Eu vou ao mercado.",
  "register": "neutral",
  "overall_structure": "SVO with obligatory contraction 'ao'",
  "sentence_structure": "Subject — auxiliary verb — contraction — noun",
  "word_explanations": [
    {
      "word": "Eu",
      "grammatical_role": "personal_pronoun",
      "color": "#FF4444",
      "meaning": "I (1st person singular)",
      "gender": "",
      "number": "singular",
      "person": "1",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "vou",
      "grammatical_role": "auxiliary_verb",
      "color": "#228B22",
      "meaning": "go/am going (1sg present of ir)",
      "gender": "",
      "number": "singular",
      "person": "1",
      "tense": "present",
      "mood": "indicative",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": "ao",
      "grammatical_role": "contraction",
      "color": "#FF7F50",
      "meaning": "to the (obligatory contraction: a + o)",
      "gender": "",
      "number": "",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": ["a", "o"]
    },
    {
      "word": "mercado",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "meaning": "market (masculine noun)",
      "gender": "masculine",
      "number": "singular",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    },
    {
      "word": ".",
      "grammatical_role": "other",
      "color": "#AAAAAA",
      "meaning": "punctuation",
      "gender": "",
      "number": "",
      "person": "",
      "tense": "",
      "mood": "",
      "copula_type": "",
      "clitic_position": "",
      "contraction_parts": []
    }
  ],
  "grammar_notes": "'ao' is an obligatory contraction of preposition 'a' + definite article 'o'.",
  "confidence": 0.92
}"""

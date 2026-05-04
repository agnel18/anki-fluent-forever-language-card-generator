# languages/russian/tests/conftest.py
"""
Pytest fixtures for Russian analyzer tests.
"""
import pytest
from unittest.mock import MagicMock, patch

from languages.russian.domain.ru_config import RuConfig
from languages.russian.domain.ru_fallbacks import RuFallbacks
from languages.russian.domain.ru_prompt_builder import RuPromptBuilder
from languages.russian.domain.ru_response_parser import RuResponseParser
from languages.russian.domain.ru_validator import RuValidator


@pytest.fixture
def config():
    return RuConfig()


@pytest.fixture
def fallbacks(config):
    return RuFallbacks(config)


@pytest.fixture
def prompt_builder(config):
    return RuPromptBuilder(config)


@pytest.fixture
def response_parser(config, fallbacks):
    return RuResponseParser(config, fallbacks)


@pytest.fixture
def validator(config):
    return RuValidator(config)


# ---------------------------------------------------------------------------
# Sample AI responses — Cyrillic sentences, rich individual_meaning fields
# ---------------------------------------------------------------------------

# Beginner: "Я читаю книгу." (I am reading a book.)
SAMPLE_BEGINNER_RESPONSE = """{
  "sentence": "Я читаю книгу.",
  "overall_structure": "Subject-Verb-Object (SVO). Personal pronoun subject, imperfective verb, feminine accusative direct object.",
  "sentence_structure": "Subject-Verb-Object (SVO). Personal pronoun subject, imperfective verb, feminine accusative direct object.",
  "word_explanations": [
    {
      "word": "Я",
      "grammatical_role": "personal_pronoun",
      "color": "#9370DB",
      "individual_meaning": "Personal pronoun 'Я' (I), 1st-person singular, nominative case. Subject of the verb читаю; Russian is pro-drop so the explicit Я is mildly emphatic here.",
      "case": "nominative",
      "gender": "",
      "number": "singular",
      "animacy": "animate",
      "aspect": "",
      "tense": "",
      "person": "1",
      "mood": "indicative",
      "voice": "",
      "governed_case": "",
      "lemma": "я"
    },
    {
      "word": "читаю",
      "grammatical_role": "verb",
      "color": "#4ECDC4",
      "individual_meaning": "Imperfective verb, 1st-conjugation, present tense, 1st-person singular, indicative mood. Lemma читать ('to read'); the perfective partner is прочитать. Imperfective marks the action as ongoing or habitual ('I am reading'). Governs an accusative direct object (книгу).",
      "case": "",
      "gender": "",
      "number": "singular",
      "animacy": "",
      "aspect": "imperfective",
      "tense": "present",
      "person": "1",
      "mood": "indicative",
      "voice": "active",
      "governed_case": "",
      "lemma": "читать"
    },
    {
      "word": "книгу",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "individual_meaning": "Noun, accusative singular feminine, 1st declension (lemma книга, 'book'). Direct object of читаю. Inanimate feminine — accusative singular is -у (книга → книгу).",
      "case": "accusative",
      "gender": "feminine",
      "number": "singular",
      "animacy": "inanimate",
      "aspect": "",
      "tense": "",
      "person": "",
      "mood": "",
      "voice": "",
      "governed_case": "",
      "lemma": "книга"
    },
    {
      "word": ".",
      "grammatical_role": "other",
      "color": "#808080",
      "individual_meaning": "Sentence-final period; ends the declarative clause.",
      "case": "",
      "gender": "",
      "number": "",
      "animacy": "",
      "aspect": "",
      "tense": "",
      "person": "",
      "mood": "",
      "voice": "",
      "governed_case": "",
      "lemma": "."
    }
  ],
  "grammar_notes": "Simple SVO sentence. Я is nominative subject; читаю is imperfective present 1sg; книгу is accusative singular feminine direct object.",
  "confidence": 0.93
}"""

# Intermediate: "Мне нужно написать письмо." (I need to write a letter.)
SAMPLE_INTERMEDIATE_RESPONSE = """{
  "sentence": "Мне нужно написать письмо.",
  "overall_structure": "Dative-subject impersonal construction: experiencer in dative + impersonal predicative 'нужно' + perfective infinitive + accusative object.",
  "sentence_structure": "Dative-subject impersonal construction with perfective infinitive complement.",
  "word_explanations": [
    {
      "word": "Мне",
      "grammatical_role": "personal_pronoun",
      "color": "#9370DB",
      "individual_meaning": "Personal pronoun 'мне' (to me / for me), 1st-person singular, dative case. Logical subject (experiencer) of the impersonal predicative 'нужно'; the dative is required by this construction.",
      "case": "dative",
      "gender": "",
      "number": "singular",
      "animacy": "animate",
      "aspect": "",
      "tense": "",
      "person": "1",
      "mood": "",
      "voice": "",
      "governed_case": "",
      "lemma": "я"
    },
    {
      "word": "нужно",
      "grammatical_role": "modal_verb",
      "color": "#00CED1",
      "individual_meaning": "Impersonal modal predicative 'нужно' (it is necessary / one needs), neuter short-form. Requires a dative experiencer (мне) and an infinitive complement (написать). Equivalent to 'надо' but slightly more formal.",
      "case": "",
      "gender": "neuter",
      "number": "singular",
      "animacy": "",
      "aspect": "",
      "tense": "present",
      "person": "",
      "mood": "indicative",
      "voice": "",
      "governed_case": "",
      "lemma": "нужный"
    },
    {
      "word": "написать",
      "grammatical_role": "infinitive",
      "color": "#4ECDC4",
      "individual_meaning": "Perfective infinitive 'написать' (to write — perfective). Lemma: написать; perfective aspect signals the action should be completed ('write and finish'). Complement of the modal 'нужно'; governs an accusative object (письмо).",
      "case": "",
      "gender": "",
      "number": "",
      "animacy": "",
      "aspect": "perfective",
      "tense": "",
      "person": "",
      "mood": "infinitive",
      "voice": "active",
      "governed_case": "",
      "lemma": "написать"
    },
    {
      "word": "письмо",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "individual_meaning": "Noun, accusative singular neuter, 2nd declension (lemma письмо, 'letter'). Direct object of написать. Inanimate neuter — accusative is identical to nominative (-о).",
      "case": "accusative",
      "gender": "neuter",
      "number": "singular",
      "animacy": "inanimate",
      "aspect": "",
      "tense": "",
      "person": "",
      "mood": "",
      "voice": "",
      "governed_case": "",
      "lemma": "письмо"
    },
    {
      "word": ".",
      "grammatical_role": "other",
      "color": "#808080",
      "individual_meaning": "Sentence-final period; ends the declarative clause.",
      "case": "",
      "gender": "",
      "number": "",
      "animacy": "",
      "aspect": "",
      "tense": "",
      "person": "",
      "mood": "",
      "voice": "",
      "governed_case": "",
      "lemma": "."
    }
  ],
  "grammar_notes": "Dative-subject impersonal construction: 'мне нужно + inf'. The dative мне is the logical subject/experiencer; нужно is an impersonal predicative; написать is a perfective infinitive; письмо is an accusative direct object.",
  "confidence": 0.91
}"""

# Advanced: "Книга, которую она читала, была интересной."
# (The book that she was reading was interesting.)
SAMPLE_ADVANCED_RESPONSE = """{
  "sentence": "Книга, которую она читала, была интересной.",
  "overall_structure": "Complex sentence: main clause (Книга … была интересной) with an embedded relative clause (которую она читала). Main clause has null-copula replaced by past 'была'; predicate adjective 'интересной' is in instrumental case (predicative instrumental after past быть).",
  "sentence_structure": "Relative clause embedded in main clause. Subject Книга → relative pronoun которую (feminine accusative) → past imperfective читала → past copula была → predicative instrumental интересной.",
  "word_explanations": [
    {
      "word": "Книга",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "individual_meaning": "Noun, nominative singular feminine, 1st declension (lemma книга, 'book'). Head noun of the main clause; subject of 'была интересной'. The relative clause 'которую она читала' modifies it.",
      "case": "nominative",
      "gender": "feminine",
      "number": "singular",
      "animacy": "inanimate",
      "aspect": "",
      "tense": "",
      "person": "",
      "mood": "",
      "voice": "",
      "governed_case": "",
      "lemma": "книга"
    },
    {
      "word": ",",
      "grammatical_role": "other",
      "color": "#808080",
      "individual_meaning": "Comma marking the boundary of the relative clause.",
      "case": "",
      "gender": "",
      "number": "",
      "animacy": "",
      "aspect": "",
      "tense": "",
      "person": "",
      "mood": "",
      "voice": "",
      "governed_case": "",
      "lemma": ","
    },
    {
      "word": "которую",
      "grammatical_role": "relative_pronoun",
      "color": "#9370DB",
      "individual_meaning": "Relative pronoun 'которую', feminine singular accusative. Agrees with the antecedent 'книга' in gender (feminine) and number (singular); takes accusative case because it is the direct object of 'читала' in the relative clause. Introduces a restrictive relative clause.",
      "case": "accusative",
      "gender": "feminine",
      "number": "singular",
      "animacy": "inanimate",
      "aspect": "",
      "tense": "",
      "person": "",
      "mood": "",
      "voice": "",
      "governed_case": "",
      "lemma": "который"
    },
    {
      "word": "она",
      "grammatical_role": "personal_pronoun",
      "color": "#9370DB",
      "individual_meaning": "Personal pronoun 'она' (she), 3rd-person singular feminine, nominative case. Subject of 'читала' in the relative clause.",
      "case": "nominative",
      "gender": "feminine",
      "number": "singular",
      "animacy": "animate",
      "aspect": "",
      "tense": "",
      "person": "3",
      "mood": "",
      "voice": "",
      "governed_case": "",
      "lemma": "она"
    },
    {
      "word": "читала",
      "grammatical_role": "verb",
      "color": "#4ECDC4",
      "individual_meaning": "Imperfective verb, past tense, feminine singular. Lemma читать ('to read'); imperfective aspect indicates an ongoing or habitual past action ('was reading'). Past tense in Russian agrees with the subject in gender (feminine -ла) and number, not person.",
      "case": "",
      "gender": "feminine",
      "number": "singular",
      "animacy": "",
      "aspect": "imperfective",
      "tense": "past",
      "person": "",
      "mood": "indicative",
      "voice": "active",
      "governed_case": "",
      "lemma": "читать"
    },
    {
      "word": ",",
      "grammatical_role": "other",
      "color": "#808080",
      "individual_meaning": "Comma marking the end of the relative clause.",
      "case": "",
      "gender": "",
      "number": "",
      "animacy": "",
      "aspect": "",
      "tense": "",
      "person": "",
      "mood": "",
      "voice": "",
      "governed_case": "",
      "lemma": ","
    },
    {
      "word": "была",
      "grammatical_role": "auxiliary",
      "color": "#00CED1",
      "individual_meaning": "Past tense of 'быть' (to be), feminine singular. Copula in the main clause; triggers predicate instrumental on the adjective ('интересной'). Feminine -ла agrees with the subject 'книга'.",
      "case": "",
      "gender": "feminine",
      "number": "singular",
      "animacy": "",
      "aspect": "imperfective",
      "tense": "past",
      "person": "",
      "mood": "indicative",
      "voice": "",
      "governed_case": "",
      "lemma": "быть"
    },
    {
      "word": "интересной",
      "grammatical_role": "adjective",
      "color": "#FF44FF",
      "individual_meaning": "Long-form adjective 'интересной', feminine singular instrumental (predicative instrumental). After past 'была', the predicate adjective takes the instrumental case — this is the predicate instrumental construction ('была интересной' = 'was interesting'). Lemma интересный.",
      "case": "instrumental",
      "gender": "feminine",
      "number": "singular",
      "animacy": "",
      "aspect": "",
      "tense": "",
      "person": "",
      "mood": "",
      "voice": "",
      "governed_case": "",
      "lemma": "интересный"
    },
    {
      "word": ".",
      "grammatical_role": "other",
      "color": "#808080",
      "individual_meaning": "Sentence-final period; ends the declarative clause.",
      "case": "",
      "gender": "",
      "number": "",
      "animacy": "",
      "aspect": "",
      "tense": "",
      "person": "",
      "mood": "",
      "voice": "",
      "governed_case": "",
      "lemma": "."
    }
  ],
  "grammar_notes": "Complex sentence with a relative clause. 'которую' agrees with 'книга' in gender/number and takes accusative from its function as direct object of 'читала'. 'была интересной' demonstrates the predicate instrumental — after past быть, the predicate complement takes instrumental.",
  "confidence": 0.90
}"""

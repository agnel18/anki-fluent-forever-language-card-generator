# languages/english/tests/conftest.py
"""
Pytest fixtures for English analyzer tests.
"""
import pytest
from unittest.mock import MagicMock, patch

from languages.english.domain.en_config import EnConfig
from languages.english.domain.en_fallbacks import EnFallbacks
from languages.english.domain.en_prompt_builder import EnPromptBuilder
from languages.english.domain.en_response_parser import EnResponseParser
from languages.english.domain.en_validator import EnValidator


@pytest.fixture
def config():
    return EnConfig()


@pytest.fixture
def fallbacks(config):
    return EnFallbacks(config)


@pytest.fixture
def prompt_builder(config):
    return EnPromptBuilder(config)


@pytest.fixture
def response_parser(config, fallbacks):
    return EnResponseParser(config, fallbacks)


@pytest.fixture
def validator(config):
    return EnValidator(config)


# ---------------------------------------------------------------------------
# Sample AI responses — match the individual_meaning schema EnPromptBuilder asks for
# ---------------------------------------------------------------------------

SAMPLE_BEGINNER_RESPONSE = """{
  "sentence": "The cat eats fish.",
  "overall_structure": "Subject-Verb-Object declarative clause; simple present tense, active voice.",
  "sentence_structure": "Subject-Verb-Object declarative clause; simple present tense, active voice.",
  "tense_aspect": "simple_present",
  "voice": "active",
  "word_explanations": [
    {
      "word": "The",
      "grammatical_role": "article",
      "color": "#FFD700",
      "individual_meaning": "Definite article marking 'cat' as a specific, already-known entity. Articles are a closed grammatical class in English; 'the' is the only definite article and is used with singular, plural, count, and mass nouns alike.",
      "tense": "",
      "aspect": "",
      "voice": "",
      "case": "",
      "number": "",
      "person": "",
      "degree": "",
      "modality": "",
      "syntactic_function": "determiner of 'cat'",
      "is_phrasal_verb_part": false,
      "lemma": "the"
    },
    {
      "word": "cat",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "individual_meaning": "Common singular count noun, functioning as the grammatical subject of the clause. In English, nouns have no case inflection; subject status is indicated by pre-verbal position in this SVO sentence.",
      "tense": "",
      "aspect": "",
      "voice": "",
      "case": "",
      "number": "singular",
      "person": "",
      "degree": "",
      "modality": "",
      "syntactic_function": "subject",
      "is_phrasal_verb_part": false,
      "lemma": "cat"
    },
    {
      "word": "eats",
      "grammatical_role": "verb",
      "color": "#4ECDC4",
      "individual_meaning": "Lexical verb 'eat' inflected with the 3rd-person singular present-tense -s ending, agreeing with the subject 'cat' (3sg). This -s agreement is the only person/number inflection that survives in modern English present tense; all other persons use the bare form 'eat'.",
      "tense": "present",
      "aspect": "simple",
      "voice": "active",
      "case": "",
      "number": "singular",
      "person": "3",
      "degree": "",
      "modality": "",
      "syntactic_function": "main predicate",
      "is_phrasal_verb_part": false,
      "lemma": "eat"
    },
    {
      "word": "fish",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "individual_meaning": "Common noun, functioning as the direct object of 'eats'. 'Fish' is one of several English nouns with an identical singular and plural form (zero-plural). As a bare noun without an article it is used here as a mass noun (uncountable sense: fish in general).",
      "tense": "",
      "aspect": "",
      "voice": "",
      "case": "",
      "number": "singular",
      "person": "",
      "degree": "",
      "modality": "",
      "syntactic_function": "direct_object",
      "is_phrasal_verb_part": false,
      "lemma": "fish"
    },
    {
      "word": ".",
      "grammatical_role": "other",
      "color": "#808080",
      "individual_meaning": "Sentence-final period; ends the declarative clause.",
      "tense": "",
      "aspect": "",
      "voice": "",
      "case": "",
      "number": "",
      "person": "",
      "degree": "",
      "modality": "",
      "syntactic_function": "punctuation",
      "is_phrasal_verb_part": false,
      "lemma": "."
    }
  ],
  "grammar_notes": "Simple SVO declarative. 'eats' shows the 3sg present -s agreement marker. 'fish' is a zero-plural noun used as a mass noun without an article.",
  "confidence": 0.93
}"""

SAMPLE_INTERMEDIATE_RESPONSE = """{
  "sentence": "I want to run quickly.",
  "overall_structure": "Subject-Verb-Infinitive_Complement-Adverb; simple present, active voice. 'to run quickly' is the infinitival complement of 'want'.",
  "sentence_structure": "Subject-Verb-Infinitive_Complement-Adverb; simple present, active voice. 'to run quickly' is the infinitival complement of 'want'.",
  "tense_aspect": "simple_present",
  "voice": "active",
  "word_explanations": [
    {
      "word": "I",
      "grammatical_role": "personal_pronoun",
      "color": "#9370DB",
      "individual_meaning": "1st-person singular subject pronoun in the NOMINATIVE case. Always capitalised in English orthography. Functions as the grammatical subject of the finite verb 'want'. The accusative counterpart would be 'me' (used as object of a verb or preposition).",
      "tense": "",
      "aspect": "",
      "voice": "",
      "case": "nominative",
      "number": "singular",
      "person": "1",
      "degree": "",
      "modality": "",
      "syntactic_function": "subject",
      "is_phrasal_verb_part": false,
      "lemma": "I"
    },
    {
      "word": "want",
      "grammatical_role": "verb",
      "color": "#4ECDC4",
      "individual_meaning": "Lexical verb 'want' in the 1st-person singular simple present tense. No -s ending because the subject 'I' is 1st person (not 3rd-person singular). 'Want' is a catenative verb that takes an infinitival complement ('to run quickly').",
      "tense": "present",
      "aspect": "simple",
      "voice": "active",
      "case": "",
      "number": "singular",
      "person": "1",
      "degree": "",
      "modality": "",
      "syntactic_function": "main predicate, head of the catenative construction",
      "is_phrasal_verb_part": false,
      "lemma": "want"
    },
    {
      "word": "to",
      "grammatical_role": "infinitive_marker",
      "color": "#FF8C00",
      "individual_meaning": "Infinitive marker — a particle, NOT a preposition. The diagnostic is that the immediately following word 'run' is a BASE-FORM verb (uninflected), which is the hallmark of the infinitival construction. If 'to' had been followed by a noun phrase (e.g. 'to the park') it would be a preposition. Here 'to run' is the infinitival complement of 'want'.",
      "tense": "",
      "aspect": "",
      "voice": "",
      "case": "",
      "number": "",
      "person": "",
      "degree": "",
      "modality": "",
      "syntactic_function": "infinitive_marker before 'run'",
      "is_phrasal_verb_part": false,
      "lemma": "to"
    },
    {
      "word": "run",
      "grammatical_role": "infinitive",
      "color": "#FFA500",
      "individual_meaning": "Base-form (bare infinitive) of the lexical verb 'run', preceded by the infinitive marker 'to'. Together 'to run' forms the infinitival complement of the matrix verb 'want'. The base form is morphologically unmarked — same as the present-tense non-3sg form.",
      "tense": "",
      "aspect": "",
      "voice": "active",
      "case": "",
      "number": "",
      "person": "",
      "degree": "",
      "modality": "",
      "syntactic_function": "head of infinitival complement",
      "is_phrasal_verb_part": false,
      "lemma": "run"
    },
    {
      "word": "quickly",
      "grammatical_role": "adverb",
      "color": "#FF6347",
      "individual_meaning": "Manner adverb derived from the adjective 'quick' via the -ly derivational suffix. Modifies the verb 'run', describing the manner of the running action. Adverbs of manner typically follow the verb or verb phrase they modify in English.",
      "tense": "",
      "aspect": "",
      "voice": "",
      "case": "",
      "number": "",
      "person": "",
      "degree": "positive",
      "modality": "",
      "syntactic_function": "manner modifier of 'run'",
      "is_phrasal_verb_part": false,
      "lemma": "quickly"
    },
    {
      "word": ".",
      "grammatical_role": "other",
      "color": "#808080",
      "individual_meaning": "Sentence-final period; ends the declarative clause.",
      "tense": "",
      "aspect": "",
      "voice": "",
      "case": "",
      "number": "",
      "person": "",
      "degree": "",
      "modality": "",
      "syntactic_function": "punctuation",
      "is_phrasal_verb_part": false,
      "lemma": "."
    }
  ],
  "grammar_notes": "Catenative construction: 'want' + infinitival complement 'to run'. 'to' is an infinitive marker (particle), not a preposition — the diagnostic is that 'run' is a base-form verb, not a noun phrase.",
  "confidence": 0.92
}"""

SAMPLE_ADVANCED_RESPONSE = """{
  "sentence": "The book that she read was interesting.",
  "overall_structure": "Main clause (The book was interesting) + restrictive relative clause (that she read); simple past, active voice in the relative clause; copular past in the main clause.",
  "sentence_structure": "Main clause (The book was interesting) + restrictive relative clause (that she read); simple past, active voice in the relative clause; copular past in the main clause.",
  "tense_aspect": "simple_past",
  "voice": "active",
  "word_explanations": [
    {
      "word": "The",
      "grammatical_role": "article",
      "color": "#FFD700",
      "individual_meaning": "Definite article 'the', marking 'book' as a specific, identifiable entity (made definite by the following restrictive relative clause 'that she read'). Definite articles are used when both speaker and hearer can identify the referent.",
      "tense": "",
      "aspect": "",
      "voice": "",
      "case": "",
      "number": "",
      "person": "",
      "degree": "",
      "modality": "",
      "syntactic_function": "determiner of 'book'",
      "is_phrasal_verb_part": false,
      "lemma": "the"
    },
    {
      "word": "book",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "individual_meaning": "Common singular count noun, functioning as the grammatical subject of the main clause. The noun phrase 'The book that she read' is the full subject, with the relative clause 'that she read' restricting which book is meant. English nouns carry no case inflection for subject vs. object status.",
      "tense": "",
      "aspect": "",
      "voice": "",
      "case": "",
      "number": "singular",
      "person": "",
      "degree": "",
      "modality": "",
      "syntactic_function": "head of subject NP, modified by relative clause",
      "is_phrasal_verb_part": false,
      "lemma": "book"
    },
    {
      "word": "that",
      "grammatical_role": "relative_pronoun",
      "color": "#9370DB",
      "individual_meaning": "Relative pronoun 'that', introducing a RESTRICTIVE relative clause ('that she read') that modifies the preceding noun 'book'. This is the RELATIVE PRONOUN reading: 'that' immediately follows a noun phrase and heads a clause that restricts the referent. Distinct from the DEMONSTRATIVE reading (which modifies or refers to a noun directly, without introducing a subordinate clause) and from the COMPLEMENTIZER reading (which would follow a verb of saying/thinking rather than a head noun).",
      "tense": "",
      "aspect": "",
      "voice": "",
      "case": "",
      "number": "",
      "person": "",
      "degree": "",
      "modality": "",
      "syntactic_function": "head of restrictive relative clause, object of 'read' within that clause",
      "is_phrasal_verb_part": false,
      "lemma": "that"
    },
    {
      "word": "she",
      "grammatical_role": "personal_pronoun",
      "color": "#9370DB",
      "individual_meaning": "3rd-person singular feminine subject pronoun in the NOMINATIVE case. Functions as the grammatical subject of the relative clause verb 'read'. Distinct from the accusative 'her' (used as object of a verb or preposition). The pronoun co-refers with some female antecedent in the broader discourse.",
      "tense": "",
      "aspect": "",
      "voice": "",
      "case": "nominative",
      "number": "singular",
      "person": "3",
      "degree": "",
      "modality": "",
      "syntactic_function": "subject of the relative clause",
      "is_phrasal_verb_part": false,
      "lemma": "she"
    },
    {
      "word": "read",
      "grammatical_role": "verb",
      "color": "#4ECDC4",
      "individual_meaning": "Lexical verb 'read' in the simple past tense. 'Read' is an irregular verb whose simple past form is homophonous with but orthographically identical to the base form (pronounced /rɛd/ in the past). Functions as the predicate of the restrictive relative clause; its direct object is the relative pronoun 'that' (which has moved to the front of the clause).",
      "tense": "past",
      "aspect": "simple",
      "voice": "active",
      "case": "",
      "number": "singular",
      "person": "3",
      "degree": "",
      "modality": "",
      "syntactic_function": "predicate of the relative clause",
      "is_phrasal_verb_part": false,
      "lemma": "read"
    },
    {
      "word": "was",
      "grammatical_role": "auxiliary",
      "color": "#00CED1",
      "individual_meaning": "Past tense of the copula 'be', 1st/3rd-person singular form. Here it functions as a COPULAR verb (not a progressive or passive auxiliary) linking the subject 'The book' to the predicate adjective 'interesting'. The past tense signals that the event is viewed as completed or located in the past.",
      "tense": "past",
      "aspect": "simple",
      "voice": "active",
      "case": "",
      "number": "singular",
      "person": "3",
      "degree": "",
      "modality": "",
      "syntactic_function": "copular main verb of the main clause",
      "is_phrasal_verb_part": false,
      "lemma": "be"
    },
    {
      "word": "interesting",
      "grammatical_role": "adjective",
      "color": "#FF44FF",
      "individual_meaning": "Predicative adjective in the positive degree, functioning as the predicate complement after the copula 'was'. 'Interesting' is a present-participle-derived adjective (from 'interest'); in this predicative position it describes a property of the subject 'The book that she read'.",
      "tense": "",
      "aspect": "",
      "voice": "",
      "case": "",
      "number": "",
      "person": "",
      "degree": "positive",
      "modality": "",
      "syntactic_function": "predicate complement (subject complement) of 'was'",
      "is_phrasal_verb_part": false,
      "lemma": "interesting"
    },
    {
      "word": ".",
      "grammatical_role": "other",
      "color": "#808080",
      "individual_meaning": "Sentence-final period; ends the declarative clause.",
      "tense": "",
      "aspect": "",
      "voice": "",
      "case": "",
      "number": "",
      "person": "",
      "degree": "",
      "modality": "",
      "syntactic_function": "punctuation",
      "is_phrasal_verb_part": false,
      "lemma": "."
    }
  ],
  "grammar_notes": "Restrictive relative clause 'that she read' modifies 'book'. The relative pronoun 'that' serves as the object of 'read' within the clause (object-gap relative). Main clause copula 'was' + adjective 'interesting'.",
  "confidence": 0.91
}"""

"""
End-to-End Pipeline Integration Test

Tests the FULL generation pipeline for languages with grammar analyzers by mocking
the Gemini API with realistic, linguistically accurate responses. Exercises:

  Content generation → Parsing → Grammar analysis → Audio → Images → Card assembly

Produces a detailed human-readable report (console + file).

Usage:
    python -m pytest tests/test_end_to_end_pipeline.py -v -s
    python -m pytest tests/test_end_to_end_pipeline.py -v -s -k "japanese"
"""

import json
import logging
import os
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch, PropertyMock
import tempfile

import pytest

# ---------------------------------------------------------------------------
# Path setup (mirrors tests/conftest.py)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "streamlit_app"))

os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Report directory
# ---------------------------------------------------------------------------
REPORT_DIR = PROJECT_ROOT / "tests" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# MOCK DATA PER LANGUAGE
# ============================================================================
# Each entry supplies:
#   word            – a top-100 frequency word
#   language_name   – full name expected by the pipeline
#   language_code   – ISO code used by the analyzer registry
#   topic           – one topic from constants.py curated list
#   mock_content_response  – exact text Gemini would return for content generation
#   mock_grammar_responses – list of JSON dicts (one per sentence) the analyzer's
#                            _call_ai would return for grammar analysis

JAPANESE_MOCK_DATA: Dict[str, Any] = {
    "word": "食べる",
    "language_name": "Japanese",
    "language_code": "ja",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 8,
    "max_length": 13,
    "difficulty": "beginner",
    # --- Mock Gemini response for content generation (sentence_generator) ---
    "mock_content_response": textwrap.dedent("""\
        MEANING: to eat (to consume food by putting it in the mouth)

        RESTRICTIONS: No specific grammatical restrictions.

        SENTENCES:
        1. 私は毎朝パンとたまごを食べます。
        2. 子供たちは学校で昼ごはんを食べます。
        3. あなたは何を食べたいですか。
        4. 母は台所でりんごを食べています。

        TRANSLATIONS:
        1. I eat bread and eggs every morning.
        2. The children eat lunch at school.
        3. What do you want to eat?
        4. My mother is eating an apple in the kitchen.

        IPA:
        1. わたし は まいあさ パン と たまご を たべます
        2. こどもたち は がっこう で ひるごはん を たべます
        3. あなた は なに を たべたい です か
        4. はは は だいどころ で りんご を たべています

        KEYWORDS:
        1. bread on plate, fried eggs, breakfast table
        2. children in cafeteria, school lunch tray, eating together
        3. restaurant menu, food choices, question mark
        4. woman in kitchen, red apple, eating fruit"""),

    # --- Mock Gemini responses for grammar analysis (one JSON per sentence) ---
    # The Japanese analyzer calls _call_ai once per batch; the batch prompt asks
    # for a JSON array. We supply the full array as a single string response.
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "私は毎朝パンとたまごを食べます。",
            "words": [
                {"word": "私", "reading": "わたし", "grammatical_role": "pronoun", "conjugation_form": None, "politeness": None, "individual_meaning": "I (first person pronoun)"},
                {"word": "は", "reading": "は", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "topic marker particle"},
                {"word": "毎朝", "reading": "まいあさ", "grammatical_role": "adverb", "conjugation_form": None, "politeness": None, "individual_meaning": "every morning"},
                {"word": "パン", "reading": "パン", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "bread"},
                {"word": "と", "reading": "と", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "and (listing particle)"},
                {"word": "たまご", "reading": "たまご", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "egg"},
                {"word": "を", "reading": "を", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "object marker particle"},
                {"word": "食べます", "reading": "たべます", "grammatical_role": "verb", "conjugation_form": "masu", "politeness": "polite", "individual_meaning": "eat (polite present)"}
            ],
            "explanations": {
                "overall_structure": "SOV sentence: Subject は Time Object を Verb (polite).",
                "key_features": "Uses topic particle は, object particle を, listing particle と, polite -ます form.",
                "complexity_notes": "Beginner-friendly polite sentence with basic particles."
            }
        },
        {
            "sentence": "子供たちは学校で昼ごはんを食べます。",
            "words": [
                {"word": "子供たち", "reading": "こどもたち", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "children (plural)"},
                {"word": "は", "reading": "は", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "topic marker particle"},
                {"word": "学校", "reading": "がっこう", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "school"},
                {"word": "で", "reading": "で", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "location of action particle"},
                {"word": "昼ごはん", "reading": "ひるごはん", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "lunch"},
                {"word": "を", "reading": "を", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "object marker particle"},
                {"word": "食べます", "reading": "たべます", "grammatical_role": "verb", "conjugation_form": "masu", "politeness": "polite", "individual_meaning": "eat (polite present)"}
            ],
            "explanations": {
                "overall_structure": "SOV sentence: Subject は Location で Object を Verb.",
                "key_features": "Uses location particle で to mark where action takes place, topic particle は, object particle を.",
                "complexity_notes": "Beginner pattern with location marker で."
            }
        },
        {
            "sentence": "あなたは何を食べたいですか。",
            "words": [
                {"word": "あなた", "reading": "あなた", "grammatical_role": "pronoun", "conjugation_form": None, "politeness": None, "individual_meaning": "you (second person pronoun)"},
                {"word": "は", "reading": "は", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "topic marker particle"},
                {"word": "何", "reading": "なに", "grammatical_role": "pronoun", "conjugation_form": None, "politeness": None, "individual_meaning": "what (interrogative)"},
                {"word": "を", "reading": "を", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "object marker particle"},
                {"word": "食べたい", "reading": "たべたい", "grammatical_role": "verb", "conjugation_form": "tai", "politeness": "plain", "individual_meaning": "want to eat (desire form)"},
                {"word": "です", "reading": "です", "grammatical_role": "copula", "conjugation_form": "masu", "politeness": "polite", "individual_meaning": "is/am/are (polite copula)"},
                {"word": "か", "reading": "か", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "question marker particle"}
            ],
            "explanations": {
                "overall_structure": "Interrogative SOV: Subject は WH-word を Verb-たい です か?",
                "key_features": "Uses -たい desire form, question particle か, polite copula です.",
                "complexity_notes": "Beginner question pattern with -たい (want to) form."
            }
        },
        {
            "sentence": "母は台所でりんごを食べています。",
            "words": [
                {"word": "母", "reading": "はは", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "mother (humble form)"},
                {"word": "は", "reading": "は", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "topic marker particle"},
                {"word": "台所", "reading": "だいどころ", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "kitchen"},
                {"word": "で", "reading": "で", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "location of action particle"},
                {"word": "りんご", "reading": "りんご", "grammatical_role": "noun", "conjugation_form": None, "politeness": None, "individual_meaning": "apple"},
                {"word": "を", "reading": "を", "grammatical_role": "particle", "conjugation_form": None, "politeness": None, "individual_meaning": "object marker particle"},
                {"word": "食べています", "reading": "たべています", "grammatical_role": "verb", "conjugation_form": "te_iru", "politeness": "polite", "individual_meaning": "is eating (progressive, polite)"}
            ],
            "explanations": {
                "overall_structure": "SOV progressive: Subject は Location で Object を Verb-ている.",
                "key_features": "Uses て-いる progressive form for ongoing action, location particle で.",
                "complexity_notes": "Beginner level — て-いる progressive is common early grammar."
            }
        }
    ], ensure_ascii=False),
}


KOREAN_MOCK_DATA: Dict[str, Any] = {
    "word": "먹다",
    "language_name": "Korean",
    "language_code": "ko",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 5,
    "max_length": 15,
    "difficulty": "beginner",
    # --- Mock Gemini response for content generation (sentence_generator) ---
    "mock_content_response": textwrap.dedent("""\
        MEANING: to eat (to consume food)

        RESTRICTIONS: No specific grammatical restrictions.

        SENTENCES:
        1. 저는 매일 아침에 밥을 먹어요.
        2. 아이들이 학교에서 점심을 먹습니다.
        3. 무엇을 먹고 싶어요?
        4. 어머니가 부엌에서 사과를 먹고 있어요.

        TRANSLATIONS:
        1. I eat rice every morning.
        2. The children eat lunch at school.
        3. What do you want to eat?
        4. Mother is eating an apple in the kitchen.

        IPA:
        1. tɕʌnɯn mɛil atɕʰime pabɯl mʌɡʌjo
        2. aidɯli hakkjoesʌ tɕʌmɕimɯl mʌksɯmnida
        3. muʌsɯl mʌkko ɕipʰʌjo
        4. ʌmʌniɡa puʌkʰesʌ saɡwarɯl mʌkko issʌjo

        KEYWORDS:
        1. rice bowl, breakfast table, morning meal
        2. children in cafeteria, school lunch, eating together
        3. menu card, food choices, question
        4. woman in kitchen, red apple, eating fruit"""),

    # --- Mock Gemini responses for grammar analysis ---
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "저는 매일 아침에 밥을 먹어요.",
            "words": [
                {"word": "저", "grammatical_role": "pronoun", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "I (humble first person pronoun)"},
                {"word": "는", "grammatical_role": "topic_marker", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "topic marker particle"},
                {"word": "매일", "grammatical_role": "adverb", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "every day"},
                {"word": "아침", "grammatical_role": "noun", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "morning"},
                {"word": "에", "grammatical_role": "locative_particle", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "at/in (time particle)"},
                {"word": "밥", "grammatical_role": "noun", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "rice/meal"},
                {"word": "을", "grammatical_role": "object_marker", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "object marker particle"},
                {"word": "먹어요", "grammatical_role": "verb", "speech_level": "polite", "tense": "present", "honorific": None, "individual_meaning": "eat (polite present form of 먹다)"}
            ],
            "explanations": {
                "overall_structure": "SOV sentence: Subject 는 Time 에 Object 을 Verb (polite).",
                "key_features": "Uses topic particle 는, time particle 에, object particle 을, polite -어요 form.",
                "complexity_notes": "Beginner-friendly polite sentence with basic particles."
            }
        },
        {
            "sentence": "아이들이 학교에서 점심을 먹습니다.",
            "words": [
                {"word": "아이들", "grammatical_role": "noun", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "children"},
                {"word": "이", "grammatical_role": "subject_marker", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "subject marker particle"},
                {"word": "학교", "grammatical_role": "noun", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "school"},
                {"word": "에서", "grammatical_role": "locative_particle", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "at (location of action particle)"},
                {"word": "점심", "grammatical_role": "noun", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "lunch"},
                {"word": "을", "grammatical_role": "object_marker", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "object marker particle"},
                {"word": "먹습니다", "grammatical_role": "verb", "speech_level": "formal", "tense": "present", "honorific": None, "individual_meaning": "eat (formal polite present form)"}
            ],
            "explanations": {
                "overall_structure": "SOV sentence: Subject 이 Location 에서 Object 을 Verb.",
                "key_features": "Uses subject marker 이, location particle 에서, formal -습니다 ending.",
                "complexity_notes": "Beginner pattern with formal speech level."
            }
        },
        {
            "sentence": "무엇을 먹고 싶어요?",
            "words": [
                {"word": "무엇", "grammatical_role": "pronoun", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "what (interrogative pronoun)"},
                {"word": "을", "grammatical_role": "object_marker", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "object marker particle"},
                {"word": "먹고", "grammatical_role": "connective_ending", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "eat + connective ending -고"},
                {"word": "싶어요", "grammatical_role": "auxiliary_verb", "speech_level": "polite", "tense": "present", "honorific": None, "individual_meaning": "want to (auxiliary, polite form of 싶다)"}
            ],
            "explanations": {
                "overall_structure": "Interrogative: WH-word 을 Verb-고 싶다 (want to)?",
                "key_features": "Uses -고 싶다 desire pattern, polite -어요 ending, question intonation.",
                "complexity_notes": "Beginner question pattern with -고 싶다 (want to) form."
            }
        },
        {
            "sentence": "어머니가 부엌에서 사과를 먹고 있어요.",
            "words": [
                {"word": "어머니", "grammatical_role": "noun", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "mother"},
                {"word": "가", "grammatical_role": "subject_marker", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "subject marker particle"},
                {"word": "부엌", "grammatical_role": "noun", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "kitchen"},
                {"word": "에서", "grammatical_role": "locative_particle", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "at (location of action particle)"},
                {"word": "사과", "grammatical_role": "noun", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "apple"},
                {"word": "를", "grammatical_role": "object_marker", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "object marker particle"},
                {"word": "먹고", "grammatical_role": "connective_ending", "speech_level": None, "tense": None, "honorific": None, "individual_meaning": "eat + connective ending -고"},
                {"word": "있어요", "grammatical_role": "auxiliary_verb", "speech_level": "polite", "tense": "present", "honorific": None, "individual_meaning": "is doing (progressive, polite form of 있다)"}
            ],
            "explanations": {
                "overall_structure": "SOV progressive: Subject 가 Location 에서 Object 를 Verb-고 있다.",
                "key_features": "Uses -고 있다 progressive form for ongoing action, location particle 에서.",
                "complexity_notes": "Beginner level — -고 있다 progressive is common early grammar."
            }
        }
    ], ensure_ascii=False),
}


HUNGARIAN_MOCK_DATA: Dict[str, Any] = {
    "word": "eszik",
    "language_name": "Hungarian",
    "language_code": "hu",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 5,
    "max_length": 15,
    "difficulty": "beginner",
    # --- Mock Gemini response for content generation (sentence_generator) ---
    "mock_content_response": textwrap.dedent("""\
        MEANING: to eat (to consume food by putting it in the mouth)

        RESTRICTIONS: Indefinite conjugation when the object is indefinite; definite conjugation when the object has a definite article.

        SENTENCES:
        1. A fiú minden reggel kenyeret eszik.
        2. A gyerekek az iskolában ebédet esznek.
        3. Mit szeretnél enni?
        4. Az anyám a konyhában almát eszik.

        TRANSLATIONS:
        1. The boy eats bread every morning.
        2. The children eat lunch at school.
        3. What would you like to eat?
        4. My mother is eating an apple in the kitchen.

        IPA:
        1. ɒ fiuː mindɛn rɛɡːɛl kɛɲeːrɛt ɛsik
        2. ɒ ɟɛrɛkɛk ɒz iskolɑːbɒn ɛbeːdɛt ɛsnɛk
        3. mit sɛrɛtneːl ɛnːi
        4. ɒz ɒɲaːm ɒ koɲhɑːbɒn ɒlmɑːt ɛsik

        KEYWORDS:
        1. bread on plate, boy eating, morning breakfast table
        2. children in cafeteria, school lunch tray, eating together
        3. restaurant menu, food choices, question mark
        4. woman in kitchen, red apple, eating fruit"""),

    # --- Mock Gemini responses for grammar analysis (batch JSON array) ---
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "A fiú minden reggel kenyeret eszik.",
            "words": [
                {"word": "A", "grammatical_role": "definite_article", "case": None, "conjugation_type": None, "individual_meaning": "the (definite article before consonant)"},
                {"word": "fiú", "grammatical_role": "noun", "case": "nominative", "conjugation_type": None, "individual_meaning": "boy (subject, nominative case)"},
                {"word": "minden", "grammatical_role": "adjective", "case": None, "conjugation_type": None, "individual_meaning": "every (determiner/adjective)"},
                {"word": "reggel", "grammatical_role": "adverb", "case": None, "conjugation_type": None, "individual_meaning": "morning (time adverb)"},
                {"word": "kenyeret", "grammatical_role": "noun", "case": "accusative", "conjugation_type": None, "individual_meaning": "bread with accusative suffix -et (direct object)"},
                {"word": "eszik", "grammatical_role": "verb", "case": None, "conjugation_type": "indefinite", "individual_meaning": "eats (3rd person singular, indefinite conjugation, present tense)"}
            ],
            "explanations": {
                "overall_structure": "SVO sentence: Subject (A fiú) + Time (minden reggel) + Object-ACC (kenyeret) + Verb (eszik, indefinite conjugation).",
                "key_features": "Accusative suffix -et on kenyér → kenyeret; indefinite conjugation because object has no definite article.",
                "complexity_notes": "Beginner-friendly sentence with basic SVO order and accusative case."
            }
        },
        {
            "sentence": "A gyerekek az iskolában ebédet esznek.",
            "words": [
                {"word": "A", "grammatical_role": "definite_article", "case": None, "conjugation_type": None, "individual_meaning": "the (definite article)"},
                {"word": "gyerekek", "grammatical_role": "noun", "case": "nominative", "conjugation_type": None, "individual_meaning": "children (plural, nominative)"},
                {"word": "az", "grammatical_role": "definite_article", "case": None, "conjugation_type": None, "individual_meaning": "the (definite article before vowel)"},
                {"word": "iskolában", "grammatical_role": "noun", "case": "inessive", "conjugation_type": None, "individual_meaning": "in the school — iskola + inessive suffix -ban (back vowel harmony)"},
                {"word": "ebédet", "grammatical_role": "noun", "case": "accusative", "conjugation_type": None, "individual_meaning": "lunch with accusative suffix -et (direct object)"},
                {"word": "esznek", "grammatical_role": "verb", "case": None, "conjugation_type": "indefinite", "individual_meaning": "eat (3rd person plural, indefinite conjugation, present tense)"}
            ],
            "explanations": {
                "overall_structure": "SVO with location: Subject + Location-INESS + Object-ACC + Verb (indefinite).",
                "key_features": "Inessive case -ban on iskola → iskolában (back vowel harmony); accusative -et on ebéd.",
                "complexity_notes": "Beginner pattern with inessive location and plural subject."
            }
        },
        {
            "sentence": "Mit szeretnél enni?",
            "words": [
                {"word": "Mit", "grammatical_role": "pronoun", "case": "accusative", "conjugation_type": None, "individual_meaning": "what (interrogative, accusative of mi + -t)"},
                {"word": "szeretnél", "grammatical_role": "verb", "case": None, "conjugation_type": "indefinite", "individual_meaning": "would you like (2nd person singular, indefinite conjugation, conditional mood)"},
                {"word": "enni", "grammatical_role": "verb", "case": None, "conjugation_type": None, "individual_meaning": "to eat (infinitive form of eszik)"}
            ],
            "explanations": {
                "overall_structure": "Interrogative: WH-word (accusative) + Conditional verb + Infinitive.",
                "key_features": "Question word mit (accusative of mi); conditional mood -né + 2sg -l; infinitive enni.",
                "complexity_notes": "Beginner question pattern with conditional politeness."
            }
        },
        {
            "sentence": "Az anyám a konyhában almát eszik.",
            "words": [
                {"word": "Az", "grammatical_role": "definite_article", "case": None, "conjugation_type": None, "individual_meaning": "the (definite article before vowel)"},
                {"word": "anyám", "grammatical_role": "noun", "case": "nominative", "conjugation_type": None, "individual_meaning": "my mother — anya + possessive 1sg suffix -m"},
                {"word": "a", "grammatical_role": "definite_article", "case": None, "conjugation_type": None, "individual_meaning": "the (definite article before consonant)"},
                {"word": "konyhában", "grammatical_role": "noun", "case": "inessive", "conjugation_type": None, "individual_meaning": "in the kitchen — konyha + inessive suffix -ban (back vowel harmony)"},
                {"word": "almát", "grammatical_role": "noun", "case": "accusative", "conjugation_type": None, "individual_meaning": "apple with accusative suffix -t"},
                {"word": "eszik", "grammatical_role": "verb", "case": None, "conjugation_type": "indefinite", "individual_meaning": "eats (3rd person singular, indefinite conjugation, present)"}
            ],
            "explanations": {
                "overall_structure": "SVO with possessive and location: Subject (Az anyám) + Location-INESS (a konyhában) + Object-ACC (almát) + Verb.",
                "key_features": "Possessive suffix -m on anya → anyám (my mother); inessive -ban; accusative -t.",
                "complexity_notes": "Beginner — possessive suffix and inessive case with SVO order."
            }
        }
    ], ensure_ascii=False),
}


# ---------------------------------------------------------------------------
# FRENCH
# ---------------------------------------------------------------------------
FRENCH_MOCK_DATA: Dict[str, Any] = {
    "word": "manger",
    "language_name": "French",
    "language_code": "fr",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 5,
    "max_length": 15,
    "difficulty": "beginner",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to eat (to consume food)

        RESTRICTIONS: Regular -er verb. Uses auxiliary 'avoir' in compound tenses.

        SENTENCES:
        1. Je mange du pain chaque matin.
        2. Les enfants mangent à la cantine de l'école.
        3. Qu'est-ce que tu veux manger ce soir ?
        4. Ma mère mange une pomme dans la cuisine.

        TRANSLATIONS:
        1. I eat bread every morning.
        2. The children eat at the school cafeteria.
        3. What do you want to eat tonight?
        4. My mother is eating an apple in the kitchen.

        IPA:
        1. ʒə mɑ̃ʒ dy pɛ̃ ʃak matɛ̃
        2. lez ɑ̃fɑ̃ mɑ̃ʒ a la kɑ̃tin də lekɔl
        3. kɛs kə ty vø mɑ̃ʒe sə swaʁ
        4. ma mɛʁ mɑ̃ʒ yn pɔm dɑ̃ la kɥizin

        KEYWORDS:
        1. bread on plate, morning breakfast
        2. children cafeteria, school lunch
        3. dinner menu, evening meal
        4. woman kitchen, red apple"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "Je mange du pain chaque matin.",
            "words": [
                {"word": "Je", "grammatical_role": "pronoun", "individual_meaning": "I (first person singular subject pronoun)"},
                {"word": "mange", "grammatical_role": "verb", "individual_meaning": "eat (present tense, 1st person singular of manger)"},
                {"word": "du", "grammatical_role": "article", "individual_meaning": "some (partitive article, contraction of de + le)"},
                {"word": "pain", "grammatical_role": "noun", "individual_meaning": "bread (masculine noun)"},
                {"word": "chaque", "grammatical_role": "adjective", "individual_meaning": "each/every (indefinite adjective)"},
                {"word": "matin", "grammatical_role": "noun", "individual_meaning": "morning (masculine noun)"}
            ],
            "explanations": {"overall_structure": "SVO: Subject + Verb + Partitive Object + Time.", "key_features": "Partitive article 'du' for uncountable nouns."}
        },
        {
            "sentence": "Les enfants mangent à la cantine de l'école.",
            "words": [
                {"word": "Les", "grammatical_role": "article", "individual_meaning": "the (definite article, plural)"},
                {"word": "enfants", "grammatical_role": "noun", "individual_meaning": "children (masculine plural noun)"},
                {"word": "mangent", "grammatical_role": "verb", "individual_meaning": "eat (present tense, 3rd person plural of manger)"},
                {"word": "à", "grammatical_role": "preposition", "individual_meaning": "at/to (preposition of location)"},
                {"word": "la", "grammatical_role": "article", "individual_meaning": "the (definite article, feminine singular)"},
                {"word": "cantine", "grammatical_role": "noun", "individual_meaning": "cafeteria (feminine noun)"},
                {"word": "de", "grammatical_role": "preposition", "individual_meaning": "of (preposition showing possession)"},
                {"word": "l'école", "grammatical_role": "noun", "individual_meaning": "the school (feminine noun with elided article)"}
            ],
            "explanations": {"overall_structure": "SVO with location: Subject + Verb + Location.", "key_features": "Elision l' before vowel; preposition à + definite article."}
        },
        {
            "sentence": "Qu'est-ce que tu veux manger ce soir ?",
            "words": [
                {"word": "Qu'est-ce que", "grammatical_role": "pronoun", "individual_meaning": "what (interrogative expression)"},
                {"word": "tu", "grammatical_role": "pronoun", "individual_meaning": "you (informal 2nd person subject pronoun)"},
                {"word": "veux", "grammatical_role": "verb", "individual_meaning": "want (present tense, 2nd person singular of vouloir)"},
                {"word": "manger", "grammatical_role": "verb", "individual_meaning": "to eat (infinitive form)"},
                {"word": "ce", "grammatical_role": "adjective", "individual_meaning": "this (demonstrative adjective, masculine)"},
                {"word": "soir", "grammatical_role": "noun", "individual_meaning": "evening (masculine noun)"}
            ],
            "explanations": {"overall_structure": "Interrogative: WH-phrase + Subject + Modal + Infinitive + Time.", "key_features": "Qu'est-ce que for 'what'; vouloir + infinitive pattern."}
        },
        {
            "sentence": "Ma mère mange une pomme dans la cuisine.",
            "words": [
                {"word": "Ma", "grammatical_role": "adjective", "individual_meaning": "my (possessive adjective, feminine singular)"},
                {"word": "mère", "grammatical_role": "noun", "individual_meaning": "mother (feminine noun)"},
                {"word": "mange", "grammatical_role": "verb", "individual_meaning": "eats/is eating (present tense, 3rd person singular)"},
                {"word": "une", "grammatical_role": "article", "individual_meaning": "a/an (indefinite article, feminine)"},
                {"word": "pomme", "grammatical_role": "noun", "individual_meaning": "apple (feminine noun)"},
                {"word": "dans", "grammatical_role": "preposition", "individual_meaning": "in (preposition of location)"},
                {"word": "la", "grammatical_role": "article", "individual_meaning": "the (definite article, feminine)"},
                {"word": "cuisine", "grammatical_role": "noun", "individual_meaning": "kitchen (feminine noun)"}
            ],
            "explanations": {"overall_structure": "SVO with location: Possessive + Subject + Verb + Object + Location.", "key_features": "Possessive adjective ma; indefinite article une; location with dans."}
        }
    ], ensure_ascii=False),
}


# ---------------------------------------------------------------------------
# SPANISH
# ---------------------------------------------------------------------------
SPANISH_MOCK_DATA: Dict[str, Any] = {
    "word": "comer",
    "language_name": "Spanish",
    "language_code": "es",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 5,
    "max_length": 15,
    "difficulty": "beginner",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to eat (to consume food)

        RESTRICTIONS: Regular -er verb.

        SENTENCES:
        1. Yo como pan cada mañana.
        2. Los niños comen en la escuela.
        3. ¿Qué quieres comer esta noche?
        4. Mi madre come una manzana en la cocina.

        TRANSLATIONS:
        1. I eat bread every morning.
        2. The children eat at school.
        3. What do you want to eat tonight?
        4. My mother eats an apple in the kitchen.

        IPA:
        1. ʝo komo pan kaða maɲana
        2. los niɲos komen en la eskwela
        3. ke kjeres komeɾ esta notʃe
        4. mi maðɾe kome una manθana en la koθina

        KEYWORDS:
        1. bread plate, morning breakfast
        2. children school, lunch cafeteria
        3. dinner question, evening food
        4. mother kitchen, red apple"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "Yo como pan cada mañana.",
            "words": [
                {"word": "Yo", "grammatical_role": "pronoun", "individual_meaning": "I (1st person singular subject pronoun)"},
                {"word": "como", "grammatical_role": "verb", "individual_meaning": "eat (present indicative, 1st person singular of comer)"},
                {"word": "pan", "grammatical_role": "noun", "individual_meaning": "bread (masculine noun)"},
                {"word": "cada", "grammatical_role": "adjective", "individual_meaning": "each/every (indefinite adjective)"},
                {"word": "mañana", "grammatical_role": "noun", "individual_meaning": "morning (feminine noun)"}
            ],
            "explanations": {"overall_structure": "SVO: Subject + Verb + Object + Time.", "key_features": "Subject pronoun Yo (often omitted in Spanish)."}
        },
        {
            "sentence": "Los niños comen en la escuela.",
            "words": [
                {"word": "Los", "grammatical_role": "article", "individual_meaning": "the (definite article, masculine plural)"},
                {"word": "niños", "grammatical_role": "noun", "individual_meaning": "children (masculine plural noun)"},
                {"word": "comen", "grammatical_role": "verb", "individual_meaning": "eat (present indicative, 3rd person plural of comer)"},
                {"word": "en", "grammatical_role": "preposition", "individual_meaning": "at/in (preposition of location)"},
                {"word": "la", "grammatical_role": "article", "individual_meaning": "the (definite article, feminine singular)"},
                {"word": "escuela", "grammatical_role": "noun", "individual_meaning": "school (feminine noun)"}
            ],
            "explanations": {"overall_structure": "SVO: Subject + Verb + Location.", "key_features": "Definite article los with masculine plural noun; preposition en for location."}
        },
        {
            "sentence": "¿Qué quieres comer esta noche?",
            "words": [
                {"word": "Qué", "grammatical_role": "pronoun", "individual_meaning": "what (interrogative pronoun)"},
                {"word": "quieres", "grammatical_role": "verb", "individual_meaning": "want (present indicative, 2nd person singular of querer, stem-changing e→ie)"},
                {"word": "comer", "grammatical_role": "verb", "individual_meaning": "to eat (infinitive)"},
                {"word": "esta", "grammatical_role": "adjective", "individual_meaning": "this (demonstrative adjective, feminine)"},
                {"word": "noche", "grammatical_role": "noun", "individual_meaning": "night/evening (feminine noun)"}
            ],
            "explanations": {"overall_structure": "Interrogative: WH-word + Modal + Infinitive + Time.", "key_features": "Stem-changing verb querer (e→ie); querer + infinitive pattern."}
        },
        {
            "sentence": "Mi madre come una manzana en la cocina.",
            "words": [
                {"word": "Mi", "grammatical_role": "adjective", "individual_meaning": "my (possessive adjective)"},
                {"word": "madre", "grammatical_role": "noun", "individual_meaning": "mother (feminine noun)"},
                {"word": "come", "grammatical_role": "verb", "individual_meaning": "eats (present indicative, 3rd person singular of comer)"},
                {"word": "una", "grammatical_role": "article", "individual_meaning": "a/an (indefinite article, feminine)"},
                {"word": "manzana", "grammatical_role": "noun", "individual_meaning": "apple (feminine noun)"},
                {"word": "en", "grammatical_role": "preposition", "individual_meaning": "in (preposition of location)"},
                {"word": "la", "grammatical_role": "article", "individual_meaning": "the (definite article, feminine)"},
                {"word": "cocina", "grammatical_role": "noun", "individual_meaning": "kitchen (feminine noun)"}
            ],
            "explanations": {"overall_structure": "SVO with location: Possessive + Subject + Verb + Object + Location.", "key_features": "Possessive Mi; indefinite article una; en + article for location."}
        }
    ], ensure_ascii=False),
}


# ---------------------------------------------------------------------------
# GERMAN
# ---------------------------------------------------------------------------
GERMAN_MOCK_DATA: Dict[str, Any] = {
    "word": "essen",
    "language_name": "German",
    "language_code": "de",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 5,
    "max_length": 15,
    "difficulty": "beginner",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to eat (to consume food)

        RESTRICTIONS: Strong verb with vowel change e→i in 2nd/3rd person singular (du isst, er isst).

        SENTENCES:
        1. Ich esse jeden Morgen Brot.
        2. Die Kinder essen in der Schule zu Mittag.
        3. Was möchtest du heute Abend essen?
        4. Meine Mutter isst einen Apfel in der Küche.

        TRANSLATIONS:
        1. I eat bread every morning.
        2. The children eat lunch at school.
        3. What would you like to eat tonight?
        4. My mother is eating an apple in the kitchen.

        IPA:
        1. ɪç ɛsə jeːdn̩ mɔʁɡn̩ bʁoːt
        2. diː kɪndɐ ɛsn̩ ɪn deːɐ̯ ʃuːlə tsuː mɪtaːk
        3. vas mœçtəst duː hɔʏ̯tə aːbn̩t ɛsn̩
        4. maɪ̯nə mʊtɐ ɪst aɪ̯nən apfl̩ ɪn deːɐ̯ kʏçə

        KEYWORDS:
        1. bread plate, morning breakfast
        2. children school cafeteria, lunch
        3. dinner question, evening menu
        4. mother kitchen, apple eating"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "Ich esse jeden Morgen Brot.",
            "words": [
                {"word": "Ich", "grammatical_role": "pronoun", "individual_meaning": "I (1st person singular subject pronoun, nominative)", "grammatical_case": "nominative"},
                {"word": "esse", "grammatical_role": "verb", "individual_meaning": "eat (present tense, 1st person singular of essen)", "tense": "present"},
                {"word": "jeden", "grammatical_role": "adjective", "individual_meaning": "every (accusative masculine, strong declension of jeder)", "grammatical_case": "accusative", "gender": "m"},
                {"word": "Morgen", "grammatical_role": "noun", "individual_meaning": "morning (masculine noun, accusative)", "grammatical_case": "accusative", "gender": "m"},
                {"word": "Brot", "grammatical_role": "noun", "individual_meaning": "bread (neuter noun, accusative)", "grammatical_case": "accusative", "gender": "n"}
            ],
            "explanations": {"overall_structure": "SVO: Subject + Verb + Time (accusative) + Object (accusative).", "key_features": "Accusative case for time expressions (jeden Morgen); no article before Brot (general concept)."}
        },
        {
            "sentence": "Die Kinder essen in der Schule zu Mittag.",
            "words": [
                {"word": "Die", "grammatical_role": "article", "individual_meaning": "the (definite article, nominative plural)", "grammatical_case": "nominative"},
                {"word": "Kinder", "grammatical_role": "noun", "individual_meaning": "children (neuter plural noun, nominative)", "grammatical_case": "nominative", "gender": "n"},
                {"word": "essen", "grammatical_role": "verb", "individual_meaning": "eat (present tense, 3rd person plural)", "tense": "present"},
                {"word": "in", "grammatical_role": "preposition", "individual_meaning": "in/at (dative preposition for location)"},
                {"word": "der", "grammatical_role": "article", "individual_meaning": "the (definite article, dative feminine)", "grammatical_case": "dative", "gender": "f"},
                {"word": "Schule", "grammatical_role": "noun", "individual_meaning": "school (feminine noun, dative)", "grammatical_case": "dative", "gender": "f"},
                {"word": "zu Mittag", "grammatical_role": "adverb", "individual_meaning": "for lunch (adverbial phrase)"}
            ],
            "explanations": {"overall_structure": "SVO: Subject + Verb + Location (dative) + Adverbial.", "key_features": "Dative case after 'in' for location (no movement); zu Mittag as fixed expression."}
        },
        {
            "sentence": "Was möchtest du heute Abend essen?",
            "words": [
                {"word": "Was", "grammatical_role": "pronoun", "individual_meaning": "what (interrogative pronoun, accusative)"},
                {"word": "möchtest", "grammatical_role": "verb", "individual_meaning": "would like (Konjunktiv II of mögen, 2nd person singular)"},
                {"word": "du", "grammatical_role": "pronoun", "individual_meaning": "you (2nd person singular, informal, nominative)", "grammatical_case": "nominative"},
                {"word": "heute Abend", "grammatical_role": "adverb", "individual_meaning": "tonight/this evening (time adverbial)"},
                {"word": "essen", "grammatical_role": "verb", "individual_meaning": "to eat (infinitive, at end of clause)"}
            ],
            "explanations": {"overall_structure": "W-question: WH-word + Modal + Subject + Time + Infinitive.", "key_features": "V2 word order with modal; infinitive at end; Konjunktiv II möchtest for politeness."}
        },
        {
            "sentence": "Meine Mutter isst einen Apfel in der Küche.",
            "words": [
                {"word": "Meine", "grammatical_role": "adjective", "individual_meaning": "my (possessive adjective, nominative feminine)", "grammatical_case": "nominative", "gender": "f"},
                {"word": "Mutter", "grammatical_role": "noun", "individual_meaning": "mother (feminine noun, nominative)", "grammatical_case": "nominative", "gender": "f"},
                {"word": "isst", "grammatical_role": "verb", "individual_meaning": "eats (present tense, 3rd person singular of essen, vowel change e→i)", "tense": "present"},
                {"word": "einen", "grammatical_role": "article", "individual_meaning": "a/an (indefinite article, accusative masculine)", "grammatical_case": "accusative", "gender": "m"},
                {"word": "Apfel", "grammatical_role": "noun", "individual_meaning": "apple (masculine noun, accusative)", "grammatical_case": "accusative", "gender": "m"},
                {"word": "in", "grammatical_role": "preposition", "individual_meaning": "in (dative preposition for location)"},
                {"word": "der", "grammatical_role": "article", "individual_meaning": "the (definite article, dative feminine)", "grammatical_case": "dative", "gender": "f"},
                {"word": "Küche", "grammatical_role": "noun", "individual_meaning": "kitchen (feminine noun, dative)", "grammatical_case": "dative", "gender": "f"}
            ],
            "explanations": {"overall_structure": "SVO: Subject + Verb + Object (accusative) + Location (dative).", "key_features": "Strong verb vowel change isst; accusative einen for direct object; dative after in for location."}
        }
    ], ensure_ascii=False),
}


# ---------------------------------------------------------------------------
# ARABIC (RTL)
# ---------------------------------------------------------------------------
ARABIC_MOCK_DATA: Dict[str, Any] = {
    "word": "أكل",
    "language_name": "Arabic",
    "language_code": "ar",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 3,
    "max_length": 15,
    "difficulty": "beginner",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to eat (to consume food)

        RESTRICTIONS: Form I triliteral verb (أ-ك-ل). Past tense: أَكَلَ. Present: يَأْكُلُ.

        SENTENCES:
        1. أنا آكل الخبز كل صباح.
        2. الأطفال يأكلون في المدرسة.
        3. ماذا تريد أن تأكل الليلة؟
        4. أمي تأكل تفاحة في المطبخ.

        TRANSLATIONS:
        1. I eat bread every morning.
        2. The children eat at school.
        3. What do you want to eat tonight?
        4. My mother is eating an apple in the kitchen.

        ROMANIZATION:
        1. ana aakul al-khubz kull sabaah
        2. al-atfaal ya'kuluun fii al-madrasa
        3. maadha turiid an ta'kul al-layla
        4. ummi ta'kul tuffaaha fii al-matbakh

        KEYWORDS:
        1. bread plate, morning breakfast
        2. children school, lunch eating
        3. dinner question, food choices
        4. mother kitchen, red apple"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "أنا آكل الخبز كل صباح.",
            "words": [
                {"word": "أنا", "grammatical_role": "pronoun", "individual_meaning": "I (first person singular pronoun)"},
                {"word": "آكل", "grammatical_role": "verb", "individual_meaning": "eat (present tense, 1st person singular of أكل)"},
                {"word": "الخبز", "grammatical_role": "noun", "individual_meaning": "the bread (definite noun with ال)"},
                {"word": "كل", "grammatical_role": "adjective", "individual_meaning": "every/each (quantifier)"},
                {"word": "صباح", "grammatical_role": "noun", "individual_meaning": "morning (masculine noun)"}
            ],
            "explanations": {"overall_structure": "VSO with fronted subject: Subject + Verb + Object + Time.", "key_features": "Definite article ال on الخبز; present tense form آكل."}
        },
        {
            "sentence": "الأطفال يأكلون في المدرسة.",
            "words": [
                {"word": "الأطفال", "grammatical_role": "noun", "individual_meaning": "the children (definite plural noun with ال)"},
                {"word": "يأكلون", "grammatical_role": "verb", "individual_meaning": "they eat (present tense, 3rd person masculine plural)"},
                {"word": "في", "grammatical_role": "preposition", "individual_meaning": "in/at (preposition of location)"},
                {"word": "المدرسة", "grammatical_role": "noun", "individual_meaning": "the school (definite feminine noun with ال)"}
            ],
            "explanations": {"overall_structure": "SV with location: Subject + Verb + Prepositional phrase.", "key_features": "Plural verb ending -ون for masculine plural; definite article ال."}
        },
        {
            "sentence": "ماذا تريد أن تأكل الليلة؟",
            "words": [
                {"word": "ماذا", "grammatical_role": "pronoun", "individual_meaning": "what (interrogative pronoun)"},
                {"word": "تريد", "grammatical_role": "verb", "individual_meaning": "you want (present tense, 2nd person masculine singular of أراد)"},
                {"word": "أن", "grammatical_role": "particle", "individual_meaning": "to (subjunctive particle)"},
                {"word": "تأكل", "grammatical_role": "verb", "individual_meaning": "eat (subjunctive, 2nd person masculine singular)"},
                {"word": "الليلة", "grammatical_role": "noun", "individual_meaning": "tonight (definite feminine noun with ال)"}
            ],
            "explanations": {"overall_structure": "Interrogative: WH-word + Verb + أن + Subjunctive + Time.", "key_features": "أن triggers subjunctive mood; ماذا for 'what'."}
        },
        {
            "sentence": "أمي تأكل تفاحة في المطبخ.",
            "words": [
                {"word": "أمي", "grammatical_role": "noun", "individual_meaning": "my mother (noun with 1st person possessive suffix ي)"},
                {"word": "تأكل", "grammatical_role": "verb", "individual_meaning": "eats/is eating (present tense, 3rd person feminine singular)"},
                {"word": "تفاحة", "grammatical_role": "noun", "individual_meaning": "an apple (indefinite feminine noun)"},
                {"word": "في", "grammatical_role": "preposition", "individual_meaning": "in (preposition of location)"},
                {"word": "المطبخ", "grammatical_role": "noun", "individual_meaning": "the kitchen (definite masculine noun with ال)"}
            ],
            "explanations": {"overall_structure": "SVO: Subject + Verb + Object + Location.", "key_features": "Possessive suffix ي on أم; feminine verb form تأكل agrees with أمي; indefinite تفاحة."}
        }
    ], ensure_ascii=False),
}


# ---------------------------------------------------------------------------
# CHINESE SIMPLIFIED
# ---------------------------------------------------------------------------
CHINESE_SIMPLIFIED_MOCK_DATA: Dict[str, Any] = {
    "word": "吃",
    "language_name": "Chinese (Simplified)",
    "language_code": "zh",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 3,
    "max_length": 15,
    "difficulty": "beginner",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to eat (to consume food)

        RESTRICTIONS: No conjugation. Can take aspect markers 了 (completed), 过 (experienced), 着 (ongoing).

        SENTENCES:
        1. 我每天早上吃面包。
        2. 孩子们在学校吃午饭。
        3. 你想吃什么？
        4. 妈妈在厨房里吃苹果。

        TRANSLATIONS:
        1. I eat bread every morning.
        2. The children eat lunch at school.
        3. What do you want to eat?
        4. Mom is eating an apple in the kitchen.

        PINYIN:
        1. wǒ měitiān zǎoshang chī miànbāo
        2. háizimen zài xuéxiào chī wǔfàn
        3. nǐ xiǎng chī shénme
        4. māma zài chúfáng lǐ chī píngguǒ

        KEYWORDS:
        1. bread plate, morning breakfast
        2. children school, lunch tray
        3. food question, menu choices
        4. mother kitchen, apple fruit"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "我每天早上吃面包。",
            "words": [
                {"word": "我", "grammatical_role": "pronoun", "individual_meaning": "I/me (first person pronoun)"},
                {"word": "每天", "grammatical_role": "adverb", "individual_meaning": "every day (time adverb)"},
                {"word": "早上", "grammatical_role": "noun", "individual_meaning": "morning (time noun)"},
                {"word": "吃", "grammatical_role": "verb", "individual_meaning": "eat (action verb, no conjugation)"},
                {"word": "面包", "grammatical_role": "noun", "individual_meaning": "bread (compound noun)"}
            ],
            "explanations": {"overall_structure": "SVO: Subject + Time + Verb + Object.", "key_features": "Chinese SVO word order; no verb conjugation; time before verb."}
        },
        {
            "sentence": "孩子们在学校吃午饭。",
            "words": [
                {"word": "孩子们", "grammatical_role": "noun", "individual_meaning": "children (noun + plural suffix 们)"},
                {"word": "在", "grammatical_role": "preposition", "individual_meaning": "at/in (location preposition)"},
                {"word": "学校", "grammatical_role": "noun", "individual_meaning": "school (compound noun)"},
                {"word": "吃", "grammatical_role": "verb", "individual_meaning": "eat (action verb)"},
                {"word": "午饭", "grammatical_role": "noun", "individual_meaning": "lunch (compound noun: noon + meal)"}
            ],
            "explanations": {"overall_structure": "S + Location + V + O: Subject + 在 + Place + Verb + Object.", "key_features": "Location phrase 在学校 before verb; 们 plural marker."}
        },
        {
            "sentence": "你想吃什么？",
            "words": [
                {"word": "你", "grammatical_role": "pronoun", "individual_meaning": "you (second person pronoun)"},
                {"word": "想", "grammatical_role": "auxiliary_verb", "individual_meaning": "want to (modal/auxiliary verb)"},
                {"word": "吃", "grammatical_role": "verb", "individual_meaning": "eat (action verb)"},
                {"word": "什么", "grammatical_role": "pronoun", "individual_meaning": "what (interrogative pronoun)"}
            ],
            "explanations": {"overall_structure": "S + Aux + V + WH: Subject + Modal + Verb + Question word.", "key_features": "WH-word 什么 stays in-situ (not fronted); 想 + verb for desire."}
        },
        {
            "sentence": "妈妈在厨房里吃苹果。",
            "words": [
                {"word": "妈妈", "grammatical_role": "noun", "individual_meaning": "mom/mother (reduplicated kinship term)"},
                {"word": "在", "grammatical_role": "preposition", "individual_meaning": "at/in (location preposition)"},
                {"word": "厨房", "grammatical_role": "noun", "individual_meaning": "kitchen (compound noun)"},
                {"word": "里", "grammatical_role": "particle", "individual_meaning": "inside (localizer/postposition)"},
                {"word": "吃", "grammatical_role": "verb", "individual_meaning": "eat (action verb)"},
                {"word": "苹果", "grammatical_role": "noun", "individual_meaning": "apple (compound noun)"}
            ],
            "explanations": {"overall_structure": "S + Location + V + O: Subject + 在Place里 + Verb + Object.", "key_features": "Location phrase 在...里 wraps noun; localizer 里 specifies 'inside'."}
        }
    ], ensure_ascii=False),
}


# ---------------------------------------------------------------------------
# CHINESE TRADITIONAL
# ---------------------------------------------------------------------------
CHINESE_TRADITIONAL_MOCK_DATA: Dict[str, Any] = {
    "word": "吃",
    "language_name": "Chinese (Traditional)",
    "language_code": "zh-tw",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 3,
    "max_length": 15,
    "difficulty": "beginner",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to eat (to consume food)

        RESTRICTIONS: No conjugation. Can take aspect markers 了 (completed), 過 (experienced), 著 (ongoing).

        SENTENCES:
        1. 我每天早上吃麵包。
        2. 孩子們在學校吃午飯。
        3. 你想吃什麼？
        4. 媽媽在廚房裡吃蘋果。

        TRANSLATIONS:
        1. I eat bread every morning.
        2. The children eat lunch at school.
        3. What do you want to eat?
        4. Mom is eating an apple in the kitchen.

        PINYIN:
        1. wǒ měitiān zǎoshang chī miànbāo
        2. háizimen zài xuéxiào chī wǔfàn
        3. nǐ xiǎng chī shénme
        4. māma zài chúfáng lǐ chī píngguǒ

        KEYWORDS:
        1. bread plate, morning breakfast
        2. children school, lunch tray
        3. food question, menu choices
        4. mother kitchen, apple fruit"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "我每天早上吃麵包。",
            "words": [
                {"word": "我", "grammatical_role": "pronoun", "individual_meaning": "I/me (first person pronoun)"},
                {"word": "每天", "grammatical_role": "adverb", "individual_meaning": "every day (time adverb)"},
                {"word": "早上", "grammatical_role": "noun", "individual_meaning": "morning (time noun)"},
                {"word": "吃", "grammatical_role": "verb", "individual_meaning": "eat (action verb, no conjugation)"},
                {"word": "麵包", "grammatical_role": "noun", "individual_meaning": "bread (compound noun, Traditional form)"}
            ],
            "explanations": {"overall_structure": "SVO: Subject + Time + Verb + Object.", "key_features": "Chinese SVO word order; no verb conjugation; time before verb."}
        },
        {
            "sentence": "孩子們在學校吃午飯。",
            "words": [
                {"word": "孩子們", "grammatical_role": "noun", "individual_meaning": "children (noun + plural suffix 們)"},
                {"word": "在", "grammatical_role": "preposition", "individual_meaning": "at/in (location preposition)"},
                {"word": "學校", "grammatical_role": "noun", "individual_meaning": "school (Traditional form)"},
                {"word": "吃", "grammatical_role": "verb", "individual_meaning": "eat (action verb)"},
                {"word": "午飯", "grammatical_role": "noun", "individual_meaning": "lunch (compound: noon + meal, Traditional form)"}
            ],
            "explanations": {"overall_structure": "S + Location + V + O.", "key_features": "Location phrase 在學校 before verb; 們 plural marker."}
        },
        {
            "sentence": "你想吃什麼？",
            "words": [
                {"word": "你", "grammatical_role": "pronoun", "individual_meaning": "you (second person pronoun)"},
                {"word": "想", "grammatical_role": "auxiliary_verb", "individual_meaning": "want to (modal/auxiliary verb)"},
                {"word": "吃", "grammatical_role": "verb", "individual_meaning": "eat (action verb)"},
                {"word": "什麼", "grammatical_role": "pronoun", "individual_meaning": "what (interrogative pronoun, Traditional form)"}
            ],
            "explanations": {"overall_structure": "S + Aux + V + WH.", "key_features": "WH-word 什麼 stays in-situ; 想 + verb for desire."}
        },
        {
            "sentence": "媽媽在廚房裡吃蘋果。",
            "words": [
                {"word": "媽媽", "grammatical_role": "noun", "individual_meaning": "mom/mother (reduplicated kinship term)"},
                {"word": "在", "grammatical_role": "preposition", "individual_meaning": "at/in (location preposition)"},
                {"word": "廚房", "grammatical_role": "noun", "individual_meaning": "kitchen (Traditional form)"},
                {"word": "裡", "grammatical_role": "particle", "individual_meaning": "inside (localizer/postposition, Traditional form of 里)"},
                {"word": "吃", "grammatical_role": "verb", "individual_meaning": "eat (action verb)"},
                {"word": "蘋果", "grammatical_role": "noun", "individual_meaning": "apple (Traditional form)"}
            ],
            "explanations": {"overall_structure": "S + Location + V + O.", "key_features": "Location phrase 在...裡 wraps noun; Traditional characters throughout."}
        }
    ], ensure_ascii=False),
}


# ---------------------------------------------------------------------------
# HINDI
# ---------------------------------------------------------------------------
HINDI_MOCK_DATA: Dict[str, Any] = {
    "word": "खाना",
    "language_name": "Hindi",
    "language_code": "hi",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 3,
    "max_length": 15,
    "difficulty": "beginner",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to eat (to consume food); also means 'food' as a noun

        RESTRICTIONS: Verb agrees with gender and number of subject (or object in perfective with ने).

        SENTENCES:
        1. मैं हर सुबह रोटी खाता हूँ।
        2. बच्चे स्कूल में खाना खाते हैं।
        3. तुम क्या खाना चाहते हो?
        4. माँ रसोई में सेब खा रही है।

        TRANSLATIONS:
        1. I eat bread every morning.
        2. The children eat food at school.
        3. What do you want to eat?
        4. Mother is eating an apple in the kitchen.

        ROMANIZATION:
        1. main har subah rotee khaata hoon
        2. bachche school mein khaanaa khaate hain
        3. tum kya khaanaa chaahte ho
        4. maan rasoee mein seb khaa rahee hai

        KEYWORDS:
        1. bread plate, morning breakfast
        2. children school, lunch eating
        3. food question, menu choices
        4. mother kitchen, apple fruit"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "मैं हर सुबह रोटी खाता हूँ।",
            "words": [
                {"word": "मैं", "grammatical_role": "pronoun", "individual_meaning": "I (first person singular pronoun)"},
                {"word": "हर", "grammatical_role": "adjective", "individual_meaning": "every (quantifier adjective)"},
                {"word": "सुबह", "grammatical_role": "noun", "individual_meaning": "morning (feminine noun)"},
                {"word": "रोटी", "grammatical_role": "noun", "individual_meaning": "bread/chapati (feminine noun)"},
                {"word": "खाता", "grammatical_role": "verb", "individual_meaning": "eat (imperfective participle, masculine singular, agrees with subject)"},
                {"word": "हूँ", "grammatical_role": "auxiliary_verb", "individual_meaning": "am (present tense auxiliary, 1st person singular)"}
            ],
            "explanations": {"overall_structure": "SOV: Subject + Time + Object + Verb + Auxiliary.", "key_features": "Hindi SOV order; verb agrees with masculine subject (खाता); compound tense with auxiliary हूँ."}
        },
        {
            "sentence": "बच्चे स्कूल में खाना खाते हैं।",
            "words": [
                {"word": "बच्चे", "grammatical_role": "noun", "individual_meaning": "children (masculine plural noun, oblique/direct)"},
                {"word": "स्कूल", "grammatical_role": "noun", "individual_meaning": "school (masculine noun, borrowed from English)"},
                {"word": "में", "grammatical_role": "postposition", "individual_meaning": "in/at (location postposition)"},
                {"word": "खाना", "grammatical_role": "noun", "individual_meaning": "food (masculine noun; also means 'to eat' as infinitive)"},
                {"word": "खाते", "grammatical_role": "verb", "individual_meaning": "eat (imperfective participle, masculine plural)"},
                {"word": "हैं", "grammatical_role": "auxiliary_verb", "individual_meaning": "are (present tense auxiliary, 3rd person plural)"}
            ],
            "explanations": {"overall_structure": "SOV: Subject + Location + Object + Verb + Auxiliary.", "key_features": "Postposition में after noun; plural verb agreement खाते; compound tense."}
        },
        {
            "sentence": "तुम क्या खाना चाहते हो?",
            "words": [
                {"word": "तुम", "grammatical_role": "pronoun", "individual_meaning": "you (2nd person informal pronoun)"},
                {"word": "क्या", "grammatical_role": "pronoun", "individual_meaning": "what (interrogative pronoun)"},
                {"word": "खाना", "grammatical_role": "verb", "individual_meaning": "to eat (infinitive form)"},
                {"word": "चाहते", "grammatical_role": "verb", "individual_meaning": "want (imperfective participle, masculine plural, agrees with तुम)"},
                {"word": "हो", "grammatical_role": "auxiliary_verb", "individual_meaning": "are (present tense auxiliary, 2nd person informal)"}
            ],
            "explanations": {"overall_structure": "S + WH + Infinitive + Modal + Aux: Subject + क्या + Verb-infinitive + चाहना + Auxiliary.", "key_features": "WH-word क्या in-situ; चाहना + infinitive for 'want to'; SOV order preserved."}
        },
        {
            "sentence": "माँ रसोई में सेब खा रही है।",
            "words": [
                {"word": "माँ", "grammatical_role": "noun", "individual_meaning": "mother (feminine noun)"},
                {"word": "रसोई", "grammatical_role": "noun", "individual_meaning": "kitchen (feminine noun)"},
                {"word": "में", "grammatical_role": "postposition", "individual_meaning": "in (location postposition)"},
                {"word": "सेब", "grammatical_role": "noun", "individual_meaning": "apple (masculine noun)"},
                {"word": "खा", "grammatical_role": "verb", "individual_meaning": "eat (verb stem)"},
                {"word": "रही", "grammatical_role": "auxiliary_verb", "individual_meaning": "is (progressive marker, feminine singular, agrees with माँ)"},
                {"word": "है", "grammatical_role": "auxiliary_verb", "individual_meaning": "is (present tense auxiliary, 3rd person singular)"}
            ],
            "explanations": {"overall_structure": "SOV progressive: Subject + Location + Object + Verb stem + रहा/रही + है.", "key_features": "Progressive tense with रही (feminine agrees with माँ); postposition में; SOV order."}
        }
    ], ensure_ascii=False),
}


# ---------------------------------------------------------------------------
# TURKISH
# ---------------------------------------------------------------------------
TURKISH_MOCK_DATA: Dict[str, Any] = {
    "word": "yemek",
    "language_name": "Turkish",
    "language_code": "tr",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 3,
    "max_length": 15,
    "difficulty": "beginner",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to eat (to consume food); also means 'food/meal' as a noun

        RESTRICTIONS: Regular verb. Follows vowel harmony (back vowels: a, ı, o, u).

        SENTENCES:
        1. Ben her sabah ekmek yerim.
        2. Çocuklar okulda öğle yemeği yerler.
        3. Bu akşam ne yemek istiyorsun?
        4. Annem mutfakta elma yiyor.

        TRANSLATIONS:
        1. I eat bread every morning.
        2. The children eat lunch at school.
        3. What do you want to eat tonight?
        4. My mother is eating an apple in the kitchen.

        IPA:
        1. ben hæɾ sabah ecmec jeɾim
        2. tʃodʒuklaɾ okuldɑ øːle jemeji jeɾleɾ
        3. bu akʃam ne jemec istijɔɾsun
        4. annem mutfakta elma jijɔɾ

        KEYWORDS:
        1. bread plate, morning breakfast
        2. children school cafeteria, lunch
        3. dinner question, evening food
        4. mother kitchen, apple eating"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "Ben her sabah ekmek yerim.",
            "words": [
                {"word": "Ben", "grammatical_role": "pronoun", "individual_meaning": "I (1st person singular pronoun)"},
                {"word": "her", "grammatical_role": "adjective", "individual_meaning": "every (determiner/quantifier)"},
                {"word": "sabah", "grammatical_role": "noun", "individual_meaning": "morning (noun, no suffix needed for time expressions)"},
                {"word": "ekmek", "grammatical_role": "noun", "individual_meaning": "bread (noun, accusative unmarked — non-specific object)"},
                {"word": "yerim", "grammatical_role": "verb", "individual_meaning": "I eat (aorist tense -r + 1st person suffix -im of yemek)"}
            ],
            "explanations": {"overall_structure": "SOV: Subject + Time + Object + Verb.", "key_features": "Aorist tense for habitual action; unmarked accusative (non-specific object); SOV word order."}
        },
        {
            "sentence": "Çocuklar okulda öğle yemeği yerler.",
            "words": [
                {"word": "Çocuklar", "grammatical_role": "noun", "individual_meaning": "children (çocuk + plural suffix -lar)"},
                {"word": "okulda", "grammatical_role": "noun", "individual_meaning": "at school (okul + locative suffix -da, back vowel harmony)"},
                {"word": "öğle", "grammatical_role": "noun", "individual_meaning": "noon (noun, part of compound)"},
                {"word": "yemeği", "grammatical_role": "noun", "individual_meaning": "meal/food (yemek + possessive 3sg -i, compound noun: öğle yemeği = lunch)"},
                {"word": "yerler", "grammatical_role": "verb", "individual_meaning": "they eat (aorist ye-r + 3rd person plural -ler)"}
            ],
            "explanations": {"overall_structure": "SOV with location: Subject + Location + Object + Verb.", "key_features": "Locative suffix -da (back vowel); compound noun öğle yemeği; plural -lar/-ler follows vowel harmony."}
        },
        {
            "sentence": "Bu akşam ne yemek istiyorsun?",
            "words": [
                {"word": "Bu", "grammatical_role": "adjective", "individual_meaning": "this (demonstrative adjective)"},
                {"word": "akşam", "grammatical_role": "noun", "individual_meaning": "evening (noun, time expression)"},
                {"word": "ne", "grammatical_role": "pronoun", "individual_meaning": "what (interrogative pronoun)"},
                {"word": "yemek", "grammatical_role": "verb", "individual_meaning": "to eat (infinitive/verbal noun form)"},
                {"word": "istiyorsun", "grammatical_role": "verb", "individual_meaning": "you want (iste- + progressive -yor + 2sg -sun)"}
            ],
            "explanations": {"overall_structure": "Time + WH + Infinitive + Modal: Time + Question + Verb-infinitive + Want.", "key_features": "Progressive -yor for current desire; infinitive yemek as complement; SOV preserved in question."}
        },
        {
            "sentence": "Annem mutfakta elma yiyor.",
            "words": [
                {"word": "Annem", "grammatical_role": "noun", "individual_meaning": "my mother (anne + 1sg possessive suffix -m)"},
                {"word": "mutfakta", "grammatical_role": "noun", "individual_meaning": "in the kitchen (mutfak + locative suffix -ta, back vowel harmony)"},
                {"word": "elma", "grammatical_role": "noun", "individual_meaning": "apple (noun, accusative unmarked — non-specific)"},
                {"word": "yiyor", "grammatical_role": "verb", "individual_meaning": "is eating (yi- + progressive suffix -yor, no person suffix for 3sg)"}
            ],
            "explanations": {"overall_structure": "SOV: Subject + Location + Object + Verb.", "key_features": "Progressive -yor for ongoing action; possessive -m; locative -ta; vowel harmony throughout."}
        }
    ], ensure_ascii=False),
}


# ---------------------------------------------------------------------------
# MALAYALAM
# ---------------------------------------------------------------------------
MALAYALAM_MOCK_DATA: Dict[str, Any] = {
    "word": "കഴിക്കുക",
    "language_name": "Malayalam",
    "language_code": "ml",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 8,
    "max_length": 13,
    "difficulty": "beginner",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to eat (to consume food)

        RESTRICTIONS: No specific grammatical restrictions.

        SENTENCES:
        1. ഞാൻ എല്ലാ ദിവസവും ചോറ് കഴിക്കുന്നു.
        2. കുട്ടികൾ സ്കൂളിൽ ഉച്ചഭക്ഷണം കഴിക്കുന്നു.
        3. നിങ്ങൾ എന്ത് കഴിക്കാൻ ഇഷ്ടപ്പെടുന്നു?
        4. അമ്മ അടുക്കളയിൽ ആപ്പിൾ കഴിക്കുന്നു.

        TRANSLATIONS:
        1. I eat rice every day.
        2. The children eat lunch at school.
        3. What do you like to eat?
        4. Mother is eating an apple in the kitchen.

        IPA:
        1. ɲaːn ellaː d̪ivasavum t͡ʃoːɾɨ kaɻikkunnɨ
        2. kuʈʈikaɭ skuːɭil ut͡ʃːabʰakʂaɳam kaɻikkunnɨ
        3. niŋːaɭ entɨ kaɻikkaːn iʂʈappeɖunnɨ
        4. amːa aɖukkaɭajil aːpːiɭ kaɻikkunnɨ

        KEYWORDS:
        1. rice plate, daily meal, eating rice
        2. children in cafeteria, school lunch, eating together
        3. food choices, question, restaurant menu
        4. woman in kitchen, red apple, eating fruit"""),

    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "ഞാൻ എല്ലാ ദിവസവും ചോറ് കഴിക്കുന്നു.",
            "words": [
                {"word": "ഞാൻ", "grammatical_role": "pronoun", "case": "nominative", "tense": None, "individual_meaning": "I (first person singular pronoun, nominative)"},
                {"word": "എല്ലാ", "grammatical_role": "determiner", "case": None, "tense": None, "individual_meaning": "every, all (determiner modifying ദിവസം)"},
                {"word": "ദിവസവും", "grammatical_role": "noun", "case": "nominative", "tense": None, "individual_meaning": "day + -ഉം (emphatic/inclusive particle meaning 'also/every')"},
                {"word": "ചോറ്", "grammatical_role": "noun", "case": "accusative", "tense": None, "individual_meaning": "rice (direct object, unmarked accusative for inanimate)"},
                {"word": "കഴിക്കുന്നു", "grammatical_role": "verb", "case": None, "tense": "present", "individual_meaning": "eat (present tense, habitual — stem കഴിക്ക + present suffix -ഉന്നു)"}
            ],
            "explanations": {
                "overall_structure": "SOV sentence: Subject (ഞാൻ) + Time (എല്ലാ ദിവസവും) + Object (ചോറ്) + Verb (കഴിക്കുന്നു).",
                "key_features": "SOV word order; emphatic particle -ഉം on time expression; present tense suffix -ഉന്നു; unmarked accusative for inanimate object.",
                "complexity_notes": "Beginner-friendly sentence with basic SOV order and present tense."
            }
        },
        {
            "sentence": "കുട്ടികൾ സ്കൂളിൽ ഉച്ചഭക്ഷണം കഴിക്കുന്നു.",
            "words": [
                {"word": "കുട്ടികൾ", "grammatical_role": "noun", "case": "nominative", "tense": None, "individual_meaning": "children (plural — കുട്ടി + plural suffix -കൾ, nominative subject)"},
                {"word": "സ്കൂളിൽ", "grammatical_role": "noun", "case": "locative", "tense": None, "individual_meaning": "in school (സ്കൂൾ + locative case suffix -ഇൽ)"},
                {"word": "ഉച്ചഭക്ഷണം", "grammatical_role": "noun", "case": "accusative", "tense": None, "individual_meaning": "lunch (compound noun: ഉച്ച 'noon' + ഭക്ഷണം 'food', direct object)"},
                {"word": "കഴിക്കുന്നു", "grammatical_role": "verb", "case": None, "tense": "present", "individual_meaning": "eat (present tense, habitual)"}
            ],
            "explanations": {
                "overall_structure": "SOV with location: Subject (കുട്ടികൾ) + Location-LOC (സ്കൂളിൽ) + Object (ഉച്ചഭക്ഷണം) + Verb (കഴിക്കുന്നു).",
                "key_features": "Locative case suffix -ഇൽ on സ്കൂൾ; plural suffix -കൾ; compound noun ഉച്ചഭക്ഷണം.",
                "complexity_notes": "Beginner pattern with locative case and plural noun."
            }
        },
        {
            "sentence": "നിങ്ങൾ എന്ത് കഴിക്കാൻ ഇഷ്ടപ്പെടുന്നു?",
            "words": [
                {"word": "നിങ്ങൾ", "grammatical_role": "pronoun", "case": "nominative", "tense": None, "individual_meaning": "you (polite/plural second person pronoun)"},
                {"word": "എന്ത്", "grammatical_role": "pronoun", "case": "accusative", "tense": None, "individual_meaning": "what (interrogative pronoun)"},
                {"word": "കഴിക്കാൻ", "grammatical_role": "infinitive", "case": None, "tense": None, "individual_meaning": "to eat (infinitive — stem കഴിക്ക + infinitive suffix -ാൻ)"},
                {"word": "ഇഷ്ടപ്പെടുന്നു", "grammatical_role": "verb", "case": None, "tense": "present", "individual_meaning": "like (present tense — ഇഷ്ടപ്പെടുക 'to like' + present suffix -ഉന്നു)"}
            ],
            "explanations": {
                "overall_structure": "Question: Subject (നിങ്ങൾ) + WH-word (എന്ത്) + Infinitive (കഴിക്കാൻ) + Main Verb (ഇഷ്ടപ്പെടുന്നു).",
                "key_features": "Polite pronoun നിങ്ങൾ; infinitive complement with -ാൻ suffix; WH-question without special marking.",
                "complexity_notes": "Beginner question with infinitive complement."
            }
        },
        {
            "sentence": "അമ്മ അടുക്കളയിൽ ആപ്പിൾ കഴിക്കുന്നു.",
            "words": [
                {"word": "അമ്മ", "grammatical_role": "noun", "case": "nominative", "tense": None, "individual_meaning": "mother (nominative subject)"},
                {"word": "അടുക്കളയിൽ", "grammatical_role": "noun", "case": "locative", "tense": None, "individual_meaning": "in the kitchen (അടുക്കള + locative suffix -യിൽ)"},
                {"word": "ആപ്പിൾ", "grammatical_role": "noun", "case": "accusative", "tense": None, "individual_meaning": "apple (direct object, loanword from English)"},
                {"word": "കഴിക്കുന്നു", "grammatical_role": "verb", "case": None, "tense": "present", "individual_meaning": "eat (present tense, ongoing action)"}
            ],
            "explanations": {
                "overall_structure": "SOV with location: Subject (അമ്മ) + Location-LOC (അടുക്കളയിൽ) + Object (ആപ്പിൾ) + Verb (കഴിക്കുന്നു).",
                "key_features": "Locative -യിൽ after vowel-ending stem; loanword ആപ്പിൾ; basic SOV.",
                "complexity_notes": "Beginner — locative case and SOV word order."
            }
        }
    ], ensure_ascii=False),
}


# ---------------------------------------------------------------------------
# LATVIAN
# ---------------------------------------------------------------------------
LATVIAN_MOCK_DATA: Dict[str, Any] = {
    "word": "runāt",
    "language_name": "Latvian",
    "language_code": "lv",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 3,
    "max_length": 15,
    "difficulty": "beginner",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to speak (to talk, to use language)

        RESTRICTIONS: Regular verb. Keep sentences natural and beginner-friendly.

        SENTENCES:
        1. Es runāju latviski.
        2. Mēs runājam skolā.
        3. Kāpēc tu runā tik ātri?
        4. Viņi vakar runāja par ēdienu.

        TRANSLATIONS:
        1. I speak Latvian.
        2. We speak at school.
        3. Why do you speak so quickly?
        4. They spoke about food yesterday.

        IPA:
        1. ɛs runaːju latviski
        2. meːs runaːjam skolaː
        3. kaːpɛts tu runaː tik aːtri
        4. vinji vakar runaːja par eːdienu

        KEYWORDS:
        1. person speaking, Latvian language
        2. students talking at school
        3. fast speech, question
        4. group discussion, food topic"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "Es runāju latviski.",
            "overall_structure": "Subject-Verb-Adverb",
            "sentence_structure": "Subject-Verb-Adverb",
            "word_explanations": [
                {"word": "Es", "grammatical_role": "personal_pronoun", "color": "#9370DB", "meaning": "I (1st person singular)", "case": "nominative", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "runāju", "grammatical_role": "verb", "color": "#4ECDC4", "meaning": "speak (1st person singular present)", "case": "", "gender": "", "number": "singular", "tense": "present", "definite_form": ""},
                {"word": "latviski", "grammatical_role": "adverb", "color": "#FF6347", "meaning": "in Latvian (manner adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Basic SVO sentence in present tense.",
            "confidence": 0.92
        },
        {
            "sentence": "Mēs runājam skolā.",
            "overall_structure": "Subject-Verb-Locative",
            "sentence_structure": "Subject-Verb-Locative",
            "word_explanations": [
                {"word": "Mēs", "grammatical_role": "personal_pronoun", "color": "#9370DB", "meaning": "we (1st person plural)", "case": "nominative", "gender": "", "number": "plural", "tense": "", "definite_form": ""},
                {"word": "runājam", "grammatical_role": "verb", "color": "#4ECDC4", "meaning": "speak (1st person plural present)", "case": "", "gender": "", "number": "plural", "tense": "present", "definite_form": ""},
                {"word": "skolā", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "at school (locative singular)", "case": "locative", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Locative case -ā marks place.",
            "confidence": 0.90
        },
        {
            "sentence": "Kāpēc tu runā tik ātri?",
            "overall_structure": "Question-Adverb-Subject-Verb-Adverb-Adverb",
            "sentence_structure": "Question with adverbial intensifier",
            "word_explanations": [
                {"word": "Kāpēc", "grammatical_role": "adverb", "color": "#FF6347", "meaning": "why (question adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "tu", "grammatical_role": "personal_pronoun", "color": "#9370DB", "meaning": "you (2nd person singular)", "case": "nominative", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "runā", "grammatical_role": "verb", "color": "#4ECDC4", "meaning": "speak (2nd/3rd person present context-dependent)", "case": "", "gender": "", "number": "singular", "tense": "present", "definite_form": ""},
                {"word": "tik", "grammatical_role": "particle", "color": "#DC143C", "meaning": "so (degree particle)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "ātri", "grammatical_role": "adverb", "color": "#FF6347", "meaning": "quickly (manner adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Question word kāpēc introduces a direct question.",
            "confidence": 0.89
        },
        {
            "sentence": "Viņi vakar runāja par ēdienu.",
            "overall_structure": "Subject-Time-Verb-Preposition-Object",
            "sentence_structure": "Past tense clause with prepositional object",
            "word_explanations": [
                {"word": "Viņi", "grammatical_role": "personal_pronoun", "color": "#9370DB", "meaning": "they (3rd person plural)", "case": "nominative", "gender": "", "number": "plural", "tense": "", "definite_form": ""},
                {"word": "vakar", "grammatical_role": "adverb", "color": "#FF6347", "meaning": "yesterday (time adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "runāja", "grammatical_role": "verb", "color": "#4ECDC4", "meaning": "spoke (past tense)", "case": "", "gender": "", "number": "plural", "tense": "past", "definite_form": ""},
                {"word": "par", "grammatical_role": "preposition", "color": "#32CD32", "meaning": "about (preposition requiring accusative)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "ēdienu", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "food (accusative singular)", "case": "accusative", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Past tense verb with preposition par + accusative object.",
            "confidence": 0.90
        }
    ], ensure_ascii=False),
}


# ---------------------------------------------------------------------------
# LATVIAN — per-difficulty mock data
# ---------------------------------------------------------------------------
# Latvian's analyzer config exposes distinct grammatical-role vocabularies for
# each complexity level (lv_config._get_default_roles). To validate that the
# analyzer + grammar processor stay coherent at every level, we run the full
# pipeline three times — once each with beginner, intermediate, and advanced
# session_state["difficulty"] — and feed level-appropriate role tags through
# the mock grammar response.
#
# beginner mock = LATVIAN_MOCK_DATA (defined above) — kept as the default
#                 entry in LANGUAGE_MOCK_DATA so the original parametrized
#                 test still runs.
# ---------------------------------------------------------------------------

_LATVIAN_INTERMEDIATE_MOCK: Dict[str, Any] = {
    "word": "runāt",
    "language_name": "Latvian",
    "language_code": "lv",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 4,
    "max_length": 18,
    "difficulty": "intermediate",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to speak (to talk, to use language)

        RESTRICTIONS: Use intermediate-level structures: prepositions, demonstratives, particles.

        SENTENCES:
        1. Mēs vakar runājām ar draugiem.
        2. Šī meitene runā ļoti skaisti.
        3. Es runāšu ar tevi rīt.
        4. Viņa runā tik ātri!

        TRANSLATIONS:
        1. We spoke with friends yesterday.
        2. This girl speaks very beautifully.
        3. I will speak with you tomorrow.
        4. She speaks so fast!

        IPA:
        1. meːs vakar runaːjaːm ar draugiɛm
        2. ʃiː mɛitɛnɛ runaː ļoti skaisti
        3. ɛs runaːʃu ar tɛvi riːt
        4. viɲa runaː tik aːtri

        KEYWORDS:
        1. friends conversation, yesterday
        2. young girl speaking
        3. future conversation, tomorrow
        4. fast speech, surprise"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "Mēs vakar runājām ar draugiem.",
            "overall_structure": "Subject-Time-Verb-Preposition-Object",
            "sentence_structure": "Past-tense clause with prepositional object",
            "word_explanations": [
                {"word": "Mēs", "grammatical_role": "personal_pronoun", "color": "#9370DB", "meaning": "we (1st person plural nominative)", "case": "nominative", "gender": "", "number": "plural", "tense": "", "definite_form": ""},
                {"word": "vakar", "grammatical_role": "adverb", "color": "#FF6347", "meaning": "yesterday (time adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "runājām", "grammatical_role": "verb", "color": "#4ECDC4", "meaning": "spoke (1st person plural past)", "case": "", "gender": "", "number": "plural", "tense": "past", "definite_form": ""},
                {"word": "ar", "grammatical_role": "preposition", "color": "#4444FF", "meaning": "with (preposition + instrumental/dative plural)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "draugiem", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "friends (dative plural)", "case": "dative", "gender": "masculine", "number": "plural", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Past tense plural with prepositional dative object.",
            "confidence": 0.91
        },
        {
            "sentence": "Šī meitene runā ļoti skaisti.",
            "overall_structure": "Demonstrative-Subject-Verb-Adverb-Adverb",
            "sentence_structure": "Demonstrative noun phrase modified by intensifier and manner adverb",
            "word_explanations": [
                {"word": "Šī", "grammatical_role": "demonstrative", "color": "#B8860B", "meaning": "this (feminine singular nominative)", "case": "nominative", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "meitene", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "girl (nominative singular feminine)", "case": "nominative", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "runā", "grammatical_role": "verb", "color": "#4ECDC4", "meaning": "speaks (3rd person singular present)", "case": "", "gender": "", "number": "singular", "tense": "present", "definite_form": ""},
                {"word": "ļoti", "grammatical_role": "particle", "color": "#20B2AA", "meaning": "very (intensifier particle)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "skaisti", "grammatical_role": "adverb", "color": "#FF6347", "meaning": "beautifully (manner adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Demonstrative agrees with feminine singular subject; intensifier particle precedes manner adverb.",
            "confidence": 0.90
        },
        {
            "sentence": "Es runāšu ar tevi rīt.",
            "overall_structure": "Subject-Verb-Preposition-Object-Time",
            "sentence_structure": "Future-tense clause with prepositional object",
            "word_explanations": [
                {"word": "Es", "grammatical_role": "personal_pronoun", "color": "#9370DB", "meaning": "I (1st person singular nominative)", "case": "nominative", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "runāšu", "grammatical_role": "verb", "color": "#4ECDC4", "meaning": "will speak (1st person singular future)", "case": "", "gender": "", "number": "singular", "tense": "future", "definite_form": ""},
                {"word": "ar", "grammatical_role": "preposition", "color": "#4444FF", "meaning": "with (preposition + accusative)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "tevi", "grammatical_role": "personal_pronoun", "color": "#9370DB", "meaning": "you (2nd person singular accusative)", "case": "accusative", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "rīt", "grammatical_role": "adverb", "color": "#FF6347", "meaning": "tomorrow (time adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Future tense -šu ending; preposition ar takes accusative for personal pronouns.",
            "confidence": 0.92
        },
        {
            "sentence": "Viņa runā tik ātri!",
            "overall_structure": "Subject-Verb-Particle-Adverb",
            "sentence_structure": "Exclamative clause with degree particle",
            "word_explanations": [
                {"word": "Viņa", "grammatical_role": "personal_pronoun", "color": "#9370DB", "meaning": "she (3rd person singular feminine nominative)", "case": "nominative", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "runā", "grammatical_role": "verb", "color": "#4ECDC4", "meaning": "speaks (3rd person singular present)", "case": "", "gender": "", "number": "singular", "tense": "present", "definite_form": ""},
                {"word": "tik", "grammatical_role": "particle", "color": "#20B2AA", "meaning": "so (degree particle)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "ātri", "grammatical_role": "adverb", "color": "#FF6347", "meaning": "quickly (manner adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Exclamation with intensifying particle tik before manner adverb.",
            "confidence": 0.90
        }
    ], ensure_ascii=False),
}


_LATVIAN_ADVANCED_MOCK: Dict[str, Any] = {
    "word": "runāt",
    "language_name": "Latvian",
    "language_code": "lv",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 5,
    "max_length": 22,
    "difficulty": "advanced",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to speak (to talk, to use language)

        RESTRICTIONS: Use advanced structures: participles, debitive, subordinate clauses, relative pronouns.

        SENTENCES:
        1. Runājot ar viņu, es sapratu patiesību.
        2. Man jārunā ar skolotāju, kurš mācīja matemātiku.
        3. Lai gan viņš runāja klusi, neviens neklausījās.
        4. Cilvēki, kuri runā ātri, dažreiz tiek pārprasti.

        TRANSLATIONS:
        1. While speaking with him, I understood the truth.
        2. I must speak with the teacher who taught mathematics.
        3. Although he spoke quietly, no one listened.
        4. People who speak quickly are sometimes misunderstood.

        IPA:
        1. runaːjot ar viɲu ɛs sapratu patiesiːbu
        2. man jaːrunaː ar skolotaːju kurʃ maːtsiːja matemaːtiku
        3. lai gan viɲʃ runaːja klusi nɛviɛns nɛklausiːjaːs
        4. tsilvɛːki kuri runaː aːtri daʒrɛiz tiɛk paːrprasti

        KEYWORDS:
        1. realization, conversation
        2. obligation, teacher, classroom
        3. quiet speech, ignored
        4. misunderstanding, fast talkers"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "Runājot ar viņu, es sapratu patiesību.",
            "overall_structure": "Participle-Preposition-Object, Subject-Verb-Object",
            "sentence_structure": "Adverbial participle clause + main clause",
            "word_explanations": [
                {"word": "Runājot", "grammatical_role": "participle", "color": "#FF8C00", "meaning": "while speaking (gerund / adverbial participle -ot)", "case": "", "gender": "", "number": "", "tense": "present", "definite_form": ""},
                {"word": "ar", "grammatical_role": "preposition", "color": "#4444FF", "meaning": "with (preposition + accusative)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "viņu", "grammatical_role": "personal_pronoun", "color": "#9370DB", "meaning": "him (3rd person singular accusative)", "case": "accusative", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "es", "grammatical_role": "personal_pronoun", "color": "#9370DB", "meaning": "I (1st person singular nominative)", "case": "nominative", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "sapratu", "grammatical_role": "verb", "color": "#4ECDC4", "meaning": "understood (1st person singular past)", "case": "", "gender": "", "number": "singular", "tense": "past", "definite_form": ""},
                {"word": "patiesību", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "truth (accusative singular feminine)", "case": "accusative", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Adverbial participle in -ot expresses concurrent action with the main past-tense clause.",
            "confidence": 0.93
        },
        {
            "sentence": "Man jārunā ar skolotāju, kurš mācīja matemātiku.",
            "overall_structure": "Dative-Debitive-Preposition-Object, Relative-Verb-Object",
            "sentence_structure": "Debitive construction with relative subordinate clause",
            "word_explanations": [
                {"word": "Man", "grammatical_role": "personal_pronoun", "color": "#9370DB", "meaning": "to me (1st person singular dative)", "case": "dative", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "jārunā", "grammatical_role": "debitive", "color": "#FF1493", "meaning": "must speak (debitive mood)", "case": "", "gender": "", "number": "", "tense": "present", "definite_form": ""},
                {"word": "ar", "grammatical_role": "preposition", "color": "#4444FF", "meaning": "with (preposition + accusative)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "skolotāju", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "teacher (accusative singular masculine)", "case": "accusative", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "kurš", "grammatical_role": "relative_pronoun", "color": "#9370DB", "meaning": "who (relative pronoun, masculine singular nominative)", "case": "nominative", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "mācīja", "grammatical_role": "verb", "color": "#4ECDC4", "meaning": "taught (3rd person singular past)", "case": "", "gender": "", "number": "singular", "tense": "past", "definite_form": ""},
                {"word": "matemātiku", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "mathematics (accusative singular feminine)", "case": "accusative", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Debitive jā- + verb root expresses obligation; subject in dative. Relative clause introduced by kurš agrees with antecedent in gender/number.",
            "confidence": 0.92
        },
        {
            "sentence": "Lai gan viņš runāja klusi, neviens neklausījās.",
            "overall_structure": "Subordinator-Subject-Verb-Adverb, Indef-Verb",
            "sentence_structure": "Concessive subordinate clause + main clause with reflexive verb",
            "word_explanations": [
                {"word": "Lai gan", "grammatical_role": "subordinating_conjunction", "color": "#888888", "meaning": "although (concessive subordinator)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "viņš", "grammatical_role": "personal_pronoun", "color": "#9370DB", "meaning": "he (3rd person singular masculine nominative)", "case": "nominative", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "runāja", "grammatical_role": "verb", "color": "#4ECDC4", "meaning": "spoke (3rd person singular past)", "case": "", "gender": "", "number": "singular", "tense": "past", "definite_form": ""},
                {"word": "klusi", "grammatical_role": "adverb", "color": "#FF6347", "meaning": "quietly (manner adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "neviens", "grammatical_role": "indefinite_pronoun", "color": "#8B7EC8", "meaning": "no one (negative indefinite pronoun, masculine singular nominative)", "case": "nominative", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "neklausījās", "grammatical_role": "reflexive_verb", "color": "#20B2AA", "meaning": "did not listen (reflexive verb, 3rd person past, negated)", "case": "", "gender": "", "number": "singular", "tense": "past", "definite_form": ""}
            ],
            "grammar_notes": "Concessive subordinator lai gan introduces a clause; main clause uses negated reflexive verb (-ās ending).",
            "confidence": 0.91
        },
        {
            "sentence": "Cilvēki, kuri runā ātri, dažreiz tiek pārprasti.",
            "overall_structure": "Subject-[Relative-Verb-Adverb]-Adverb-Auxiliary-Participle",
            "sentence_structure": "Subject with restrictive relative clause + passive periphrastic main verb",
            "word_explanations": [
                {"word": "Cilvēki", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "people (nominative plural masculine)", "case": "nominative", "gender": "masculine", "number": "plural", "tense": "", "definite_form": ""},
                {"word": "kuri", "grammatical_role": "relative_pronoun", "color": "#9370DB", "meaning": "who (relative pronoun, masculine plural nominative)", "case": "nominative", "gender": "masculine", "number": "plural", "tense": "", "definite_form": ""},
                {"word": "runā", "grammatical_role": "verb", "color": "#4ECDC4", "meaning": "speak (3rd person plural present)", "case": "", "gender": "", "number": "plural", "tense": "present", "definite_form": ""},
                {"word": "ātri", "grammatical_role": "adverb", "color": "#FF6347", "meaning": "quickly (manner adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "dažreiz", "grammatical_role": "adverb", "color": "#FF6347", "meaning": "sometimes (frequency adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "tiek", "grammatical_role": "auxiliary", "color": "#00CED1", "meaning": "is/are being (auxiliary, 3rd person present)", "case": "", "gender": "", "number": "", "tense": "present", "definite_form": ""},
                {"word": "pārprasti", "grammatical_role": "participle", "color": "#FF8C00", "meaning": "misunderstood (past passive participle, masculine plural nominative)", "case": "nominative", "gender": "masculine", "number": "plural", "tense": "past", "definite_form": ""}
            ],
            "grammar_notes": "Periphrastic passive: tiek + past passive participle. Relative clause kuri runā ātri restricts the subject Cilvēki.",
            "confidence": 0.92
        }
    ], ensure_ascii=False),
}


# beginner reuses LATVIAN_MOCK_DATA so reports / role coverage stay in sync.
LATVIAN_LEVEL_MOCK_DATA: Dict[str, Dict[str, Any]] = {
    "beginner": LATVIAN_MOCK_DATA,
    "intermediate": _LATVIAN_INTERMEDIATE_MOCK,
    "advanced": _LATVIAN_ADVANCED_MOCK,
}


# ---------------------------------------------------------------------------
# PORTUGUESE
# ---------------------------------------------------------------------------
PORTUGUESE_MOCK_DATA: Dict[str, Any] = {
    "word": "falar",
    "language_name": "Portuguese",
    "language_code": "pt",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 3,
    "max_length": 15,
    "difficulty": "beginner",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to speak (to talk, to say words)

        RESTRICTIONS: Regular -ar verb. Keep sentences simple and beginner-friendly.

        SENTENCES:
        1. Eu falo português.
        2. Nós falamos na escola.
        3. Por que você fala tão rápido?
        4. Eles falaram sobre comida ontem.

        TRANSLATIONS:
        1. I speak Portuguese.
        2. We speak at school.
        3. Why do you speak so fast?
        4. They spoke about food yesterday.

        IPA:
        1. ew ˈfalu poɾtuˈɡes
        2. ˈnɔs faˈlɐ̃muʃ na eʃˈkɔlɐ
        3. poɾ ke voˈse ˈfalɐ tɐ̃w ˈʁapidu
        4. ˈelɨʃ faˈlaɾɐ̃w ˈsobɾɨ koˈmidɐ ˈõtẽj

        KEYWORDS:
        1. person speaking, Portuguese language
        2. students talking, school setting
        3. speed, question
        4. group conversation, food topic"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "Eu falo português.",
            "overall_structure": "Subject-Verb-Object",
            "sentence_structure": "Subject-Verb-Object",
            "word_explanations": [
                {"word": "Eu", "grammatical_role": "pronoun", "color": "#FF4444", "meaning": "I (1st person singular subject pronoun)", "case": "", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "falo", "grammatical_role": "verb", "color": "#44FF44", "meaning": "speak (1st person singular present indicative)", "case": "", "gender": "", "number": "singular", "tense": "present", "definite_form": ""},
                {"word": "português", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "Portuguese (the language)", "case": "", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Simple SVO sentence. Pro-drop means 'Eu' is optional but included here for clarity.",
            "confidence": 0.93
        },
        {
            "sentence": "Nós falamos na escola.",
            "overall_structure": "Subject-Verb-Preposition-Noun",
            "sentence_structure": "Subject-Verb-Locative",
            "word_explanations": [
                {"word": "Nós", "grammatical_role": "pronoun", "color": "#FF4444", "meaning": "we (1st person plural subject pronoun)", "case": "", "gender": "", "number": "plural", "tense": "", "definite_form": ""},
                {"word": "falamos", "grammatical_role": "verb", "color": "#44FF44", "meaning": "speak / we speak (1st person plural present indicative)", "case": "", "gender": "", "number": "plural", "tense": "present", "definite_form": ""},
                {"word": "na", "grammatical_role": "preposition", "color": "#4444FF", "meaning": "at/in the — contraction of em + a (feminine)", "case": "", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "escola", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "school (feminine singular)", "case": "", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Locative phrase 'na escola' uses the obligatory contraction na (em + a).",
            "confidence": 0.91
        },
        {
            "sentence": "Por que você fala tão rápido?",
            "overall_structure": "Question-Subject-Verb-Adverb-Adverb",
            "sentence_structure": "Interrogative clause with adverbial intensifier",
            "word_explanations": [
                {"word": "Por que", "grammatical_role": "conjunction", "color": "#888888", "meaning": "why (question word)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "você", "grammatical_role": "pronoun", "color": "#FF4444", "meaning": "you (2nd person singular, BR register)", "case": "", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "fala", "grammatical_role": "verb", "color": "#44FF44", "meaning": "speak (3rd person singular present indicative)", "case": "", "gender": "", "number": "singular", "tense": "present", "definite_form": ""},
                {"word": "tão", "grammatical_role": "adverb", "color": "#44FFFF", "meaning": "so / as (degree adverb before adjective/adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "rápido", "grammatical_role": "adverb", "color": "#44FFFF", "meaning": "fast / quickly (manner adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Você requires 3rd-person conjugation. Tão + adjective/adverb = intensifier.",
            "confidence": 0.90
        },
        {
            "sentence": "Eles falaram sobre comida ontem.",
            "overall_structure": "Subject-Verb-Preposition-Object-Adverb",
            "sentence_structure": "Past tense clause with prepositional object",
            "word_explanations": [
                {"word": "Eles", "grammatical_role": "pronoun", "color": "#FF4444", "meaning": "they (3rd person plural masculine)", "case": "", "gender": "masculine", "number": "plural", "tense": "", "definite_form": ""},
                {"word": "falaram", "grammatical_role": "verb", "color": "#44FF44", "meaning": "spoke (3rd person plural preterite)", "case": "", "gender": "", "number": "plural", "tense": "past", "definite_form": ""},
                {"word": "sobre", "grammatical_role": "preposition", "color": "#4444FF", "meaning": "about / on (preposition)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "comida", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "food (feminine singular)", "case": "", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "ontem", "grammatical_role": "adverb", "color": "#44FFFF", "meaning": "yesterday (time adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Preterite (pretérito perfeito) used for completed past action.",
            "confidence": 0.92
        }
    ], ensure_ascii=False),
}


# ---------------------------------------------------------------------------
# PORTUGUESE — per-difficulty mock data
# ---------------------------------------------------------------------------
# Portuguese exposes distinct grammatical-role vocabularies per complexity
# level (pt_config._get_default_roles). To validate analyzer + grammar
# processor coherence at every level, we run the full pipeline three times —
# once each for beginner, intermediate, and advanced — feeding level-
# appropriate role tags through the mock grammar response.
#
# beginner mock = PORTUGUESE_MOCK_DATA (defined above) — kept as the default
#                 entry in LANGUAGE_MOCK_DATA so the original parametrized
#                 test still runs.
# ---------------------------------------------------------------------------

_PORTUGUESE_INTERMEDIATE_MOCK: Dict[str, Any] = {
    "word": "falar",
    "language_name": "Portuguese",
    "language_code": "pt",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 4,
    "max_length": 18,
    "difficulty": "intermediate",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to speak (to talk, to use language)

        RESTRICTIONS: Use intermediate structures: personal pronouns, copulas ser/estar, contractions, auxiliary verbs.

        SENTENCES:
        1. Ela está falando ao telefone agora.
        2. Eu sou brasileiro e falo três línguas.
        3. Nós vamos falar com o professor amanhã.
        4. Você não se lembra de mim?

        TRANSLATIONS:
        1. She is speaking on the phone right now.
        2. I am Brazilian and I speak three languages.
        3. We are going to speak with the teacher tomorrow.
        4. Don't you remember me?

        IPA:
        1. ˈɛlɐ ˈɛʃtɐ faˈlɐ̃du aw teleˈfɔnɨ ɐˈgoɾɐ
        2. ew ˈsow bɾaziˈlejɾu i ˈfalu ˈtɾeʃ ˈlĩŋɡwɐʃ
        3. ˈnɔs ˈvɐ̃muʃ faˈlaɾ kõ u pɾoˈfɛsoɾ ɐˈmɐ̃ɲɐ
        4. voˈse nɐ̃w sɨ ˈlẽbɾɐ dɨ ˈmĩ

        KEYWORDS:
        1. phone call, present progressive
        2. nationality, multilingual
        3. near future, teacher
        4. memory, reflexive verb"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "Ela está falando ao telefone agora.",
            "overall_structure": "Subject-Copula-Gerund-Contraction-Object-Adverb",
            "sentence_structure": "Present progressive with locative prepositional phrase",
            "word_explanations": [
                {"word": "Ela", "grammatical_role": "personal_pronoun", "color": "#FF4444", "meaning": "she (3rd person singular feminine)", "case": "", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "está", "grammatical_role": "copula", "color": "#00B894", "meaning": "is (estar, 3rd person singular present — temporary state/progressive)", "case": "", "gender": "", "number": "singular", "tense": "present", "definite_form": "", "copula_type": "estar"},
                {"word": "falando", "grammatical_role": "verb", "color": "#44FF44", "meaning": "speaking (present participle / gerund)", "case": "", "gender": "", "number": "", "tense": "present", "definite_form": ""},
                {"word": "ao", "grammatical_role": "contraction", "color": "#FF7F50", "meaning": "at the / on the — contraction of a + o (masculine)", "case": "", "gender": "", "number": "singular", "tense": "", "definite_form": "", "contraction_parts": ["a", "o"]},
                {"word": "telefone", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "telephone (masculine singular)", "case": "", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "agora", "grammatical_role": "adverb", "color": "#44FFFF", "meaning": "now (time adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "BR progressive: estar + gerund (-ndo). 'Ao' is mandatory contraction of a+o; PT equivalent would be 'está a falar'.",
            "confidence": 0.93
        },
        {
            "sentence": "Eu sou brasileiro e falo três línguas.",
            "overall_structure": "Subject-Copula-Adjective-Conjunction-Verb-Numeral-Object",
            "sentence_structure": "Coordinate clause with copula identity predicate",
            "word_explanations": [
                {"word": "Eu", "grammatical_role": "personal_pronoun", "color": "#FF4444", "meaning": "I (1st person singular)", "case": "", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "sou", "grammatical_role": "copula", "color": "#00B894", "meaning": "am (ser, 1st person singular present — permanent identity)", "case": "", "gender": "", "number": "singular", "tense": "present", "definite_form": "", "copula_type": "ser"},
                {"word": "brasileiro", "grammatical_role": "adjective", "color": "#FF44FF", "meaning": "Brazilian (masculine singular predicate adjective)", "case": "", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "e", "grammatical_role": "conjunction", "color": "#888888", "meaning": "and (coordinating conjunction)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "falo", "grammatical_role": "verb", "color": "#44FF44", "meaning": "speak (1st person singular present, pro-dropped subject)", "case": "", "gender": "", "number": "singular", "tense": "present", "definite_form": ""},
                {"word": "três", "grammatical_role": "numeral", "color": "#3CB371", "meaning": "three (cardinal numeral)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "línguas", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "languages (feminine plural)", "case": "", "gender": "feminine", "number": "plural", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Ser (sou) encodes permanent identity; contrast with estar for temporary states.",
            "confidence": 0.92
        },
        {
            "sentence": "Nós vamos falar com o professor amanhã.",
            "overall_structure": "Subject-Auxiliary-Verb-Preposition-Article-Noun-Adverb",
            "sentence_structure": "Near-future periphrasis with definite article",
            "word_explanations": [
                {"word": "Nós", "grammatical_role": "personal_pronoun", "color": "#FF4444", "meaning": "we (1st person plural)", "case": "", "gender": "", "number": "plural", "tense": "", "definite_form": ""},
                {"word": "vamos", "grammatical_role": "auxiliary_verb", "color": "#228B22", "meaning": "are going to (ir, near future auxiliary)", "case": "", "gender": "", "number": "plural", "tense": "present", "definite_form": ""},
                {"word": "falar", "grammatical_role": "verb", "color": "#44FF44", "meaning": "speak (infinitive)", "case": "", "gender": "", "number": "", "tense": "infinitive", "definite_form": ""},
                {"word": "com", "grammatical_role": "preposition", "color": "#4444FF", "meaning": "with (preposition)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "o", "grammatical_role": "definite_article", "color": "#AA44FF", "meaning": "the (masculine singular definite article)", "case": "", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "professor", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "teacher (masculine singular)", "case": "", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "amanhã", "grammatical_role": "adverb", "color": "#44FFFF", "meaning": "tomorrow (time adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "IR + infinitive expresses near future. Definite article 'o' precedes masculine noun.",
            "confidence": 0.91
        },
        {
            "sentence": "Você não se lembra de mim?",
            "overall_structure": "Subject-Particle-Reflexive-Verb-Preposition-Pronoun",
            "sentence_structure": "Reflexive / pronominal verb in interrogative",
            "word_explanations": [
                {"word": "Você", "grammatical_role": "personal_pronoun", "color": "#FF4444", "meaning": "you (2nd person singular, BR register, takes 3rd-person verb)", "case": "", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "não", "grammatical_role": "particle", "color": "#A1887F", "meaning": "not (negation particle)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "se", "grammatical_role": "reflexive_pronoun", "color": "#DC143C", "meaning": "oneself (reflexive clitic, 3rd person)", "case": "", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "lembra", "grammatical_role": "pronominal_verb", "color": "#20B2AA", "meaning": "remember (lembrar-se, pronominal verb, 3rd person singular present)", "case": "", "gender": "", "number": "singular", "tense": "present", "definite_form": ""},
                {"word": "de", "grammatical_role": "preposition", "color": "#4444FF", "meaning": "of (preposition required by lembrar-se de)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "mim", "grammatical_role": "pronoun", "color": "#FF4444", "meaning": "me (1st person singular prepositional form)", "case": "", "gender": "", "number": "singular", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Lembrar-se de is a pronominal verb; reflexive clitic 'se' occupies proclitic position after negation.",
            "confidence": 0.90
        }
    ], ensure_ascii=False),
}


_PORTUGUESE_ADVANCED_MOCK: Dict[str, Any] = {
    "word": "falar",
    "language_name": "Portuguese",
    "language_code": "pt",
    "topic": "Food & Cooking",
    "num_sentences": 4,
    "min_length": 5,
    "max_length": 22,
    "difficulty": "advanced",
    "mock_content_response": textwrap.dedent("""\
        MEANING: to speak (to talk, to use language)

        RESTRICTIONS: Use advanced structures: gerund, past participle, personal infinitive, clitic pronouns (enclitic/proclitic), relative pronoun, subordinating conjunction, subjunctive, mesoclitic.

        SENTENCES:
        1. Disse-me a verdade sem hesitar.
        2. O livro foi escrito para sermos honestos connosco.
        3. Falar-lhe-ei amanhã, embora ela raramente atenda.
        4. O relatório que foi entregue ontem estava muito bem escrito.

        TRANSLATIONS:
        1. He/She told me the truth without hesitating.
        2. The book was written so that we may be honest with ourselves.
        3. I will speak to her tomorrow, although she rarely answers.
        4. The report that was handed in yesterday was very well written.

        IPA:
        1. diˈsɛjmɨ a vɨɾˈdadɨ sẽj eziˈtaɾ
        2. u ˈlivɾu foj iʃˈkɾitu ˈpaɾɐ ˈseɾmuʃ oˈnɛʃtuʃ koˈnosku
        3. faˈlaɾljɐˈej ɐˈmɐ̃ɲɐ ˈẽboɾɐ ˈɛlɐ ʁaɾɐˈmẽtɨ ɐˈtẽdɐ
        4. u ʁɨlaˈtoɾju kɨ foj ẽtɾɨˈɡɨ oˈntẽj ˈeʃtɐvɐ ˈmujtʊ bẽj iʃˈkɾitu

        KEYWORDS:
        1. truth, clitic pronoun, enclitic
        2. passive, personal infinitive, reflexive
        3. mesoclitic, concessive, future
        4. relative clause, past participle, passive"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "Disse-me a verdade sem hesitar.",
            "overall_structure": "Verb-Clitic-Article-Object-Preposition-Infinitive",
            "sentence_structure": "Main clause with enclitic pronoun + adverbial infinitive phrase",
            "word_explanations": [
                {"word": "Disse", "grammatical_role": "verb", "color": "#44FF44", "meaning": "said / told (3rd person singular preterite of dizer)", "case": "", "gender": "", "number": "singular", "tense": "past", "definite_form": ""},
                {"word": "me", "grammatical_role": "clitic_pronoun", "color": "#E91E63", "meaning": "me (1st person singular dative/accusative clitic)", "case": "", "gender": "", "number": "singular", "tense": "", "definite_form": "", "clitic_position": "enclitic"},
                {"word": "a", "grammatical_role": "definite_article", "color": "#AA44FF", "meaning": "the (feminine singular definite article)", "case": "", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "verdade", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "truth (feminine singular)", "case": "", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "sem", "grammatical_role": "preposition", "color": "#4444FF", "meaning": "without (preposition introducing infinitive phrase)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "hesitar", "grammatical_role": "verb", "color": "#44FF44", "meaning": "hesitate (impersonal infinitive after sem)", "case": "", "gender": "", "number": "", "tense": "infinitive", "definite_form": ""}
            ],
            "grammar_notes": "Enclitic clitic: 'Disse-me' — the pronoun attaches to the right of the finite verb after sentence-initial V. 'Sem + infinitivo' expresses negative adverbial manner.",
            "confidence": 0.93
        },
        {
            "sentence": "O livro foi escrito para sermos honestos connosco.",
            "overall_structure": "Article-Subject-Auxiliary-PastParticiple-Conjunction-PersonalInfinitive-Adjective-Contraction",
            "sentence_structure": "Passive clause + purposive clause with personal infinitive",
            "word_explanations": [
                {"word": "O", "grammatical_role": "definite_article", "color": "#AA44FF", "meaning": "the (masculine singular definite article)", "case": "", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "livro", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "book (masculine singular)", "case": "", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "foi", "grammatical_role": "auxiliary_verb", "color": "#228B22", "meaning": "was (ser, 3rd person singular preterite — passive auxiliary)", "case": "", "gender": "", "number": "singular", "tense": "past", "definite_form": ""},
                {"word": "escrito", "grammatical_role": "past_participle", "color": "#FFA500", "meaning": "written (past participle of escrever, masculine singular)", "case": "", "gender": "masculine", "number": "singular", "tense": "past", "definite_form": ""},
                {"word": "para", "grammatical_role": "subordinating_conjunction", "color": "#777777", "meaning": "so that / in order to (purposive subordinator introducing personal infinitive)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "sermos", "grammatical_role": "personal_infinitive", "color": "#6C5CE7", "meaning": "to be (personal infinitive of ser, 1st person plural — inflected -mos)", "case": "", "gender": "", "number": "plural", "tense": "infinitive", "definite_form": ""},
                {"word": "honestos", "grammatical_role": "adjective", "color": "#FF44FF", "meaning": "honest (masculine plural predicate adjective)", "case": "", "gender": "masculine", "number": "plural", "tense": "", "definite_form": ""},
                {"word": "connosco", "grammatical_role": "pronoun", "color": "#FF4444", "meaning": "with ourselves (com + nós suppletive form)", "case": "", "gender": "", "number": "plural", "tense": "", "definite_form": ""}
            ],
            "grammar_notes": "Ser + past participle = passive voice. Personal infinitive 'sermos' is inflected for 1pl — unique to Portuguese among Romance languages. Para introduces a purposive clause.",
            "confidence": 0.92
        },
        {
            "sentence": "Falar-lhe-ei amanhã, embora ela raramente atenda.",
            "overall_structure": "Verb-Mesoclitic-Adverb-SubjConj-Subject-Adverb-Verb",
            "sentence_structure": "Main clause with mesoclitic + concessive subjunctive subordinate clause",
            "word_explanations": [
                {"word": "Falar", "grammatical_role": "verb", "color": "#44FF44", "meaning": "speak (verbal stem — future tense with mesoclitic splits stem from ending)", "case": "", "gender": "", "number": "", "tense": "future", "definite_form": ""},
                {"word": "lhe", "grammatical_role": "mesoclitic", "color": "#FF1493", "meaning": "to her (dative clitic inserted between verb stem and future ending — mesoclisis)", "case": "", "gender": "", "number": "singular", "tense": "", "definite_form": "", "clitic_position": "mesoclitic"},
                {"word": "ei", "grammatical_role": "verb", "color": "#44FF44", "meaning": "-ei (1st person singular future ending of falar)", "case": "", "gender": "", "number": "singular", "tense": "future", "definite_form": ""},
                {"word": "amanhã", "grammatical_role": "adverb", "color": "#44FFFF", "meaning": "tomorrow (time adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "embora", "grammatical_role": "subordinating_conjunction", "color": "#777777", "meaning": "although / even though (concessive subordinating conjunction — triggers subjunctive)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "ela", "grammatical_role": "personal_pronoun", "color": "#FF4444", "meaning": "she (3rd person singular feminine subject pronoun)", "case": "", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "raramente", "grammatical_role": "adverb", "color": "#44FFFF", "meaning": "rarely (frequency adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "atenda", "grammatical_role": "subjunctive_marker", "color": "#9C27B0", "meaning": "answer / pick up (present subjunctive of atender, 3rd person singular — triggered by embora)", "case": "", "gender": "", "number": "singular", "tense": "present_subjunctive", "definite_form": ""}
            ],
            "grammar_notes": "Mesoclisis: clitic 'lhe' is inserted between the verbal stem 'Falar-' and the future suffix '-ei' — a formal/literary Portuguese-only pattern. 'Embora' obligatorily triggers present subjunctive.",
            "confidence": 0.94
        },
        {
            "sentence": "O relatório que foi entregue ontem estava muito bem escrito.",
            "overall_structure": "Article-Subject-[RelPron-Auxiliary-PastParticiple-Adverb]-Copula-Adverb-Adverb-PastParticiple",
            "sentence_structure": "Noun phrase with restrictive relative clause + copular predicate",
            "word_explanations": [
                {"word": "O", "grammatical_role": "definite_article", "color": "#AA44FF", "meaning": "the (masculine singular definite article)", "case": "", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "relatório", "grammatical_role": "noun", "color": "#FFAA00", "meaning": "report (masculine singular)", "case": "", "gender": "masculine", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "que", "grammatical_role": "relative_pronoun", "color": "#FF4500", "meaning": "that / which (relative pronoun introducing restrictive clause)", "case": "", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "foi", "grammatical_role": "auxiliary_verb", "color": "#228B22", "meaning": "was (ser, 3rd person singular preterite — passive auxiliary)", "case": "", "gender": "", "number": "singular", "tense": "past", "definite_form": ""},
                {"word": "entregue", "grammatical_role": "past_participle", "color": "#FFA500", "meaning": "handed in / submitted (past participle of entregar, irregular form)", "case": "", "gender": "", "number": "singular", "tense": "past", "definite_form": ""},
                {"word": "ontem", "grammatical_role": "adverb", "color": "#44FFFF", "meaning": "yesterday (time adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "estava", "grammatical_role": "copula", "color": "#00B894", "meaning": "was (estar, 3rd person singular imperfect — temporary/resultant state)", "case": "", "gender": "", "number": "singular", "tense": "imperfect", "definite_form": "", "copula_type": "estar"},
                {"word": "muito", "grammatical_role": "adverb", "color": "#44FFFF", "meaning": "very (degree adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "bem", "grammatical_role": "adverb", "color": "#44FFFF", "meaning": "well (manner adverb)", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
                {"word": "escrito", "grammatical_role": "past_participle", "color": "#FFA500", "meaning": "written (past participle of escrever, predicate participle in copular construction)", "case": "", "gender": "masculine", "number": "singular", "tense": "past", "definite_form": ""}
            ],
            "grammar_notes": "Restrictive relative clause with 'que'. Double past-participle: 'foi entregue' (passive preterite) inside the relative, and 'escrito' as predicate in the main copular clause with estar.",
            "confidence": 0.91
        }
    ], ensure_ascii=False),
}


# beginner reuses PORTUGUESE_MOCK_DATA so reports / role coverage stay in sync.
PORTUGUESE_LEVEL_MOCK_DATA: Dict[str, Dict[str, Any]] = {
    "beginner": PORTUGUESE_MOCK_DATA,
    "intermediate": _PORTUGUESE_INTERMEDIATE_MOCK,
    "advanced": _PORTUGUESE_ADVANCED_MOCK,
}


# ---------------------------------------------------------------------------
# ENGLISH
# ---------------------------------------------------------------------------
ENGLISH_MOCK_DATA: Dict[str, Any] = {
    "word": "cat",
    "language_name": "English",
    "language_code": "en",
    "topic": "Animals & Nature",
    "num_sentences": 4,
    "min_length": 3,
    "max_length": 12,
    "difficulty": "beginner",
    "mock_content_response": textwrap.dedent("""\
        MEANING: cat (a small domesticated carnivorous mammal kept as a household pet)

        RESTRICTIONS: Common count noun. Use simple SVO sentences with basic vocabulary.

        SENTENCES:
        1. The cat eats fish.
        2. A small cat sleeps on the bed.
        3. My cat likes warm milk.
        4. The black cat ran away.

        TRANSLATIONS:
        1. El gato come pescado.
        2. Un gato pequeño duerme en la cama.
        3. A mi gato le gusta la leche tibia.
        4. El gato negro huyó.

        IPA:
        1. ðə kæt iːts fɪʃ
        2. ə smɔːl kæt sliːps ɒn ðə bɛd
        3. maɪ kæt laɪks wɔːm mɪlk
        4. ðə blæk kæt ræn əˈweɪ

        KEYWORDS:
        1. cat eating fish, bowl of fish, pet cat
        2. small cat sleeping, bed, cozy pet
        3. cat drinking milk, warm drink, happy pet
        4. black cat running, outdoor cat, escape"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "The cat eats fish.",
            "overall_structure": "Subject-Verb-Object",
            "sentence_structure": "Simple SVO declarative sentence",
            "word_explanations": [
                {"word": "The", "grammatical_role": "article", "individual_meaning": "Definite article 'the' — marks 'cat' as specific or already known to the speaker; a closed-class function word with no inflection in English."},
                {"word": "cat", "grammatical_role": "noun", "individual_meaning": "Common count noun 'cat' — subject of the clause; singular nominative position (English nouns lack overt case marking)."},
                {"word": "eats", "grammatical_role": "verb", "individual_meaning": "Present-tense verb 'eat', 3rd-person singular form — adds the obligatory -s suffix (minimal verb agreement unique to 3sg present in English)."},
                {"word": "fish", "grammatical_role": "noun", "individual_meaning": "Common noun 'fish' — direct object; zero-inflected (fish is its own plural form). Functions as accusative without overt case marking."}
            ],
            "grammar_notes": "Basic SVO present-tense sentence. Definite article marks specific referent; 3sg -s is English's only productive verb-agreement suffix.",
            "confidence": 0.93
        },
        {
            "sentence": "A small cat sleeps on the bed.",
            "overall_structure": "Article-Adjective-Subject-Verb-Preposition-Article-Object",
            "sentence_structure": "SVO with attributive adjective and prepositional phrase",
            "word_explanations": [
                {"word": "A", "grammatical_role": "article", "individual_meaning": "Indefinite article 'a' — introduces 'cat' as non-specific or first-mentioned; used before consonant onset /sm/."},
                {"word": "small", "grammatical_role": "adjective", "individual_meaning": "Attributive adjective 'small' — precedes and modifies 'cat'; English adjectives are invariable (no gender/number agreement)."},
                {"word": "cat", "grammatical_role": "noun", "individual_meaning": "Common count noun 'cat' — subject of the clause in singular form."},
                {"word": "sleeps", "grammatical_role": "verb", "individual_meaning": "Present-tense verb 'sleep', 3rd-person singular — obligatory -s agreement suffix marks the 3sg subject."},
                {"word": "on", "grammatical_role": "preposition", "individual_meaning": "Preposition 'on' — expresses contact/surface location; heads the prepositional phrase 'on the bed'."},
                {"word": "the", "grammatical_role": "article", "individual_meaning": "Definite article 'the' — marks 'bed' as a specific known entity in context."},
                {"word": "bed", "grammatical_role": "noun", "individual_meaning": "Common count noun 'bed' — object of the preposition 'on'; English nouns have no overt case marking after prepositions."}
            ],
            "grammar_notes": "Attributive adjective precedes the noun; prepositional phrase 'on the bed' is a locative adjunct. Indefinite article 'a' vs definite 'the' contrast shown within the same sentence.",
            "confidence": 0.92
        },
        {
            "sentence": "My cat likes warm milk.",
            "overall_structure": "PossessiveDeterminer-Subject-Verb-Adjective-Object",
            "sentence_structure": "SVO with possessive determiner and attributive adjective",
            "word_explanations": [
                {"word": "My", "grammatical_role": "pronoun", "individual_meaning": "Possessive determiner 'my' (1st-person singular) — precedes the noun 'cat' as a genitive determiner; distinct from the possessive pronoun 'mine' which stands alone."},
                {"word": "cat", "grammatical_role": "noun", "individual_meaning": "Common count noun 'cat' — subject; possessed by the speaker via 'my'."},
                {"word": "likes", "grammatical_role": "verb", "individual_meaning": "Present-tense verb 'like', 3rd-person singular — adds -s suffix for 3sg agreement; stative verb expressing preference."},
                {"word": "warm", "grammatical_role": "adjective", "individual_meaning": "Attributive adjective 'warm' — modifies 'milk' by preceding it directly; no inflection for agreement in English."},
                {"word": "milk", "grammatical_role": "noun", "individual_meaning": "Mass (uncountable) noun 'milk' — direct object; used without an article because it refers to milk in general (generic/bare mass noun reading)."}
            ],
            "grammar_notes": "Possessive determiner 'my' occupies the determiner slot before the noun. 'Milk' is a bare mass noun (generic reading, no article needed). Stative verb 'likes' in simple present.",
            "confidence": 0.92
        },
        {
            "sentence": "The black cat ran away.",
            "overall_structure": "Article-Adjective-Subject-Verb-Adverb",
            "sentence_structure": "SVO past-tense clause with directional adverb",
            "word_explanations": [
                {"word": "The", "grammatical_role": "article", "individual_meaning": "Definite article 'the' — marks 'cat' as specific and identifiable; used here with an adjective-noun phrase."},
                {"word": "black", "grammatical_role": "adjective", "individual_meaning": "Attributive adjective 'black' — describes colour of the cat; invariable in English (no case/gender/number inflection)."},
                {"word": "cat", "grammatical_role": "noun", "individual_meaning": "Common count noun 'cat' — subject; the noun follows the article + adjective sequence in English NP structure."},
                {"word": "ran", "grammatical_role": "verb", "individual_meaning": "Irregular past-tense form of 'run' (run → ran) — simple past marks completed action; English irregular verbs change their stem vowel (ablaut) rather than adding -ed."},
                {"word": "away", "grammatical_role": "adverb", "individual_meaning": "Directional adverb 'away' — indicates movement in a departing direction; functions as an adverbial adjunct modifying 'ran'."}
            ],
            "grammar_notes": "Simple past tense with irregular ablaut form 'ran'. Directional adverb 'away' is an adjunct. Article + adjective + noun is the canonical English NP word order.",
            "confidence": 0.93
        }
    ], ensure_ascii=False),
}


# ---------------------------------------------------------------------------
# ENGLISH — per-difficulty mock data
# ---------------------------------------------------------------------------
# English exposes distinct grammatical-role vocabularies for each complexity
# level (en_config._get_default_roles). To validate analyzer + grammar-processor
# coherence at every level we run the full pipeline three times — once each for
# beginner, intermediate, and advanced — feeding level-appropriate role tags.
#
# beginner mock = ENGLISH_MOCK_DATA (defined above) — kept as the default
#                 entry in LANGUAGE_MOCK_DATA so the original parametrized
#                 test still runs.
# ---------------------------------------------------------------------------

_ENGLISH_INTERMEDIATE_MOCK: Dict[str, Any] = {
    "word": "learn",
    "language_name": "English",
    "language_code": "en",
    "topic": "Education",
    "num_sentences": 4,
    "min_length": 4,
    "max_length": 14,
    "difficulty": "intermediate",
    "mock_content_response": textwrap.dedent("""\
        MEANING: learn (to gain knowledge or a skill through study or experience)

        RESTRICTIONS: Use intermediate structures: infinitives, modal verbs, phrasal verbs, gerunds, participles, possessive determiners, demonstratives.

        SENTENCES:
        1. I want to learn English quickly.
        2. She is reading an interesting book.
        3. We should turn off the lights.
        4. Running every morning helps me focus.

        TRANSLATIONS:
        1. Quiero aprender inglés rápidamente.
        2. Ella está leyendo un libro interesante.
        3. Deberíamos apagar las luces.
        4. Correr cada mañana me ayuda a concentrarme.

        IPA:
        1. aɪ wɒnt tə lɜːn ˈɪŋɡlɪʃ ˈkwɪkli
        2. ʃiː ɪz ˈriːdɪŋ ən ɪnˈtɛrɪstɪŋ bʊk
        3. wiː ʃʊd tɜːn ɒf ðə laɪts
        4. ˈrʌnɪŋ ˈɛvri ˈmɔːnɪŋ hɛlps miː ˈfəʊkəs

        KEYWORDS:
        1. language learning, study, English book
        2. woman reading, interesting book, library
        3. light switch, turning off, energy saving
        4. morning run, jogging, focus concentration"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "I want to learn English quickly.",
            "overall_structure": "Subject-Verb-InfinitiveMarker-Verb-Object-Adverb",
            "sentence_structure": "SVO with infinitive complement",
            "word_explanations": [
                {"word": "I", "grammatical_role": "pronoun", "individual_meaning": "1st-person singular subject pronoun 'I' — always capitalised; nominative case, subject of finite verb 'want'."},
                {"word": "want", "grammatical_role": "verb", "individual_meaning": "Stative verb 'want' in simple present, 1st-person singular — no -s suffix since subject is 1sg; heads a to-infinitive complement."},
                {"word": "to", "grammatical_role": "infinitive_marker", "individual_meaning": "Infinitive marker 'to' — introduces the base-form verb 'learn'; purely grammatical (not a preposition here); marks the complement as a to-infinitive clause."},
                {"word": "learn", "grammatical_role": "infinitive", "individual_meaning": "Base-form verb 'learn' as to-infinitive — complement of 'want'; no inflection for person/number in the infinitive form."},
                {"word": "English", "grammatical_role": "noun", "individual_meaning": "Proper noun 'English' used as a bare object — language names are capitalised in English; functions as direct object of 'learn'."},
                {"word": "quickly", "grammatical_role": "adverb", "individual_meaning": "Manner adverb 'quickly' derived from adjective 'quick' + -ly suffix — modifies the infinitive 'learn'; adverbial adjunct indicating speed of learning."}
            ],
            "grammar_notes": "To-infinitive complement after 'want'. Infinitive marker 'to' is distinct from the preposition 'to'. Adverb 'quickly' is an end-adjunct.",
            "confidence": 0.92
        },
        {
            "sentence": "She is reading an interesting book.",
            "overall_structure": "Subject-Auxiliary-PresentParticiple-Article-Adjective-Object",
            "sentence_structure": "Present progressive (be + -ing) with indefinite NP",
            "word_explanations": [
                {"word": "She", "grammatical_role": "pronoun", "individual_meaning": "3rd-person singular feminine subject pronoun 'she' — nominative case; triggers 3sg verb agreement on 'is'."},
                {"word": "is", "grammatical_role": "auxiliary", "individual_meaning": "Auxiliary verb 'be', 3rd-person singular present 'is' — combines with the present participle 'reading' to form the progressive aspect; marks an ongoing action at the time of speaking."},
                {"word": "reading", "grammatical_role": "present_participle", "individual_meaning": "Present participle 'reading' formed by adding -ing to 'read' — together with auxiliary 'is' marks progressive aspect; the -ing form has no tense of its own."},
                {"word": "an", "grammatical_role": "article", "individual_meaning": "Indefinite article 'an' (vowel onset variant of 'a') — used before 'interesting' which begins with a vowel sound /ɪ/; introduces a non-specific book."},
                {"word": "interesting", "grammatical_role": "adjective", "individual_meaning": "Attributive adjective 'interesting' — participial adjective derived from the verb 'interest'; precedes 'book' in the noun phrase; invariable in English."},
                {"word": "book", "grammatical_role": "noun", "individual_meaning": "Common count noun 'book' — direct object of 'reading'; singular, no case marking needed in English object position."}
            ],
            "grammar_notes": "Present progressive = be (auxiliary) + present participle (-ing). 'An' before vowel onset. Participial adjective 'interesting' precedes the noun.",
            "confidence": 0.93
        },
        {
            "sentence": "We should turn off the lights.",
            "overall_structure": "Subject-ModalVerb-Verb-PhrasalVerbParticle-Article-Object",
            "sentence_structure": "Modal + base verb + separable phrasal verb",
            "word_explanations": [
                {"word": "We", "grammatical_role": "pronoun", "individual_meaning": "1st-person plural subject pronoun 'we' — nominative case; modal verbs take the base form regardless of subject person/number."},
                {"word": "should", "grammatical_role": "modal_verb", "individual_meaning": "Modal verb 'should' — defective paradigm (no -s, no infinitive, no past form); expresses mild obligation or recommendation; followed by bare infinitive 'turn'."},
                {"word": "turn", "grammatical_role": "verb", "individual_meaning": "Base-form verb 'turn' — bare infinitive after modal 'should'; part of the phrasal verb 'turn off' (non-compositional: meaning is 'extinguish', not merely 'rotate away')."},
                {"word": "off", "grammatical_role": "phrasal_verb_particle", "individual_meaning": "Phrasal-verb particle 'off' — combines with 'turn' to form the phrasal verb 'turn off' (stop electricity/light); separable: a pronoun object would move between verb and particle ('turn them off')."},
                {"word": "the", "grammatical_role": "article", "individual_meaning": "Definite article 'the' — marks 'lights' as specific lights already known in context."},
                {"word": "lights", "grammatical_role": "noun", "individual_meaning": "Common count noun 'lights' — direct object in plural form; English regular plural adds -s suffix; here the full NP ('the lights') follows the particle."}
            ],
            "grammar_notes": "Modal 'should' + bare infinitive. 'Turn off' is a separable phrasal verb: full NP object may follow the particle, but a pronoun must precede it ('turn them off').",
            "confidence": 0.91
        },
        {
            "sentence": "Running every morning helps me focus.",
            "overall_structure": "Gerund-Determiner-Noun-Verb-Pronoun-BareInfinitive",
            "sentence_structure": "Gerund subject + bare infinitive object complement",
            "word_explanations": [
                {"word": "Running", "grammatical_role": "gerund", "individual_meaning": "Gerund 'running' — -ing form of 'run' used as the subject noun phrase of the sentence; a gerund is a verbal noun that preserves some verb properties (can take adverbials) while functioning syntactically as a noun."},
                {"word": "every", "grammatical_role": "determiner", "individual_meaning": "Universal determiner 'every' — distributes over singular countable nouns; heads the NP 'every morning' which is a temporal adverbial modifying 'running'."},
                {"word": "morning", "grammatical_role": "noun", "individual_meaning": "Common count noun 'morning' — object of the determiner 'every'; the NP 'every morning' is a temporal adjunct within the gerund phrase."},
                {"word": "helps", "grammatical_role": "verb", "individual_meaning": "Present-tense verb 'help', 3rd-person singular — adds -s because the gerund subject 'Running every morning' is syntactically singular; takes a bare-infinitive object complement."},
                {"word": "me", "grammatical_role": "pronoun", "individual_meaning": "1st-person singular object pronoun 'me' — accusative case; indirect object / beneficiary argument of 'helps'."},
                {"word": "focus", "grammatical_role": "infinitive", "individual_meaning": "Bare infinitive 'focus' — base form without 'to'; appears as the second complement of 'help' in the 'help someone (to) do' construction; the 'to' is optionally dropped after 'help'."}
            ],
            "grammar_notes": "Gerund as subject makes the clause nominally-headed. 'Every morning' is an adverbial adjunct within the gerund phrase. 'Helps me focus' uses the bare-infinitive complement pattern of 'help'.",
            "confidence": 0.91
        }
    ], ensure_ascii=False),
}


_ENGLISH_ADVANCED_MOCK: Dict[str, Any] = {
    "word": "read",
    "language_name": "English",
    "language_code": "en",
    "topic": "Education",
    "num_sentences": 4,
    "min_length": 5,
    "max_length": 22,
    "difficulty": "advanced",
    "mock_content_response": textwrap.dedent("""\
        MEANING: read (to look at and comprehend written text)

        RESTRICTIONS: Use advanced structures: relative pronouns, subordinating conjunctions, comparative/superlative, reflexive pronouns, coordinating conjunctions, phrasal verbs.

        SENTENCES:
        1. The book that she gave me was the most interesting one I had ever read.
        2. Although it was raining heavily, we went outside to play football.
        3. She picked herself up and continued running, even though she was exhausted.
        4. Who wrote the better essay, you or your classmate?

        TRANSLATIONS:
        1. El libro que ella me dio fue el más interesante que jamás había leído.
        2. Aunque llovía mucho, salimos a jugar al fútbol.
        3. Se levantó y continuó corriendo, aunque estaba agotada.
        4. ¿Quién escribió el mejor ensayo, tú o tu compañero?

        IPA:
        1. ðə bʊk ðæt ʃiː ɡeɪv miː wɒz ðə məʊst ˈɪntrɪstɪŋ wʌn aɪ həd ˈɛvər rɛd
        2. ɔːlˈðəʊ ɪt wɒz ˈreɪnɪŋ ˈhɛvɪli wiː wɛnt ˈaʊtsaɪd tə pleɪ ˈfʊtbɔːl
        3. ʃiː pɪkt hɜːˈsɛlf ʌp ənd kənˈtɪnjuːd ˈrʌnɪŋ iːvən ðəʊ ʃiː wɒz ɪɡˈzɔːstɪd
        4. huː rəʊt ðə ˈbɛtər ˈɛseɪ juː ɔː jɔː ˈklɑːsmeɪt

        KEYWORDS:
        1. book reading, interesting novel, past reading
        2. rainy day, outdoor football, despite rain
        3. resilience, running after falling, tired athlete
        4. essay writing, comparison, classmates"""),
    "mock_grammar_batch_response": json.dumps([
        {
            "sentence": "The book that she gave me was the most interesting one I had ever read.",
            "overall_structure": "Article-Subject-[RelPron-Subject-Verb-Object]-Verb-Article-Superlative-Adjective-Pronoun-[Subject-Auxiliary-Adverb-Verb]",
            "sentence_structure": "Main clause with restrictive relative clause + predicate containing superlative + reduced relative",
            "word_explanations": [
                {"word": "The", "grammatical_role": "article", "individual_meaning": "Definite article 'the' — marks 'book' as specific (the particular book already in discourse focus)."},
                {"word": "book", "grammatical_role": "noun", "individual_meaning": "Common count noun 'book' — head of the subject NP; modified by the restrictive relative clause 'that she gave me'."},
                {"word": "that", "grammatical_role": "relative_pronoun", "individual_meaning": "Relative pronoun 'that' — introduces a restrictive relative clause; its antecedent is 'book' (the head noun); 'that' functions as the direct object of 'gave' within the clause."},
                {"word": "she", "grammatical_role": "pronoun", "individual_meaning": "3rd-person singular feminine subject pronoun 'she' — subject of the relative clause verb 'gave'; nominative case."},
                {"word": "gave", "grammatical_role": "verb", "individual_meaning": "Irregular past-tense form of 'give' (give → gave) — simple past; ditransitive verb taking two objects: indirect 'me' and direct (relativised) 'that/book'."},
                {"word": "me", "grammatical_role": "pronoun", "individual_meaning": "1st-person singular object pronoun 'me' — accusative/dative; indirect object (recipient) of the ditransitive verb 'gave'."},
                {"word": "was", "grammatical_role": "verb", "individual_meaning": "Past-tense form of copula 'be' (3rd-person singular) — main verb of the matrix clause linking subject 'book' to predicate 'the most interesting one'."},
                {"word": "the", "grammatical_role": "article", "individual_meaning": "Definite article 'the' — required before superlative adjectives; marks the highest degree in the comparison class."},
                {"word": "most", "grammatical_role": "superlative", "individual_meaning": "Superlative marker 'most' — periphrastic superlative used before multi-syllable adjectives; 'the most interesting' is the superlative of 'interesting'."},
                {"word": "interesting", "grammatical_role": "adjective", "individual_meaning": "Adjective 'interesting' — takes periphrastic superlative 'most' (not *interestingest); predicate adjective in the copular construction."},
                {"word": "one", "grammatical_role": "pronoun", "individual_meaning": "Pro-form 'one' — indefinite pronoun standing in for 'book'; avoids repetition; head of the NP 'one [that] I had ever read'."},
                {"word": "I", "grammatical_role": "pronoun", "individual_meaning": "1st-person singular subject pronoun 'I' — subject of the reduced relative clause 'I had ever read'; nominative case."},
                {"word": "had", "grammatical_role": "auxiliary", "individual_meaning": "Past perfect auxiliary 'had' — combines with past participle 'read' to form the past perfect aspect; signals that the reading preceded another past event (the giving)."},
                {"word": "ever", "grammatical_role": "adverb", "individual_meaning": "Frequency adverb 'ever' — used in a superlative/comparative context to mean 'at any point in time'; reinforces the absolute superlative claim."},
                {"word": "read", "grammatical_role": "past_participle", "individual_meaning": "Irregular past participle 'read' (homographic with base/past; /rɛd/ not /riːd/) — used with auxiliary 'had' to form past perfect; the book is the understood object."}
            ],
            "grammar_notes": "Restrictive relative clause with 'that' (object position — zero-relativiser also possible). Periphrastic superlative 'the most interesting'. Past perfect 'had ever read' signals anterior action. Pro-form 'one' avoids NP repetition.",
            "confidence": 0.94
        },
        {
            "sentence": "Although it was raining heavily, we went outside to play football.",
            "overall_structure": "SubordConj-Subject-Auxiliary-PresentParticiple-Adverb-Subject-Verb-Adverb-InfMarker-Verb-Object",
            "sentence_structure": "Concessive adverbial subordinate clause + main clause with purpose infinitive",
            "word_explanations": [
                {"word": "Although", "grammatical_role": "subordinating_conjunction", "individual_meaning": "Subordinating conjunction 'although' — introduces a concessive adverbial clause expressing a contrast or unexpected result; equivalent to 'even though'; triggers a finite subordinate clause."},
                {"word": "it", "grammatical_role": "pronoun", "individual_meaning": "Expletive pronoun 'it' — dummy/placeholder subject with no referential content; required by English's strict subject-mandatory syntax (pro-drop is not permitted); used in weather and environmental constructions."},
                {"word": "was", "grammatical_role": "auxiliary", "individual_meaning": "Past-tense auxiliary 'be' (3rd-person singular 'was') — combines with present participle 'raining' to form past progressive; sets temporal frame of the concessive clause."},
                {"word": "raining", "grammatical_role": "present_participle", "individual_meaning": "Present participle 'raining' — -ing form of weather verb 'rain'; with past auxiliary 'was' forms past progressive indicating ongoing rain at the reference time."},
                {"word": "heavily", "grammatical_role": "adverb", "individual_meaning": "Manner adverb 'heavily' — derived from adjective 'heavy' + -ly; modifies 'raining'; indicates intensity of the rain."},
                {"word": "we", "grammatical_role": "pronoun", "individual_meaning": "1st-person plural subject pronoun 'we' — nominative case; subject of the main clause."},
                {"word": "went", "grammatical_role": "verb", "individual_meaning": "Irregular past-tense of 'go' (go → went, suppletion) — simple past main verb; directional motion verb."},
                {"word": "outside", "grammatical_role": "adverb", "individual_meaning": "Directional adverb 'outside' — adverbial complement indicating destination of 'went'; can also function as a preposition (here adverb since no NP follows)."},
                {"word": "to", "grammatical_role": "infinitive_marker", "individual_meaning": "Infinitive marker 'to' — introduces purpose infinitive clause 'to play football'; the infinitive here expresses the purpose/intention of going outside."},
                {"word": "play", "grammatical_role": "verb", "individual_meaning": "Base-form verb 'play' as to-infinitive — expresses the purpose of the motion; no inflection in infinitive form."},
                {"word": "football", "grammatical_role": "noun", "individual_meaning": "Mass/activity noun 'football' — direct object of 'play'; used without an article in sporting activity constructions ('play football', not *'play the football')."}
            ],
            "grammar_notes": "Sentence-initial concessive 'although'-clause is fronted for contrast emphasis. Expletive 'it' subject in weather clause. Purpose infinitive 'to play' after motion verb 'went outside'. Past progressive in subordinate clause.",
            "confidence": 0.93
        },
        {
            "sentence": "She picked herself up and continued running, even though she was exhausted.",
            "overall_structure": "Subject-PhrasalVerb-ReflexivePronoun-Particle-CoordConj-Verb-Gerund-SubordConj-Subject-Auxiliary-PastParticiple",
            "sentence_structure": "Coordinated main clauses + concessive subordinate clause",
            "word_explanations": [
                {"word": "She", "grammatical_role": "pronoun", "individual_meaning": "3rd-person singular feminine subject pronoun 'she' — nominative case; co-referential with 'herself' in the same clause."},
                {"word": "picked", "grammatical_role": "phrasal_verb", "individual_meaning": "Past-tense verb 'picked' — part of the phrasal verb 'pick up' (non-compositional meaning: recover/rise from a fall); the reflexive 'herself' is the separating object between verb and particle."},
                {"word": "herself", "grammatical_role": "reflexive_pronoun", "individual_meaning": "3rd-person singular feminine reflexive pronoun 'herself' — refers back to the subject 'she'; required here because the phrasal verb 'pick up' is transitive and the agent and patient are co-referential."},
                {"word": "up", "grammatical_role": "phrasal_verb", "individual_meaning": "Phrasal-verb particle 'up' in 'pick up' — separated from 'picked' by the reflexive object 'herself' (separable phrasal verb); together with 'picked' expresses recovering from a fallen position."},
                {"word": "and", "grammatical_role": "coordinating_conjunction", "individual_meaning": "Coordinating conjunction 'and' (FANBOYS) — joins the two main-clause predicates 'picked herself up' and 'continued running'; expresses sequential or simultaneous addition."},
                {"word": "continued", "grammatical_role": "verb", "individual_meaning": "Past-tense verb 'continued' — aspectual continuative verb; takes a gerund complement ('running') rather than a to-infinitive."},
                {"word": "running", "grammatical_role": "present_participle", "individual_meaning": "Gerund/present participle 'running' (-ing form of 'run') — here functions as the gerund complement of 'continued'; 'continue' preferentially takes -ing over to-infinitive with slight meaning difference."},
                {"word": "even though", "grammatical_role": "subordinating_conjunction", "individual_meaning": "Subordinating conjunction 'even though' — a reinforced concessive subordinator (stronger than 'although'); introduces a concessive clause expressing a surprising contrast."},
                {"word": "she", "grammatical_role": "pronoun", "individual_meaning": "3rd-person singular feminine subject pronoun 'she' — subject of the concessive clause; co-referential with the main-clause subject."},
                {"word": "was", "grammatical_role": "auxiliary", "individual_meaning": "Past-tense copula/auxiliary 'was' (3rd-person singular) — links subject 'she' to the predicate adjective 'exhausted'; here functions as copula in a stative past construction."},
                {"word": "exhausted", "grammatical_role": "past_participle", "individual_meaning": "Past participle 'exhausted' — used as a predicate adjective after copula 'was'; derived from the verb 'exhaust'; describes a resultant state of being extremely tired."}
            ],
            "grammar_notes": "Separable phrasal verb 'pick up' split by reflexive object 'herself'. Coordinating conjunction 'and' links two VP predicates. 'Even though' is a stronger concessive than 'although'. 'Exhausted' is a participial adjective in copular predicate.",
            "confidence": 0.93
        },
        {
            "sentence": "Who wrote the better essay, you or your classmate?",
            "overall_structure": "IntPronoun-Verb-Article-Comparative-Noun-Pronoun-CoordConj-PossessiveDeterminer-Noun",
            "sentence_structure": "Wh-interrogative with comparative adjective and alternative question tag",
            "word_explanations": [
                {"word": "Who", "grammatical_role": "interrogative_pronoun", "individual_meaning": "Interrogative pronoun 'who' — asks about a person; subject of the question (subject-position wh-word does not trigger subject-auxiliary inversion in standard English); nominative case."},
                {"word": "wrote", "grammatical_role": "verb", "individual_meaning": "Irregular past-tense form of 'write' (write → wrote, ablaut) — simple past; transitive verb; 'who' in subject position, 'the better essay' as direct object."},
                {"word": "the", "grammatical_role": "article", "individual_meaning": "Definite article 'the' — required before comparative adjectives in a definite-context comparison ('the better essay' = the superior of the two); marks uniqueness within the comparison set."},
                {"word": "better", "grammatical_role": "comparative", "individual_meaning": "Comparative form of adjective 'good' (good → better, suppletive) — irregular comparative; 'the better essay' implies a comparison between exactly two essays; precedes the noun as attributive."},
                {"word": "essay", "grammatical_role": "noun", "individual_meaning": "Common count noun 'essay' — direct object of 'wrote'; modified by the comparative adjective 'better'; singular form."},
                {"word": "you", "grammatical_role": "pronoun", "individual_meaning": "2nd-person pronoun 'you' — part of the appended alternative question fragment 'you or your classmate?'; English does not distinguish nominative/accusative for 'you'; identifies one of the two compared agents."},
                {"word": "or", "grammatical_role": "coordinating_conjunction", "individual_meaning": "Coordinating conjunction 'or' (FANBOYS) — connects the two alternatives 'you' and 'your classmate' in an alternative question structure asking the listener to identify one."},
                {"word": "your", "grammatical_role": "pronoun", "individual_meaning": "2nd-person possessive determiner 'your' — precedes 'classmate' as a genitive determiner; expresses possession/association; distinct from possessive pronoun 'yours' which stands alone."},
                {"word": "classmate", "grammatical_role": "noun", "individual_meaning": "Compound noun 'classmate' — a fellow member of the same class; object of comparison in the alternative tag; the alternative to 'you' in the question."}
            ],
            "grammar_notes": "Subject-position 'who' does not trigger do-support or inversion (contrast object-position 'Whom did she see?'). Suppletive comparative 'better' (not *'gooder'). Definite article 'the' before comparative in bounded comparison. Alternative question fragment 'you or your classmate?' appended after the main clause.",
            "confidence": 0.92
        }
    ], ensure_ascii=False),
}


# beginner reuses ENGLISH_MOCK_DATA so reports / role coverage stay in sync.
ENGLISH_LEVEL_MOCK_DATA: Dict[str, Dict[str, Any]] = {
    "beginner": ENGLISH_MOCK_DATA,
    "intermediate": _ENGLISH_INTERMEDIATE_MOCK,
    "advanced": _ENGLISH_ADVANCED_MOCK,
}


# ============================================================================
# Mapping: add more languages here to extend coverage
# ============================================================================
LANGUAGE_MOCK_DATA = {
    "french": FRENCH_MOCK_DATA,
    "spanish": SPANISH_MOCK_DATA,
    "german": GERMAN_MOCK_DATA,
    "arabic": ARABIC_MOCK_DATA,
    "chinese_simplified": CHINESE_SIMPLIFIED_MOCK_DATA,
    "chinese_traditional": CHINESE_TRADITIONAL_MOCK_DATA,
    "hindi": HINDI_MOCK_DATA,
    "turkish": TURKISH_MOCK_DATA,
    "japanese": JAPANESE_MOCK_DATA,
    "korean": KOREAN_MOCK_DATA,
    "hungarian": HUNGARIAN_MOCK_DATA,
    "malayalam": MALAYALAM_MOCK_DATA,
    "latvian": LATVIAN_MOCK_DATA,
    "portuguese": PORTUGUESE_MOCK_DATA,
    "english": ENGLISH_MOCK_DATA,
}


# ============================================================================
# HELPERS
# ============================================================================

class PipelineReport:
    """Accumulates test results and renders a human-readable report."""

    def __init__(self, language_name: str, word: str, difficulty: str, topic: str):
        self.language_name = language_name
        self.word = word
        self.difficulty = difficulty
        self.topic = topic
        self.started_at = datetime.now()
        self.stages: List[Dict[str, Any]] = []
        self.sentences_data: List[Dict[str, Any]] = []
        self.audio_files: List[str] = []
        self.image_files: List[str] = []
        self.meaning = ""
        self.errors: List[str] = []

    def add_stage(self, name: str, passed: bool, detail: str = ""):
        self.stages.append({"name": name, "passed": passed, "detail": detail})

    def render(self) -> str:
        elapsed = (datetime.now() - self.started_at).total_seconds()
        sep = "=" * 80
        thin = "-" * 80

        lines = [
            sep,
            f"  END-TO-END PIPELINE REPORT — {self.language_name.upper()}",
            sep,
            f"  Word          : {self.word}",
            f"  Language       : {self.language_name}",
            f"  Difficulty     : {self.difficulty}",
            f"  Topic          : {self.topic}",
            f"  Generated at   : {self.started_at:%Y-%m-%d %H:%M:%S}",
            f"  Elapsed        : {elapsed:.2f}s",
            sep,
            "",
            "STAGE RESULTS",
            thin,
        ]

        all_passed = True
        for s in self.stages:
            icon = "PASS" if s["passed"] else "FAIL"
            all_passed = all_passed and s["passed"]
            lines.append(f"  [{icon}] {s['name']}")
            if s["detail"]:
                for d in s["detail"].split("\n"):
                    lines.append(f"         {d}")

        lines += ["", thin, f"  OVERALL: {'ALL STAGES PASSED' if all_passed else 'SOME STAGES FAILED'}", thin, ""]

        # Content generation
        lines += ["CONTENT GENERATION OUTPUT", thin]
        lines.append(f"  Meaning: {self.meaning}")
        lines.append("")

        for i, sd in enumerate(self.sentences_data, 1):
            lines.append(f"  --- Sentence {i} ---")
            lines.append(f"  Original   : {sd.get('sentence', 'N/A')}")
            lines.append(f"  Translation: {sd.get('english_translation', 'N/A')}")
            lines.append(f"  IPA/Reading: {sd.get('ipa', 'N/A')}")
            lines.append(f"  Keywords   : {sd.get('image_keywords', 'N/A')}")
            lines.append("")

            # Grammar analysis
            colored = sd.get("colored_sentence", "")
            explanations = sd.get("word_explanations", [])
            summary = sd.get("grammar_summary", "")

            lines.append(f"  Colored HTML : {colored[:200]}{'…' if len(colored) > 200 else ''}")
            lines.append(f"  Grammar Summ : {summary}")
            lines.append(f"  Word Explanations ({len(explanations)} words):")
            for exp in explanations:
                if len(exp) >= 4:
                    lines.append(f"    {exp[0]:12s}  {exp[1]:14s}  {exp[2]:8s}  {exp[3]}")
                else:
                    lines.append(f"    {exp}")
            lines.append("")

        # Audio / Images
        lines += ["AUDIO FILES", thin]
        for a in self.audio_files:
            lines.append(f"  {a}")
        if not self.audio_files:
            lines.append("  (none — mock returned empty list)")

        lines += ["", "IMAGE FILES", thin]
        for img in self.image_files:
            lines.append(f"  {img}")
        if not self.image_files:
            lines.append("  (none — mock returned empty list)")

        # Errors
        if self.errors:
            lines += ["", "ERRORS", thin]
            for e in self.errors:
                lines.append(f"  !! {e}")

        lines += ["", sep, "  END OF REPORT", sep, ""]
        return "\n".join(lines)


def _build_mock_session_state(difficulty: str = "beginner") -> dict:
    """Return a dict that behaves like st.session_state for test purposes."""
    return {
        "google_api_key": "AIzaFAKE_TEST_KEY_1234567890",
        "google_tts_api_key": "AIzaFAKE_TTS_KEY_1234567890",
        "pixabay_api_key": "FAKE_PIXABAY_KEY_12345",
        "difficulty": difficulty,
        "enable_topics": True,
        "selected_topics": ["Food & Cooking"],
        "native_language": "English",
        "audio_speed": 0.8,
        "gemini_api_calls": 0,
        "gemini_tokens_used": 0,
    }


# ============================================================================
# MAIN TEST
# ============================================================================

def _run_full_pipeline(data: Dict[str, Any], report_key: str, tmp_path: Path) -> None:
    """
    Run the full pipeline (Stages 1-7) for one mock-data dict and write a report.

    Used by both the multi-language parametrized test and the per-level Latvian
    test. Asserts on stage outcomes; raises AssertionError on any failure.
    """
    word = data["word"]
    language_name = data["language_name"]
    language_code = data["language_code"]
    difficulty = data["difficulty"]
    topic = data["topic"]
    num_sentences = data["num_sentences"]
    min_length = data["min_length"]
    max_length = data["max_length"]

    report = PipelineReport(language_name, word, difficulty, topic)

    # ---- Session state mock --------------------------------------------------
    mock_state = _build_mock_session_state(difficulty)

    # We need a dict-like object that also supports attribute access for
    # st.session_state.get() and st.session_state.xxx patterns.
    class MockSessionState(dict):
        def __getattr__(self, name):
            try:
                return self[name]
            except KeyError:
                raise AttributeError(name)
        def __setattr__(self, name, value):
            self[name] = value

    session_state = MockSessionState(mock_state)

    # ---- Build mock Gemini responses -----------------------------------------
    # The pipeline makes two distinct API calls to Gemini:
    #   1. Content generation  (content_generator → genai.generate_content)
    #   2. Grammar analysis    (ja_analyzer._call_ai → genai.generate_content)
    #
    # We use a side-effect function that returns the right response based on
    # whether the call is for content or grammar.

    content_response_text = data["mock_content_response"]
    grammar_response_text = data["mock_grammar_batch_response"]

    call_counter = {"content": 0, "grammar": 0}

    def mock_generate_content(*args, **kwargs):
        """Route mock responses based on prompt content."""
        mock_resp = MagicMock()

        # Inspect the prompt/contents to decide which response to return
        contents = kwargs.get("contents", "")
        if not contents and args:
            # positional: model, contents, ...
            contents = args[1] if len(args) > 1 else ""

        contents_str = str(contents).lower()

        # Grammar analysis prompts contain "grammatical_role" or "grammatical role"
        # or "json" + "words" pattern
        if "grammatical_role" in contents_str or ("json" in contents_str and "words" in contents_str and "sentence" in contents_str):
            mock_resp.text = grammar_response_text
            call_counter["grammar"] += 1
        else:
            # Content generation
            mock_resp.text = content_response_text
            call_counter["content"] += 1

        return mock_resp

    # ---- Mock audio & image generation ---------------------------------------
    def mock_generate_audio(sentences_list, voice, output_dir, **kwargs):
        """Return fake audio file paths."""
        return [f"audio_{i}.mp3" for i in range(len(sentences_list))]

    def mock_generate_images(queries, media_dir, **kwargs):
        """Return fake image file paths and used URLs set."""
        return [f"image_{i}.jpg" for i in range(len(queries))], set()

    # ---- Run the pipeline under mocks ----------------------------------------
    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir, exist_ok=True)

    # Patch points:
    #  1. st.session_state      → our MockSessionState
    #  2. genai.generate_content → mock_generate_content (via the client wrapper)
    #  3. generate_audio         → mock_generate_audio
    #  4. generate_images_pixabay → mock_generate_images
    #  5. genai.configure        → no-op
    #  6. genai.types            → mock with GenerateContentConfig

    mock_genai = MagicMock()
    mock_genai.generate_content = mock_generate_content
    mock_genai.configure = MagicMock()  # no-op
    mock_genai.genai = MagicMock()
    mock_genai.genai.types.GenerateContentConfig = dict  # simple dict for config

    with patch("streamlit.session_state", session_state), \
         patch("streamlit_app.services.generation.content_generator.get_gemini_api", return_value=mock_genai), \
         patch("streamlit_app.shared_utils.get_gemini_api", return_value=mock_genai), \
         patch("streamlit_app.core_functions.generate_audio", mock_generate_audio), \
         patch("streamlit_app.core_functions.generate_images_pixabay", mock_generate_images):

        # ---- STAGE 1: Analyzer Discovery -----------------------------------
        from streamlit_app.language_analyzers.analyzer_registry import AnalyzerRegistry
        registry = AnalyzerRegistry()
        registry._discover_analyzers()
        analyzer = registry.get_analyzer(language_code)
        analyzer_found = analyzer is not None

        report.add_stage(
            "1. Analyzer Discovery",
            analyzer_found,
            f"Analyzer for '{language_code}': {type(analyzer).__name__ if analyzer else 'NOT FOUND'}"
        )

        # ---- STAGE 2: Content Generation -----------------------------------
        from streamlit_app.services.generation.content_generator import ContentGenerator
        cg = ContentGenerator()

        content_result = cg.generate_word_meaning_sentences_and_keywords(
            word=word,
            language=language_name,
            num_sentences=num_sentences,
            gemini_api_key=session_state["google_api_key"],
            min_length=min_length,
            max_length=max_length,
            difficulty=difficulty,
            topics=[topic],
        )

        sentences_parsed = len(content_result.get("sentences", []))
        translations_parsed = len(content_result.get("translations", []))
        ipa_parsed = len(content_result.get("ipa", []))
        keywords_parsed = len(content_result.get("keywords", []))
        meaning = content_result.get("meaning", "")

        content_ok = (
            sentences_parsed == num_sentences
            and translations_parsed == num_sentences
            and meaning != ""
        )

        report.meaning = meaning
        report.add_stage(
            "2. Content Generation + Parsing",
            content_ok,
            f"Meaning: {meaning}\n"
            f"Sentences: {sentences_parsed}/{num_sentences}, "
            f"Translations: {translations_parsed}/{num_sentences}, "
            f"IPA: {ipa_parsed}/{num_sentences}, "
            f"Keywords: {keywords_parsed}/{num_sentences}"
        )

        # ---- Build sentence dicts (mimics sentence_generator.py) -----------
        sentences_list = []
        for i, s in enumerate(content_result.get("sentences", [])):
            sentences_list.append({
                "sentence": s,
                "english_translation": content_result["translations"][i] if i < len(content_result.get("translations", [])) else "",
                "ipa": content_result["ipa"][i] if i < len(content_result.get("ipa", [])) else "",
                "image_keywords": content_result["keywords"][i] if i < len(content_result.get("keywords", [])) else "",
                "context": "general",
                "role_of_word": "target",
                "word": word,
                "meaning": meaning,
            })

        # ---- STAGE 3: Grammar Analysis (batch) -----------------------------
        # Patch _call_ai on the analyzer so it returns our mock grammar JSON
        # instead of actually calling Gemini
        from streamlit_app.services.generation.grammar_processor import GrammarProcessor
        gp = GrammarProcessor()

        grammar_results = gp.batch_analyze_grammar_and_color(
            sentences=[s["sentence"] for s in sentences_list],
            target_words=[word] * len(sentences_list),
            language=language_name,
            gemini_api_key=session_state["google_api_key"],
            language_code=language_code,
        )

        # Merge grammar results into sentence dicts
        grammar_ok = True
        grammar_details = []
        for i, result in enumerate(grammar_results):
            sentences_list[i]["colored_sentence"] = result.get("colored_sentence", "")
            sentences_list[i]["word_explanations"] = result.get("word_explanations", [])
            sentences_list[i]["grammar_summary"] = result.get("grammar_summary", "")

            has_colored = bool(result.get("colored_sentence"))
            has_explanations = len(result.get("word_explanations", [])) > 0
            has_summary = bool(result.get("grammar_summary"))

            sentence_ok = has_colored and has_explanations and has_summary
            grammar_ok = grammar_ok and sentence_ok
            grammar_details.append(
                f"Sentence {i+1}: colored={'YES' if has_colored else 'NO'}, "
                f"explanations={len(result.get('word_explanations', []))}, "
                f"summary={'YES' if has_summary else 'NO'}"
            )

        report.add_stage(
            "3. Grammar Analysis (Batch)",
            grammar_ok,
            "\n".join(grammar_details)
        )
        report.sentences_data = sentences_list

        # ---- STAGE 4: Audio Generation (mocked) ---------------------------
        audio_files = mock_generate_audio(
            [s["sentence"] for s in sentences_list],
            "ja-JP-NanamiNeural",
            str(tmp_path / "media"),
        )
        report.audio_files = audio_files
        report.add_stage(
            "4. Audio Generation (mocked)",
            len(audio_files) == num_sentences,
            f"Generated {len(audio_files)} audio file paths"
        )

        # ---- STAGE 5: Image Generation (mocked) ---------------------------
        image_files, _ = mock_generate_images(
            [s.get("image_keywords", "") for s in sentences_list],
            str(tmp_path / "media"),
        )
        report.image_files = image_files
        report.add_stage(
            "5. Image Generation (mocked)",
            len(image_files) == num_sentences,
            f"Generated {len(image_files)} image file paths"
        )

        # ---- STAGE 6: Card Assembly Verification ---------------------------
        card_assembly_ok = True
        assembly_issues = []
        for i, s in enumerate(sentences_list):
            required = ["sentence", "english_translation", "ipa", "image_keywords",
                        "colored_sentence", "word_explanations", "grammar_summary"]
            for field in required:
                if field not in s or not s[field]:
                    card_assembly_ok = False
                    assembly_issues.append(f"Sentence {i+1} missing '{field}'")

        report.add_stage(
            "6. Card Assembly Verification",
            card_assembly_ok,
            "\n".join(assembly_issues) if assembly_issues else "All required fields present for all sentences"
        )

        # ---- STAGE 7: Difficulty Setting Verification ----------------------
        # Verify that difficulty='beginner' was respected (not overridden to 'intermediate')
        difficulty_ok = session_state.get("difficulty") == difficulty
        report.add_stage(
            "7. Difficulty Setting Respected",
            difficulty_ok,
            f"Session state difficulty: {session_state.get('difficulty')}, expected: {difficulty}"
        )

    # ---- Render & save report ------------------------------------------------
    report_text = report.render()
    try:
        import sys
        sys.stdout.buffer.write(("\n" + report_text + "\n").encode("utf-8", errors="replace"))
        sys.stdout.buffer.flush()
    except Exception:
        # Last resort: strip non-ASCII for truly broken terminals
        print("\n" + report_text.encode("ascii", errors="replace").decode("ascii"))

    report_file = REPORT_DIR / f"pipeline_report_{report_key}.txt"
    report_file.write_text(report_text, encoding="utf-8")
    logger.info(f"Report saved to {report_file}")

    # ---- Assertions ----------------------------------------------------------
    assert analyzer_found, f"Analyzer for {language_code} was NOT discovered"
    assert content_ok, f"Content generation failed: {sentences_parsed}/{num_sentences} sentences"
    assert grammar_ok, "Grammar analysis missing colored_sentence, word_explanations, or grammar_summary"
    assert card_assembly_ok, f"Card assembly issues: {assembly_issues}"
    assert difficulty_ok, f"Difficulty was overridden: got {session_state.get('difficulty')}, expected {difficulty}"


# ============================================================================
# MAIN TEST — one run per language (default difficulty in mock data)
# ============================================================================

@pytest.mark.parametrize("lang_key", list(LANGUAGE_MOCK_DATA.keys()))
def test_end_to_end_pipeline(lang_key: str, tmp_path: Path):
    """Full end-to-end pipeline test for a language."""
    _run_full_pipeline(LANGUAGE_MOCK_DATA[lang_key], lang_key, tmp_path)


# ============================================================================
# LATVIAN — full pipeline must pass at all 3 difficulty levels.
# Tracks the project-wide requirement that every analyzer is validated for
# beginner, intermediate, and advanced complexity (see CLAUDE.md "E2E Test
# Sentence Difficulty Coverage").
# ============================================================================

@pytest.mark.parametrize("difficulty", ["beginner", "intermediate", "advanced"])
def test_latvian_all_difficulty_levels(difficulty: str, tmp_path: Path):
    """Run the full pipeline for Latvian at beginner, intermediate, and advanced."""
    data = LATVIAN_LEVEL_MOCK_DATA[difficulty]
    _run_full_pipeline(data, f"latvian_{difficulty}", tmp_path)


# ============================================================================
# PORTUGUESE — full pipeline must pass at all 3 difficulty levels.
# Tracks the project-wide requirement that every analyzer is validated for
# beginner, intermediate, and advanced complexity (see CLAUDE.md "E2E Test
# Sentence Difficulty Coverage").
# ============================================================================

@pytest.mark.parametrize("difficulty", ["beginner", "intermediate", "advanced"])
def test_portuguese_all_difficulty_levels(difficulty: str, tmp_path: Path):
    """Run the full pipeline for Portuguese at beginner, intermediate, and advanced."""
    data = PORTUGUESE_LEVEL_MOCK_DATA[difficulty]
    _run_full_pipeline(data, f"portuguese_{difficulty}", tmp_path)


# ============================================================================
# ENGLISH — full pipeline must pass at all 3 difficulty levels.
# Tracks the project-wide requirement that every analyzer is validated for
# beginner, intermediate, and advanced complexity (see CLAUDE.md "E2E Test
# Sentence Difficulty Coverage").
# ============================================================================

@pytest.mark.parametrize("difficulty", ["beginner", "intermediate", "advanced"])
def test_english_all_difficulty_levels(difficulty: str, tmp_path: Path):
    """Run the full pipeline for English at beginner, intermediate, and advanced."""
    data = ENGLISH_LEVEL_MOCK_DATA[difficulty]
    _run_full_pipeline(data, f"english_{difficulty}", tmp_path)


# ============================================================================
# STANDALONE RUNNER (for running outside pytest)
# ============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])

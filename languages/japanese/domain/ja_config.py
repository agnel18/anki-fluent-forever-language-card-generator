# languages/japanese/domain/ja_config.py
"""
Japanese Configuration - Domain Component

Loads external YAML/JSON configuration files and provides
Japanese-specific settings for grammar analysis.
"""

import json
import logging
import yaml
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ComplexityLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class GrammaticalRole(Enum):
    """Japanese grammatical roles."""
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    I_ADJECTIVE = "i_adjective"
    NA_ADJECTIVE = "na_adjective"
    ADVERB = "adverb"
    PARTICLE = "particle"
    TOPIC_PARTICLE = "topic_particle"
    SUBJECT_PARTICLE = "subject_particle"
    OBJECT_PARTICLE = "object_particle"
    COPULA = "copula"
    AUXILIARY_VERB = "auxiliary_verb"
    CONJUNCTION = "conjunction"
    COUNTER = "counter"
    HONORIFIC_VERB = "honorific_verb"
    HUMBLE_VERB = "humble_verb"
    POTENTIAL_VERB = "potential_verb"
    PASSIVE_VERB = "passive_verb"
    CAUSATIVE_VERB = "causative_verb"
    TE_FORM = "te_form"
    CONDITIONAL_FORM = "conditional_form"
    VOLITIONAL_FORM = "volitional_form"
    SENTENCE_FINAL_PARTICLE = "sentence_final_particle"
    NOMINALIZER = "nominalizer"
    QUOTATION_PARTICLE = "quotation_particle"
    INTERJECTION = "interjection"
    PRONOUN = "pronoun"


@dataclass
class JaConfig:
    """Configuration for Japanese analyzer, loaded from external files."""
    grammatical_roles: Dict[str, Any]
    particle_patterns: Dict[str, Any]
    verb_conjugations: Dict[str, Any]
    adjective_patterns: Dict[str, Any]
    honorific_patterns: Dict[str, Any]
    counter_patterns: Dict[str, Any]
    word_meanings: Dict[str, Any]
    prompt_templates: Dict[str, str]
    patterns: Dict[str, Any]

    def __init__(self):
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = self._load_yaml(config_dir / "ja_grammatical_roles.yaml")
        self.particle_patterns = self._load_yaml(config_dir / "ja_particle_patterns.yaml")
        self.verb_conjugations = self._load_yaml(config_dir / "ja_verb_conjugations.yaml")
        self.adjective_patterns = self._load_yaml(config_dir / "ja_adjective_patterns.yaml")
        self.honorific_patterns = self._load_yaml(config_dir / "ja_honorific_patterns.yaml")
        self.counter_patterns = self._load_yaml(config_dir / "ja_counter_patterns.yaml")
        self.word_meanings = self._load_json(config_dir / "ja_word_meanings.json")
        self.patterns = self._load_yaml(config_dir / "ja_patterns.yaml")

        self.prompt_templates = {
            "single": """Analyze this Japanese sentence and provide a detailed grammatical breakdown.

Sentence: {{sentence}}
Target word: {{target_word}}
Complexity level: {{complexity}}

JAPANESE GRAMMAR ANALYSIS REQUIREMENTS:
- Break the sentence into individual words/morphemes (Japanese has no spaces between words)
- Identify all particles (は, が, を, に, で, の, と, から, まで, へ, も, よ, ね, か) and their grammatical functions
- Note verb conjugation forms (dictionary, masu, te-form, ta-form, nai-form, potential, passive, causative)
- Distinguish between い-adjectives and な-adjectives
- Identify politeness level (plain, polite/masu-desu, humble, honorific)
- Recognize counter words and their associated numbers
- Note SOV (Subject-Object-Verb) word order patterns
- Include readings in hiragana for kanji words

Return a JSON object with exactly this structure:
{
  "sentence": "{{sentence}}",
  "words": [
    {
      "word": "first_word_or_morpheme",
      "reading": "hiragana_reading_if_contains_kanji",
      "grammatical_role": "noun|verb|i_adjective|na_adjective|adverb|particle|topic_particle|subject_particle|object_particle|copula|auxiliary_verb|conjunction|counter|honorific_verb|humble_verb|potential_verb|passive_verb|causative_verb|te_form|sentence_final_particle|nominalizer|quotation_particle|pronoun|interjection|other",
      "conjugation_form": "dictionary|masu|te|ta|nai|potential|passive|causative|conditional|volitional|null",
      "politeness": "plain|polite|humble|honorific|null",
      "individual_meaning": "detailed explanation of this word's grammatical role and meaning"
    }
  ],
  "explanations": {
    "overall_structure": "sentence structure analysis noting SOV order and particle usage",
    "key_features": "notable Japanese grammar features in this sentence",
    "complexity_notes": "how {{complexity}} level features are demonstrated"
  }
}

Important:
- Break compound expressions into individual morphemes where appropriate
- Provide readings (hiragana) for all kanji words
- Explain particle functions clearly
- Note verb group (godan/ichidan/irregular) where applicable
- Use only valid JSON format
""",
            "batch": """Analyze these Japanese sentences and provide detailed grammatical breakdowns for each.

Sentences: {{sentences_text}}
Target word: {{target_word}}
Complexity level: {{complexity}}

Break each sentence into individual words/morphemes (Japanese has no spaces).
Identify particles, verb forms, adjective types, and politeness levels.

Return a JSON object with exactly this structure:
{
  "batch_results": [
    {
      "sentence": "first sentence",
      "words": [
        {
          "word": "word_or_morpheme",
          "reading": "hiragana_reading",
          "grammatical_role": "noun|verb|i_adjective|na_adjective|adverb|particle|topic_particle|subject_particle|object_particle|copula|auxiliary_verb|conjunction|counter|pronoun|other",
          "individual_meaning": "brief explanation of this word's role"
        }
      ],
      "explanations": {
        "overall_structure": "brief explanation",
        "key_features": "notable features"
      }
    }
  ]
}

Important:
- Analyze each sentence separately
- Break each sentence into individual words/morphemes
- Assign appropriate Japanese grammatical roles
- Provide meaningful explanations in English
- Use only valid JSON format
"""
        }

        self.voice_config = {
            'language_code': 'ja-JP',
            'name': 'ja-JP-Neural2-B',
            'ssml_gender': 'FEMALE',
            'speaking_rate': 0.9,
            'pitch': 0.0
        }

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load YAML file {path}: {e}")
            return {}

    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON file {path}: {e}")
            return {}

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for Japanese grammatical elements based on complexity."""
        schemes = {
            "beginner": {
                "noun": "#FFAA00",
                "verb": "#44FF44",
                "adjective": "#FF44FF",
                "i_adjective": "#FF44FF",
                "na_adjective": "#FF44FF",
                "particle": "#4444FF",
                "adverb": "#44FFFF",
                "copula": "#AA44FF",
                "conjunction": "#888888",
                "pronoun": "#FF4444",
                "interjection": "#FFD700",
                "other": "#AAAAAA"
            },
            "intermediate": {
                "noun": "#FFAA00",
                "verb": "#44FF44",
                "auxiliary_verb": "#228B22",
                "i_adjective": "#FF44FF",
                "na_adjective": "#FF88CC",
                "adjective": "#FF44FF",
                "adverb": "#44FFFF",
                "particle": "#4444FF",
                "topic_particle": "#1E90FF",
                "subject_particle": "#4169E1",
                "object_particle": "#6495ED",
                "copula": "#AA44FF",
                "counter": "#FFD700",
                "conjunction": "#888888",
                "pronoun": "#FF4444",
                "interjection": "#FFD700",
                "other": "#AAAAAA"
            },
            "advanced": {
                "noun": "#FFAA00",
                "verb": "#44FF44",
                "auxiliary_verb": "#228B22",
                "honorific_verb": "#006400",
                "humble_verb": "#2E8B57",
                "potential_verb": "#3CB371",
                "passive_verb": "#66CDAA",
                "causative_verb": "#8FBC8F",
                "te_form": "#32CD32",
                "conditional_form": "#90EE90",
                "volitional_form": "#98FB98",
                "i_adjective": "#FF44FF",
                "na_adjective": "#FF88CC",
                "adjective": "#FF44FF",
                "adverb": "#44FFFF",
                "particle": "#4444FF",
                "topic_particle": "#1E90FF",
                "subject_particle": "#4169E1",
                "object_particle": "#6495ED",
                "sentence_final_particle": "#FF6347",
                "nominalizer": "#CD853F",
                "quotation_particle": "#DEB887",
                "copula": "#AA44FF",
                "counter": "#FFD700",
                "conjunction": "#888888",
                "pronoun": "#FF4444",
                "interjection": "#FFD700",
                "other": "#AAAAAA"
            }
        }
        return schemes.get(complexity, schemes["intermediate"])

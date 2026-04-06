# languages/korean/domain/ko_config.py
"""
Korean Configuration - Domain Component

Loads external YAML/JSON configuration files and provides
Korean-specific settings for grammar analysis.
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
    """Korean grammatical roles."""
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    DESCRIPTIVE_VERB = "descriptive_verb"
    ADVERB = "adverb"
    PARTICLE = "particle"
    TOPIC_MARKER = "topic_marker"
    SUBJECT_MARKER = "subject_marker"
    OBJECT_MARKER = "object_marker"
    HONORIFIC_PARTICLE = "honorific_particle"
    POSSESSIVE_PARTICLE = "possessive_particle"
    LOCATIVE_PARTICLE = "locative_particle"
    INSTRUMENTAL_PARTICLE = "instrumental_particle"
    COMITATIVE_PARTICLE = "comitative_particle"
    COPULA = "copula"
    AUXILIARY_VERB = "auxiliary_verb"
    CONJUNCTION = "conjunction"
    COUNTER = "counter"
    HONORIFIC_VERB = "honorific_verb"
    HUMBLE_VERB = "humble_verb"
    PASSIVE_VERB = "passive_verb"
    CAUSATIVE_VERB = "causative_verb"
    CONNECTIVE_ENDING = "connective_ending"
    SENTENCE_FINAL_ENDING = "sentence_final_ending"
    NOMINALIZER = "nominalizer"
    QUOTATIVE = "quotative"
    INTERJECTION = "interjection"
    PRONOUN = "pronoun"


@dataclass
class KoConfig:
    """Configuration for Korean analyzer, loaded from external files."""
    grammatical_roles: Dict[str, Any]
    particle_patterns: Dict[str, Any]
    verb_conjugations: Dict[str, Any]
    honorific_patterns: Dict[str, Any]
    word_meanings: Dict[str, Any]
    prompt_templates: Dict[str, str]
    patterns: Dict[str, Any]

    def __init__(self):
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = self._load_yaml(config_dir / "ko_grammatical_roles.yaml")
        self.particle_patterns = self._load_yaml(config_dir / "ko_particle_patterns.yaml")
        self.verb_conjugations = self._load_yaml(config_dir / "ko_verb_conjugations.yaml")
        self.honorific_patterns = self._load_yaml(config_dir / "ko_honorific_patterns.yaml")
        self.word_meanings = self._load_json(config_dir / "ko_word_meanings.json")
        self.patterns = self._load_yaml(config_dir / "ko_patterns.yaml")

        self.prompt_templates = {
            "single": """Analyze this Korean sentence and provide a detailed grammatical breakdown.

Sentence: {{sentence}}
Target word: {{target_word}}
Complexity level: {{complexity}}

KOREAN GRAMMAR ANALYSIS REQUIREMENTS:
- Identify all particles (은/는 topic, 이/가 subject, 을/를 object, 에/에서 location, 의 possessive, etc.)
- Note verb conjugation: tense (present/past/future), speech level (formal/polite/casual/plain)
- Identify honorific markers: -(으)시- suffix, special honorific vocabulary
- Recognize connective endings: -고, -서, -면, -지만, -는데, etc.
- Distinguish adjectives (which conjugate like verbs in Korean)
- Identify counters/classifiers used with numbers
- Note the SOV (Subject-Object-Verb) word order

Return a JSON object with exactly this structure:
{
  "sentence": "{{sentence}}",
  "words": [
    {
      "word": "first_word",
      "grammatical_role": "noun|verb|adjective|adverb|particle|topic_marker|subject_marker|object_marker|honorific_particle|possessive_particle|locative_particle|instrumental_particle|comitative_particle|copula|auxiliary_verb|conjunction|counter|honorific_verb|humble_verb|passive_verb|causative_verb|connective_ending|sentence_final_ending|nominalizer|quotative|pronoun|interjection|other",
      "speech_level": "formal|polite|casual|plain|null",
      "tense": "present|past|future|null",
      "honorific": "true|false|null",
      "individual_meaning": "detailed explanation of this word's grammatical role and meaning"
    }
  ],
  "explanations": {
    "overall_structure": "sentence structure analysis noting SOV order and particle usage",
    "key_features": "notable Korean grammar features in this sentence",
    "complexity_notes": "how {{complexity}} level features are demonstrated"
  }
}

Important:
- Korean uses spaces between words, so split on spaces
- Particles are attached to the preceding noun — analyze them separately
- Explain speech level and politeness where applicable
- Note verb/adjective stems and conjugation patterns
- Use only valid JSON format
""",
            "batch": """Analyze these Korean sentences and provide detailed grammatical breakdowns for each.

Sentences: {{sentences_text}}
Target word: {{target_word}}
Complexity level: {{complexity}}

Identify particles, verb conjugations, speech levels, and honorific forms.

Return a JSON object with exactly this structure:
{
  "batch_results": [
    {
      "sentence": "first sentence",
      "words": [
        {
          "word": "word",
          "grammatical_role": "noun|verb|adjective|adverb|particle|topic_marker|subject_marker|object_marker|copula|auxiliary_verb|conjunction|counter|pronoun|other",
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
- Split each sentence into individual words (Korean uses spaces)
- Separate particles from their host nouns
- Assign appropriate Korean grammatical roles
- Provide meaningful explanations in English
- Use only valid JSON format
"""
        }

        self.voice_config = {
            'language_code': 'ko-KR',
            'name': 'ko-KR-Neural2-A',
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
        """Return color scheme for Korean grammatical elements based on complexity."""
        schemes = {
            "beginner": {
                "noun": "#FFAA00",
                "verb": "#44FF44",
                "adjective": "#FF44FF",
                "adverb": "#44FFFF",
                "particle": "#4444FF",
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
                "adjective": "#FF44FF",
                "adverb": "#44FFFF",
                "particle": "#4444FF",
                "topic_marker": "#1E90FF",
                "subject_marker": "#4169E1",
                "object_marker": "#6495ED",
                "locative_particle": "#7B68EE",
                "copula": "#AA44FF",
                "counter": "#FFD700",
                "conjunction": "#888888",
                "pronoun": "#FF4444",
                "connective_ending": "#FF6347",
                "interjection": "#FFD700",
                "other": "#AAAAAA"
            },
            "advanced": {
                "noun": "#FFAA00",
                "verb": "#44FF44",
                "auxiliary_verb": "#228B22",
                "honorific_verb": "#006400",
                "humble_verb": "#2E8B57",
                "passive_verb": "#66CDAA",
                "causative_verb": "#8FBC8F",
                "adjective": "#FF44FF",
                "descriptive_verb": "#FF88CC",
                "adverb": "#44FFFF",
                "particle": "#4444FF",
                "topic_marker": "#1E90FF",
                "subject_marker": "#4169E1",
                "object_marker": "#6495ED",
                "honorific_particle": "#00CED1",
                "possessive_particle": "#87CEEB",
                "locative_particle": "#7B68EE",
                "instrumental_particle": "#9370DB",
                "comitative_particle": "#BA55D3",
                "copula": "#AA44FF",
                "counter": "#FFD700",
                "conjunction": "#888888",
                "pronoun": "#FF4444",
                "connective_ending": "#FF6347",
                "sentence_final_ending": "#CD853F",
                "nominalizer": "#DEB887",
                "quotative": "#D2691E",
                "interjection": "#FFD700",
                "other": "#AAAAAA"
            }
        }
        return schemes.get(complexity, schemes["intermediate"])

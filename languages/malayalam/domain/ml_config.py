# languages/malayalam/domain/ml_config.py
"""
Malayalam Configuration - Domain Component

Loads external YAML/JSON configuration files and provides
Malayalam-specific settings for grammar analysis.

Malayalam is a Dravidian language with:
- Agglutinative morphology
- SOV word order
- Rich case system (7 primary cases)
- No grammatical gender
- Postpositions (not prepositions)
- 3-level honorific system
- Sandhi (phonological joining rules)
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
    """Malayalam grammatical roles."""
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PRONOUN = "pronoun"
    POSTPOSITION = "postposition"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    DEMONSTRATIVE = "demonstrative"
    # Malayalam-specific roles
    CASE_MARKER = "case_marker"
    VERBAL_PARTICIPLE = "verbal_participle"
    AUXILIARY_VERB = "auxiliary_verb"
    CAUSATIVE_VERB = "causative_verb"
    PASSIVE_VERB = "passive_verb"
    COPULA = "copula"
    NEGATIVE_PARTICLE = "negative_particle"
    QUESTION_PARTICLE = "question_particle"
    EMPHATIC_PARTICLE = "emphatic_particle"
    HONORIFIC_PRONOUN = "honorific_pronoun"
    RELATIVE_PARTICIPLE = "relative_participle"
    CONDITIONAL_FORM = "conditional_form"
    CONCESSIVE_FORM = "concessive_form"
    INFINITIVE = "infinitive"
    CLASSIFIER = "classifier"
    DETERMINER = "determiner"


@dataclass
class MlConfig:
    """Configuration for Malayalam analyzer, loaded from external files."""
    grammatical_roles: Dict[str, Any]
    case_patterns: Dict[str, Any]
    verb_conjugations: Dict[str, Any]
    postposition_patterns: Dict[str, Any]
    sandhi_rules: Dict[str, Any]
    honorific_patterns: Dict[str, Any]
    word_meanings: Dict[str, Any]
    prompt_templates: Dict[str, str]
    patterns: Dict[str, Any]

    def __init__(self):
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = self._load_yaml(config_dir / "ml_grammatical_roles.yaml")
        self.case_patterns = self._load_yaml(config_dir / "ml_case_patterns.yaml")
        self.verb_conjugations = self._load_yaml(config_dir / "ml_verb_conjugations.yaml")
        self.postposition_patterns = self._load_yaml(config_dir / "ml_postposition_patterns.yaml")
        self.sandhi_rules = self._load_yaml(config_dir / "ml_sandhi_rules.yaml")
        self.honorific_patterns = self._load_yaml(config_dir / "ml_honorific_patterns.yaml")
        self.word_meanings = self._load_json(config_dir / "ml_word_meanings.json")
        self.patterns = self._load_yaml(config_dir / "ml_patterns.yaml")

        self.prompt_templates = {
            "single": """Analyze this Malayalam sentence and provide a detailed grammatical breakdown.

Sentence: {{sentence}}
Target word: {{target_word}}
Complexity level: {{complexity}}

MALAYALAM GRAMMAR ANALYSIS REQUIREMENTS:
- Malayalam is a Dravidian language with SOV (Subject-Object-Verb) word order
- Identify agglutinative morphology: stems + case suffixes + postpositions
- Recognize all 7 cases: nominative, accusative (-എ/-യെ/-നെ), dative (-ക്കു/-ക്ക്), genitive (-ന്റെ/-ഉടെ), instrumental (-ആൽ/-കൊണ്ട്), locative (-ഇൽ/-ത്ത്), sociative (-ഓട്/-ഓടു)
- Note verb tenses: past (-ഇ/-ത്ത), present (-ഉന്ന), future (-ഉം)
- Identify verbal participles and converbs (conjunctive, conditional, concessive)
- Recognize postpositions (Malayalam uses postpositions, NOT prepositions)
- Note sandhi (phonological joining) effects
- Identify honorific levels: informal (നീ), polite (നിങ്ങൾ), formal (താങ്കൾ)
- Malayalam has NO grammatical gender — only natural gender distinctions

Return a JSON object with exactly this structure:
{
  "sentence": "{{sentence}}",
  "words": [
    {
      "word": "first_word",
      "grammatical_role": "noun|verb|adjective|adverb|pronoun|postposition|conjunction|case_marker|verbal_participle|auxiliary_verb|causative_verb|passive_verb|copula|negative_particle|question_particle|emphatic_particle|honorific_pronoun|relative_participle|conditional_form|concessive_form|infinitive|classifier|demonstrative|determiner|interjection|other",
      "case": "nominative|accusative|dative|genitive|instrumental|locative|sociative|null",
      "tense": "past|present|future|null",
      "individual_meaning": "detailed explanation including Malayalam-specific grammatical features"
    }
  ],
  "explanations": {
    "overall_structure": "sentence structure noting SOV order and case usage",
    "key_features": "notable Malayalam grammar features in this sentence",
    "complexity_notes": "how {{complexity}} level features are demonstrated"
  }
}

Important:
- Include case, tense, aspect information where applicable
- Explain agglutinative suffixes and their grammatical functions
- Note postposition usage and sandhi effects
- Break down compound verb forms
- Use only valid JSON format
""",
            "batch": """Analyze these Malayalam sentences and provide detailed grammatical breakdowns for each.

Sentences: {{sentences_text}}
Target word: {{target_word}}
Complexity level: {{complexity}}

Malayalam is a Dravidian agglutinative language with SOV word order.
Identify case markers, verb conjugations, postpositions, and sandhi effects.

Return a JSON object with exactly this structure:
{
  "batch_results": [
    {
      "sentence": "first sentence",
      "words": [
        {
          "word": "word",
          "grammatical_role": "noun|verb|adjective|adverb|pronoun|postposition|conjunction|case_marker|verbal_participle|auxiliary_verb|copula|negative_particle|question_particle|demonstrative|other",
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
- Identify Malayalam-specific grammatical roles
- Note case markers and agglutinative suffixes
- Provide meaningful explanations in English
- Use only valid JSON format
"""
        }

        self.voice_config = {
            'language_code': 'ml-IN',
            'name': 'ml-IN-AadhiNeural',
            'ssml_gender': 'MALE',
            'speaking_rate': 1.0,
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
        """Return color scheme for Malayalam grammatical elements based on complexity."""
        schemes = {
            "beginner": {
                "noun": "#FFAA00",
                "verb": "#44FF44",
                "adjective": "#FF44FF",
                "adverb": "#44FFFF",
                "pronoun": "#4FC3F7",
                "postposition": "#FF6B6B",
                "conjunction": "#888888",
                "case_marker": "#81C784",
                "copula": "#AA44FF",
                "negative_particle": "#FF5252",
                "question_particle": "#FFD740",
                "demonstrative": "#CE93D8",
                "determiner": "#A5D6A7",
                "other": "#AAAAAA",
                "target_word": "#FF4444"
            },
            "intermediate": {
                "noun": "#FFAA00",
                "verb": "#44FF44",
                "adjective": "#FF44FF",
                "adverb": "#44FFFF",
                "pronoun": "#4FC3F7",
                "postposition": "#FF6B6B",
                "conjunction": "#888888",
                "case_marker": "#81C784",
                "verbal_participle": "#B39DDB",
                "auxiliary_verb": "#CE93D8",
                "copula": "#AA44FF",
                "negative_particle": "#FF5252",
                "question_particle": "#FFD740",
                "emphatic_particle": "#FFAB91",
                "honorific_pronoun": "#80CBC4",
                "demonstrative": "#CE93D8",
                "determiner": "#A5D6A7",
                "infinitive": "#AED581",
                "other": "#AAAAAA",
                "target_word": "#FF4444"
            },
            "advanced": {
                "noun": "#FFAA00",
                "verb": "#44FF44",
                "adjective": "#FF44FF",
                "adverb": "#44FFFF",
                "pronoun": "#4FC3F7",
                "postposition": "#FF6B6B",
                "conjunction": "#888888",
                "case_marker": "#81C784",
                "verbal_participle": "#B39DDB",
                "auxiliary_verb": "#CE93D8",
                "causative_verb": "#F48FB1",
                "passive_verb": "#80DEEA",
                "copula": "#AA44FF",
                "negative_particle": "#FF5252",
                "question_particle": "#FFD740",
                "emphatic_particle": "#FFAB91",
                "honorific_pronoun": "#80CBC4",
                "relative_participle": "#DCE775",
                "conditional_form": "#FFE082",
                "concessive_form": "#BCAAA4",
                "infinitive": "#AED581",
                "classifier": "#FF8A65",
                "demonstrative": "#CE93D8",
                "determiner": "#A5D6A7",
                "interjection": "#E0E0E0",
                "other": "#AAAAAA",
                "target_word": "#FF4444"
            }
        }
        return schemes.get(complexity, schemes["intermediate"])

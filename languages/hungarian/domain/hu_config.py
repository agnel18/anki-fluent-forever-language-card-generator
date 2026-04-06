# languages/hungarian/domain/hu_config.py
"""
Hungarian Configuration - Domain Component

Loads external YAML/JSON configuration files and provides
Hungarian-specific settings for grammar analysis.
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
    """Hungarian grammatical roles."""
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PRONOUN = "pronoun"
    DEFINITE_ARTICLE = "definite_article"
    INDEFINITE_ARTICLE = "indefinite_article"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    NUMERAL = "numeral"
    # Case markers (Hungarian-specific: 18 cases)
    ACCUSATIVE = "accusative"
    DATIVE = "dative"
    INSTRUMENTAL = "instrumental"
    CAUSAL_FINAL = "causal_final"
    TRANSLATIVE = "translative"
    INESSIVE = "inessive"
    SUPERESSIVE = "superessive"
    ADESSIVE = "adessive"
    SUBLATIVE = "sublative"
    DELATIVE = "delative"
    ELATIVE = "elative"
    ILLATIVE = "illative"
    ALLATIVE = "allative"
    ABLATIVE = "ablative"
    TERMINATIVE = "terminative"
    ESSIVE_FORMAL = "essive_formal"
    DISTRIBUTIVE = "distributive"
    # Verb-specific
    PREVERB = "preverb"
    DEFINITE_CONJUGATION = "definite_conjugation"
    INDEFINITE_CONJUGATION = "indefinite_conjugation"
    AUXILIARY_VERB = "auxiliary_verb"
    CAUSATIVE_VERB = "causative_verb"
    POTENTIAL_VERB = "potential_verb"
    COPULA = "copula"
    # Postpositions
    POSTPOSITION = "postposition"
    # Possessive
    POSSESSIVE_SUFFIX = "possessive_suffix"
    # Other
    OTHER = "other"


@dataclass
class HuConfig:
    """Configuration for Hungarian analyzer, loaded from external files."""
    grammatical_roles: Dict[str, Any]
    word_meanings: Dict[str, Any]
    prompt_templates: Dict[str, str]
    patterns: Dict[str, Any]

    def __init__(self):
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = self._load_yaml(config_dir / "hu_grammatical_roles.yaml")
        self.word_meanings = self._load_json(config_dir / "hu_word_meanings.json")
        self.patterns = self._load_yaml(config_dir / "hu_patterns.yaml")

        self.prompt_templates = {
            "single": """Analyze this Hungarian sentence and provide a detailed grammatical breakdown.

Sentence: {{sentence}}
Target word: {{target_word}}
Complexity level: {{complexity}}

HUNGARIAN GRAMMAR ANALYSIS REQUIREMENTS:
- Identify all case markers (accusative -t, dative -nak/-nek, instrumental -val/-vel, inessive -ban/-ben, etc.)
- Note definite ("a/az" + definite conjugation) vs indefinite conjugation on verbs
- Identify preverbs (meg-, el-, ki-, be-, fel-, le-, vissza-, össze-) and note if separated
- Recognize postpositions (mellett, alatt, felett, mögött, előtt, között, etc.)
- Identify possessive suffixes (-m, -d, -ja/-je, -nk, -tok/-tek/-tök, -juk/-jük)
- Note vowel harmony in suffix selection (back: -ban vs front: -ben)
- Identify verb tense (present, past -t-), mood (indicative, conditional -ná/-né, subjunctive -j-)
- Identify definite (a, az) and indefinite (egy) articles
- Note focus position (element immediately before verb receives emphasis)

Return a JSON object with exactly this structure:
{
  "sentence": "{{sentence}}",
  "words": [
    {
      "word": "first_word",
      "grammatical_role": "noun|verb|adjective|adverb|pronoun|definite_article|indefinite_article|conjunction|interjection|numeral|accusative|dative|instrumental|causal_final|translative|inessive|superessive|adessive|sublative|delative|elative|illative|allative|ablative|terminative|essive_formal|distributive|preverb|definite_conjugation|indefinite_conjugation|auxiliary_verb|causative_verb|potential_verb|copula|postposition|possessive_suffix|other",
      "case": "nominative|accusative|dative|instrumental|inessive|superessive|adessive|sublative|delative|elative|illative|allative|ablative|terminative|causal_final|translative|essive_formal|distributive|null",
      "conjugation_type": "definite|indefinite|null",
      "tense": "present|past|future|null",
      "mood": "indicative|conditional|subjunctive|imperative|null",
      "possessive": "1sg|2sg|3sg|1pl|2pl|3pl|null",
      "preverb": "meg|el|ki|be|fel|le|vissza|össze|null",
      "vowel_harmony": "front|back|mixed|null",
      "individual_meaning": "detailed explanation of this word's grammatical role and meaning"
    }
  ],
  "explanations": {
    "overall_structure": "sentence structure analysis noting word order, focus position, and case usage",
    "key_features": "notable Hungarian grammar features in this sentence",
    "complexity_notes": "how {{complexity}} level features are demonstrated"
  }
}

Important:
- Hungarian uses spaces between words
- Case suffixes are attached to nouns — analyze the base noun and its case suffix
- Preverbs may be attached to or separated from the verb
- Note definite vs indefinite conjugation explicitly
- Explain vowel harmony where relevant
- Use only valid JSON format
""",
            "batch": """Analyze these Hungarian sentences and provide detailed grammatical breakdowns for each.

Sentences: {{sentences_text}}
Target word: {{target_word}}
Complexity level: {{complexity}}

Identify case markers, verb conjugation type (definite/indefinite), preverbs, postpositions, and possessive suffixes.

Return a JSON object with exactly this structure:
{
  "batch_results": [
    {
      "sentence": "first sentence",
      "words": [
        {
          "word": "word",
          "grammatical_role": "noun|verb|adjective|adverb|pronoun|definite_article|indefinite_article|conjunction|numeral|preverb|postposition|copula|other",
          "case": "nominative|accusative|dative|instrumental|inessive|null",
          "conjugation_type": "definite|indefinite|null",
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
- Split each sentence into individual words (Hungarian uses spaces)
- Identify case suffixes on nouns and conjugation type on verbs
- Assign appropriate Hungarian grammatical roles
- Provide meaningful explanations in English
- Use only valid JSON format
"""
        }

        self.voice_config = {
            'language_code': 'hu-HU',
            'name': 'hu-HU-NoemiNeural',
            'ssml_gender': 'FEMALE',
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
        """Return color scheme for Hungarian grammatical elements based on complexity.

        Hungarian-specific colors for:
        - Case markers (shades of blue/purple for the 18 cases)
        - Definite vs indefinite conjugation (distinct greens)
        - Preverbs (orange/amber tones)
        - Postpositions (teal/cyan shades)
        - Possessive suffixes (pink/rose tones)
        """
        schemes = {
            "beginner": {
                "noun": "#FFAA00",           # Amber — nouns
                "verb": "#44FF44",           # Green — verbs
                "adjective": "#FF44FF",      # Magenta — adjectives
                "adverb": "#44FFFF",         # Cyan — adverbs
                "pronoun": "#FF4444",        # Red — pronouns
                "definite_article": "#87CEEB",  # Sky blue — definite article
                "indefinite_article": "#B0E0E6", # Powder blue — indefinite article
                "conjunction": "#888888",    # Gray — conjunctions
                "copula": "#AA44FF",         # Purple — copula
                "postposition": "#20B2AA",   # Teal — postpositions
                "preverb": "#FF8C00",        # Dark orange — preverbs
                "numeral": "#FFD700",        # Gold — numerals
                "interjection": "#FFD700",   # Gold — interjections
                "other": "#AAAAAA"           # Gray — other
            },
            "intermediate": {
                "noun": "#FFAA00",
                "verb": "#44FF44",
                "definite_conjugation": "#228B22",   # Forest green — definite conj.
                "indefinite_conjugation": "#32CD32",  # Lime green — indefinite conj.
                "auxiliary_verb": "#2E8B57",          # Sea green — auxiliary
                "adjective": "#FF44FF",
                "adverb": "#44FFFF",
                "pronoun": "#FF4444",
                "definite_article": "#87CEEB",
                "indefinite_article": "#B0E0E6",
                "conjunction": "#888888",
                "copula": "#AA44FF",
                "postposition": "#20B2AA",
                "preverb": "#FF8C00",
                "numeral": "#FFD700",
                # Case markers
                "accusative": "#4169E1",      # Royal blue — accusative -t
                "dative": "#6495ED",          # Cornflower blue — dative -nak/-nek
                "instrumental": "#7B68EE",    # Medium slate blue — instrumental -val/-vel
                "inessive": "#4682B4",        # Steel blue — inessive -ban/-ben
                "superessive": "#5F9EA0",     # Cadet blue — superessive -n/-on/-en/-ön
                "sublative": "#6A5ACD",       # Slate blue — sublative -ra/-re
                "elative": "#483D8B",         # Dark slate blue — elative -ból/-ből
                "illative": "#191970",        # Midnight blue — illative -ba/-be
                "allative": "#1E90FF",        # Dodger blue — allative -hoz/-hez/-höz
                "ablative": "#00BFFF",        # Deep sky blue — ablative -tól/-től
                # Possessive
                "possessive_suffix": "#FF69B4",  # Hot pink — possessive suffixes
                "interjection": "#FFD700",
                "other": "#AAAAAA"
            },
            "advanced": {
                "noun": "#FFAA00",
                "verb": "#44FF44",
                "definite_conjugation": "#228B22",
                "indefinite_conjugation": "#32CD32",
                "auxiliary_verb": "#2E8B57",
                "causative_verb": "#66CDAA",
                "potential_verb": "#8FBC8F",
                "adjective": "#FF44FF",
                "adverb": "#44FFFF",
                "pronoun": "#FF4444",
                "definite_article": "#87CEEB",
                "indefinite_article": "#B0E0E6",
                "conjunction": "#888888",
                "copula": "#AA44FF",
                "postposition": "#20B2AA",
                "preverb": "#FF8C00",
                "numeral": "#FFD700",
                # All 18 case markers
                "accusative": "#4169E1",
                "dative": "#6495ED",
                "instrumental": "#7B68EE",
                "causal_final": "#9370DB",
                "translative": "#BA55D3",
                "inessive": "#4682B4",
                "superessive": "#5F9EA0",
                "adessive": "#00CED1",
                "sublative": "#6A5ACD",
                "delative": "#8A2BE2",
                "elative": "#483D8B",
                "illative": "#191970",
                "allative": "#1E90FF",
                "ablative": "#00BFFF",
                "terminative": "#87CEFA",
                "essive_formal": "#B0C4DE",
                "distributive": "#778899",
                # Possessive
                "possessive_suffix": "#FF69B4",
                "interjection": "#FFD700",
                "other": "#AAAAAA"
            }
        }
        return schemes.get(complexity, schemes["intermediate"])

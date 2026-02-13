# languages/french/domain/fr_config.py
"""
French Configuration - Domain Component

FRENCH CONFIGURATION PATTERN:
This file demonstrates how to structure French-specific configuration.
It serves as the single source of truth for all French-specific settings.

RESPONSIBILITIES:
1. Load external configuration files (YAML/JSON)
2. Define grammatical roles and mappings for French
3. Provide color schemes for different complexity levels
4. Store French-specific patterns and rules
5. Handle configuration loading errors gracefully

CONFIGURATION FILES LOADED:
- fr_grammatical_roles.yaml: Role definitions and mappings
- fr_common_determiners.yaml: Determiner lists
- fr_verb_conjugations.yaml: Verb conjugation patterns
- fr_preposition_patterns.yaml: Preposition usage rules
- fr_word_meanings.json: Pre-defined word meanings
- fr_patterns.yaml: Regex patterns and validation rules

USAGE FOR FRENCH:
1. Create French-specific YAML/JSON config files
2. Copy this structure, changing only file names and content
3. Implement French-appropriate grammatical roles
4. Define complexity-appropriate color schemes
5. Add French-specific patterns and markers

INTEGRATION:
- Used by all domain components (prompt_builder, validator, fallbacks)
- Provides consistent configuration across the analyzer
- Supports multiple complexity levels with appropriate distinctions
"""

import json
import logging
import yaml
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ComplexityLevel(Enum):
    """Standard complexity levels for grammar analysis."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class GrammaticalRole(Enum):
    """French grammatical roles - comprehensive coverage."""
    NOUN = "noun"
    VERB = "verb"
    PRONOUN = "pronoun"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    DETERMINER = "determiner"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    # French-specific roles
    AUXILIARY_VERB = "auxiliary_verb"
    MODAL_VERB = "modal_verb"
    REFLEXIVE_PRONOUN = "reflexive_pronoun"
    POSSESSIVE_PRONOUN = "possessive_pronoun"
    DEMONSTRATIVE_PRONOUN = "demonstrative_pronoun"
    RELATIVE_PRONOUN = "relative_pronoun"
    INDEFINITE_PRONOUN = "indefinite_pronoun"
    PERSONAL_PRONOUN = "personal_pronoun"
    # Add more as needed

@dataclass
class FrConfig:
    """
    Configuration for French analyzer, loaded from external files.

    FRENCH CONFIGURATION:
    - External files: Keep configuration separate from code
    - Error handling: Graceful fallbacks for missing files
    - Type safety: Use dataclasses and enums for validation
    - Modularity: Separate concerns (roles, colors, patterns)

    CONFIGURATION PHILOSOPHY:
    - Complexity progression: Beginner → Intermediate → Advanced
    - Inclusive design: Support different learning levels
    - Maintainability: Easy to modify without code changes
    """
    grammatical_roles: Dict[str, str]
    common_determiners: List[str]
    verb_conjugations: Dict[str, str]
    preposition_patterns: Dict[str, str]
    pronoun_patterns: Dict[str, str]
    word_meanings: Dict[str, str]
    prompt_templates: Dict[str, str]
    patterns: Dict[str, Any]  # For regex patterns, etc.

    def __init__(self):
        """
        Initialize configuration by loading external files.

        CONFIGURATION LOADING STRATEGY:
        1. Define file paths relative to this module
        2. Load YAML files for structured data (roles, patterns)
        3. Load JSON files for key-value data (meanings)
        4. Provide empty dicts as fallbacks for missing files
        5. Log errors but don't crash - maintain functionality
        """
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = self._load_yaml(config_dir / "fr_grammatical_roles.yaml")
        self.common_determiners = self._load_yaml(config_dir / "fr_common_determiners.yaml")
        self.verb_conjugations = self._load_yaml(config_dir / "fr_verb_conjugations.yaml")
        self.preposition_patterns = self._load_yaml(config_dir / "fr_preposition_patterns.yaml")
        self.pronoun_patterns = self._load_yaml(config_dir / "fr_pronoun_patterns.yaml")
        self.word_meanings = self._load_json(config_dir / "fr_word_meanings.json")

        # French-specific prompt templates
        self.prompt_templates = {
            "single": """
Analyze this French sentence and provide DETAILED grammatical breakdown.

Sentence: {{sentence}}
Target word: {{target_word}}
Complexity level: {{complexity}}

For EACH word in the sentence, provide:
- Its specific grammatical function and role
- Gender agreement (masculine/feminine) for nouns/adjectives
- Verb conjugation details (person, number, tense, mood)
- Agreement relationships with other words
- French-specific features (elision, liaison, preposition choice)

Return a JSON object with exactly this structure:
{
  "sentence": "{{sentence}}",
  "words": [
    {
      "word": "word",
      "grammatical_role": "noun|verb|adjective|pronoun|determiner|preposition|...",
      "gender": "masculine|feminine|neutral"  // for nouns/adjectives
      "number": "singular|plural"  // for nouns/adjectives/verbs
      "person": "1|2|3"  // for verbs/pronouns
      "tense": "present|past|future|..."  // for verbs
      "mood": "indicative|subjunctive|conditional|..."  // for verbs
      "individual_meaning": "Detailed explanation of this element's function, agreement relationships, and contribution to sentence meaning"
    }
  ],
  "explanations": {
    "overall_structure": "Detailed explanation of sentence structure and word relationships",
    "agreement_patterns": "Gender/number agreement chains and their linguistic significance",
    "key_features": "Notable French grammatical features like verb conjugations, preposition usage, adjective placement"
  }
}

CRITICAL: Always explain gender agreement, verb conjugations, and French-specific grammatical patterns.
""",
            "batch": """
Analyze these French sentences and provide grammatical breakdowns for each.

Sentences: {{sentences}}
Target word: {{target_word}}
Complexity level: {{complexity}}

For EACH sentence, provide word-by-word analysis with gender/number/person details for verbs/adjectives.
Focus on French-specific features like verb conjugations and agreement patterns.

Return a JSON object with exactly this structure:
{
  "batch_results": [
    {
      "sentence": "first sentence",
      "words": [
        {
          "word": "word",
          "grammatical_role": "noun|verb|adjective|pronoun|determiner|preposition|...",
          "gender": "masculine|feminine|neutral",
          "number": "singular|plural",
          "person": "1|2|3",
          "tense": "present|past|future|...",
          "mood": "indicative|subjunctive|conditional|...",
          "individual_meaning": "Brief explanation of function and agreement"
        }
      ],
      "explanations": {
        "overall_structure": "Brief structural analysis",
        "agreement_patterns": "Key agreement chains",
        "key_features": "Main French grammatical features"
      }
    }
  ]
}

CRITICAL: Keep explanations under 75 characters. Focus on essential French grammar.
"""
        }
        self.patterns = self._load_yaml(config_dir / "fr_patterns.yaml")

        # Voice configuration for Google Cloud Text-to-Speech
        self.voice_config = {
            'language_code': 'fr-FR',  # French (France)
            'name': 'fr-FR-Neural2-D',  # High quality female voice
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
        """
        Return color scheme for French grammatical elements based on complexity.

        FRENCH COLOR CODING:
        - Progressive disclosure: More roles at higher complexity levels
        - Consistency: Same colors for same roles across levels
        - Accessibility: High contrast, colorblind-friendly colors
        - Language-appropriate: Colors that reflect French grammatical concepts

        COMPLEXITY PROGRESSION:
        - BEGINNER: Core roles only (noun, verb, adjective, determiners)
        - INTERMEDIATE: More distinctions (pronoun types, verb auxiliaries, prepositions)
        - ADVANCED: Full granularity (all pronoun subtypes, verb moods, complex determiners)

        COLOR PHILOSOPHY:
        - Warm colors for content words (nouns, verbs)
        - Cool colors for function words (determiners, prepositions)
        - Distinct colors for agreement elements (pronouns, adjectives)
        - Consistent target word highlighting
        """
        schemes = {
            "beginner": {
                "noun": "#FFAA00",          # Orange - content words
                "adjective": "#FF44FF",     # Magenta - modifiers with agreement
                "verb": "#44FF44",          # Green - actions with conjugation
                "adverb": "#44FFFF",        # Cyan - manner
                "pronoun": "#FF4444",       # Red - replacements with agreement
                "determiner": "#AA44FF",    # Purple - articles/determiners
                "preposition": "#4444FF",   # Blue - relationships
                "conjunction": "#888888",   # Gray - connectors
                "interjection": "#FFD700",  # Gold - exclamations
                "other": "#AAAAAA"          # Light gray - miscellaneous
            },
            "intermediate": {
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#44FF44",          # Green - main verbs
                "auxiliary_verb": "#228B22", # Forest green - avoir/être
                "modal_verb": "#32CD32",    # Lime green - pouvoir, devoir, vouloir
                "adverb": "#44FFFF",
                "pronoun": "#FF4444",       # Red - general pronouns
                "personal_pronoun": "#FF4444",
                "reflexive_pronoun": "#DC143C", # Crimson - me, te, se, nous, vous, se
                "possessive_pronoun": "#B22222", # Firebrick - le mien, la mienne, etc.
                "demonstrative_pronoun": "#FF6347", # Tomato - celui, celle, ceux, celles
                "determiner": "#AA44FF",
                "preposition": "#4444FF",
                "conjunction": "#888888",
                "other": "#AAAAAA"
            },
            "advanced": {
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#44FF44",
                "auxiliary_verb": "#228B22", # Forest green - avoir/être
                "modal_verb": "#32CD32",    # Lime green - pouvoir, devoir, vouloir, savoir
                "adverb": "#44FFFF",
                "pronoun": "#FF4444",       # Red - general pronouns
                "personal_pronoun": "#FF4444",
                "reflexive_pronoun": "#DC143C", # Crimson - me, te, se, nous, vous, se
                "possessive_pronoun": "#B22222", # Firebrick - le mien, la mienne, etc.
                "demonstrative_pronoun": "#FF6347", # Tomato - celui, celle, ceux, celles
                "relative_pronoun": "#FF4500", # Orange red - qui, que, dont, où
                "indefinite_pronoun": "#CD5C5C", # Indian red - quelqu'un, quelque chose, etc.
                "determiner": "#AA44FF",
                "preposition": "#4444FF",
                "conjunction": "#888888",
                "interjection": "#FFD700",
                "other": "#AAAAAA"
            }
        }
        return schemes.get(complexity, schemes["intermediate"])
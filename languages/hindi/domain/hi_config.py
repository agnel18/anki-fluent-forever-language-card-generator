# languages/hindi/domain/hi_config.py
"""
Hindi Configuration - Domain Component

GOLD STANDARD CONFIGURATION PATTERN:
This file demonstrates how to structure language-specific configuration.
It serves as the single source of truth for all Hindi-specific settings.

RESPONSIBILITIES:
1. Load external configuration files (YAML/JSON)
2. Define grammatical roles and mappings
3. Provide color schemes for different complexity levels
4. Store language-specific patterns and rules
5. Handle configuration loading errors gracefully

CONFIGURATION FILES LOADED:
- hi_grammatical_roles.yaml: Role definitions and mappings
- hi_common_postpositions.yaml: Postposition lists
- hi_gender_markers.yaml: Gender agreement patterns
- hi_case_markers.yaml: Case marking rules
- hi_honorific_markers.yaml: Honorific system patterns
- hi_word_meanings.json: Pre-defined word meanings
- hi_patterns.yaml: Regex patterns and validation rules

USAGE FOR NEW LANGUAGES:
1. Create language-specific YAML/JSON config files
2. Copy this structure, changing only file names and content
3. Implement language-appropriate grammatical roles
4. Define complexity-appropriate color schemes
5. Add language-specific patterns and markers

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
    """Hindi grammatical roles - comprehensive coverage."""
    NOUN = "noun"
    VERB = "verb"
    PRONOUN = "pronoun"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    POSTPOSITION = "postposition"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    PARTICLE = "particle"
    # Add more as needed

@dataclass
class HiConfig:
    """
    Configuration for Hindi analyzer, loaded from external files.

    GOLD STANDARD CONFIGURATION:
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
    common_postpositions: List[str]
    gender_markers: Dict[str, str]
    case_markers: Dict[str, str]
    honorific_markers: Dict[str, str]
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
        self.grammatical_roles = self._load_yaml(config_dir / "hi_grammatical_roles.yaml")
        self.common_postpositions = self._load_yaml(config_dir / "hi_common_postpositions.yaml")
        self.gender_markers = self._load_yaml(config_dir / "hi_gender_markers.yaml")
        self.case_markers = self._load_yaml(config_dir / "hi_case_markers.yaml")
        self.honorific_markers = self._load_yaml(config_dir / "hi_honorific_markers.yaml")
        self.word_meanings = self._load_json(config_dir / "hi_word_meanings.json")
        # For simplicity, define templates inline or load from file
        self.prompt_templates = {
            "single": """
Analyze this Hindi sentence and provide a detailed grammatical breakdown.

Sentence: {{sentence}}
Target word: {{target_word}}
Complexity level: {{complexity}}

Return a JSON object with exactly this structure:
{
  "sentence": "{{sentence}}",
  "words": [
    {
      "word": "first_word",
      "grammatical_role": "noun|verb|pronoun|adjective|adverb|postposition|conjunction|interjection|particle|other",
      "individual_meaning": "brief explanation of this word's role in the sentence"
    },
    {
      "word": "second_word", 
      "grammatical_role": "noun|verb|pronoun|adjective|adverb|postposition|conjunction|interjection|particle|other",
      "individual_meaning": "brief explanation of this word's role in the sentence"
    }
  ],
  "explanations": {
    "overall_structure": "brief explanation of sentence structure",
    "key_features": "any notable grammatical features"
  }
}

Important: 
- Break down the sentence into individual words
- Assign appropriate grammatical roles from the list above
- Provide meaningful explanations for each word
- Use only valid JSON format
""",
            "batch": """
Analyze these Hindi sentences and provide detailed grammatical breakdowns for each.

Sentences: {{sentences}}
Target word: {{target_word}}
Complexity level: {{complexity}}

Return a JSON object with exactly this structure:
{
  "batch_results": [
    {
      "sentence": "first sentence",
      "words": [
        {
          "word": "first_word",
          "grammatical_role": "noun|verb|pronoun|adjective|adverb|postposition|conjunction|interjection|particle|other",
          "individual_meaning": "brief explanation of this word's role"
        }
      ],
      "explanations": {
        "overall_structure": "brief explanation",
        "key_features": "notable features"
      }
    },
    {
      "sentence": "second sentence",
      "words": [...],
      "explanations": {...}
    }
  ]
}

Important:
- Analyze each sentence separately
- Break down each sentence into individual words
- Assign appropriate grammatical roles
- Provide meaningful explanations
- Use only valid JSON format
"""
        }
        self.patterns = self._load_yaml(config_dir / "hi_patterns.yaml")
        self.postpositions = self.common_postpositions  # Alias for compatibility

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
        Return color scheme for Hindi grammatical elements based on complexity.

        GOLD STANDARD COLOR CODING:
        - Progressive disclosure: More roles at higher complexity levels
        - Consistency: Same colors for same roles across levels
        - Accessibility: High contrast, colorblind-friendly colors
        - Language-appropriate: Colors that reflect Hindi grammatical concepts

        COMPLEXITY PROGRESSION:
        - BEGINNER: Core roles only (noun, verb, adjective, etc.)
        - INTERMEDIATE: More distinctions (pronoun types, auxiliary verbs)
        - ADVANCED: Full granularity (all particle types, honorifics)

        COLOR PHILOSOPHY:
        - Warm colors for content words (nouns, verbs)
        - Cool colors for function words (postpositions, particles)
        - Distinct colors for different pronoun types
        - Consistent target word highlighting
        """
        schemes = {
            "beginner": {
                "noun": "#FFAA00",          # Orange - content words
                "adjective": "#FF44FF",     # Magenta - modifiers
                "verb": "#44FF44",          # Green - actions
                "adverb": "#44FFFF",        # Cyan - manner
                "pronoun": "#FF4444",       # Red - replacements
                "postposition": "#4444FF",  # Blue - relationships
                "conjunction": "#888888",   # Gray - connectors
                "interjection": "#FFD700",  # Gold - exclamations
                "particle": "#AA44FF",      # Purple - grammatical particles
                "other": "#AAAAAA"          # Light gray - miscellaneous
            },
            "intermediate": {
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#4ECDC4",          # Teal - main verbs
                "adverb": "#44FFFF",
                "pronoun": "#FFEAA7",       # Light orange - general pronouns
                "personal_pronoun": "#FFEAA7",
                "demonstrative_pronoun": "#FFEAA7",
                "postposition": "#4444FF",
                "auxiliary_verb": "#4ECDC4", # Same as verb - related function
                "conjunction": "#888888",
              "interjection": "#FFD700",
                "particle": "#AA44FF",
                "other": "#AAAAAA"
            },
            "advanced": {
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#44FF44",
                "adverb": "#44FFFF",
                "pronoun": "#FF4444",       # Dark red - general pronouns
                "personal_pronoun": "#FF4444",
                "demonstrative_pronoun": "#FF4444",
                "interrogative_pronoun": "#FF4444",
                "relative_pronoun": "#FF4444",
                "postposition": "#4444FF",
                "auxiliary_verb": "#44FF44",
                "conjunction": "#888888",
                "interjection": "#FFD700",
                "particle": "#AA44FF",
                "onomatopoeia": "#FFD700",   # Same as interjection
                "ideophone": "#FFD700",     # Same as interjection
                "echo_word": "#FFD700",     # Same as interjection
                "other": "#AAAAAA"
            }
        }
        return schemes.get(complexity, schemes["intermediate"])
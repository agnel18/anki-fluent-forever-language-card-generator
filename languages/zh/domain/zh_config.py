# languages/zh/domain/zh_config.py
"""
Chinese Simplified Configuration - Domain Component

CHINESE CONFIGURATION PATTERN:
This file demonstrates how to structure Chinese-specific configuration.
It serves as the single source of truth for all Chinese-specific settings.

RESPONSIBILITIES:
1. Load external configuration files (YAML/JSON)
2. Define grammatical roles and mappings for Chinese
3. Provide color schemes for different complexity levels
4. Store Chinese-specific patterns and rules
5. Handle configuration loading errors gracefully

CONFIGURATION FILES LOADED:
- zh_grammatical_roles.yaml: Role definitions and mappings
- zh_common_classifiers.yaml: Classifier lists
- zh_aspect_markers.yaml: Aspect particle patterns
- zh_structural_particles.yaml: Particle system rules
- zh_word_meanings.json: Pre-defined word meanings
- zh_patterns.yaml: Regex patterns and validation rules

USAGE FOR CHINESE:
1. Create Chinese-specific YAML/JSON config files
2. Copy this structure, changing only file names and content
3. Implement Chinese-appropriate grammatical roles
4. Define complexity-appropriate color schemes
5. Add Chinese-specific patterns and markers

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
    """Chinese grammatical roles - comprehensive coverage."""
    NOUN = "noun"
    VERB = "verb"
    PRONOUN = "pronoun"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    NUMERAL = "numeral"
    CLASSIFIER = "classifier"
    PARTICLE = "particle"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    ASPECT_MARKER = "aspect_marker"
    MODAL_PARTICLE = "modal_particle"
    STRUCTURAL_PARTICLE = "structural_particle"
    # Add more as needed

@dataclass
class ZhConfig:
    """
    Configuration for Chinese Simplified analyzer, loaded from external files.

    CHINESE CONFIGURATION:
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
    common_classifiers: List[str]
    aspect_markers: Dict[str, str]
    structural_particles: Dict[str, str]
    modal_particles: Dict[str, str]
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
        self.grammatical_roles = self._load_yaml(config_dir / "zh_grammatical_roles.yaml")
        self.common_classifiers = self._load_yaml(config_dir / "zh_common_classifiers.yaml")
        self.aspect_markers = self._load_yaml(config_dir / "zh_aspect_markers.yaml")
        self.structural_particles = self._load_yaml(config_dir / "zh_structural_particles.yaml")
        self.modal_particles = self._load_yaml(config_dir / "zh_modal_particles.yaml")
        self.word_meanings = self._load_json(config_dir / "zh_word_meanings.json")
        # For simplicity, define templates inline or load from file
        self.prompt_templates = {
            "single": """
Analyze this Chinese sentence and provide DETAILED grammatical breakdown.

Sentence: {{sentence}}
Target word: {{target_word}}
Complexity level: {{complexity}}

For EACH word/character in the sentence, provide:
- Its specific grammatical function and role
- How it contributes to the sentence meaning
- Relationships with adjacent words
- Chinese-specific features (aspect, classifiers, particles)

Return a JSON object with exactly this structure:
{
  "sentence": "{{sentence}}",
  "words": [
    {
      "word": "character/word",
      "grammatical_role": "noun|verb|aspect_marker|classifier|particle|...",
      "individual_meaning": "Detailed explanation of this element's function, relationships, and contribution to sentence meaning"
    }
  ],
  "explanations": {
    "overall_structure": "Detailed explanation of sentence structure and word relationships",
    "key_features": "Notable Chinese grammatical features like aspect usage, classifier selection, particle functions"
  }
}

CRITICAL: Provide COMPREHENSIVE explanations for EVERY element, explaining relationships and functions in detail.
""",
            "batch": """
Analyze these Chinese sentences and provide detailed grammatical breakdowns for each.

Sentences: {{sentences}}
Target word: {{target_word}}
Complexity level: {{complexity}}

For EACH sentence, provide comprehensive analysis including:
- Word-by-word grammatical breakdown
- Chinese-specific features (aspect markers, classifiers, particles)
- Relationships between sentence elements
- Overall sentence structure and function

Return a JSON object with exactly this structure:
{
  "batch_results": [
    {
      "sentence": "first sentence",
      "words": [
        {
          "word": "character/word",
          "grammatical_role": "noun|verb|aspect_marker|classifier|particle|...",
          "individual_meaning": "Detailed explanation of function and relationships"
        }
      ],
      "explanations": {
        "overall_structure": "Detailed structural analysis",
        "key_features": "Chinese grammatical features and their functions"
      }
    }
  ]
}

CRITICAL: Provide COMPREHENSIVE explanations for ALL elements in EACH sentence.
"""
        }
        self.patterns = self._load_yaml(config_dir / "zh_patterns.yaml")
        self.classifiers = self.common_classifiers  # Alias for compatibility

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
        Return color scheme for Chinese Simplified grammatical elements based on complexity.

        CHINESE COLOR CODING:
        - Progressive disclosure: More roles at higher complexity levels
        - Consistency: Same colors for same roles across levels
        - Accessibility: High contrast, colorblind-friendly colors
        - Language-appropriate: Colors that reflect Chinese grammatical concepts

        COMPLEXITY PROGRESSION:
        - BEGINNER: Core roles only (noun, verb, adjective, particles)
        - INTERMEDIATE: More distinctions (classifiers, aspect markers, pronouns)
        - ADVANCED: Full granularity (all particle types, structural elements)

        COLOR PHILOSOPHY:
        - Warm colors for content words (nouns, verbs)
        - Cool colors for function words (particles, classifiers)
        - Distinct colors for aspect markers and modal particles
        - Consistent target word highlighting
        """
        schemes = {
            "beginner": {
                "noun": "#FFAA00",          # Orange - content words
                "adjective": "#FF44FF",     # Magenta - modifiers
                "verb": "#44FF44",          # Green - actions
                "adverb": "#44FFFF",        # Cyan - manner
                "pronoun": "#FF4444",       # Red - replacements
                "particle": "#AA44FF",      # Purple - grammatical particles
                "aspect_marker": "#9370DB", # Medium purple - aspect particles (了, 着, 过)
                "numeral": "#FFD700",       # Gold - numbers
                "classifier": "#FF8C00",    # Dark orange - measure words
                "preposition": "#4444FF",   # Blue - relationships
                "conjunction": "#888888",   # Gray - connectors
                "interjection": "#FFD700",  # Gold - exclamations
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
                "particle": "#AA44FF",
                "aspect_marker": "#9370DB", # Medium purple - aspect particles
                "modal_particle": "#DA70D6", # Plum - modal particles
                "structural_particle": "#AA44FF", # Purple - structural particles
                "numeral": "#FFD700",
                "classifier": "#FF8C00",
                "preposition": "#4444FF",
                "conjunction": "#888888",
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
                "particle": "#AA44FF",
                "aspect_marker": "#9370DB", # Medium purple - 了, 着, 过
                "modal_particle": "#DA70D6", # Plum - 吗, 呢, 吧, 啊
                "structural_particle": "#AA44FF", # Purple - 的, 地, 得
                "numeral": "#FFD700",
                "classifier": "#FF8C00",
                "preposition": "#4444FF",
                "conjunction": "#888888",
                "interjection": "#FFD700",
                "other": "#AAAAAA"
            }
        }
        return schemes.get(complexity, schemes["intermediate"])
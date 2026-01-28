# languages/chinese_traditional/domain/zh_tw_config.py
"""
Chinese Traditional Configuration - Domain Component

Following Chinese Simplified Clean Architecture gold standard:
- External configuration files (YAML/JSON)
- Integrated domain component (not separate infrastructure)
- Type safety with dataclasses and enums
- Graceful error handling for missing files

RESPONSIBILITIES:
1. Load external configuration files (YAML/JSON)
2. Define grammatical roles and mappings for Chinese Traditional
3. Provide color schemes for different complexity levels
4. Store Chinese-specific patterns and rules
5. Handle configuration loading errors gracefully

CONFIGURATION FILES LOADED:
- zh_tw_grammatical_roles.yaml: Role definitions and mappings
- zh_tw_common_classifiers.yaml: Classifier lists
- zh_tw_aspect_markers.yaml: Aspect particle patterns
- zh_tw_structural_particles.yaml: Particle system rules
- zh_tw_word_meanings.json: Pre-defined word meanings
- zh_tw_patterns.yaml: Regex patterns and validation rules

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

logger = logging.getLogger(__name__)

class ComplexityLevel(Enum):
    """Standard complexity levels for grammar analysis."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class ZhTwConfig:
    """
    Configuration for Chinese Traditional analyzer, loaded from external files.

    Following Chinese Simplified Clean Architecture:
    - External files: Keep configuration separate from code
    - Error handling: Graceful fallbacks for missing files
    - Type safety: Use dataclasses for validation
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
    patterns: Dict[str, Any]

    def __init__(self):
        """
        Initialize configuration by loading external files.

        CONFIGURATION LOADING STRATEGY (following Chinese Simplified):
        1. Define file paths relative to this module
        2. Load YAML files for structured data (roles, patterns)
        3. Load JSON files for key-value data (meanings)
        4. Provide empty dicts as fallbacks for missing files
        5. Log errors but don't crash - maintain functionality
        """
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"

        # Load external configuration files
        self.grammatical_roles = self._load_yaml(config_dir / "zh_tw_grammatical_roles.yaml")
        self.common_classifiers = self._load_yaml(config_dir / "zh_tw_common_classifiers.yaml")
        self.aspect_markers = self._load_yaml(config_dir / "zh_tw_aspect_markers.yaml")
        self.structural_particles = self._load_yaml(config_dir / "zh_tw_structural_particles.yaml")
        self.modal_particles = self._load_yaml(config_dir / "zh_tw_modal_particles.yaml")
        self.word_meanings = self._load_json(config_dir / "zh_tw_word_meanings.json")

        # Define prompt templates (following Chinese Simplified pattern)
        self.prompt_templates = {
            "single": """
Analyze this Chinese Traditional sentence and provide DETAILED grammatical breakdown.

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
      "grammatical_role": "noun|verb|aspect_particle|measure_word|particle|...",
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
Analyze these Chinese Traditional sentences and provide detailed grammatical breakdowns for each.

Sentences: {{sentences}}
Target word: {{target_word}}
Complexity level: {{complexity}}

For EACH sentence, provide comprehensive analysis including:
- Word-by-word grammatical breakdown
- Chinese-specific features (aspect particles, measure words, modal particles)
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
          "grammatical_role": "noun|verb|aspect_particle|measure_word|particle|...",
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

        self.patterns = self._load_yaml(config_dir / "zh_tw_patterns.yaml")
        self.classifiers = self.common_classifiers  # Alias for compatibility

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file with error handling."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load YAML file {path}: {e}")
            return {}

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON file with error handling."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON file {path}: {e}")
            return {}

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """
        Get color scheme for grammatical roles based on complexity.

        Following Chinese Traditional linguistic categories:
        - Content words (實詞): nouns, verbs, adjectives, etc.
        - Function words (虛詞): particles, prepositions, conjunctions, etc.
        """
        base_scheme = {
            # Content Words (實詞 / Shící) - Independent Meaning
            "noun": "#FFAA00",                    # Orange - People/places/things/concepts
            "verb": "#44FF44",                    # Green - Actions/states/changes
            "adjective": "#FF44FF",               # Magenta - Qualities/descriptions
            "numeral": "#FFFF44",                 # Yellow - Numbers/quantities
            "measure_word": "#FFD700",            # Gold - Classifiers (個, 本, 杯)
            "pronoun": "#FF4444",                 # Red - Replacements for nouns
            "time_word": "#FFA500",               # Orange-red - Time expressions
            "locative_word": "#FF8C00",           # Dark orange - Location/direction

            # Function Words (虛詞 / Xūcí) - Structural/Grammatical
            "aspect_particle": "#8A2BE2",         # Purple - Aspect markers (了, 著, 過)
            "modal_particle": "#DA70D6",          # Plum - Tone/mood particles (嗎, 呢, 吧)
            "structural_particle": "#9013FE",     # Violet - Structural particles (的, 地, 得)
            "preposition": "#4444FF",             # Blue - Prepositions/coverbs
            "conjunction": "#888888",             # Gray - Connectors
            "adverb": "#44FFFF",                  # Cyan - Modifies verbs/adjectives
            "interjection": "#FFD700",            # Gold - Emotions/exclamations
            "onomatopoeia": "#FFD700"             # Gold - Sound imitation
        }

        # Adjust colors based on complexity
        if complexity == "beginner":
            # Simpler, more distinct colors for beginners
            pass  # Use base scheme
        elif complexity == "advanced":
            # More nuanced colors for advanced learners
            pass  # Could add more distinctions

        return base_scheme
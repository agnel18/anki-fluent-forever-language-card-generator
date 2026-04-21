# languages/chinese_simplified/domain/zh_config.py
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
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from .zh_types import AnalysisRequest, AnalysisResult, BatchAnalysisResult, ParsedWord, ParsedSentence, ParseResult, ValidationResult

logger = logging.getLogger(__name__)

@dataclass
class ZhConfig:
    """
    Configuration for Chinese Simplified analyzer, loaded from external files.
    Uses dataclasses for type safety and maintainability.
    """
    grammatical_roles: Dict[str, str] = field(default_factory=dict)
    common_classifiers: List[str] = field(default_factory=list)
    aspect_markers: Dict[str, str] = field(default_factory=dict)
    structural_particles: Dict[str, str] = field(default_factory=dict)
    modal_particles: Dict[str, str] = field(default_factory=dict)
    word_meanings: Dict[str, str] = field(default_factory=dict)
    prompt_templates: Dict[str, str] = field(default_factory=dict)
    patterns: Dict[str, Any] = field(default_factory=dict)
    classifiers: List[str] = field(default_factory=list)

    def __post_init__(self):
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = self._load_yaml(config_dir / "zh_grammatical_roles.yaml")
        self.common_classifiers = self._load_yaml(config_dir / "zh_common_classifiers.yaml")
        self.aspect_markers = self._load_yaml(config_dir / "zh_aspect_markers.yaml")
        self.structural_particles = self._load_yaml(config_dir / "zh_structural_particles.yaml")
        self.modal_particles = self._load_yaml(config_dir / "zh_modal_particles.yaml")
        self.word_meanings = self._load_json(config_dir / "zh_word_meanings.json")
        self.prompt_templates = {
            "single": """
Analyze this Chinese sentence and provide a detailed grammatical breakdown.

Sentence: {{sentence}}
Target word: {{target_word}}
Complexity level: {{complexity}}

**STRICT OUTPUT RULES (must follow exactly):**
- For EVERY word/character you MUST return BOTH:
  - "grammatical_role": exactly one of these lowercase values: noun, verb, adjective, adverb, pronoun, particle, classifier, numeral, aspect_marker, structural_particle, modal_particle, preposition, conjunction, interjection, determiner, other
  - "individual_meaning": rich 1-2 sentence learner-friendly explanation of its function in THIS sentence
- Do NOT capitalize roles. Do NOT use phrases like "Structural particle" or "Personal pronoun".
- Target word gets the richest explanation, but ALL words must have meaningful explanations.

Return valid JSON with this EXACT structure:
{
  "sentence": "{{sentence}}",
  "words": [
    {
      "word": "character/word",
      "grammatical_role": "noun|verb|adjective|adverb|pronoun|particle|classifier|numeral|aspect_marker|structural_particle|modal_particle|...",
      "individual_meaning": "Rich, educational explanation of this word's function in the sentence"
    }
  ],
  "explanations": {
    "overall_structure": "Detailed explanation of sentence structure",
    "key_features": "Notable Chinese grammatical features"
  }
}

CRITICAL: Every word object MUST contain grammatical_role (lowercase) and individual_meaning.
""",
            "batch": """
Analyze these Chinese sentences and provide detailed grammatical breakdowns for each.

Sentences: {{sentences}}
Target word: {{target_word}}
Complexity level: {{complexity}}

**STRICT OUTPUT RULES (must follow exactly):**
Same rules as single prompt above. Every word in every sentence must have lowercase "grammatical_role" + rich "individual_meaning".

Return valid JSON with this EXACT structure:
{
  "batch_results": [
    {
      "sentence": "first sentence",
      "words": [ ... ],
      "explanations": { ... }
    }
  ]
}

CRITICAL: Every word object MUST contain grammatical_role (lowercase) and individual_meaning.
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
                "target_word": "#E63939",   # bright red (or any high-contrast color you like)
                "noun": "#FFAA00",          # Orange - content words
                "adjective": "#FF44FF",     # Magenta - modifiers
                "verb": "#44FF44",          # Green - actions
                "adverb": "#44FFFF",        # Cyan - manner
                "pronoun": "#FF4444",       # Red - replacements
                "particle": "#AA44FF",      # Purple - grammatical particles
                "aspect_marker": "#8A2BE2", # Purple - aspect particles (äº†, ç€, è¿‡)
                "numeral": "#FFD700",       # Gold - numbers
                "classifier": "#FF8C00",    # Dark orange - measure words
                "preposition": "#4444FF",   # Blue - relationships
                "conjunction": "#888888",   # Gray - connectors
                "interjection": "#FFD700",  # Gold - exclamations
                "other": "#AAAAAA"          # Light gray - miscellaneous
            },
            "intermediate": {
                "target_word": "#E63939",   # bright red (or any high-contrast color you like)
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#44FF44",          # Bright green - main verbs
                "adverb": "#44FFFF",
                "pronoun": "#FF4444",       # Bright red - general pronouns
                "personal_pronoun": "#FF4444",
                "demonstrative_pronoun": "#FF4444",
                "particle": "#AA44FF",
                "aspect_marker": "#8A2BE2", # Purple - aspect particles
                "modal_particle": "#DA70D6", # Plum - modal particles
                "structural_particle": "#9013FE", # Violet - structural particles
                "numeral": "#FFD700",
                "classifier": "#FF8C00",
                "preposition": "#4444FF",
                "conjunction": "#888888",
                "other": "#AAAAAA"
            },
            "advanced": {
                "target_word": "#E63939",   # bright red (or any high-contrast color you like)
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#44FF44",
                "adverb": "#44FFFF",
                "pronoun": "#FF4444",       # Bright red - general pronouns
                "personal_pronoun": "#FF4444",
                "demonstrative_pronoun": "#FF4444",
                "interrogative_pronoun": "#FF4444",
                "particle": "#AA44FF",
                "aspect_marker": "#8A2BE2", # Purple - äº†, ç€, è¿‡
                "modal_particle": "#DA70D6", # Plum - å—, å‘¢, å§, å•Š
                "structural_particle": "#9013FE", # Violet - çš„, åœ°, å¾—
                "numeral": "#FFD700",
                "classifier": "#FF8C00",
                "preposition": "#4444FF",
                "conjunction": "#888888",
                "interjection": "#FFD700",
                "other": "#AAAAAA"
            }
        }
        return schemes.get(complexity, schemes["intermediate"])
    
    def _get_grammatical_roles_list(self, complexity: str) -> str:
        """
        Gold-standard: Return formatted bullet list of allowed roles (soft guidance).
        Beginner = simple list, Advanced = full Chinese-specific roles.
        """
        if complexity == "beginner":
            role_list = [
                "noun", "verb", "adjective", "adverb", "pronoun",
                "particle", "classifier", "numeral"
            ]
        elif complexity == "intermediate":
            role_list = [
                "noun", "verb", "adjective", "adverb", "pronoun",
                "particle", "classifier", "numeral", "aspect_marker",
                "structural_particle", "modal_particle"
            ]
        else:  # advanced
            role_list = [
                "noun", "verb", "adjective", "adverb", "pronoun",
                "particle", "classifier", "numeral", "aspect_marker",
                "structural_particle", "modal_particle", "determiner",
                "preposition", "conjunction", "interjection"
            ]

        formatted_list = '\n'.join([f'- {role}' for role in role_list])
        return formatted_list    


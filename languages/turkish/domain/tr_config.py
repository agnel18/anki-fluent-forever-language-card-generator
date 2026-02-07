# languages/turkish/domain/tr_config.py
"""
Turkish Configuration - Domain Component

TURKISH CONFIGURATION PATTERN:
This file demonstrates how to structure Turkish-specific configuration.
It serves as the single source of truth for all Turkish-specific settings.

RESPONSIBILITIES:
1. Load external configuration files (YAML/JSON)
2. Define grammatical roles and mappings for Turkish
3. Provide color schemes for different complexity levels
4. Store Turkish-specific patterns and rules
5. Handle configuration loading errors gracefully

CONFIGURATION FILES LOADED:
- tr_grammatical_roles.yaml: Role definitions and mappings
- tr_case_markers.yaml: Case system markers
- tr_vowel_harmony.yaml: Vowel harmony patterns
- tr_suffixes.yaml: Agglutination suffixes
- tr_word_meanings.json: Pre-defined word meanings
- tr_patterns.yaml: Regex patterns and validation rules

USAGE FOR TURKISH:
1. Create Turkish-specific YAML/JSON config files
2. Copy this structure, changing only file names and content
3. Implement Turkish-appropriate grammatical roles
4. Define complexity-appropriate color schemes
5. Add Turkish-specific patterns and markers

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
    """Turkish grammatical roles - comprehensive coverage."""
    NOUN = "noun"
    VERB = "verb"
    PRONOUN = "pronoun"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    NUMERAL = "numeral"
    POSTPOSITION = "postposition"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    CASE_MARKER = "case_marker"
    POSSESSIVE_SUFFIX = "possessive_suffix"
    TENSE_MARKER = "tense_marker"
    QUESTION_PARTICLE = "question_particle"
    NEGATION = "negation"
    PLURAL = "plural"

@dataclass
class TrConfig:
    """
    Configuration for Turkish analyzer, loaded from external files.

    TURKISH CONFIGURATION:
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
    case_markers: Dict[str, Any]
    vowel_harmony: Dict[str, Any]
    suffixes: Dict[str, Any]
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
        # Set language name for templates
        self.language_name = "Turkish"
        self.complexity_levels = [
            ComplexityLevel.BEGINNER.value,
            ComplexityLevel.INTERMEDIATE.value,
            ComplexityLevel.ADVANCED.value
        ]
        
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = self._load_yaml(config_dir / "tr_grammatical_roles.yaml")
        self.case_markers = self._load_yaml(config_dir / "tr_case_markers.yaml")
        self.vowel_harmony = self._load_yaml(config_dir / "tr_vowel_harmony.yaml")
        self.suffixes = self._load_yaml(config_dir / "tr_suffixes.yaml")
        self.word_meanings = self._load_json(config_dir / "tr_word_meanings.json")
        self.patterns = self._load_yaml(config_dir / "tr_patterns.yaml")

        # Load prompt templates from template files
        self.prompt_templates = self._load_prompt_templates()

        # Voice configuration for Google Cloud Text-to-Speech
        self.voice_config = {
            'language_code': 'tr',  # Turkish
            'primary_voice': {
                'name': 'tr-TR-Wavenet-A',
                'ssml_gender': 'FEMALE',
                'natural_sample_rate_hertz': 24000
            },
            'fallback_voices': [
                {'name': 'tr-TR-Wavenet-B', 'ssml_gender': 'MALE'},
                {'name': 'tr-TR-Standard-A', 'ssml_gender': 'FEMALE'}
            ],
            'voice_quality': 'Wavenet',
            'speaking_rate': 1.0,
            'pitch': 0.0
        }

    def get_categories_for_complexity(self, complexity: str) -> List[str]:
        """Return grammatical categories for the requested complexity."""
        return list(self.get_color_scheme(complexity).keys())

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

    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates from template files."""
        import os
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        templates = {}

        # Single sentence template
        single_path = os.path.join(template_dir, 'tr_single_prompt.j2')
        if os.path.exists(single_path):
            try:
                with open(single_path, 'r', encoding='utf-8') as f:
                    templates['single'] = f.read()
            except Exception as e:
                logger.error(f"Failed to load single template: {e}")
                templates['single'] = self._get_default_single_template()
        else:
            templates['single'] = self._get_default_single_template()

        # Batch template
        batch_path = os.path.join(template_dir, 'tr_batch_prompt.j2')
        if os.path.exists(batch_path):
            try:
                with open(batch_path, 'r', encoding='utf-8') as f:
                    templates['batch'] = f.read()
            except Exception as e:
                logger.error(f"Failed to load batch template: {e}")
                templates['batch'] = self._get_default_batch_template()
        else:
            templates['batch'] = self._get_default_batch_template()

        return templates

    def _get_default_single_template(self) -> str:
        """Default single sentence template."""
        return """Analyze this Turkish sentence: {{sentence}}
Target word: {{target_word}}
Complexity level: {{complexity}}

TURKISH GRAMMAR ANALYSIS REQUIREMENTS:

MORPHOLOGICAL ANALYSIS:
- Identify root words in agglutinated forms
- Break down suffixes and their functions
- Note vowel harmony patterns (back/front vowels)
- Identify case markers and their grammatical functions

GRAMMATICAL ROLES:
{{grammatical_roles_list}}

CASE SYSTEM (6 cases in Turkish):
- Nominative: subject case, no marker
- Accusative: direct object, -(y)i marker
- Dative: indirect object/direction, -(y)e marker
- Locative: location, -(d)e marker
- Ablative: source/origin, -(d)en marker
- Genitive: possession, -(n)in marker

OUTPUT FORMAT:
Return JSON with analysis array containing word, grammatical_role, individual_meaning, and color for each word."""

    def _get_default_batch_template(self) -> str:
        """Default batch analysis template."""
        return """Analyze these Turkish sentences:
{{sentences}}

Target word: {{target_word}}
Complexity level: {{complexity}}

TURKISH GRAMMAR ANALYSIS REQUIREMENTS:
- Identify morphological structure for each sentence
- Note vowel harmony patterns
- Identify case markers and their functions
- Use consistent grammatical roles: {{grammatical_roles_list}}

Return JSON with batch_results array containing analysis for each sentence."""

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """
        Return color scheme for Turkish grammatical elements based on complexity.

        TURKISH COLOR CODING:
        - Progressive disclosure: More morphological details at higher complexity levels
        - Consistency: Same colors for same roles across levels
        - Accessibility: High contrast, colorblind-friendly colors
        - Language-appropriate: Colors that reflect Turkish grammatical concepts

        COMPLEXITY PROGRESSION:
        - BEGINNER: Core roles only (noun, verb, adjective, basic particles)
        - INTERMEDIATE: Morphological distinctions (case markers, possessives)
        - ADVANCED: Full granularity (all suffixes, tense/aspect markers)

        COLOR PHILOSOPHY:
        - Warm colors for content words (nouns, verbs)
        - Cool colors for function words (postpositions, conjunctions)
        - Distinct colors for morphological markers
        - Consistent target word highlighting
        """
        schemes = {
            "beginner": {
                "noun": "#FFAA00",          # Orange - content words (isim)
                "adjective": "#FF44FF",     # Magenta - modifiers (sıfat)
                "verb": "#44FF44",          # Green - actions (fiil)
                "adverb": "#44FFFF",        # Cyan - manner (zarf)
                "pronoun": "#FF4444",       # Red - replacements (zamir)
                "postposition": "#AA44FF",  # Purple - grammatical particles (edat)
                "numeral": "#FFD700",       # Gold - numbers (sayı)
                "conjunction": "#888888",   # Gray - connectors (bağlaç)
                "interjection": "#FFD700",  # Gold - exclamations (ünlem)
                "other": "#AAAAAA"          # Light gray - miscellaneous
            },
            "intermediate": {
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#44FF44",
                "adverb": "#44FFFF",
                "pronoun": "#FF4444",
                "postposition": "#AA44FF",
                "case_marker": "#FFD700",   # Gold - case suffixes (hal eki)
                "possessive_suffix": "#FF6347", # Tomato - possessive suffixes (iyelik eki)
                "question_particle": "#FF1493", # Deep Pink - question particle (mı)
                "numeral": "#FFD700",
                "conjunction": "#888888",
                "other": "#AAAAAA"
            },
            "advanced": {
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#44FF44",
                "adverb": "#44FFFF",
                "pronoun": "#FF4444",
                "postposition": "#AA44FF",
                "case_marker": "#FFD700",
                "possessive_suffix": "#FF6347",
                "question_particle": "#FF1493",
                "tense_marker": "#32CD32",   # Lime Green - tense suffixes
                "negation": "#DC143C",       # Crimson - negation (negative verbs)
                "plural": "#8A2BE2",         # Blue Violet - plural markers
                "numeral": "#FFD700",
                "conjunction": "#888888",
                "other": "#AAAAAA"
            }
        }
        return schemes.get(complexity, schemes["intermediate"])

    def get_voice_config(self) -> Dict[str, Any]:
        """Get voice configuration for text-to-speech"""
        return self.voice_config.copy()

    def get_primary_voice(self) -> Dict[str, Any]:
        """Get primary voice for high-quality synthesis"""
        return self.voice_config['primary_voice'].copy()

    def get_fallback_voices(self) -> List[Dict[str, Any]]:
        """Get fallback voices for error recovery"""
        return self.voice_config['fallback_voices'].copy()
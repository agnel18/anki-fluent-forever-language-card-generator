# languages/{language}/domain/{lang_code}_config.py
"""
Language-specific configuration for {Language} analyzer.
GOLD STANDARD CONFIGURATION PATTERN:
This file demonstrates how to structure language-specific configuration.
It serves as the single source of truth for all {Language}-specific settings.

RESPONSIBILITIES:
1. Load external configuration files (YAML/JSON)
2. Define grammatical roles and mappings
3. Provide color schemes for different complexity levels
4. Store language-specific patterns and rules
5. Handle configuration loading errors gracefully

CONFIGURATION FILES LOADED:
- {lang_code}_grammatical_roles.yaml: Role definitions and mappings
- {lang_code}_word_meanings.json: Pre-defined word meanings
- {lang_code}_patterns.yaml: Regex patterns and validation rules
- {lang_code}_*.yaml: Additional language-specific configuration files

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
# type: ignore  # Template file with placeholders - ignore type checking

import json
import logging
import yaml
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ComplexityLevel(Enum):
    """Standard complexity levels for grammar analysis."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class LanguageConfig:
    """Language metadata configuration."""
    code: str
    name: str
    family: str
    script: str
    word_order: str
    has_diacritics: bool

class LanguageConfig:
    """
    Configuration class for {Language} grammatical analysis.

    GOLD STANDARD CONFIGURATION APPROACH:
    - External configuration files for maintainability
    - Complexity-based grammatical roles
    - Language-specific color schemes
    - Comprehensive linguistic feature support
    - Error handling and fallbacks
    """

    def __init__(self):
        """Initialize configuration with external file loading."""
        # Language metadata
        self.language_config = LanguageConfig(
            code="{lang_code}",
            name="{Language}",
            family="{language_family}",  # e.g., "Indo-European", "Sino-Tibetan", "Afroasiatic"
            script="{script_type}",  # e.g., "latin", "cyrillic", "arabic", "devanagari"
            word_order="{word_order}",  # e.g., "SVO", "SOV", "VSO"
            has_diacritics=True  # Placeholder - customize for your language
        )

        # Setup configuration directory path
        self._config_dir = Path(__file__).parent / "infrastructure" / "data"

        # Load external configuration files
        self.grammatical_roles = self._load_yaml(self._config_dir / "{lang_code}_grammatical_roles.yaml")
        self.word_meanings = self._load_json(self._config_dir / "{lang_code}_word_meanings.json")
        self.patterns = self._load_yaml(self._config_dir / "{lang_code}_patterns.yaml")

        # Load additional language-specific files (customize as needed)
        # self.case_markers = self._load_yaml(self._config_dir / "{lang_code}_case_markers.yaml")
        # self.verb_patterns = self._load_yaml(self._config_dir / "{lang_code}_verb_patterns.yaml")
        # self.plural_patterns = self._load_yaml(self._config_dir / "{lang_code}_plural_patterns.yaml")

        # Language-specific attributes (loaded from external files)
        self.genders = []  # e.g., ['masculine', 'feminine', 'neuter'] - customize for your language
        self.numbers = []  # e.g., ['singular', 'plural', 'dual'] - customize for your language
        self.cases = []  # e.g., ['nominative', 'accusative', 'dative'] - customize for your language
        self.tenses = []  # e.g., ['present', 'past', 'future'] - customize for your language
        self.aspects = []  # e.g., ['perfective', 'imperfective'] - customize for your language
        self.moods = []  # e.g., ['indicative', 'subjunctive', 'imperative'] - customize for your language

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML configuration file with error handling."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {path}")
            return {}
        except Exception as e:
            logger.error(f"Error loading YAML file {path}: {e}")
            return {}

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON configuration file with error handling."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {path}")
            return {}
        except Exception as e:
            logger.error(f"Error loading JSON file {path}: {e}")
            return {}

    def get_grammatical_roles(self, complexity: str) -> Dict[str, Any]:
        """Get grammatical roles for given complexity level."""
        roles = self.grammatical_roles.get(complexity, {})
        if not roles:
            # Fallback to intermediate if complexity not found
            roles = self.grammatical_roles.get('intermediate', {})
        return roles

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """
        Get color scheme for grammatical elements based on complexity.

        GOLD STANDARD COLOR SCHEME APPROACH:
        - Complexity-appropriate color coding
        - Language-appropriate color choices
        - Consistent color mapping across components
        - Accessibility considerations
        - Cultural appropriateness for colors
        """
        # Base color schemes by complexity
        schemes = {
            'beginner': {
                'noun': '#4A90E2',      # Blue - basic concepts
                'verb': '#F5A623',      # Orange - action words
                'adjective': '#7ED321', # Green - descriptive words
                'adverb': '#BD10E0',    # Purple - modifiers
                'pronoun': '#50E3C2',   # Teal - replacements
                'preposition': '#D0021B', # Red - relationships
                'conjunction': '#F8E71C', # Yellow - connectors
                'interjection': '#9013FE', # Violet - expressions
            },
            'intermediate': {
                'noun': '#2171B5',      # Darker blue
                'verb': '#E65100',      # Darker orange
                'adjective': '#388E3C', # Darker green
                'adverb': '#7B1FA2',    # Darker purple
                'pronoun': '#00695C',   # Darker teal
                'preposition': '#B71C1C', # Darker red
                'conjunction': '#F57F17', # Darker yellow
                'interjection': '#4A148C', # Darker violet
                # Additional roles for intermediate
                'subject': '#0D47A1',   # Deep blue
                'object': '#1B5E20',    # Deep green
                'predicate': '#E65100', # Deep orange
            },
            'advanced': {
                'noun': '#0D47A1',      # Deep blue
                'verb': '#BF360C',      # Deep orange
                'adjective': '#1B5E20', # Deep green
                'adverb': '#4A148C',    # Deep purple
                'pronoun': '#004D40',   # Deep teal
                'preposition': '#880E4F', # Deep red
                'conjunction': '#E65100', # Deep yellow
                'interjection': '#311B92', # Deep violet
                # Advanced grammatical roles
                'subject': '#000051',   # Darkest blue
                'object': '#004D40',    # Darkest green
                'predicate': '#BF360C', # Darkest orange
                'modifier': '#4A148C',  # Darkest purple
                'complement': '#880E4F', # Darkest red
                'determiner': '#E65100', # Darkest yellow
            }
        }

        return schemes.get(complexity, schemes['intermediate'])

    def get_language_specific_rules(self) -> Dict[str, Any]:
        """Get language-specific grammatical rules."""
        return self.patterns.get('language_specific_rules', {})

    def is_language_text(self, text: str) -> bool:
        """Check if text contains {Language} characters."""
        # Basic validation - customize for your language
        if not text or not text.strip():
            return False

        # Check for language-specific character patterns
        # This is a placeholder - implement based on your language's script
        return True

    def get_word_meaning(self, word: str) -> Optional[str]:
        """Get pre-defined meaning for a word."""
        return self.word_meanings.get(word.lower())
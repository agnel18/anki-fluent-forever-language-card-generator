# languages/latvian/domain/lv_config.py
"""
Latvian Configuration — Domain Component

Latvian (Latviešu valoda) is an Indo-European Baltic language.
Key features: 7-case system, 2 genders, definite/indefinite adjective forms,
debitive mood, extensive participle system, SVO word order (flexible).
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class LvConfig:
    """
    Configuration for Latvian grammar analysis.
    Follows Clean Architecture pattern with external configuration files.
    """

    def __init__(self):
        self.language_code = "lv"
        self.language_name = "Latvian"
        self.language_name_native = "Latviešu"

        # Latvian is LTR
        self.is_rtl = False
        self.text_direction = "ltr"

        # Script properties
        self.script_type = "alphabetic"

        # Load external configuration files
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = (
            self._load_yaml(config_dir / "lv_grammatical_roles.yaml")
            or self._get_default_roles()
        )
        self.patterns = self._load_yaml(config_dir / "lv_patterns.yaml") or {}
        self.word_meanings = self._load_json(config_dir / "lv_word_meanings.json") or {}

        # Color schemes for each complexity level
        self.color_schemes = self._load_color_schemes()

        # Linguistic feature flags
        self.linguistic_features = {
            "case_system": True,          # 7 cases
            "grammatical_gender": True,   # masculine/feminine
            "definite_adjective": True,   # long/short form distinction
            "debitive_mood": True,        # jā- construction
            "reflexive_verbs": True,      # -ties suffix
            "participial_system": True,   # 4 participle types
            "aspect_prefixes": True,      # verbal prefixes
            "free_word_order": True,      # SVO default but flexible
        }

        # Latvian noun cases
        self.cases = [
            "nominative", "genitive", "dative", "accusative",
            "instrumental", "locative", "vocative"
        ]

        # Latvian genders
        self.genders = ["masculine", "feminine"]

        # Common verb prefixes (aspect/directional)
        self.verb_prefixes = [
            "aiz", "ap", "at", "ie", "iz", "no", "pa", "par", "pār",
            "pie", "sa", "uz"
        ]

        # Debitive marker
        self.debitive_marker = "jā"

    # ------------------------------------------------------------------
    # Default grammatical roles (used if YAML not found)
    # ------------------------------------------------------------------

    def _get_default_roles(self) -> Dict[str, Any]:
        """Default grammatical roles for Latvian, organized by complexity level."""
        return {
            "beginner": {
                "noun": "noun (lietvārds)",
                "verb": "verb (darbības vārds)",
                "adjective": "adjective (īpašības vārds)",
                "pronoun": "pronoun (vietniekvārds)",
                "preposition": "preposition (prievārds)",
                "conjunction": "conjunction (saiklis)",
                "adverb": "adverb (apstākļa vārds)",
                "numeral": "numeral (skaitļa vārds)",
            },
            "intermediate": {
                "noun": "noun (lietvārds)",
                "verb": "verb (darbības vārds)",
                "adjective": "adjective (īpašības vārds)",
                "adjective_definite": "definite adjective (noteiktā forma)",
                "adjective_indefinite": "indefinite adjective (nenoteiktā forma)",
                "pronoun": "pronoun (vietniekvārds)",
                "personal_pronoun": "personal pronoun (personas vietniekvārds)",
                "reflexive_pronoun": "reflexive pronoun (atgriezeniskais vietniekvārds)",
                "demonstrative": "demonstrative (norādāmais vietniekvārds)",
                "preposition": "preposition (prievārds)",
                "conjunction": "conjunction (saiklis)",
                "adverb": "adverb (apstākļa vārds)",
                "auxiliary": "auxiliary verb (palīgdarbības vārds)",
                "reflexive_verb": "reflexive verb (atgriezeniskais darbības vārds)",
                "numeral": "numeral (skaitļa vārds)",
                "particle": "particle (partikula)",
            },
            "advanced": {
                "noun": "noun (lietvārds)",
                "verb": "verb (darbības vārds)",
                "adjective": "adjective (īpašības vārds)",
                "adjective_definite": "definite adjective (noteiktā forma)",
                "adjective_indefinite": "indefinite adjective (nenoteiktā forma)",
                "pronoun": "pronoun (vietniekvārds)",
                "personal_pronoun": "personal pronoun (personas vietniekvārds)",
                "reflexive_pronoun": "reflexive pronoun (atgriezeniskais vietniekvārds)",
                "demonstrative": "demonstrative (norādāmais vietniekvārds)",
                "relative_pronoun": "relative pronoun (attieksmiskais vietniekvārds)",
                "indefinite_pronoun": "indefinite pronoun (nenoteiktais vietniekvārds)",
                "preposition": "preposition (prievārds)",
                "conjunction": "conjunction (saiklis)",
                "subordinating_conjunction": "subordinating conjunction (pakārtojuma saiklis)",
                "adverb": "adverb (apstākļa vārds)",
                "auxiliary": "auxiliary verb (palīgdarbības vārds)",
                "reflexive_verb": "reflexive verb (atgriezeniskais darbības vārds)",
                "participle": "participle (divdabis)",
                "debitive": "debitive (vajadzības izteiksme)",
                "numeral": "numeral (skaitļa vārds)",
                "particle": "particle (partikula)",
                "interjection": "interjection (izsauksmes vārds)",
                "verbal_noun": "verbal noun (darbības vārda lietvārds)",
            },
        }

    # ------------------------------------------------------------------
    # Color schemes
    # ------------------------------------------------------------------

    def _load_color_schemes(self) -> Dict[str, Dict[str, str]]:
        """Color schemes for Latvian grammatical roles at each complexity level."""
        base = {
            "noun": "#FFAA00",
            "verb": "#4ECDC4",
            "adjective": "#FF44FF",
            "adjective_definite": "#FF44FF",
            "adjective_indefinite": "#CC33CC",
            "adverb": "#FF6347",
            "pronoun": "#9370DB",
            "personal_pronoun": "#9370DB",
            "reflexive_pronoun": "#DDA0DD",
            "demonstrative": "#B8860B",
            "relative_pronoun": "#9370DB",
            "indefinite_pronoun": "#8B7EC8",
            "preposition": "#4444FF",
            "conjunction": "#AAAAAA",
            "subordinating_conjunction": "#888888",
            "auxiliary": "#00CED1",
            "reflexive_verb": "#20B2AA",
            "participle": "#FF8C00",
            "debitive": "#FF1493",
            "numeral": "#3CB371",
            "particle": "#20B2AA",
            "interjection": "#FF69B4",
            "verbal_noun": "#DAA520",
            "other": "#808080",
        }
        return {
            "beginner": base,
            "intermediate": base,
            "advanced": base,
        }

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for the given complexity level."""
        return self.color_schemes.get(complexity, self.color_schemes["intermediate"])

    def get_color_for_role(self, role: str, complexity: str = "intermediate") -> str:
        """Get the display color for a specific grammatical role."""
        scheme = self.get_color_scheme(complexity)
        return scheme.get(role, scheme.get("other", "#808080"))

    def get_role_label(self, role: str, complexity: str = "intermediate") -> str:
        """Get human-readable label for a grammatical role."""
        roles = self._get_default_roles()
        level_roles = roles.get(complexity, roles["intermediate"])
        return level_roles.get(role, role)

    # ------------------------------------------------------------------
    # File loaders
    # ------------------------------------------------------------------

    def _load_yaml(self, path: Path) -> Optional[Dict]:
        """Load YAML file if it exists, return None on failure."""
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Failed to load YAML {path}: {e}")
        return None

    def _load_json(self, path: Path) -> Optional[Dict]:
        """Load JSON file if it exists, return None on failure."""
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load JSON {path}: {e}")
        return None

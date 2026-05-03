# languages/english/domain/en_config.py
"""
English Configuration — Domain Component

English is an Indo-European West Germanic language.
Key features: analytic morphology, strict SVO word order, auxiliary verb system,
minimal inflection, phrasal verbs, categorical ambiguity.
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class EnConfig:
    """
    Configuration for English grammar analysis.
    Follows Clean Architecture pattern with external configuration files.
    """

    def __init__(self):
        self.language_code = "en"
        self.language_name = "English"
        self.language_name_native = "English"

        # English is LTR
        self.is_rtl = False
        self.text_direction = "ltr"

        # Script properties
        self.script_type = "alphabetic"

        # Load external configuration files
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = (
            self._load_yaml(config_dir / "en_grammatical_roles.yaml")
            or self._get_default_roles()
        )
        self.patterns = self._load_yaml(config_dir / "en_patterns.yaml") or {}
        self.word_meanings = self._load_json(config_dir / "en_word_meanings.json") or {}

        # Color schemes for each complexity level
        self.color_schemes = self._load_color_schemes()

        # Linguistic feature flags
        self.linguistic_features = {
            "case_system": False,            # English has lost noun case
            "pronoun_case": True,             # I/me, he/him, who/whom survives
            "grammatical_gender": False,      # No grammatical gender on nouns
            "auxiliary_stack": True,          # modal+have+be+be+main
            "do_support": True,
            "phrasal_verbs": True,
            "strict_svo": True,
            "subject_aux_inversion": True,
            "comparative_inflection": True,   # -er/-est vs more/most
            "minimal_verb_agreement": True,   # only 3sg -s
        }

        # English pronoun cases (the strongest case-system survival)
        self.pronoun_cases = ["nominative", "accusative", "genitive_determiner",
                              "genitive_pronoun", "reflexive"]

        # Common modal verbs (defective paradigm)
        self.modal_verbs = [
            "can", "could", "will", "would", "shall", "should",
            "may", "might", "must", "ought",
        ]

        # Common auxiliaries
        self.be_forms = ["be", "am", "is", "are", "was", "were", "been", "being"]
        self.have_forms = ["have", "has", "had", "having"]
        self.do_forms = ["do", "does", "did", "done", "doing"]

        # Articles
        self.articles = ["a", "an", "the"]

    # ------------------------------------------------------------------
    # Default grammatical roles (used if YAML not found)
    # ------------------------------------------------------------------

    def _get_default_roles(self) -> Dict[str, Any]:
        """Default grammatical roles for English, organized by complexity level.

        Aligned with the role hierarchy specified in en_grammar_concepts.md
        ('Prompt Complexity Levels' section).
        """
        return {
            "beginner": {
                "noun": "noun",
                "verb": "verb",
                "adjective": "adjective",
                "pronoun": "pronoun",
                "preposition": "preposition",
                "conjunction": "conjunction",
                "adverb": "adverb",
                "article": "article (a / an / the)",
                "auxiliary": "auxiliary verb (be / have / do)",
                "interjection": "interjection",
            },
            "intermediate": {
                "noun": "noun",
                "verb": "verb",
                "adjective": "adjective",
                "pronoun": "pronoun",
                "preposition": "preposition",
                "conjunction": "conjunction",
                "adverb": "adverb",
                "article": "article (a / an / the)",
                "auxiliary": "auxiliary verb (be / have / do)",
                "modal_verb": "modal verb (can / will / must / ...)",
                "particle": "particle (infinitive 'to' / phrasal-verb particle / negation 'not')",
                "infinitive_marker": "infinitive marker ('to' before a base verb)",
                "phrasal_verb_particle": "phrasal-verb particle (up / down / out / off / ...)",
                "determiner": "determiner (this / that / some / any / each / ...)",
                "demonstrative": "demonstrative (this / that / these / those)",
                "possessive_determiner": "possessive determiner (my / your / his / her / its / our / their)",
                "possessive_pronoun": "possessive pronoun (mine / yours / hers / ours / theirs)",
                "present_participle": "present participle (-ing form, after be: 'is running')",
                "past_participle": "past participle (-ed/-en form, after have/be)",
                "gerund": "gerund (-ing form used as a noun)",
                "infinitive": "infinitive (base verb, often with 'to')",
                "interjection": "interjection",
            },
            "advanced": {
                "noun": "noun",
                "verb": "verb",
                "adjective": "adjective",
                "pronoun": "pronoun",
                "preposition": "preposition",
                "conjunction": "conjunction",
                "adverb": "adverb",
                "article": "article (a / an / the)",
                "auxiliary": "auxiliary verb (be / have / do)",
                "modal_verb": "modal verb (can / will / must / ...)",
                "particle": "particle",
                "infinitive_marker": "infinitive marker ('to' before a base verb)",
                "phrasal_verb_particle": "phrasal-verb particle",
                "determiner": "determiner",
                "demonstrative": "demonstrative (this / that / these / those)",
                "possessive_determiner": "possessive determiner (my / your / his / ...)",
                "possessive_pronoun": "possessive pronoun (mine / yours / ...)",
                "present_participle": "present participle (-ing)",
                "past_participle": "past participle (-ed / -en)",
                "gerund": "gerund (-ing as noun)",
                "infinitive": "infinitive (base verb)",
                "relative_pronoun": "relative pronoun (who / whom / which / that / whose)",
                "subordinating_conjunction": "subordinating conjunction (because / although / if / when / ...)",
                "coordinating_conjunction": "coordinating conjunction (FANBOYS: for / and / nor / but / or / yet / so)",
                "interrogative_pronoun": "interrogative pronoun (who / what / which / whose)",
                "reflexive_pronoun": "reflexive pronoun (myself / yourself / themselves / ...)",
                "indefinite_pronoun": "indefinite pronoun (someone / anyone / nothing / each / ...)",
                "comparative": "comparative form (-er / more X)",
                "superlative": "superlative form (-est / most X)",
                "phrasal_verb": "phrasal verb (verb + particle non-compositional)",
                "interjection": "interjection",
            },
        }

    # ------------------------------------------------------------------
    # Color schemes
    # ------------------------------------------------------------------

    def _load_color_schemes(self) -> Dict[str, Dict[str, str]]:
        """Color schemes for English grammatical roles at each complexity level.

        Hex values for shared role names follow Latvian's mapping verbatim
        (so the UI is consistent across languages); English-specific roles
        (article, modal_verb, infinitive_marker, gerund, present_participle,
        past_participle, phrasal_verb_particle) get distinct colors.
        """
        base = {
            # --- shared with Latvian (verbatim) ---
            "noun": "#FFAA00",
            "verb": "#4ECDC4",
            "adjective": "#FF44FF",
            "adverb": "#FF6347",
            "pronoun": "#9370DB",
            "personal_pronoun": "#9370DB",
            "reflexive_pronoun": "#DDA0DD",
            "demonstrative": "#B8860B",
            "relative_pronoun": "#9370DB",
            "indefinite_pronoun": "#8B7EC8",
            "interrogative_pronoun": "#9370DB",
            "preposition": "#4444FF",
            "conjunction": "#AAAAAA",
            "subordinating_conjunction": "#888888",
            "coordinating_conjunction": "#AAAAAA",
            "auxiliary": "#00CED1",
            "numeral": "#3CB371",
            "particle": "#20B2AA",
            "interjection": "#FF69B4",
            "other": "#808080",
            # --- English-specific ---
            "article": "#FFD700",                  # gold — for a/an/the
            "modal_verb": "#9370DB",                # medium purple, distinct from auxiliary
            "phrasal_verb_particle": "#20B2AA",
            "phrasal_verb": "#20B2AA",
            "infinitive_marker": "#FF8C00",         # for "to"
            "gerund": "#FFA500",
            "infinitive": "#FFA500",
            "present_participle": "#FF7F50",
            "past_participle": "#FF6347",
            # determiners / possessives
            "determiner": "#B8860B",
            "possessive_determiner": "#B8860B",
            "possessive_pronoun": "#9370DB",
            # comparison
            "comparative": "#FF44FF",
            "superlative": "#FF44FF",
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

    def get_roles_for_complexity(self, complexity: str) -> List[str]:
        """Return the role keys allowed at the given complexity level."""
        roles = self._get_default_roles()
        level_roles = roles.get(complexity, roles["intermediate"])
        return list(level_roles.keys())

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

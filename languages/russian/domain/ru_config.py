# languages/russian/domain/ru_config.py
"""
Russian Configuration — Domain Component

Russian (Русский язык) is an Indo-European East-Slavic language.
Key features: 6-case system, 3 genders (masc/fem/neut), aspect system
(perfective/imperfective), reflexive verbs (-ся/-сь), 4 participle types,
gerunds (verbal adverbs), free word order, verbs of motion sub-grammar.

The role vocabulary follows the Phase-1 grammar concepts document
(`ru_grammar_concepts.md`) — the same vocabulary the Phase-5 YAML will
populate; the inline `_get_default_roles()` is the in-code source of truth
until the YAML lands.
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class RuConfig:
    """
    Configuration for Russian grammar analysis.
    Follows Clean Architecture pattern with external configuration files.
    """

    def __init__(self):
        self.language_code = "ru"
        self.language_name = "Russian"
        self.language_name_native = "Русский"

        # Russian is LTR
        self.is_rtl = False
        self.text_direction = "ltr"

        # Script properties
        self.script_type = "alphabetic"  # Cyrillic alphabet

        # Load external configuration files (Phase 5 will populate)
        config_dir = Path(__file__).parent.parent / "infrastructure" / "data"
        self.grammatical_roles = (
            self._load_yaml(config_dir / "ru_grammatical_roles.yaml")
            or self._get_default_roles()
        )
        self.patterns = self._load_yaml(config_dir / "ru_patterns.yaml") or {}
        self.word_meanings = self._load_json(config_dir / "ru_word_meanings.json") or {}

        # Color schemes for each complexity level
        self.color_schemes = self._load_color_schemes()

        # Linguistic feature flags
        self.linguistic_features = {
            "case_system": True,           # 6 cases
            "grammatical_gender": True,    # masculine/feminine/neuter (+ common)
            "animacy": True,               # masc-acc + pl-acc distinguish anim/inan
            "verbal_aspect": True,         # imperfective ↔ perfective pairs
            "reflexive_verbs": True,       # -ся / -сь clitic
            "participial_system": True,    # 4 participle types
            "gerunds": True,               # деепричастия (verbal adverbs)
            "free_word_order": True,       # information-structure driven
            "pro_drop": True,
            "null_copula_present": True,
            "verbs_of_motion": True,       # 14 indeterminate/determinate pairs
            "negative_concord": True,      # multiple negation required
        }

        # Russian noun cases
        self.cases = [
            "nominative", "genitive", "dative",
            "accusative", "instrumental", "prepositional",
        ]
        # Russian gender values
        self.genders = ["masculine", "feminine", "neuter", "common"]

        # Common perfectivising verb prefixes (heuristic for fallback aspect)
        self.perfective_prefixes = [
            "по", "на", "про", "за", "пере", "вы", "с",
            "у", "при", "до", "под", "от", "раз", "в", "из",
        ]
        # Imperfectivising suffixes (rare in fallback but worth marking)
        self.imperfective_suffixes = ["ива", "ыва", "ва"]

    # ------------------------------------------------------------------
    # Default grammatical roles (used if YAML not found)
    # Mirrors the Phase-1 doc "Complexity Hierarchy" exactly.
    # ------------------------------------------------------------------

    def _get_default_roles(self) -> Dict[str, Any]:
        """Default grammatical roles for Russian, organized by complexity level."""
        return {
            "beginner": {
                "noun": "noun (имя существительное)",
                "verb": "verb (глагол)",
                "adjective": "adjective (имя прилагательное)",
                "pronoun": "pronoun (местоимение)",
                "preposition": "preposition (предлог)",
                "conjunction": "conjunction (союз)",
                "adverb": "adverb (наречие)",
                "particle": "particle (частица)",
                "numeral": "numeral (имя числительное)",
                "interjection": "interjection (междометие)",
                "other": "other",
            },
            "intermediate": {
                "noun": "noun (имя существительное)",
                "verb": "verb (глагол)",
                "adjective": "adjective (имя прилагательное)",
                "short_adjective": "short-form adjective (краткое прилагательное)",
                "comparative": "comparative (сравнительная степень)",
                "superlative": "superlative (превосходная степень)",
                "pronoun": "pronoun (местоимение)",
                "personal_pronoun": "personal pronoun (личное местоимение)",
                "possessive_pronoun": "possessive pronoun (притяжательное местоимение)",
                "possessive_determiner": "possessive determiner (притяжательное определение)",
                "demonstrative": "demonstrative (указательное местоимение)",
                "reflexive_pronoun": "reflexive pronoun (возвратное местоимение)",
                "reflexive_verb": "reflexive verb (возвратный глагол)",
                "preposition": "preposition (предлог)",
                "conjunction": "conjunction (союз)",
                "adverb": "adverb (наречие)",
                "auxiliary": "auxiliary verb (вспомогательный глагол)",
                "modal_verb": "modal verb (модальный глагол)",
                "infinitive": "infinitive (инфинитив)",
                "imperative": "imperative (повелительное наклонение)",
                "particle": "particle (частица)",
                "numeral": "numeral (имя числительное)",
                "interjection": "interjection (междометие)",
                "other": "other",
            },
            "advanced": {
                "noun": "noun (имя существительное)",
                "verb": "verb (глагол)",
                "imperfective_verb": "imperfective verb (несовершенный вид)",
                "perfective_verb": "perfective verb (совершенный вид)",
                "adjective": "adjective (имя прилагательное)",
                "short_adjective": "short-form adjective (краткое прилагательное)",
                "comparative": "comparative (сравнительная степень)",
                "superlative": "superlative (превосходная степень)",
                "pronoun": "pronoun (местоимение)",
                "personal_pronoun": "personal pronoun (личное местоимение)",
                "possessive_pronoun": "possessive pronoun (притяжательное местоимение)",
                "possessive_determiner": "possessive determiner (притяжательное определение)",
                "demonstrative": "demonstrative (указательное местоимение)",
                "reflexive_pronoun": "reflexive pronoun (возвратное местоимение)",
                "reflexive_verb": "reflexive verb (возвратный глагол)",
                "relative_pronoun": "relative pronoun (относительное местоимение)",
                "interrogative_pronoun": "interrogative pronoun (вопросительное местоимение)",
                "indefinite_pronoun": "indefinite pronoun (неопределённое местоимение)",
                "negative_pronoun": "negative pronoun (отрицательное местоимение)",
                "preposition": "preposition (предлог)",
                "conjunction": "conjunction (союз)",
                "coordinating_conjunction": "coordinating conjunction (сочинительный союз)",
                "subordinating_conjunction": "subordinating conjunction (подчинительный союз)",
                "adverb": "adverb (наречие)",
                "auxiliary": "auxiliary verb (вспомогательный глагол)",
                "modal_verb": "modal verb (модальный глагол)",
                "infinitive": "infinitive (инфинитив)",
                "imperative": "imperative (повелительное наклонение)",
                "copula": "copula (связка)",
                "present_active_participle": "present active participle (действительное причастие настоящего времени)",
                "past_active_participle": "past active participle (действительное причастие прошедшего времени)",
                "present_passive_participle": "present passive participle (страдательное причастие настоящего времени)",
                "past_passive_participle": "past passive participle (страдательное причастие прошедшего времени)",
                "participle": "participle (причастие)",
                "gerund": "gerund / verbal adverb (деепричастие)",
                "verbal_noun": "verbal noun (отглагольное существительное)",
                "particle": "particle (частица)",
                "aspectual_particle": "aspectual / conditional particle (бы)",
                "conditional_particle": "conditional particle (бы)",
                "negation_particle": "negation particle (не / ни)",
                "numeral": "numeral (имя числительное)",
                "interjection": "interjection (междометие)",
                "other": "other",
            },
        }

    # ------------------------------------------------------------------
    # Color schemes
    # ------------------------------------------------------------------

    def _load_color_schemes(self) -> Dict[str, Dict[str, str]]:
        """Color schemes for Russian roles at each complexity level.

        Russian-specific notes (from task spec):
          - All 6 cases share the noun color (#FFAA00); the case is conveyed via
            the `individual_meaning` text, NOT a per-case color.
          - imperfective_verb / perfective_verb share the verb color (#4ECDC4).
          - aspectual_particle (бы) reuses Latvian's debitive color (#FF1493) —
            both mark a non-indicative mood.
          - reflexive_verb #20B2AA, participle #FF8C00, gerund #FFA500.
          - negation_particle (не / ни) #FF6347.
          - All other roles use Latvian's hex codes for visual continuity.
        """
        base = {
            # Open-class
            "noun": "#FFAA00",
            "verb": "#4ECDC4",
            "imperfective_verb": "#4ECDC4",
            "perfective_verb": "#4ECDC4",
            "infinitive": "#4ECDC4",
            "imperative": "#4ECDC4",
            "modal_verb": "#00CED1",
            "auxiliary": "#00CED1",
            "copula": "#00CED1",
            "reflexive_verb": "#20B2AA",
            "adjective": "#FF44FF",
            "short_adjective": "#CC33CC",
            "comparative": "#FF44FF",
            "superlative": "#FF44FF",
            "adverb": "#FF6347",
            # Pronouns
            "pronoun": "#9370DB",
            "personal_pronoun": "#9370DB",
            "possessive_pronoun": "#9370DB",
            "possessive_determiner": "#9370DB",
            "reflexive_pronoun": "#DDA0DD",
            "demonstrative": "#B8860B",
            "relative_pronoun": "#9370DB",
            "interrogative_pronoun": "#9370DB",
            "indefinite_pronoun": "#8B7EC8",
            "negative_pronoun": "#8B7EC8",
            # Closed-class
            "preposition": "#4444FF",
            "conjunction": "#AAAAAA",
            "coordinating_conjunction": "#AAAAAA",
            "subordinating_conjunction": "#888888",
            # Particles
            "particle": "#20B2AA",
            "aspectual_particle": "#FF1493",
            "conditional_particle": "#FF1493",
            "negation_particle": "#FF6347",
            # Numerals & misc
            "numeral": "#3CB371",
            "interjection": "#FF69B4",
            # Verbal forms
            "participle": "#FF8C00",
            "present_active_participle": "#FF8C00",
            "past_active_participle": "#FF8C00",
            "present_passive_participle": "#FF8C00",
            "past_passive_participle": "#FF8C00",
            "gerund": "#FFA500",
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
                    data = yaml.safe_load(f)
                    # Only accept non-empty mappings (the Phase-2 scaffolds
                    # leave a near-empty placeholder file behind).
                    if isinstance(data, dict) and data:
                        return data
            except Exception as e:
                logger.warning(f"Failed to load YAML {path}: {e}")
        return None

    def _load_json(self, path: Path) -> Optional[Dict]:
        """Load JSON file if it exists, return None on failure."""
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and data:
                        return data
            except Exception as e:
                logger.warning(f"Failed to load JSON {path}: {e}")
        return None

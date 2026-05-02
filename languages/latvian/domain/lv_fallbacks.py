# languages/latvian/domain/lv_fallbacks.py
"""
Latvian Fallbacks — Domain Component

Rule-based fallback grammar analysis for Latvian.
Used when AI response is unavailable or unparseable.
"""

import logging
import re
from typing import Any, Dict, List

from .lv_config import LvConfig

logger = logging.getLogger(__name__)

# Common Latvian function words for rule-based analysis
_CONJUNCTIONS = {
    "un", "bet", "vai", "jo", "tāpēc", "taču", "tomēr",
    "ka", "kad", "ja", "lai", "kaut", "gan",
}

_PREPOSITIONS = {
    "bez", "līdz", "no", "pēc", "pie", "priekš", "starp",
    "pret", "ap", "caur", "gar", "pār", "par", "uz",
    "aiz", "iekš", "pa",
}

_PRONOUNS = {
    "es", "tu", "viņš", "viņa", "mēs", "jūs", "viņi", "viņas",
    "man", "tev", "viņam", "viņai", "mums", "jums",
    "mani", "tevi", "viņu",
    "kas", "ko", "kurš", "kura", "šis", "šī", "tas", "tā",
    "sevi", "sev",
}

_ADVERBS = {
    "labi", "ātri", "lēni", "ļoti", "diezgan", "gandrīz",
    "tagad", "tad", "vienmēr", "nekad", "šeit", "tur", "mājās",
    "jau", "vēl", "tikai", "arī",
}

_AUXILIARY = {"ir", "bija", "būs", "būtu", "esmu", "esi", "esam", "esat"}

_NUMERALS = {
    "viens", "viena", "divi", "divas", "trīs", "četri", "četras",
    "pieci", "piecas", "seši", "sešas", "septiņi", "septiņas",
    "astoņi", "astoņas", "deviņi", "deviņas", "desmit",
}


class LvFallbacks:
    """Rule-based fallback analysis for Latvian grammar."""

    def __init__(self, config: LvConfig):
        self.config = config

    def create_fallback(self, sentence: str, complexity: str) -> Dict[str, Any]:
        """Create a basic rule-based grammar analysis."""
        words = sentence.split()
        word_explanations = []

        for word in words:
            clean = word.strip(".,!?;:\"'()[]")
            role, meaning = self._classify_word(clean, complexity)
            color = self.config.get_color_for_role(role, complexity)
            word_explanations.append({
                "word": word,
                "role": role,
                "color": color,
                "meaning": meaning,
                "case": "",
                "gender": "",
                "number": "",
                "tense": "",
                "definite_form": "",
            })

        return {
            "word_explanations": word_explanations,
            "overall_structure": "Latvian sentence (rule-based fallback)",
            "sentence_structure": "Latvian sentence (rule-based fallback)",
            "explanations": {
                item["word"]: item["meaning"] for item in word_explanations
            },
            "elements": {item["word"]: item["role"] for item in word_explanations},
            "grammar_notes": "Rule-based fallback analysis — AI unavailable.",
            "confidence": 0.35,
        }

    def _classify_word(self, word: str, complexity: str):
        """Simple rule-based word classification."""
        lower = word.lower()

        if not word or not word.strip():
            return "other", word

        if lower in _AUXILIARY:
            return "auxiliary", f"{word} (auxiliary verb 'būt' = to be)"

        if lower in _CONJUNCTIONS:
            return "conjunction", f"{word} (conjunction)"

        if lower in _PREPOSITIONS:
            return "preposition", f"{word} (preposition)"

        if lower in _PRONOUNS:
            return "pronoun", f"{word} (pronoun)"

        if lower in _ADVERBS:
            return "adverb", f"{word} (adverb)"

        if lower in _NUMERALS:
            return "numeral", f"{word} (numeral)"

        # Reflexive verb: ends in -ties or -ās
        if complexity != "beginner" and (lower.endswith("ties") or lower.endswith("ās")):
            return "reflexive_verb", f"{word} (reflexive verb)"

        # Debitive: starts with jā
        if complexity != "beginner" and lower.startswith("jā"):
            return "debitive", f"{word} (debitive — obligation)"

        # Participle (advanced): ends in -ošs/-oša, -is/-usi, -ts/-ta, -ams/-ama
        if complexity == "advanced" and re.search(r"(ošs|oša|ošu|ošam|ošai|oši|ošas|amais|ošais)$", lower):
            return "participle", f"{word} (present active participle)"
        if complexity == "advanced" and re.search(r"(āts|āta|ātu|ātam|ātai)$", lower):
            return "participle", f"{word} (past passive participle)"

        # Verbal noun: ends in -šana
        if complexity == "advanced" and lower.endswith("šana"):
            return "verbal_noun", f"{word} (verbal noun)"

        # Definite adjective form: ends in -ais/-ā (simplified heuristic)
        if complexity != "beginner" and re.search(r"(ais|ā|ie|ās)$", lower) and len(word) > 3:
            return "adjective_definite", f"{word} (definite adjective)"

        # Common verb endings
        if re.search(r"(āju|āji|ā|ājam|ājat|āja|ās|ājies|āsies)$", lower):
            return "verb", f"{word} (verb)"

        # Noun heuristics: -s, -is, -us masculine; -a, -e feminine
        if re.search(r"(s|is|us)$", lower) and len(word) > 2:
            return "noun", f"{word} (noun — likely masculine)"
        if re.search(r"(a|e)$", lower) and len(word) > 2:
            return "noun", f"{word} (noun — likely feminine)"

        return "other", f"{word}"

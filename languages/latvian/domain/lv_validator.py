# languages/latvian/domain/lv_validator.py
"""
Latvian Validator — Domain Component

Validates grammar analysis results and returns a confidence score (0.0–1.0).
Target: ≥ 0.85 for production deployment.
"""

import logging
from typing import Any, Dict, List

from .lv_config import LvConfig

logger = logging.getLogger(__name__)

# Roles that MUST be present for a minimal valid analysis
_REQUIRED_ROLES = {"noun", "verb"}

# Valid Latvian grammatical roles (superset)
_VALID_ROLES = {
    "noun", "verb", "adjective", "adjective_definite", "adjective_indefinite",
    "pronoun", "personal_pronoun", "reflexive_pronoun", "demonstrative",
    "relative_pronoun", "indefinite_pronoun", "preposition", "conjunction",
    "subordinating_conjunction", "adverb", "auxiliary", "reflexive_verb",
    "participle", "debitive", "numeral", "particle", "interjection",
    "verbal_noun", "other",
}

_VALID_CASES = {
    "nominative", "genitive", "dative", "accusative",
    "instrumental", "locative", "vocative", "",
}

_VALID_GENDERS = {"masculine", "feminine", ""}


class LvValidator:
    """Validates Latvian grammar analysis results."""

    def __init__(self, config: LvConfig):
        self.config = config

    def validate_result(
        self, result: Dict[str, Any], sentence: str
    ) -> Dict[str, Any]:
        """
        Validate and enrich the analysis result.
        Returns the result dict with a 'confidence' key set.
        """
        if not result or not isinstance(result, dict):
            return {"confidence": 0.0, "word_explanations": []}

        confidence = self._calculate_confidence(result, sentence)
        result["confidence"] = confidence
        return result

    def validate_analysis(
        self, parsed_data: Dict[str, Any], original_sentence: str
    ) -> float:
        """Return confidence score for abstract method compliance."""
        result = self.validate_result(parsed_data, original_sentence)
        return result.get("confidence", 0.0)

    # ------------------------------------------------------------------
    # Confidence calculation
    # ------------------------------------------------------------------

    def _calculate_confidence(
        self, result: Dict[str, Any], sentence: str
    ) -> float:
        """Multi-dimensional confidence scoring."""
        scores: List[float] = []

        word_explanations = result.get("word_explanations", [])

        # 1. Coverage score: were all words accounted for?
        scores.append(self._score_coverage(word_explanations, sentence))

        # 2. Role validity: are roles from the valid set?
        scores.append(self._score_role_validity(word_explanations))

        # 3. Completeness: do explanations have required fields?
        scores.append(self._score_completeness(word_explanations))

        # 4. Latvian-specific: case / gender presence where applicable
        scores.append(self._score_latvian_features(word_explanations))

        # 5. Structure description present?
        has_structure = bool(
            result.get("overall_structure") or result.get("sentence_structure")
        )
        scores.append(0.9 if has_structure else 0.5)

        if not scores:
            return 0.5
        confidence = sum(scores) / len(scores)
        return round(min(max(confidence, 0.0), 1.0), 3)

    def _score_coverage(
        self, word_explanations: List[Dict], sentence: str
    ) -> float:
        """How well do the word_explanations cover the sentence tokens?"""
        if not word_explanations:
            return 0.2
        sentence_tokens = [w.strip(".,!?;:\"'()[]") for w in sentence.split() if w.strip()]
        explained_words = {
            item.get("word", "").strip(".,!?;:\"'()[]").lower()
            for item in word_explanations
            if isinstance(item, dict)
        }
        if not sentence_tokens:
            return 0.5
        covered = sum(
            1 for t in sentence_tokens if t.lower() in explained_words
        )
        ratio = covered / len(sentence_tokens)
        if ratio >= 0.9:
            return 0.95
        elif ratio >= 0.7:
            return 0.75
        elif ratio >= 0.5:
            return 0.55
        return 0.3

    def _score_role_validity(self, word_explanations: List[Dict]) -> float:
        """What fraction of roles are from the valid role set?"""
        if not word_explanations:
            return 0.3
        valid_count = sum(
            1 for item in word_explanations
            if isinstance(item, dict) and item.get("role", "").lower() in _VALID_ROLES
        )
        ratio = valid_count / len(word_explanations)
        return 0.9 if ratio >= 0.9 else (0.7 if ratio >= 0.7 else 0.5)

    def _score_completeness(self, word_explanations: List[Dict]) -> float:
        """Are meaning and color fields populated?"""
        if not word_explanations:
            return 0.3
        complete = sum(
            1 for item in word_explanations
            if isinstance(item, dict)
            and item.get("word")
            and item.get("meaning")
            and item.get("color")
        )
        ratio = complete / len(word_explanations)
        return 0.9 if ratio >= 0.9 else (0.7 if ratio >= 0.7 else 0.5)

    def _score_latvian_features(self, word_explanations: List[Dict]) -> float:
        """Do noun/adjective entries include case and gender info?"""
        relevant = [
            item for item in word_explanations
            if isinstance(item, dict)
            and item.get("role", "") in {
                "noun", "adjective", "adjective_definite", "adjective_indefinite",
                "pronoun", "personal_pronoun",
            }
        ]
        if not relevant:
            return 0.85  # No nouns/adjectives — not penalised
        with_case = sum(1 for item in relevant if item.get("case", "").strip())
        ratio = with_case / len(relevant)
        return 0.9 if ratio >= 0.7 else (0.7 if ratio >= 0.4 else 0.5)

    def validate_explanation_quality(
        self, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check explanation quality and return a quality report."""
        word_explanations = result.get("word_explanations", [])
        issues = []
        for item in word_explanations:
            if not isinstance(item, dict):
                continue
            if not item.get("meaning"):
                issues.append(f"Missing meaning for '{item.get('word', '?')}'")
            if not item.get("color"):
                issues.append(f"Missing color for '{item.get('word', '?')}'")
            if item.get("role", "") not in _VALID_ROLES:
                issues.append(
                    f"Invalid role '{item.get('role')}' for '{item.get('word', '?')}'"
                )
        quality_score = max(0.5, 1.0 - len(issues) * 0.05)
        return {"issues": issues, "quality_score": quality_score}

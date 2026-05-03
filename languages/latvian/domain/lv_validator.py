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
        """Check explanation quality and return a quality report.

        Mirrors de_validator.validate_explanation_quality — penalises shallow
        stubs (e.g. "Šis (pronoun): Šis (pronoun)") so confidence drops below
        the deployment threshold and the analyzer signals "low quality" rather
        than blessing nonsense output as valid.

        Penalty factors (multiplicative):
          - Missing meaning / color: -0.1 per issue
          - Invalid role: -0.05 per issue
          - "Stub" explanations (< 20 chars OR meaning equals word OR meaning
            equals "{word} ({role}):") — strong penalty: -0.2 per issue
          - Missing Latvian-specific features (case/gender/definiteness mention)
            on inflected words (nouns/adjectives/pronouns): -0.05 per issue
        """
        word_explanations = result.get("word_explanations", [])
        issues = []
        stub_count = 0
        feature_gap_count = 0

        latvian_feature_keywords = [
            "case", "nominative", "genitive", "dative", "accusative",
            "instrumental", "locative", "vocative",
            "gender", "masculine", "feminine",
            "definite", "indefinite",
            "singular", "plural",
            "person", "1st", "2nd", "3rd",
            "tense", "present", "past", "future",
            "agree", "agrees", "agreement",
            "subject", "object", "predicate",
            "lemma", "conjugation", "declension",
        ]

        inflected_roles = {
            "noun", "adjective", "adjective_definite", "adjective_indefinite",
            "pronoun", "personal_pronoun", "reflexive_pronoun", "demonstrative",
            "relative_pronoun", "indefinite_pronoun", "verb", "auxiliary",
            "reflexive_verb", "participle", "debitive", "verbal_noun",
        }

        for item in word_explanations:
            if not isinstance(item, dict):
                continue
            word = item.get("word", "?")
            role = item.get("role", "")
            meaning = (item.get("meaning") or "").strip()
            individual = (item.get("individual_meaning") or "").strip()

            if not meaning:
                issues.append(f"Missing meaning for '{word}'")
                continue
            if not item.get("color"):
                issues.append(f"Missing color for '{word}'")
            if role not in _VALID_ROLES:
                issues.append(f"Invalid role '{role}' for '{word}'")

            # Stub detection — explanation that is just "{word} ({role}):" with
            # no body, or simply repeats the word, or is fewer than 20 characters.
            stripped_prefix = f"{word} ({role}):".strip()
            body = meaning[len(stripped_prefix):].strip() if meaning.startswith(stripped_prefix) else meaning
            if len(body) < 20 or body.lower() == word.lower():
                stub_count += 1
                issues.append(f"Stub explanation for '{word}' (body too short or empty)")
                continue

            # Inflected-word feature check.
            if role in inflected_roles:
                explanation_text = (individual or body).lower()
                if not any(kw in explanation_text for kw in latvian_feature_keywords):
                    feature_gap_count += 1
                    issues.append(
                        f"Inflected word '{word}' ({role}) — explanation lacks "
                        f"case/gender/tense/agreement detail"
                    )

        # Quality score combines all penalty types.
        score = 1.0
        score -= 0.1 * sum(1 for i in issues if i.startswith("Missing"))
        score -= 0.05 * sum(1 for i in issues if i.startswith("Invalid"))
        score -= 0.2 * stub_count
        score -= 0.05 * feature_gap_count
        quality_score = max(0.0, min(score, 1.0))

        return {
            "issues": issues,
            "quality_score": quality_score,
            "stub_count": stub_count,
            "feature_gap_count": feature_gap_count,
        }

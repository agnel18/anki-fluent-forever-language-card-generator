# languages/portuguese/domain/pt_validator.py
"""
Portuguese Validator — Domain Component

Validates grammar analysis results and returns a confidence score (0.0–1.0).
Production threshold: ≥ 0.85 on well-formed Portuguese sentences.

Multi-dimensional confidence scoring:
  1. Coverage      — what fraction of sentence tokens are explained?
  2. Role validity — do roles come from the valid Portuguese role set?
  3. Completeness  — do entries have meaning/color/word populated?
  4. PT features   — gender on nouns, copula_type on copulas, clitic_position
                     on clitics, contraction_parts on contractions
  5. Structure     — is overall_structure / sentence_structure populated?

Plus targeted bonuses/penalties from pt_grammar_concepts.md §"Confidence
Scoring Criteria" — ser/estar correctly distinguished, contractions split,
clitic position identified, personal infinitive recognised, future
subjunctive disambiguated, BR/PT register tagged.
"""

import logging
from typing import Any, Dict, List

from .pt_config import PtConfig

logger = logging.getLogger(__name__)


# Valid Portuguese grammatical roles (superset across all complexity levels).
_VALID_ROLES = {
    # Core
    "noun", "verb", "adjective", "adverb", "pronoun",
    "preposition", "conjunction", "interjection", "article", "numeral",
    # Pronoun subtypes
    "personal_pronoun", "possessive_pronoun", "demonstrative_pronoun",
    "reflexive_pronoun", "relative_pronoun", "indefinite_pronoun",
    "interrogative_pronoun",
    # Article subtypes
    "definite_article", "indefinite_article",
    # Verb subtypes
    "auxiliary_verb", "modal_verb", "pronominal_verb",
    # Portuguese-specific
    "copula", "contraction", "personal_infinitive", "mesoclitic",
    "clitic_pronoun", "gerund", "past_participle", "subjunctive_marker",
    "conditional", "debitive", "particle", "subordinating_conjunction",
    # Misc
    "other",
}

_VALID_GENDERS = {"masculine", "feminine", "m", "f", "neutral", ""}
_VALID_COPULA_TYPES = {"ser", "estar", ""}
_VALID_CLITIC_POSITIONS = {"proclitic", "enclitic", "mesoclitic", ""}


class PtValidator:
    """Validates Portuguese grammar analysis results."""

    def __init__(self, config: PtConfig):
        self.config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

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

        if confidence < 0.85:
            logger.info(
                f"Confidence {confidence:.2f} below 0.85 threshold "
                f"for: {sentence[:60]}"
            )
        return result

    def validate_analysis(
        self, parsed_data: Dict[str, Any], original_sentence: str
    ) -> float:
        """Abstract-method-compatible scalar return."""
        result = self.validate_result(parsed_data, original_sentence)
        return result.get("confidence", 0.0)

    # ------------------------------------------------------------------
    # Confidence calculation
    # ------------------------------------------------------------------

    def _calculate_confidence(
        self, result: Dict[str, Any], sentence: str
    ) -> float:
        """Multi-dimensional confidence scoring."""
        word_explanations = result.get("word_explanations", []) or []
        word_details = result.get("word_details", []) or []

        scores: List[float] = []

        # 1. Coverage
        scores.append(self._score_coverage(word_explanations, sentence))

        # 2. Role validity
        scores.append(self._score_role_validity(word_explanations))

        # 3. Completeness (meaning + color present)
        scores.append(self._score_completeness(word_explanations))

        # 4. Portuguese-specific feature checks
        scores.append(self._score_portuguese_features(word_details))

        # 5. Structure description present
        has_structure = bool(
            result.get("overall_structure")
            or result.get("sentence_structure")
            or (
                isinstance(result.get("explanations"), dict)
                and (
                    result["explanations"].get("overall_structure")
                    or result["explanations"].get("sentence_structure")
                )
            )
        )
        scores.append(0.9 if has_structure else 0.5)

        if not scores:
            return 0.5

        confidence = sum(scores) / len(scores)

        # Apply Portuguese-specific bonuses (small additive nudges)
        confidence += self._portuguese_bonus(result, word_details)

        # Penalties for clearly wrong tagging
        confidence -= self._portuguese_penalty(word_details)

        return round(min(max(confidence, 0.0), 1.0), 3)

    def _score_coverage(
        self, word_explanations: List[Any], sentence: str
    ) -> float:
        """How well do the word_explanations cover the sentence tokens?"""
        if not word_explanations:
            return 0.2
        sentence_tokens = [
            w.strip(".,!?;:\"'()[]") for w in sentence.split() if w.strip()
        ]
        explained_words = set()
        for item in word_explanations:
            if isinstance(item, dict):
                w = str(item.get("word", "")).strip(".,!?;:\"'()[]").lower()
            elif isinstance(item, (list, tuple)) and len(item) >= 1:
                w = str(item[0]).strip(".,!?;:\"'()[]").lower()
            else:
                continue
            if w:
                explained_words.add(w)

        if not sentence_tokens:
            return 0.5
        covered = sum(
            1 for t in sentence_tokens if t.lower() in explained_words
        )
        ratio = covered / len(sentence_tokens)
        if ratio >= 0.9:
            return 0.95
        if ratio >= 0.7:
            return 0.78
        if ratio >= 0.5:
            return 0.6
        return 0.35

    def _score_role_validity(
        self, word_explanations: List[Any]
    ) -> float:
        """What fraction of roles are from the valid Portuguese role set?"""
        if not word_explanations:
            return 0.3
        valid_count = 0
        total = 0
        for item in word_explanations:
            total += 1
            if isinstance(item, dict):
                role = str(item.get("grammatical_role") or item.get("role") or "").lower()
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                role = str(item[1]).lower()
            else:
                continue
            if role in _VALID_ROLES:
                valid_count += 1
        if total == 0:
            return 0.3
        ratio = valid_count / total
        if ratio >= 0.95:
            return 0.95
        if ratio >= 0.85:
            return 0.88
        if ratio >= 0.7:
            return 0.75
        return 0.55

    def _score_completeness(self, word_explanations: List[Any]) -> float:
        """Are word, meaning, and color all populated?"""
        if not word_explanations:
            return 0.3
        complete = 0
        total = 0
        for item in word_explanations:
            total += 1
            if isinstance(item, dict):
                if item.get("word") and item.get("meaning") and item.get("color"):
                    complete += 1
            elif isinstance(item, (list, tuple)) and len(item) >= 4:
                if item[0] and item[2] and item[3]:
                    complete += 1
        if total == 0:
            return 0.3
        ratio = complete / total
        if ratio >= 0.9:
            return 0.93
        if ratio >= 0.75:
            return 0.8
        return 0.55

    def _score_portuguese_features(
        self, word_details: List[Dict[str, Any]]
    ) -> float:
        """
        Are Portuguese-specific meta fields populated where applicable?
        - Nouns / adjectives should have gender
        - Copulas should have copula_type ('ser' or 'estar')
        - Clitic_pronoun / mesoclitic should have clitic_position
        - Contraction should have contraction_parts (length 2)
        """
        if not word_details:
            return 0.7  # No detail → cannot score, neutral

        total = 0
        ok = 0

        for item in word_details:
            if not isinstance(item, dict):
                continue
            role = item.get("grammatical_role") or item.get("role") or ""

            if role in ("noun", "adjective"):
                total += 1
                if item.get("gender") in ("masculine", "feminine", "m", "f"):
                    ok += 1

            elif role == "copula":
                total += 1
                if item.get("copula_type") in ("ser", "estar"):
                    ok += 1

            elif role in ("clitic_pronoun", "mesoclitic"):
                total += 1
                if item.get("clitic_position") in (
                    "proclitic", "enclitic", "mesoclitic"
                ):
                    ok += 1

            elif role == "contraction":
                total += 1
                parts = item.get("contraction_parts") or []
                if isinstance(parts, list) and len(parts) >= 2:
                    ok += 1

        if total == 0:
            return 0.85  # No applicable items — not penalised
        ratio = ok / total
        if ratio >= 0.85:
            return 0.95
        if ratio >= 0.6:
            return 0.78
        if ratio >= 0.3:
            return 0.6
        return 0.45

    # ------------------------------------------------------------------
    # Portuguese-specific bonuses & penalties
    # (Calibrated to keep top-end well-formed analyses ≥ 0.85.)
    # ------------------------------------------------------------------

    def _portuguese_bonus(
        self,
        result: Dict[str, Any],
        word_details: List[Dict[str, Any]],
    ) -> float:
        """Small positive nudges for distinctly Portuguese constructs."""
        bonus = 0.0
        # Register tagged
        if result.get("register") in ("BR", "PT", "neutral"):
            bonus += 0.01
        for item in word_details or []:
            if not isinstance(item, dict):
                continue
            role = item.get("grammatical_role") or item.get("role") or ""
            if role == "copula" and item.get("copula_type") in ("ser", "estar"):
                bonus += 0.02
            elif role == "contraction" and len(item.get("contraction_parts") or []) >= 2:
                bonus += 0.02
            elif role in ("clitic_pronoun", "mesoclitic") and item.get("clitic_position"):
                bonus += 0.02
            elif role == "personal_infinitive":
                bonus += 0.02
            elif role == "subjunctive_marker":
                bonus += 0.01
        # Cap the additive bonus
        return min(bonus, 0.10)

    def _portuguese_penalty(
        self, word_details: List[Dict[str, Any]]
    ) -> float:
        """Penalties for confused/missed Portuguese-specific tags."""
        penalty = 0.0
        for item in word_details or []:
            if not isinstance(item, dict):
                continue
            role = item.get("grammatical_role") or item.get("role") or ""
            # Copula tagged but no copula_type — that's a confused analysis
            if role == "copula" and item.get("copula_type") not in ("ser", "estar"):
                penalty += 0.03
            # Contraction tagged but no parts — missed split
            if role == "contraction" and not (item.get("contraction_parts") or []):
                penalty += 0.02
        return min(penalty, 0.15)

    # ------------------------------------------------------------------
    # Quality report (used by the analyzer facade for logging)
    # ------------------------------------------------------------------

    def validate_explanation_quality(
        self, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Surface specific issues found in the explanations."""
        issues: List[str] = []
        word_details = result.get("word_details") or []
        word_explanations = result.get("word_explanations") or []

        # Per-word issues
        for item in word_explanations:
            if isinstance(item, dict):
                w = item.get("word", "?")
                role = item.get("grammatical_role") or item.get("role")
                if not item.get("meaning"):
                    issues.append(f"Missing meaning for '{w}'")
                if not item.get("color"):
                    issues.append(f"Missing color for '{w}'")
                if role and role not in _VALID_ROLES:
                    issues.append(f"Unknown role '{role}' for '{w}'")
            elif isinstance(item, (list, tuple)):
                if len(item) < 4:
                    issues.append(f"Word entry too short: {item}")
                else:
                    w, role, color, meaning = item[0], item[1], item[2], item[3]
                    if not meaning:
                        issues.append(f"Missing meaning for '{w}'")
                    if not color:
                        issues.append(f"Missing color for '{w}'")
                    if role not in _VALID_ROLES:
                        issues.append(f"Unknown role '{role}' for '{w}'")

        # Portuguese-specific issues
        for item in word_details:
            if not isinstance(item, dict):
                continue
            role = item.get("grammatical_role") or item.get("role") or ""
            if role == "copula" and item.get("copula_type") not in ("ser", "estar"):
                issues.append(
                    f"Copula '{item.get('word')}' missing copula_type"
                )
            if role == "contraction" and not (item.get("contraction_parts") or []):
                issues.append(
                    f"Contraction '{item.get('word')}' missing contraction_parts"
                )
            if role in ("clitic_pronoun", "mesoclitic") and not item.get(
                "clitic_position"
            ):
                issues.append(
                    f"Clitic '{item.get('word')}' missing clitic_position"
                )

        quality_score = max(0.5, 1.0 - 0.04 * len(issues))
        return {
            "issues": issues,
            "quality_score": round(quality_score, 3),
            "recommendations": self._recommendations(issues),
        }

    def _recommendations(self, issues: List[str]) -> List[str]:
        recs: List[str] = []
        if any("copula" in i.lower() for i in issues):
            recs.append(
                "Always tag ser/estar with copula_type to preserve the "
                "essential/transient contrast."
            )
        if any("contraction" in i.lower() for i in issues):
            recs.append(
                "Split obligatory contractions (do, no, ao, pelo, dele, "
                "naquele, daquilo, ...) into preposition + article/pronoun."
            )
        if any("clitic" in i.lower() for i in issues):
            recs.append(
                "Mark clitic_position (proclitic / enclitic / mesoclitic) "
                "for every clitic pronoun."
            )
        if any("missing meaning" in i.lower() for i in issues):
            recs.append(
                "Provide an English meaning + grammatical info for every word."
            )
        if any("unknown role" in i.lower() for i in issues):
            recs.append(
                "Use only the documented Portuguese role labels — "
                "no ad-hoc invented roles."
            )
        if not recs:
            recs.append(
                "Analysis quality looks good. Consider adding more BR/PT "
                "register cues if applicable."
            )
        return recs

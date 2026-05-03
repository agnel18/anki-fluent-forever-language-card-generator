# languages/english/domain/en_validator.py
"""
English Validator — Domain Component

Validates grammar analysis results and returns a confidence score (0.0–1.0).
Target: ≥ 0.85 for production deployment.

Mirrors the Latvian pattern (multi-dimensional confidence scoring +
explanation-quality auditor that penalises stub explanations and missing
English-specific feature mentions).
"""

import logging
from typing import Any, Dict, List

from .en_config import EnConfig

logger = logging.getLogger(__name__)

# Roles that MUST be present for a minimal valid analysis
_REQUIRED_ROLES = {"noun", "verb"}

# Valid English grammatical roles (superset across all complexity levels)
_VALID_ROLES = {
    "noun", "verb", "adjective", "adverb",
    "pronoun", "personal_pronoun", "reflexive_pronoun", "demonstrative",
    "relative_pronoun", "indefinite_pronoun", "interrogative_pronoun",
    "preposition", "conjunction", "subordinating_conjunction",
    "coordinating_conjunction",
    "auxiliary", "modal_verb",
    "article", "determiner", "possessive_determiner", "possessive_pronoun",
    "particle", "phrasal_verb_particle", "phrasal_verb",
    "infinitive_marker", "infinitive", "gerund",
    "present_participle", "past_participle",
    "comparative", "superlative",
    "numeral", "interjection", "other",
}

_VALID_CASES = {
    "nominative", "accusative", "genitive", "genitive_determiner",
    "genitive_pronoun", "reflexive", "",
}

# Roles whose explanation MUST mention an English feature keyword
# (tense / aspect / case / etc.) — these are the inflected / case-bearing words.
_INFLECTED_ROLES = {
    "verb", "auxiliary", "modal_verb",
    "pronoun", "personal_pronoun", "reflexive_pronoun",
    "relative_pronoun", "indefinite_pronoun", "interrogative_pronoun",
    "possessive_determiner", "possessive_pronoun",
    "present_participle", "past_participle", "gerund", "infinitive",
    "comparative", "superlative",
}


class EnValidator:
    """Validates English grammar analysis results."""

    def __init__(self, config: EnConfig):
        self.config = config

    def validate_result(
        self, result: Dict[str, Any], sentence: str
    ) -> Dict[str, Any]:
        """
        Validate and enrich the analysis result.
        Returns the result dict with a 'confidence' key set.

        IMPORTANT: if the analysis carries `is_fallback: True` (set by
        EnFallbacks), confidence is hard-capped at 0.3 regardless of
        explanation quality. This mirrors de_validator.validate_result and
        es_validator.
        """
        if not result or not isinstance(result, dict):
            return {"confidence": 0.0, "word_explanations": []}

        # Hard cap for rule-based fallbacks — explanation quality cannot lift this.
        if result.get("is_fallback", False):
            result["confidence"] = 0.3
            return result

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

        # 4. English-specific: tense/aspect/voice + pronoun-case info present
        #    where applicable.
        scores.append(self._score_english_features(word_explanations))

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
        covered = sum(1 for t in sentence_tokens if t.lower() in explained_words)
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
            if isinstance(item, dict)
            and item.get("role", "").lower() in _VALID_ROLES
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

    def _score_english_features(self, word_explanations: List[Dict]) -> float:
        """Do verb / pronoun entries include tense or case info?"""
        relevant = [
            item for item in word_explanations
            if isinstance(item, dict)
            and item.get("role", "") in {
                "verb", "auxiliary", "modal_verb",
                "pronoun", "personal_pronoun",
                "present_participle", "past_participle",
            }
        ]
        if not relevant:
            return 0.85  # No verbs/pronouns — not penalised
        with_feature = sum(
            1 for item in relevant
            if (item.get("tense", "").strip()
                or item.get("aspect", "").strip()
                or item.get("case", "").strip()
                or item.get("voice", "").strip())
        )
        ratio = with_feature / len(relevant)
        return 0.9 if ratio >= 0.7 else (0.7 if ratio >= 0.4 else 0.5)

    def validate_explanation_quality(
        self, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check explanation quality and return a quality report.

        Penalty factors (multiplicative):
          - Missing meaning / color: -0.1 per issue
          - Invalid role: -0.05 per issue
          - "Stub" explanations (< 20 chars OR meaning equals word OR meaning
            equals "{word} ({role}):") — strong penalty: -0.2 per issue
          - Missing English-feature keywords (tense / aspect / voice / agreement /
            case / inflection / 3sg / past / perfect / progressive / passive /
            subject / object / modifier) on inflected words: -0.05 per issue
        """
        word_explanations = result.get("word_explanations", [])
        issues: List[str] = []
        stub_count = 0
        feature_gap_count = 0

        english_feature_keywords = [
            # tense / aspect / voice
            "tense", "aspect", "voice", "active", "passive",
            "present", "past", "future",
            "simple", "progressive", "perfect", "perfect_progressive", "perfect progressive",
            # agreement / inflection
            "agreement", "agree", "agrees", "inflection", "inflected",
            "3sg", "third-person singular", "third person singular",
            "1sg", "2sg", "1pl", "2pl", "3pl",
            # case
            "case", "nominative", "accusative", "genitive",
            "objective", "subjective", "subject", "object", "predicate",
            # function
            "modifier", "modifies", "modify",
            "complement", "head",
            # English-specific constructions
            "auxiliary", "modal", "phrasal", "infinitive", "gerund",
            "participle", "comparative", "superlative",
            "lemma", "definite", "indefinite",
            # number / person
            "singular", "plural", "person",
        ]

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
            body = (
                meaning[len(stripped_prefix):].strip()
                if meaning.startswith(stripped_prefix)
                else meaning
            )
            if len(body) < 20 or body.lower() == word.lower():
                stub_count += 1
                issues.append(f"Stub explanation for '{word}' (body too short or empty)")
                continue

            # Inflected-word feature check.
            if role in _INFLECTED_ROLES:
                explanation_text = (individual or body).lower()
                if not any(kw in explanation_text for kw in english_feature_keywords):
                    feature_gap_count += 1
                    issues.append(
                        f"Inflected word '{word}' ({role}) — explanation lacks "
                        f"tense/aspect/voice/agreement/case detail"
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

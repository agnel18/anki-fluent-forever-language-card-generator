# languages/english/domain/en_response_parser.py
"""
English Response Parser — Domain Component

5-level fallback parsing strategy:
1. Direct JSON parsing
2. Markdown code-block extraction
3. JSON repair (truncated/malformed)
4. Text pattern extraction
5. Rule-based fallback (delegated to EnFallbacks)
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from .en_config import EnConfig
from .en_fallbacks import EnFallbacks

logger = logging.getLogger(__name__)


class EnResponseParser:
    """Parses AI grammar analysis responses for English."""

    def __init__(self, config: EnConfig, fallbacks: EnFallbacks):
        self.config = config
        self.fallbacks = fallbacks

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_response(
        self,
        ai_response: str,
        complexity: str,
        sentence: str,
        target_word: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Parse a single-sentence AI response with 5-level fallback."""
        if not ai_response or not ai_response.strip():
            logger.warning("Empty AI response — using fallback")
            return self.fallbacks.create_fallback(sentence, complexity)

        parsed = self._try_parse(ai_response)
        if parsed is None:
            logger.warning("All parse levels failed — using fallback")
            return self.fallbacks.create_fallback(sentence, complexity)

        # If the result is a list, take the first item
        if isinstance(parsed, list):
            parsed = parsed[0] if parsed else {}

        return self._normalize(parsed, sentence, complexity)

    def parse_batch_response(
        self,
        ai_response: str,
        sentences: List[str],
        complexity: str,
        target_word: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Parse a batch AI response into per-sentence dicts."""
        if not ai_response or not ai_response.strip():
            logger.warning("Empty batch AI response — using fallbacks")
            return [self.fallbacks.create_fallback(s, complexity) for s in sentences]

        parsed = self._try_parse(ai_response)

        # Normalise to a list. The model may emit either a top-level array,
        # a single object, or a wrapper {"batch_results": [...]} — handle all.
        if isinstance(parsed, dict):
            if "batch_results" in parsed and isinstance(parsed["batch_results"], list):
                parsed = parsed["batch_results"]
            elif "results" in parsed and isinstance(parsed["results"], list):
                parsed = parsed["results"]
            else:
                parsed = [parsed]
        elif not isinstance(parsed, list):
            parsed = None

        if parsed is None:
            logger.warning("Batch parse failed — using fallbacks for all")
            return [self.fallbacks.create_fallback(s, complexity) for s in sentences]

        results = []
        for i, sentence in enumerate(sentences):
            if i < len(parsed):
                item = parsed[i]
                if isinstance(item, dict):
                    results.append(self._normalize(item, sentence, complexity))
                else:
                    results.append(self.fallbacks.create_fallback(sentence, complexity))
            else:
                results.append(self.fallbacks.create_fallback(sentence, complexity))
        return results

    # ------------------------------------------------------------------
    # 5-level parse cascade
    # ------------------------------------------------------------------

    def _try_parse(self, text: str) -> Optional[Any]:
        """Try all parsing levels in order."""
        # Level 1: Direct JSON
        result = self._parse_direct_json(text)
        if result is not None:
            return result

        # Level 2: Markdown code block
        result = self._parse_markdown_json(text)
        if result is not None:
            return result

        # Level 3: JSON repair (truncated)
        result = self._parse_repaired_json(text)
        if result is not None:
            return result

        # Level 4: Text pattern extraction
        result = self._parse_text_patterns(text)
        if result is not None:
            return result

        # Level 5: None — caller delegates to rule-based fallback
        return None

    def _parse_direct_json(self, text: str) -> Optional[Any]:
        """Level 1: Try to parse the entire text as JSON."""
        try:
            return json.loads(text.strip())
        except (json.JSONDecodeError, ValueError):
            return None

    def _parse_markdown_json(self, text: str) -> Optional[Any]:
        """Level 2: Extract JSON from a markdown code block."""
        patterns = [
            r"```json\s*([\s\S]*?)\s*```",
            r"```\s*([\s\S]*?)\s*```",
            r"`([\s\S]*?)`",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                candidate = match.group(1).strip()
                try:
                    return json.loads(candidate)
                except (json.JSONDecodeError, ValueError):
                    continue
        return None

    def _parse_repaired_json(self, text: str) -> Optional[Any]:
        """Level 3: Try to repair truncated JSON by closing open structures.

        Also attempts to fix common issues: trailing commas, smart quotes,
        unterminated strings.
        """
        # Find the first { or [
        start = -1
        for i, ch in enumerate(text):
            if ch in "{[":
                start = i
                break
        if start < 0:
            return None

        candidate = text[start:]

        # Replace smart quotes with straight quotes
        candidate = (
            candidate.replace("“", '"')
            .replace("”", '"')
            .replace("‘", "'")
            .replace("’", "'")
        )
        # Strip trailing commas before } or ]
        candidate = re.sub(r",\s*([}\]])", r"\1", candidate)

        # Try to close truncated JSON
        for suffix in ["", "}", "]", "}]", "}}", "]}", '"}', '"]}', '"}]'] :
            try:
                return json.loads(candidate + suffix)
            except (json.JSONDecodeError, ValueError):
                continue
        return None

    def _parse_text_patterns(self, text: str) -> Optional[Any]:
        """Level 4: Extract word-role pairs from unstructured text."""
        word_explanations = []
        # Look for patterns like: "word" -> role or word: role
        patterns = [
            r'"(\w+)"\s*[-:>]+\s*(\w+)',
            r"(\w+)\s*[-:>]+\s*(noun|verb|adjective|pronoun|adverb|preposition|conjunction|article|auxiliary|modal_verb|particle|determiner)",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for word, role in matches:
                    color = self.config.get_color_for_role(role.lower())
                    word_explanations.append({
                        "word": word,
                        "role": role.lower(),
                        "color": color,
                        "meaning": word,
                    })
                if word_explanations:
                    return {
                        "word_explanations": word_explanations,
                        "overall_structure": "parsed via text patterns",
                        "sentence_structure": "parsed via text patterns",
                        "confidence": 0.4,
                    }
        return None

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def _normalize(
        self, data: Dict[str, Any], sentence: str, complexity: str
    ) -> Dict[str, Any]:
        """Normalise a parsed dict into a consistent structure."""
        if not isinstance(data, dict):
            return self.fallbacks.create_fallback(sentence, complexity)

        # Accept multiple key names: word_explanations / words / analysis
        word_explanations = (
            data.get("word_explanations")
            or data.get("words")
            or data.get("analysis")
            or []
        )
        if not isinstance(word_explanations, list):
            word_explanations = []

        # Normalise each word entry
        normalized_words = []
        for item in word_explanations:
            if not isinstance(item, dict):
                continue
            word = str(item.get("word", "")).strip()
            if not word:
                continue
            role = str(
                item.get("grammatical_role", item.get("role", "other"))
            ).strip().lower()
            # Replace any whitespace inside role with underscores so e.g.
            # "modal verb" -> "modal_verb" (matches color-scheme keys).
            role = re.sub(r"\s+", "_", role)
            color = item.get("color") or self.config.get_color_for_role(role, complexity)

            # Prefer the rich `individual_meaning` field; fall back to `meaning` /
            # `explanation`. Strip a duplicate "{word} ({role}):" prefix if the
            # model added one (avoids double-prefixing in the rendered display).
            raw_individual = str(item.get("individual_meaning", "")).strip()
            raw_meaning = str(
                item.get("meaning", item.get("explanation", ""))
            ).strip()
            explanation = raw_individual or raw_meaning
            if explanation:
                stripped_prefix_pattern = f"{word} ({role}):"
                if explanation.lower().startswith(stripped_prefix_pattern.lower()):
                    explanation = explanation[len(stripped_prefix_pattern):].strip()
                meaning = f"{word} ({role}): {explanation}"
            else:
                meaning = f"{word} ({role}): {word}"

            normalized_words.append({
                "word": word,
                "role": role,
                "color": color,
                "meaning": meaning,
                "individual_meaning": raw_individual or raw_meaning,
                "case": item.get("case", ""),
                "number": item.get("number", ""),
                "tense": item.get("tense", ""),
                "aspect": item.get("aspect", ""),
                "voice": item.get("voice", ""),
                "person": item.get("person", ""),
                "degree": item.get("degree", ""),
                "modality": item.get("modality", ""),
                "syntactic_function": item.get("syntactic_function", ""),
                "is_phrasal_verb_part": bool(item.get("is_phrasal_verb_part", False)),
                "lemma": item.get("lemma", ""),
            })

        # Overall structure — support both key names used by different analyzers
        overall = (
            data.get("overall_structure")
            or data.get("sentence_structure")
            or "English sentence"
        )

        return {
            "word_explanations": normalized_words,
            "overall_structure": overall,
            "sentence_structure": overall,
            "tense_aspect": data.get("tense_aspect", ""),
            "voice": data.get("voice", ""),
            "explanations": {item["word"]: item["meaning"] for item in normalized_words},
            "elements": {item["word"]: item["role"] for item in normalized_words},
            "grammar_notes": data.get("grammar_notes", ""),
            "confidence": float(data.get("confidence", 0.7)),
        }

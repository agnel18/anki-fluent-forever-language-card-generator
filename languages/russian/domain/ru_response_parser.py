# languages/russian/domain/ru_response_parser.py
"""
Russian Response Parser — Domain Component

5-level fallback parsing strategy:
1. Direct JSON parsing
2. Markdown code-block extraction
3. JSON repair (truncated/malformed)
4. Text pattern extraction
5. Rule-based fallback (delegated to RuFallbacks)

The parser preserves `individual_meaning` and formats display as
``f"{word} ({role}): {individual_meaning}"`` (German/Latvian rich-explanation
contract). Duplicate ``"{word} ({role}):"`` prefixes emitted by the AI are
stripped before the canonical prefix is added back.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from .ru_config import RuConfig
from .ru_fallbacks import RuFallbacks

logger = logging.getLogger(__name__)


class RuResponseParser:
    """Parses AI grammar analysis responses for Russian."""

    def __init__(self, config: RuConfig, fallbacks: RuFallbacks):
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
        target_word: str = "",
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
        target_word: str = "",
    ) -> List[Dict[str, Any]]:
        """Parse a batch AI response into per-sentence dicts."""
        if not ai_response or not ai_response.strip():
            logger.warning("Empty batch AI response — using fallbacks")
            return [self.fallbacks.create_fallback(s, complexity) for s in sentences]

        parsed = self._try_parse(ai_response)

        # Ensure we have a list. A single-object response covering one
        # sentence is treated as a length-1 batch.
        if isinstance(parsed, dict):
            # If the dict already contains a `batch_results` or `results`
            # key, unwrap it.
            for key in ("batch_results", "results", "sentences"):
                if isinstance(parsed.get(key), list):
                    parsed = parsed[key]
                    break
            else:
                parsed = [parsed]
        elif not isinstance(parsed, list):
            parsed = None

        if parsed is None:
            logger.warning("Batch parse failed — using fallbacks for all")
            return [self.fallbacks.create_fallback(s, complexity) for s in sentences]

        results = []
        for i, sentence in enumerate(sentences):
            if i < len(parsed) and isinstance(parsed[i], dict):
                results.append(self._normalize(parsed[i], sentence, complexity))
            else:
                results.append(self.fallbacks.create_fallback(sentence, complexity))
        return results

    # ------------------------------------------------------------------
    # 5-level parse cascade
    # ------------------------------------------------------------------

    def _try_parse(self, text: str) -> Optional[Any]:
        """Try all 5 parsing levels in order."""
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

        # Level 5: None — caller uses rule-based fallback
        return None

    def _parse_direct_json(self, text: str) -> Optional[Any]:
        """Level 1: Try to parse the entire text as JSON."""
        try:
            return json.loads(text.strip())
        except (json.JSONDecodeError, ValueError):
            return None

    # Public-name aliases (required by stub method signatures)
    def _parse_json_direct(self, response: str) -> Optional[Dict]:
        return self._parse_direct_json(response)

    def _parse_markdown_code_block(self, response: str) -> Optional[Dict]:
        return self._parse_markdown_json(response)

    def _repair_and_parse(self, response: str) -> Optional[Dict]:
        return self._parse_repaired_json(response)

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
        """Level 3: Try to repair truncated JSON by closing open structures."""
        # Find the first { or [
        start = -1
        for i, ch in enumerate(text):
            if ch in "{[":
                start = i
                break
        if start < 0:
            return None

        candidate = text[start:]
        # Try to close truncated JSON with various combinations of closers.
        for suffix in ["", "}", "]", "}}", "]]", "}]", "]}", "\"}}", "\"]}"]:
            try:
                return json.loads(candidate + suffix)
            except (json.JSONDecodeError, ValueError):
                continue
        return None

    def _parse_text_patterns(self, text: str) -> Optional[Any]:
        """Level 4: Extract word-role pairs from unstructured text.

        Recognises Cyrillic word characters (a-z, А-Я, а-я, ё, Ё).
        """
        word_explanations = []
        word_class = r"[A-Za-zА-Яа-яЁё]+"
        patterns = [
            rf'"({word_class})"\s*[-:>]+\s*({word_class})',
            rf"({word_class})\s*[-:>]+\s*(noun|verb|adjective|pronoun|adverb|preposition|conjunction|particle|numeral|interjection)",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.UNICODE)
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

        word_explanations = data.get("word_explanations") or data.get("words") or []
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
            ).strip().lower().replace(" ", "_")
            color = item.get("color") or self.config.get_color_for_role(role, complexity)

            # Prefer the rich `individual_meaning` field; fall back to other
            # fields for legacy responses. Format display string as
            # "{word} ({role}): {explanation}" — German/Latvian rich-explanation
            # contract.
            raw_individual = str(
                item.get("individual_meaning", "")
                or item.get("explanation", "")
            ).strip()
            raw_meaning = str(item.get("meaning", "")).strip()
            explanation = raw_individual or raw_meaning

            if explanation:
                # Strip "{word} ({role}):" prefix (case-insensitive) that the
                # model may have added itself, to avoid double-prefixing.
                lower_exp = explanation.lower()
                for candidate_role in (role, item.get("grammatical_role", "")):
                    if not candidate_role:
                        continue
                    prefix = f"{word} ({candidate_role}):".lower()
                    if lower_exp.startswith(prefix):
                        explanation = explanation[len(prefix):].strip()
                        break
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
                "gender": item.get("gender", ""),
                "number": item.get("number", ""),
                "animacy": item.get("animacy", ""),
                "aspect": item.get("aspect", ""),
                "tense": item.get("tense", ""),
                "person": item.get("person", ""),
                "mood": item.get("mood", ""),
                "voice": item.get("voice", ""),
                "governed_case": item.get("governed_case", ""),
                "lemma": item.get("lemma", ""),
            })

        # Overall structure — support both key names used by different analyzers
        overall = (
            data.get("overall_structure")
            or data.get("sentence_structure")
            or "Russian sentence"
        )

        return {
            "word_explanations": normalized_words,
            "overall_structure": overall,
            "sentence_structure": overall,
            "explanations": {
                item["word"]: item["meaning"] for item in normalized_words
            },
            "elements": {item["word"]: item["role"] for item in normalized_words},
            "grammar_notes": data.get("grammar_notes", ""),
            "confidence": float(data.get("confidence", 0.7)),
        }

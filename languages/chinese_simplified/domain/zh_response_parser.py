# languages/chinese_simplified/domain/zh_response_parser.py
"""
Chinese Simplified Response Parser - Domain Component

CHINESE RESPONSE PARSING:
This component demonstrates robust AI response handling with comprehensive fallbacks.
It parses JSON responses, applies transformations, and provides graceful error recovery.

RESPONSIBILITIES:
1. Parse AI JSON responses with error handling
2. Apply fallbacks when parsing fails
3. Transform data to standard internal format
4. Handle batch responses with per-item fallbacks
5. Extract and clean JSON from markdown-formatted responses

FALLBACK HIERARCHY:
1. Primary: Successful AI parsing and transformation
2. Secondary: Pattern-based parsing with partial recovery
3. Tertiary: Rule-based fallbacks using Chinese patterns
4. Quaternary: Basic character-splitting fallbacks

USAGE FOR CHINESE:
1. Copy parsing logic structure
2. Update JSON field mappings for Chinese-specific roles
3. Implement Chinese-appropriate fallback patterns
4. Test with various AI response formats (clean JSON, markdown, errors)
5. Ensure fallbacks maintain reasonable quality

INTEGRATION:
- Called by main analyzer after AI calls
- Uses fallbacks component for error recovery
- Transforms to standard format expected by validator
- Maintains sentence correspondence in batch processing
"""

import json
import logging
from typing import List, Dict, Any, Optional
from .zh_config import ZhConfig
from .zh_fallbacks import ZhFallbacks

logger = logging.getLogger(__name__)

from .zh_types import ParseResult, ParsedSentence, ParsedWord

class ZhResponseParser:
    """
    Parses AI responses, cleans data, and applies fallbacks.
    Uses dataclasses for type safety and stricter schema validation.
    """
    def __init__(self, config: ZhConfig):
        self.config: ZhConfig = config
        self.fallbacks = ZhFallbacks(config)

    def parse_response(self, ai_response: str, complexity: str, sentence: str, target_word: Optional[str] = None) -> ParseResult:
        logger.info(f"DEBUG: Raw AI response for sentence '{sentence}': {ai_response[:500]}")
        try:
            json_data = self._extract_json(ai_response)
            if isinstance(json_data, dict) and json_data.get('sentence') == 'error':
                raise ValueError("AI returned error response")
            return self._transform_to_standard_format(json_data, complexity, target_word)
        except Exception as e:
            logger.warning(f"Parsing failed for sentence '{sentence}': {e}")
            fallback = self.fallbacks.create_fallback(sentence, complexity)
            return ParseResult(sentences=[], success=False, error_message=str(e), fallback_used=True)

    def parse_batch_response(self, ai_response: str, sentences: List[str], complexity: str, target_word: Optional[str] = None) -> ParseResult:
        logger.info(f"DEBUG: Raw AI batch response: {ai_response[:1000]}")
        try:
            json_data = self._extract_json(ai_response)
            if isinstance(json_data, dict) and json_data.get('sentence') == 'error':
                raise ValueError("AI returned error response")
            if isinstance(json_data, list):
                batch_results = json_data
            else:
                batch_results = json_data.get('batch_results', [])
            if not batch_results:
                raise ValueError("No valid batch results in AI response")
            parsed_sentences = []
            for i, item in enumerate(batch_results):
                if i < len(sentences):
                    try:
                        parsed = self._transform_to_standard_format(item, complexity, target_word)
                        if parsed.sentences:
                            parsed_sentences.extend(parsed.sentences)
                    except Exception as e:
                        logger.warning(f"Batch item {i} failed: {e}")
            return ParseResult(sentences=parsed_sentences, success=True)
        except Exception as e:
            logger.error(f"Batch parsing failed: {e}")
            return ParseResult(sentences=[], success=False, error_message=str(e), fallback_used=True)

    def _extract_json(self, response: str) -> Dict[str, Any]:
        logger.info(f"DEBUG: Extracting JSON from response: {response[:1000]}...")
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```" )[0].strip()
            elif "```" in response:
                response = response.split("```" )[1].split("```" )[0].strip()
            logger.info(f"DEBUG: Cleaned response: {response[:1000]}...")
            result = json.loads(response)
            logger.info(f"DEBUG: Parsed JSON: {result}")
            return result
        except Exception as e:
            logger.error(f"DEBUG: Failed to extract JSON from response: {e}")
            logger.error(f"DEBUG: Response that failed: {response}")
            raise

    def _transform_to_standard_format(self, data: Dict[str, Any], complexity: str, target_word: Optional[str] = None) -> ParseResult:
        # Try to extract detailed explanations from a block ("Grammar Explanations:")
        explanations_block = None
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, str) and v.strip().startswith("Grammar Explanations:"):
                    explanations_block = v.strip()
                    break
        if explanations_block is None and isinstance(data, str) and data.strip().startswith("Grammar Explanations:"):
            explanations_block = data.strip()

        explanations_map = {}
        if explanations_block:
            # Parse lines like: 你 (pronoun): A second-person singular pronoun, meaning 'you'. ...
            for line in explanations_block.splitlines():
                line = line.strip()
                if not line or ":" not in line or "(" not in line or ")" not in line:
                    continue
                try:
                    word_part, rest = line.split("(", 1)
                    word = word_part.strip()
                    pos_and_expl = rest.split("):", 1)
                    if len(pos_and_expl) != 2:
                        continue
                    pos = pos_and_expl[0].strip()
                    explanation = pos_and_expl[1].strip()
                    explanations_map[word] = (pos, explanation)
                except Exception:
                    continue

        words = data.get('words', [])
        parsed_words = []
        colors = self._get_color_scheme(complexity)
        for word_data in words:
            word = word_data.get('word', '')
            raw_role = (word_data.get('grammatical_role') or word_data.get('role') or 'other')
            # Always define standard_role
            if target_word and word == target_word:
                standard_role = 'target_word'
            else:
                role_map = {
                    "Pronoun": "pronoun",
                    "Adverb": "adverb",
                    "Verb": "verb",
                    "Adjective": "adjective",
                    "Noun": "noun",
                    "Structural particle": "structural_particle",
                    "Modal particle": "modal_particle",
                    "Particle": "particle",
                    "Classifier": "classifier",
                    "Aspect marker": "aspect_marker",
                    "Interrogative pronoun": "pronoun",
                    "Demonstrative pronoun": "pronoun",
                    "Personal pronoun": "pronoun",
                }
                normalized = role_map.get(raw_role.strip(), raw_role.lower().replace(" ", "_").replace("-", "_"))
                standard_role = self.config.grammatical_roles.get(normalized, normalized)
            # Prefer detailed explanation from explanations_map if available
            explanation = None
            if word in explanations_map:
                pos, detailed_expl = explanations_map[word]
                explanation = detailed_expl
            else:
                explanation = word_data.get('individual_meaning')
                if not explanation or str(explanation).strip() in ("", standard_role):
                    explanations_dict = data.get('explanations', {})
                    explanation = (
                        explanations_dict.get(word) or
                        explanations_dict.get('explanation') or
                        explanations_dict.get('overall_structure') or
                        standard_role
                    )
                else:
                    explanation = str(explanation).strip()
            parsed_words.append(ParsedWord(word=word, grammatical_role=standard_role, individual_meaning=explanation))
        parsed_sentence = ParsedSentence(
            sentence=data.get('sentence', ''),
            words=parsed_words,
            overall_structure=data.get('explanations', {}).get('overall_structure', ''),
            key_features=data.get('explanations', {}).get('key_features', ''),
            confidence=1.0
        )
        return ParseResult(sentences=[parsed_sentence], success=True)
    def _get_color_scheme(self, complexity: str) -> Dict[str, str]:
        return self.config.get_color_scheme(complexity)

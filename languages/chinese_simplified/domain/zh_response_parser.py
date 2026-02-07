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
from typing import List, Dict, Any
from .zh_config import ZhConfig
from .zh_fallbacks import ZhFallbacks

logger = logging.getLogger(__name__)

class ZhResponseParser:
    """
    Parses AI responses, cleans data, and applies fallbacks.

    CHINESE PARSING STRATEGY:
    - JSON extraction: Handle various response formats (clean, markdown, malformed)
    - Error detection: Identify and handle AI error responses
    - Batch processing: Parse multiple results with individual fallbacks
    - Data transformation: Convert to internal standard format
    - Fallback integration: Seamless degradation when parsing fails

    PARSING ROBUSTNESS:
    - Multiple JSON extraction methods (direct, markdown, cleaned)
    - Per-item validation in batch processing
    - Meaningful error logging for debugging
    - Consistent output format regardless of success/failure
    """

    def __init__(self, config: ZhConfig):
        """
        Initialize parser with configuration and fallbacks.

        DEPENDENCY INJECTION:
        1. Config provides role mappings and validation rules
        2. Fallbacks component provides error recovery
        3. Maintains separation of concerns
        4. Enables testing with mock components
        """
        self.config = config
        self.fallbacks = ZhFallbacks(config)

    def parse_response(self, ai_response: str, complexity: str, sentence: str, target_word: str = None) -> Dict[str, Any]:
        """Parse single response with fallbacks."""
        logger.info(f"DEBUG: Raw AI response for sentence '{sentence}': {ai_response[:500]}")
        try:
            json_data = self._extract_json(ai_response)

            # Check if this looks like an error response
            if isinstance(json_data, dict) and json_data.get('sentence') == 'error':
                raise ValueError("AI returned error response")

            return self._transform_to_standard_format(json_data, complexity, target_word)
        except Exception as e:
            logger.warning(f"Parsing failed for sentence '{sentence}': {e}")
            return self.fallbacks.create_fallback(sentence, complexity)

    def parse_batch_response(self, ai_response: str, sentences: List[str], complexity: str, target_word: str = None) -> List[Dict[str, Any]]:
        """Parse batch response with per-result fallbacks."""
        logger.info(f"DEBUG: Raw AI batch response: {ai_response[:1000]}")
        try:
            json_data = self._extract_json(ai_response)

            # Check if this looks like an error response
            if isinstance(json_data, dict) and json_data.get('sentence') == 'error':
                raise ValueError("AI returned error response")

            if isinstance(json_data, list):
                batch_results = json_data
            else:
                batch_results = json_data.get('batch_results', [])

            # If no valid batch results, treat as error
            if not batch_results:
                raise ValueError("No valid batch results in AI response")

            results = []
            for i, item in enumerate(batch_results):
                if i < len(sentences):
                    try:
                        parsed = self._transform_to_standard_format(item, complexity, target_word)
                        results.append(parsed)
                    except Exception as e:
                        logger.warning(f"Batch item {i} failed: {e}")
                        results.append(self.fallbacks.create_fallback(sentences[i], complexity))
                else:
                    results.append(self.fallbacks.create_fallback(sentences[i], complexity))

            # If we don't have results for all sentences, add fallbacks
            while len(results) < len(sentences):
                results.append(self.fallbacks.create_fallback(sentences[len(results)], complexity))

            return results
        except Exception as e:
            logger.error(f"Batch parsing failed: {e}")
            return [self.fallbacks.create_fallback(s, complexity) for s in sentences]

    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Extract JSON from AI response."""
        logger.info(f"DEBUG: Extracting JSON from response: {response[:1000]}...")
        try:
            # Strip markdown if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            logger.info(f"DEBUG: Cleaned response: {response[:1000]}...")
            result = json.loads(response)
            logger.info(f"DEBUG: Parsed JSON: {result}")
            return result
        except Exception as e:
            logger.error(f"DEBUG: Failed to extract JSON from response: {e}")
            logger.error(f"DEBUG: Response that failed: {response}")
            raise

    def _transform_to_standard_format(self, data: Dict[str, Any], complexity: str, target_word: str = None) -> Dict[str, Any]:
        """Transform parsed data to standard format."""
        # Simplified: apply role mapping, etc. from config
        words = data.get('words', [])
        elements = {}
        word_explanations = []
        colors = self._get_color_scheme(complexity)

        for word_data in words:
            word = word_data.get('word', '')
            role = word_data.get('grammatical_role', 'other')
            if target_word and word == target_word:
                role = 'target_word'
            # Map role using config
            standard_role = self.config.grammatical_roles.get(role, role)
            color = colors.get(standard_role, '#AAAAAA')
            explanation = word_data.get('individual_meaning', standard_role)
            word_explanations.append([word, standard_role, color, explanation])

            if standard_role not in elements:
                elements[standard_role] = []
            elements[standard_role].append(word_data)

        return {
            'sentence': data.get('sentence', ''),
            'elements': elements,
            'explanations': data.get('explanations', {}),
            'word_explanations': word_explanations
        }

    def _get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Get color scheme based on complexity."""
        return self.config.get_color_scheme(complexity)

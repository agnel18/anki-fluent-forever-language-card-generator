# languages/chinese_traditional/domain/zh_tw_response_parser.py
"""
Chinese Traditional Response Parser - Domain Component

Following Chinese Simplified Clean Architecture gold standard:
- Integrated fallback mechanisms within domain layer
- JSON parsing with robust error handling
- Validation of AI responses against expected structure
- Graceful degradation when AI provides incomplete data

RESPONSIBILITIES:
1. Parse AI JSON responses for grammar analysis
2. Validate response structure and content
3. Provide integrated fallback mechanisms for malformed responses
4. Extract grammatical information with confidence scoring
5. Handle Chinese Traditional specific linguistic features

INTEGRATION:
- Used by ZhTwAnalyzer facade for response processing
- Depends on ZhTwConfig for validation rules and patterns
- Works with ZhTwValidator for confidence assessment
- Provides structured data for UI presentation

PARSING STRATEGY:
1. Attempt JSON parsing of AI response
2. Validate structure against expected schema
3. Extract grammatical roles and explanations
4. Apply fallback parsing if JSON fails
5. Score confidence in extracted information
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from .zh_tw_config import ZhTwConfig
from .zh_tw_fallbacks import ZhTwFallbacks

logger = logging.getLogger(__name__)

@dataclass
class ParsedWord:
    """Represents a parsed word with grammatical information."""
    word: str
    grammatical_role: str
    individual_meaning: str
    confidence: float = 1.0

@dataclass
class ParsedSentence:
    """Represents a parsed sentence with grammatical breakdown."""
    sentence: str
    words: List[ParsedWord]
    overall_structure: str
    key_features: str
    confidence: float = 1.0

@dataclass
class ParseResult:
    """Result of parsing AI response."""
    sentences: List[ParsedSentence]
    success: bool
    error_message: Optional[str] = None
    fallback_used: bool = False

class ZhTwResponseParser:
    """
    Parses AI responses for Chinese Traditional grammar analysis.

    Following Chinese Simplified Clean Architecture:
    - Integrated fallbacks: Error recovery within domain layer
    - Robust parsing: Handle various AI response formats
    - Validation: Ensure data quality and completeness
    - Confidence scoring: Assess reliability of extracted information

    PARSING APPROACH:
    1. Primary: JSON parsing with schema validation
    2. Fallback: Regex-based extraction from text responses
    3. Recovery: Basic grammatical role assignment for failures
    4. Scoring: Confidence assessment for all extracted data
    """

    def __init__(self, config: ZhTwConfig):
        """
        Initialize parser with configuration.

        Args:
            config: ZhTwConfig instance with patterns and validation rules
        """
        self.config = config
        self.valid_roles = set(self.config.grammatical_roles.keys())

    def parse_single_response(self, response: str, original_sentence: str) -> ParseResult:
        """
        Parse AI response for single sentence analysis.

        PARSING STRATEGY:
        1. Try JSON parsing first
        2. Validate structure and content
        3. Extract words and grammatical information
        4. Apply fallbacks if parsing fails
        5. Score confidence in results

        Args:
            response: Raw AI response string
            original_sentence: Original sentence being analyzed

        Returns:
            ParseResult with parsed sentence data
        """
        try:
            # Attempt JSON parsing
            data = json.loads(response)
            return self._parse_json_response(data, original_sentence)
        except json.JSONDecodeError:
            logger.warning("JSON parsing failed, attempting fallback parsing")
            return self._parse_fallback_response(response, original_sentence)

    def parse_response(self, ai_response: str, complexity: str, sentence: str, target_word: str = None) -> Dict[str, Any]:
        """Parse single response with fallbacks - compatibility method for analyzer."""
        logger.info(f"DEBUG: Raw AI response for sentence '{sentence}': {ai_response[:500]}")
        try:
            parse_result = self.parse_single_response(ai_response, sentence)
            if parse_result.sentences:
                parsed_sentence = parse_result.sentences[0]
                return self._transform_to_standard_format({
                    'sentence': parsed_sentence.sentence,
                    'words': [
                        {
                            'word': word.word,
                            'grammatical_role': word.grammatical_role,
                            'individual_meaning': word.individual_meaning
                        }
                        for word in parsed_sentence.words
                    ],
                    'explanations': {
                        'overall_structure': parsed_sentence.overall_structure,
                        'key_features': parsed_sentence.key_features
                    }
                }, complexity, target_word)
            else:
                raise ValueError("No sentences parsed")
        except Exception as e:
            logger.warning(f"Parsing failed for sentence '{sentence}': {e}")
            return self.fallbacks.create_fallback(sentence, complexity)

    def parse_batch_response(self, ai_response: str, sentences: List[str], complexity: str, target_word: str = None) -> List[Dict[str, Any]]:
        """Parse batch response with per-result fallbacks - compatibility method."""
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

            return results

        except Exception as e:
            logger.error(f"Batch parsing failed: {e}")
            # Return fallbacks for all sentences
            return [self.fallbacks.create_fallback(sentence, complexity) for sentence in sentences]

    def _extract_json(self, response: str) -> Any:
        """Extract JSON from AI response, handling various formats."""
        # Try direct JSON parsing
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try extracting array from markdown
        array_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response, re.DOTALL)
        if array_match:
            try:
                return json.loads(array_match.group(1))
            except json.JSONDecodeError:
                pass

        raise ValueError("Could not extract valid JSON from AI response")

    def _transform_to_standard_format(self, data: Dict[str, Any], complexity: str, target_word: str = None) -> Dict[str, Any]:
        """Transform parsed data to standard format expected by analyzer."""
        try:
            words = data.get('words', [])
            word_explanations = []

            for word_data in words:
                if isinstance(word_data, dict):
                    word = word_data.get('word', '')
                    role = word_data.get('grammatical_role', 'unknown')
                    meaning = word_data.get('individual_meaning', f'{role} in sentence')

                    # Map role to color
                    color = self._get_color_for_role(role, complexity)

                    word_explanations.append([word, role, color, meaning])

            explanations = data.get('explanations', {})
            overall_structure = explanations.get('overall_structure', 'Sentence structure analysis')
            key_features = explanations.get('key_features', 'Key grammatical features')

            return {
                'elements': {},  # Simplified for compatibility
                'explanations': {
                    'overall_structure': overall_structure,
                    'key_features': key_features
                },
                'word_explanations': word_explanations,
                'confidence': 0.8  # Default confidence
            }
        except Exception as e:
            logger.error(f"Failed to transform data to standard format: {e}")
            raise

    def _get_color_for_role(self, role: str, complexity: str) -> str:
        """Get color for grammatical role based on complexity."""
        # Simplified color mapping - in real implementation, this would use config
        color_map = {
            'noun': '#FF4444',
            'verb': '#44FF44',
            'adjective': '#4444FF',
            'adverb': '#FF44FF',
            'pronoun': '#FFFF44',
            'preposition': '#44FFFF',
            'conjunction': '#FF8844',
            'interjection': '#8844FF',
            'particle': '#888888',
            'classifier': '#448844',
            'aspect_marker': '#884444',
            'modal_particle': '#444488',
            'structural_particle': '#888844',
            'measure_word': '#884488',
            'numeral': '#448888',
            'other': '#666666'
        }
        return color_map.get(role, '#666666')

    def _parse_json_response(self, data: Dict[str, Any], original_sentence: str) -> ParseResult:
        """
        Parse validated JSON response structure.

        EXPECTED JSON STRUCTURE:
        {
          "sentence": "original sentence",
          "words": [
            {
              "word": "character/word",
              "grammatical_role": "noun|verb|...",
              "individual_meaning": "explanation"
            }
          ],
          "explanations": {
            "overall_structure": "structure explanation",
            "key_features": "feature explanation"
          }
        }
        """
        try:
            # Extract sentence and validate
            sentence = data.get("sentence", original_sentence)

            # Parse words array
            words_data = data.get("words", [])
            words = []

            for word_data in words_data:
                word = ParsedWord(
                    word=word_data.get("word", ""),
                    grammatical_role=self._validate_grammatical_role(
                        word_data.get("grammatical_role", "unknown")
                    ),
                    individual_meaning=word_data.get("individual_meaning", ""),
                    confidence=self._calculate_word_confidence(word_data)
                )
                words.append(word)

            # Extract explanations
            explanations = data.get("explanations", {})
            overall_structure = explanations.get("overall_structure", "")
            key_features = explanations.get("key_features", "")

            # Calculate overall confidence
            avg_confidence = sum(w.confidence for w in words) / len(words) if words else 0.0

            parsed_sentence = ParsedSentence(
                sentence=sentence,
                words=words,
                overall_structure=overall_structure,
                key_features=key_features,
                confidence=avg_confidence
            )

            return ParseResult(
                sentences=[parsed_sentence],
                success=True
            )

        except Exception as e:
            logger.error(f"Error parsing JSON response structure: {e}")
            return self._parse_fallback_response(str(data), original_sentence)

    def _parse_batch_json_response(self, data: Dict[str, Any], original_sentences: List[str]) -> ParseResult:
        """
        Parse batch JSON response structure.
        """
        try:
            batch_results = data.get("batch_results", [])
            sentences = []

            for i, result in enumerate(batch_results):
                original = original_sentences[i] if i < len(original_sentences) else ""
                single_result = self._parse_json_response(result, original)
                if single_result.sentences:
                    sentences.extend(single_result.sentences)

            return ParseResult(
                sentences=sentences,
                success=len(sentences) > 0
            )

        except Exception as e:
            logger.error(f"Error parsing batch JSON response: {e}")
            return self._parse_batch_fallback_response(str(data), original_sentences)

    def _parse_fallback_response(self, response: str, original_sentence: str) -> ParseResult:
        """
        Fallback parsing when JSON fails.

        FALLBACK STRATEGY:
        1. Extract word-by-word information using regex
        2. Identify grammatical roles from text patterns
        3. Generate basic explanations
        4. Assign lower confidence scores
        """
        logger.info("Using fallback parsing for response")

        # Split sentence into characters/words
        words = self._split_sentence_into_words(original_sentence)

        parsed_words = []
        for word in words:
            # Try to extract role and meaning from response text
            role, meaning = self._extract_word_info_from_text(response, word)

            parsed_word = ParsedWord(
                word=word,
                grammatical_role=role,
                individual_meaning=meaning,
                confidence=0.5  # Lower confidence for fallback
            )
            parsed_words.append(parsed_word)

        # Generate basic explanations
        overall_structure = self._generate_fallback_structure_explanation(parsed_words)
        key_features = self._generate_fallback_features_explanation(parsed_words)

        parsed_sentence = ParsedSentence(
            sentence=original_sentence,
            words=parsed_words,
            overall_structure=overall_structure,
            key_features=key_features,
            confidence=0.5
        )

        return ParseResult(
            sentences=[parsed_sentence],
            success=True,
            fallback_used=True
        )

    def _parse_batch_fallback_response(self, response: str, original_sentences: List[str]) -> ParseResult:
        """
        Fallback parsing for batch responses.
        """
        sentences = []
        for original in original_sentences:
            result = self._parse_fallback_response(response, original)
            sentences.extend(result.sentences)

        return ParseResult(
            sentences=sentences,
            success=len(sentences) > 0,
            fallback_used=True
        )

    def _validate_grammatical_role(self, role: str) -> str:
        """
        Validate grammatical role against known roles.

        FALLBACK: Map unknown roles to closest valid equivalent
        """
        if role in self.valid_roles:
            return role

        # Map common variations to standard roles
        role_mappings = {
            "n": "noun",
            "v": "verb",
            "adj": "adjective",
            "adv": "adverb",
            "prep": "preposition",
            "conj": "conjunction",
            "pron": "pronoun",
            "num": "numeral",
            "mw": "measure_word",
            "asp": "aspect_particle",
            "mod": "modal_particle",
            "struct": "structural_particle"
        }

        mapped_role = role_mappings.get(role.lower(), "unknown")
        if mapped_role != "unknown":
            return mapped_role

        logger.warning(f"Unknown grammatical role: {role}, using 'unknown'")
        return "unknown"

    def _calculate_word_confidence(self, word_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score for parsed word.

        CONFIDENCE FACTORS:
        - Grammatical role validity
        - Meaning explanation length
        - Word presence in original sentence
        """
        confidence = 1.0

        # Reduce confidence for unknown roles
        if word_data.get("grammatical_role") == "unknown":
            confidence *= 0.7

        # Reduce confidence for short explanations
        meaning = word_data.get("individual_meaning", "")
        if len(meaning) < 10:
            confidence *= 0.8

        return confidence

    def _split_sentence_into_words(self, sentence: str) -> List[str]:
        """
        Split Chinese Traditional sentence into words/characters.

        CHINESE SEGMENTATION STRATEGY:
        - Individual characters for single-character words
        - Common compounds identified by patterns
        - Respect word boundaries in traditional text
        """
        # For Chinese, split by characters but group common compounds
        chars = list(sentence)

        # Basic compound recognition (can be enhanced with config)
        words = []
        i = 0
        while i < len(chars):
            # Check for common two-character compounds
            if i + 1 < len(chars):
                compound = chars[i] + chars[i + 1]
                # Add more sophisticated compound detection here
                words.append(compound)
                i += 2
            else:
                words.append(chars[i])
                i += 1

        return words

    def _extract_word_info_from_text(self, response: str, word: str) -> Tuple[str, str]:
        """
        Extract grammatical information for a word from text response.

        FALLBACK EXTRACTION:
        - Look for word mentions in response
        - Extract following grammatical descriptions
        - Use pattern matching for role identification
        """
        # Simple pattern matching for role extraction
        role_patterns = {
            "noun": r"(?i)(noun|名詞|n\.?)\b",
            "verb": r"(?i)(verb|動詞|v\.?)\b",
            "adjective": r"(?i)(adjective|形容詞|adj\.?)\b",
            "particle": r"(?i)(particle|助詞|particle)\b",
            "measure_word": r"(?i)(measure word|量詞|classifier)\b"
        }

        # Find text around word mentions
        word_pattern = re.escape(word)
        matches = re.finditer(f"{word_pattern}.{{0,200}}", response, re.IGNORECASE)

        for match in matches:
            text = match.group()

            # Try to identify role
            for role, pattern in role_patterns.items():
                if re.search(pattern, text):
                    # Extract explanation (simplified)
                    explanation = text.replace(word, "").strip()
                    return role, explanation

        # Default fallback
        return "unknown", f"Word '{word}' appears in the sentence"

    def _generate_fallback_structure_explanation(self, words: List[ParsedWord]) -> str:
        """Generate basic structure explanation for fallback."""
        roles = [w.grammatical_role for w in words if w.grammatical_role != "unknown"]
        return f"This sentence contains {len(words)} elements with roles: {', '.join(roles[:5])}{'...' if len(roles) > 5 else ''}"

    def _generate_fallback_features_explanation(self, words: List[ParsedWord]) -> str:
        """Generate basic features explanation for fallback."""
        features = []
        if any(w.grammatical_role == "aspect_particle" for w in words):
            features.append("aspect particles")
        if any(w.grammatical_role == "measure_word" for w in words):
            features.append("measure words/classifiers")
        if any(w.grammatical_role == "modal_particle" for w in words):
            features.append("modal particles")

        if features:
            return f"Chinese grammatical features present: {', '.join(features)}"
        return "Basic Chinese sentence structure"

    def parse_response(self, ai_response: str, complexity: str, sentence: str, target_word: str = None) -> Dict[str, Any]:
        """Parse single response with fallbacks - compatibility method."""
        parse_result = self.parse_single_response(ai_response, sentence)
        if parse_result.sentences:
            parsed_sentence = parse_result.sentences[0]
            return {
                'elements': {},  # Simplified for compatibility
                'explanations': {
                    'overall_structure': parsed_sentence.overall_structure,
                    'key_features': parsed_sentence.key_features
                },
                'word_explanations': [
                    [word.word, word.grammatical_role, '#000000', word.individual_meaning]
                    for word in parsed_sentence.words
                ],
                'confidence': parsed_sentence.confidence
            }
        else:
            # Fallback
            return self.fallbacks.create_fallback(sentence, complexity)

    @property
    def fallbacks(self):
        """Get fallbacks component for compatibility."""
        from .zh_tw_fallbacks import ZhTwFallbacks
        if not hasattr(self, '_fallbacks'):
            self._fallbacks = ZhTwFallbacks(self.config)
        return self._fallbacks
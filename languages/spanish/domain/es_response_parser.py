# Spanish Response Parser
# Handles AI response parsing for Spanish grammar analysis
# Robust JSON extraction with Spanish-specific fallbacks

import json
import logging
import re
from typing import Dict, List, Any, Optional
from .es_config import EsConfig

logger = logging.getLogger(__name__)

class EsResponseParser:
    """
    Parses AI responses for Spanish analysis with robust JSON extraction.
    Handles Spanish-specific linguistic patterns and provides fallbacks.
    """

    def __init__(self, config: EsConfig):
        self.config = config

    def parse_response(self, ai_response: str, complexity: str, sentence: str, target_word: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse and validate AI response with robust JSON extraction.
        Spanish-specific handling for agreement, conjugation, etc.
        """
        try:
            logger.info(f"Parsing Spanish response for sentence: {sentence}")

            # Robust JSON extraction - handles markdown blocks, explanatory text, etc.
            json_data = self._extract_json(ai_response)
            if not json_data:
                logger.warning("No JSON found in response, using fallback")
                return self._create_fallback_analysis(sentence, complexity, target_word)

            # Basic validation
            if 'words' not in json_data and 'batch_results' not in json_data:
                logger.warning("No word explanations found, using fallback")
                return self._create_fallback_analysis(sentence, complexity, target_word)

            # Validate Spanish-specific patterns
            validated_data = self._validate_spanish_patterns(json_data, sentence)

            logger.info(f"Successfully parsed Spanish response with {len(validated_data.get('words', []))} words")
            return validated_data

        except Exception as e:
            logger.error(f"Error parsing Spanish response: {e}")
            return self._create_fallback_analysis(sentence, complexity, target_word)

    def _extract_json(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from AI response with ROBUST MULTIPLE FALLBACK METHODS - GOLD STANDARD PATTERN"""
        try:
            cleaned_response = ai_response.strip()

            # Method 1: Direct parsing if starts with JSON (like gold standards)
            if cleaned_response.startswith(('{', '[')):
                return json.loads(cleaned_response)

            # Method 2: Extract from markdown code blocks (like Hindi parser)
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_response, re.DOTALL | re.IGNORECASE)
            if json_match:
                return json.loads(json_match.group(1))

            # Method 3: Extract JSON between curly braces (like Arabic parser)
            brace_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if brace_match:
                return json.loads(brace_match.group(0))

            # Method 4: Try entire response as fallback
            return json.loads(cleaned_response)

        except json.JSONDecodeError as e:
            logger.warning(f"JSON extraction failed: {e}")
            return None

    def _validate_spanish_patterns(self, data: Dict[str, Any], original_sentence: str) -> Dict[str, Any]:
        """Validate Spanish-specific linguistic patterns and create elements structure - ENHANCED with uniqueness validation like Arabic gold standard"""
        validated_data = dict(data)  # Copy the original

        if 'words' in data:
            words_data = data['words']

            # ENHANCED: Validate uniqueness of meanings (like Arabic gold standard)
            meanings = []
            for word in words_data:
                meaning = word.get('individual_meaning', word.get('meaning', ''))
                # Extract just the meaning part, not the formatted string
                if ': ' in meaning:
                    meaning = meaning.split(': ', 1)[1]
                meanings.append(meaning)

            # Check for duplicates
            if len(meanings) != len(set(meanings)):
                logger.warning("Duplicate meanings detected - AI did not follow uniqueness requirement")
                # Find duplicates
                seen = set()
                duplicates = set()
                for meaning in meanings:
                    if meaning in seen:
                        duplicates.add(meaning)
                    else:
                        seen.add(meaning)

                if duplicates:
                    logger.warning(f"Duplicate meanings found: {duplicates}")

            # Create elements dictionary grouped by grammatical role
            elements = {}
            for word_data in words_data:
                # Handle different role field names
                role = (word_data.get('grammatical_roles') or
                       word_data.get('grammatical_role') or
                       word_data.get('role', 'other'))
                if isinstance(role, list):
                    role = role[-1] if role else 'other'

                # Map role using config for the specific complexity level
                # For now, use basic role mapping - can be enhanced with complexity-specific mapping
                standard_role = role  # Could map using self.config.get_grammatical_roles(complexity)
                if standard_role not in elements:
                    elements[standard_role] = []
                elements[standard_role].append(word_data)

            validated_data['elements'] = elements

            # ENHANCED: Ensure word explanations follow the required format with individual_meaning
            for word_data in words_data:
                # Handle both old "meaning" and new "individual_meaning" fields
                meaning_key = 'individual_meaning' if 'individual_meaning' in word_data else 'meaning'
                if meaning_key in word_data:
                    meaning = word_data[meaning_key]
                    word = word_data.get('word', '')
                    role = word_data.get('grammatical_role', '')

                    # Keep the individual_meaning as-is without post-processing
                    word_data['meaning'] = meaning

        return validated_data

    def _create_fallback_analysis(self, sentence: str, complexity: str, target_word: Optional[str] = None) -> Dict[str, Any]:
        """Create basic fallback analysis for Spanish sentences"""
        logger.info(f"Creating fallback analysis for Spanish sentence: {sentence}")

        # Simple word splitting (Spanish doesn't use spaces for all compounds like Chinese)
        words = sentence.split()

        fallback_words = []
        elements = {}

        for word in words:
            # Basic role assignment based on Spanish patterns
            role = self._guess_spanish_role(word)
            meaning = f"{word} ({role}): {word}; word in sentence"

            word_data = {
                "word": word,
                "grammatical_role": role,
                "meaning": meaning
            }

            fallback_words.append(word_data)

            # Group by role for elements
            if role not in elements:
                elements[role] = []
            elements[role].append(word_data)

        return {
            "words": fallback_words,
            "elements": elements,
            "overall_analysis": {
                "sentence_structure": "Basic Spanish sentence structure",
                "key_features": "Fallback analysis due to parsing error"
            },
            "confidence": 0.3
        }

    def _guess_spanish_role(self, word: str) -> str:
        """Guess grammatical role based on Spanish word patterns"""
        word_lower = word.lower()

        # Articles
        if word_lower in ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas']:
            return 'determiner'

        # Prepositions
        if word_lower in ['a', 'de', 'en', 'con', 'por', 'para', 'sin', 'desde', 'hasta']:
            return 'preposition'

        # Conjunctions
        if word_lower in ['y', 'o', 'pero', 'que', 'como', 'si', 'cuando']:
            return 'conjunction'

        # Pronouns
        if word_lower in ['yo', 'tú', 'él', 'ella', 'nosotros', 'nosotras', 'ellos', 'ellas', 'me', 'te', 'se', 'lo', 'la', 'los', 'las', 'le', 'les']:
            return 'pronoun'

        # Common verb infinitives (check first - most specific)
        if any(word_lower.endswith(ending) for ending in ['ar', 'er', 'ir']):
            return 'verb'
        
        # Very specific verb conjugations - check BEFORE adjectives
        # First person singular present: -o (but only for known verbs)
        known_verbs_o = ['como', 'tengo', 'estoy', 'soy', 'voy', 'doy', 'hago', 'digo', 'salgo', 'vengo', 'hablo', 'estudio', 'trabajo', 'vivo', 'amo']
        if word_lower.endswith('o') and word_lower in known_verbs_o:
            return 'verb'
        
        # Past tense specific endings (more reliable)
        if word_lower.endswith(('é', 'aste', 'ó', 'asteis', 'aron', 'aba', 'abas', 'ábamos', 'abais', 'aban')):
            return 'verb'

        # Third person present: -e, -en (but NOT if it's a common adjective)
        known_adjectives_e = ['grande', 'pequeñe', 'buene', 'male', 'mejore', 'peore']
        if word_lower.endswith(('e', 'en')) and len(word_lower) > 3 and word_lower not in known_adjectives_e and not word_lower.endswith(('mente', 'ble')):
            return 'verb'

        # Default to noun for most words (Spanish has many nouns)
        # Only classify as adjective if we're very confident
        return 'noun'

    def _tokenize_spanish(self, sentence: str) -> List[str]:
        """Tokenize Spanish text into words"""
        return sentence.strip().split()

    def _classify_spanish_word(self, word: str) -> str:
        """Classify a Spanish word into grammatical category"""
        return self._guess_spanish_role(word)

    def parse_batch_response(self, ai_response: str, sentences: List[str], complexity: str, target_word: str = None) -> List[Dict[str, Any]]:
        """
        Parse batch AI response for Spanish grammar analysis.
        Handles multiple Spanish sentences efficiently with LTR text direction.
        """
        logger.info(f"Parsing batch Spanish response for {len(sentences)} sentences")
        logger.debug(f"AI response length: {len(ai_response)}")
        logger.debug(f"AI response preview: {ai_response[:500]}...")
        try:
            # Clean the response
            cleaned_response = ai_response.strip()

            # Try to extract JSON if it's wrapped in markdown code blocks or other text
            if not cleaned_response.startswith(('{', '[')):
                # Look for JSON code blocks
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group(1)
                else:
                    # Look for JSON between curly braces
                    brace_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                    if brace_match:
                        cleaned_response = brace_match.group(0)

            # Parse JSON response
            json_data = json.loads(cleaned_response)
            logger.debug(f"Parsed JSON data keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'not dict'}")

            # Check if this looks like an error response
            if isinstance(json_data, dict) and json_data.get('sentence') == 'error':
                raise ValueError("AI returned error response")

            if isinstance(json_data, list):
                batch_results = json_data
            else:
                batch_results = json_data.get('batch_results', [])
                logger.debug(f"Found {len(batch_results)} batch results")

            # If no valid batch results, treat as error
            if not batch_results:
                logger.warning("No valid batch results in AI response")
                raise ValueError("No valid batch results in AI response")

            results = []
            for i, item in enumerate(batch_results):
                if i < len(sentences):
                    try:
                        sentence = sentences[i]
                        result_data = item

                        # Handle nested batch responses
                        if 'batch_results' in result_data:
                            result_data = result_data['batch_results'][0] if result_data['batch_results'] else {'words': [], 'explanations': {}}

                        # Process the result data
                        words_data = result_data.get('words') or result_data.get('analysis', [])

                        # For batch format, convert analysis array to words format
                        if result_data.get('analysis') and not result_data.get('words'):
                            words_data = []
                            for analysis_item in result_data['analysis']:
                                word_data = {
                                    'word': analysis_item.get('word', ''),
                                    'grammatical_role': analysis_item.get('grammatical_role', ''),
                                    'individual_meaning': analysis_item.get('individual_meaning', '')
                                }
                                words_data.append(word_data)

                        # Create validated_data structure for _validate_spanish_patterns
                        temp_data = {
                            'words': words_data,
                            'overall_analysis': result_data.get('explanations', {})
                        }

                        # Validate Spanish-specific patterns
                        validated_data = self._validate_spanish_patterns(temp_data, sentence)

                        # Get color scheme for complexity
                        color_scheme = self.config.get_color_scheme(complexity)

                        result = {
                            'word_explanations': validated_data.get('words', []),
                            'explanations': validated_data.get('overall_analysis', {}),
                            'elements': validated_data.get('elements', {}),
                            'confidence': result_data.get('confidence', 0.8),
                            'color_scheme': color_scheme,
                            'is_rtl': False,
                            'text_direction': 'ltr',
                            'sentence': sentence,
                            'target_word': target_word
                        }

                        results.append(result)
                    except Exception as e:
                        logger.warning(f"Batch item {i} failed: {e}")
                        results.append(self._create_fallback_analysis(sentences[i], complexity, target_word))
                else:
                    results.append(self._create_fallback_analysis(sentences[i], complexity, target_word))

            # Ensure we have results for all sentences
            while len(results) < len(sentences):
                results.append(self._create_fallback_analysis(sentences[len(results)], complexity, target_word))

            return results

        except Exception as e:
            logger.error(f"Batch parsing failed: {e}")
            return [self._create_fallback_analysis(s, complexity, target_word) for s in sentences]
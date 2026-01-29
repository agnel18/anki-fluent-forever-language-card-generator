# Arabic Response Parser
# Parses AI responses for Arabic grammar analysis
# CRITICAL: Handles RTL text - explanations should be in reading order (same as sentence)

import json
import logging
import re
from typing import Dict, List, Any, Tuple, Optional
from .ar_config import ArConfig
from .ar_fallbacks import ArFallbacks

logger = logging.getLogger(__name__)

class ArResponseParser:
    """
    Parses AI responses for Arabic grammar analysis.
    Key consideration: Arabic is RTL, so word explanations must be in reverse order.
    """

    def __init__(self, config: ArConfig):
        self.config = config
        self.fallbacks = ArFallbacks(config)

    def parse_response(self, response: str, complexity: str, sentence: str, target_word: str) -> Dict[str, Any]:
        """
        Parse AI response and return structured analysis.
        CRITICAL: For Arabic (RTL), word explanations should be in READING order (same as sentence).
        """
        try:
            # Clean the response
            cleaned_response = response.strip()

            # Try to extract JSON if it's wrapped in markdown code blocks or other text
            if not cleaned_response.startswith(('{', '[')):
                # Look for JSON code blocks
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group(1)
                else:
                    # Look for JSON between curly braces
                    brace_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                    if brace_match:
                        cleaned_response = brace_match.group(0)

            # Parse JSON response
            data = json.loads(cleaned_response)

            # Handle both single and batch responses
            if 'batch_results' in data:
                # Batch response - take first result for now
                result_data = data['batch_results'][0] if data['batch_results'] else {'words': [], 'explanations': {}}
            else:
                result_data = data

            # Extract words and explanations
            words_data = result_data.get('words', [])
            explanations = result_data.get('explanations', {})

            # Process word explanations with RTL consideration
            word_explanations = self._process_word_explanations(words_data, complexity, sentence)

            # Create elements dictionary grouped by grammatical role
            elements = {}
            for word_data in words_data:
                role = word_data.get('grammatical_role', 'other')
                # Map role using config for the specific complexity level
                complexity_roles = self.config.grammatical_roles.get(complexity, {})
                standard_role = complexity_roles.get(role, role)
                if standard_role not in elements:
                    elements[standard_role] = []
                elements[standard_role].append(word_data)

            # Build structured response
            result = {
                'word_explanations': word_explanations,
                'explanations': explanations,
                'elements': elements,
                'metadata': {
                    'language_code': self.config.language_code,
                    'complexity': complexity,
                    'is_rtl': True,
                    'text_direction': 'rtl',
                    'sentence': sentence,
                    'target_word': target_word
                }
            }

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return self._create_fallback_response(sentence, target_word, complexity)
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return self._create_fallback_response(sentence, target_word, complexity)

    def parse_batch_response(self, ai_response: str, sentences: List[str], complexity: str, target_word: str = None) -> List[Dict[str, Any]]:
        """
        Parse batch response with per-result fallbacks.
        
        ARABIC BATCH PROCESSING:
        - Handles multiple Arabic sentences efficiently
        - Maintains RTL reading order for explanations
        - Applies per-sentence validation and fallbacks
        - Returns consistent results for all input sentences
        """
        logger.info(f"DEBUG: Raw AI batch response: {ai_response[:1000]}")
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
                        # Process individual batch item like single response
                        sentence = sentences[i]
                        result_data = item
                        
                        # Handle both single and batch responses
                        if 'batch_results' in result_data:
                            # Nested batch response - take first result
                            result_data = result_data['batch_results'][0] if result_data['batch_results'] else {'words': [], 'explanations': {}}
                        
                        # Process the result data
                        words_data = result_data.get('words', [])
                        word_explanations = self._process_word_explanations(words_data, complexity, sentence)
                        
                        explanations = result_data.get('explanations', {})
                        
                        # Create elements dictionary grouped by grammatical role
                        elements = {}
                        for word_data in words_data:
                            role = word_data.get('grammatical_role', 'other')
                            # Map role using config for the specific complexity level
                            complexity_roles = self.config.grammatical_roles.get(complexity, {})
                            standard_role = complexity_roles.get(role, role)
                            if standard_role not in elements:
                                elements[standard_role] = []
                            elements[standard_role].append(word_data)
                        
                        # Get color scheme
                        color_scheme = self.config.get_color_scheme(complexity)
                        
                        result = {
                            'word_explanations': word_explanations,
                            'explanations': explanations,
                            'elements': elements,
                            'confidence': result_data.get('confidence', 0.8),
                            'color_scheme': color_scheme,
                            'is_rtl': True,
                            'text_direction': 'rtl',
                            'sentence': sentence,
                            'target_word': target_word
                        }
                        
                        results.append(result)
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

    def _process_word_explanations(self, words_data: List[Dict], complexity: str, sentence: str) -> List[List]:
        """
        Process word explanations.
        CRITICAL: For Arabic (RTL), explanations should be in READING order (same as sentence words).
        """
        if not words_data:
            return self._create_basic_word_explanations(sentence, complexity)

        processed_explanations = []

        # Get color scheme for complexity level
        color_scheme = self.config.get_color_scheme(complexity)
        grammatical_roles = self.config.get_grammatical_roles(complexity)

        for word_data in words_data:
            word = word_data.get('word', '')
            role_key = word_data.get('grammatical_role', 'other')
            meaning = word_data.get('meaning', '')

            # Normalize role key
            normalized_role = self._normalize_grammatical_role(role_key)

            # Get color for role
            color = color_scheme.get(normalized_role, color_scheme.get('other', '#708090'))

            # Get display name for role
            role_display = grammatical_roles.get(normalized_role, role_key)

            # Enhance meaning with root analysis for advanced complexity
            enhanced_meaning = self._enhance_with_root_analysis(word, meaning, complexity)

            # Create explanation tuple: [word, role_display, color, meaning]
            explanation = [word, role_display, color, enhanced_meaning]
            processed_explanations.append(explanation)

        # CRITICAL: For Arabic (RTL), explanations should be in the SAME order as words appear in sentence
        # Do NOT reverse - explanations should follow reading order (right to left)
        # processed_explanations.reverse()  # REMOVED: This was causing wrong order

        return processed_explanations

    def _normalize_grammatical_role(self, role_key: str) -> str:
        """Normalize grammatical role key to match configuration"""
        # Handle variations in role naming
        role_mapping = {
            'noun_term': 'noun',
            'verb_form': 'verb',
            'adjective_desc': 'adjective',
            'prep': 'preposition',
            'conj': 'conjunction',
            'interrog': 'interrogative',
            'neg': 'negation',
            'article': 'definite_article',
            'pron': 'pronoun',
            'nom': 'nominative',
            'acc': 'accusative',
            'gen': 'genitive',
            'perfect': 'perfect_verb',
            'imperfect': 'imperfect_verb',
            'imperative': 'imperative_verb',
            'active_part': 'active_participle',
            'passive_part': 'passive_participle',
            'dual_num': 'dual',
            'sound_pl': 'sound_plural',
            'broken_pl': 'broken_plural'
        }

        return role_mapping.get(role_key.lower().replace(' ', '_'), role_key.lower().replace(' ', '_'))

    def _create_basic_word_explanations(self, sentence: str, complexity: str) -> List[List]:
        """Create basic word explanations when AI response is incomplete"""
        # Split sentence into words (basic tokenization for Arabic)
        words = self._tokenize_arabic_sentence(sentence)

        color_scheme = self.config.get_color_scheme(complexity)
        grammatical_roles = self.config.get_grammatical_roles(complexity)

        explanations = []
        for word in words:
            # Basic fallback: assume most words are nouns
            role_key = 'noun'
            color = color_scheme.get(role_key, '#708090')
            role_display = grammatical_roles.get(role_key, 'noun')
            meaning = f'Word in sentence (basic analysis)'

            explanations.append([word, role_display, color, meaning])

        # For RTL, explanations should be in reading order (same as sentence order)
        # explanations.reverse()  # REMOVED: Wrong for RTL
        return explanations

    def _tokenize_arabic_sentence(self, sentence: str) -> List[str]:
        """Basic Arabic sentence tokenization"""
        # Remove extra whitespace and split on spaces
        # This is a simplified tokenizer - real Arabic tokenization is complex
        import re
        # Split on whitespace but keep Arabic punctuation attached
        words = re.findall(r'\S+', sentence.strip())
        return words

    def _create_fallback_response(self, sentence: str, target_word: str, complexity: str) -> Dict[str, Any]:
        """Create fallback response when parsing fails"""
        logger.warning("Using fallback response for Arabic analysis")

        word_explanations = self._create_basic_word_explanations(sentence, complexity)

        return {
            'word_explanations': word_explanations,
            'explanations': {
                'overall_structure': 'Basic sentence analysis (fallback)',
                'key_features': 'Unable to perform detailed grammatical analysis'
            },
            'metadata': {
                'language_code': self.config.language_code,
                'complexity': complexity,
                'is_rtl': True,
                'text_direction': 'rtl',
                'sentence': sentence,
                'target_word': target_word,
                'fallback_used': True
            }
        }

    def _enhance_with_root_analysis(self, word: str, meaning: str, complexity: str) -> str:
        """Enhance word meaning with root analysis for advanced complexity"""
        if complexity != 'advanced':
            return meaning

        # Extract potential root
        root = self.config.extract_arabic_root(word)
        if root:
            root_meaning = self.config.get_root_meaning(root)
            if root_meaning:
                return f"{meaning} [Root: {root} - {root_meaning}]"

        return meaning

    def validate_response_structure(self, response_data: Dict) -> bool:
        """Validate that response has required structure"""
        if not isinstance(response_data, dict):
            return False

        # Check for words array
        if 'words' not in response_data and 'batch_results' not in response_data:
            return False

        # Check explanations
        if 'explanations' not in response_data:
            return False

        return True
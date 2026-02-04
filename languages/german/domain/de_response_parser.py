# German Response Parser
# Parses AI responses for German grammar analysis
# Clean Architecture implementation

import json
import logging
import re
from typing import Dict, Any, List, Optional

from .de_config import DeConfig

logger = logging.getLogger(__name__)

class DeResponseParser:
    """
    Parses AI responses for comprehensive German grammar analysis.
    Handles case system, gender agreement, verb conjugations, and complex constructions.
    Based on Duden German grammar standards.
    """

    def __init__(self, config: DeConfig):
        self.config = config

    def parse_response(self, ai_response: str, complexity: str, sentence: str, target_word: str) -> Dict[str, Any]:
        """
        Parse AI response for comprehensive German grammar analysis.

        Args:
            ai_response: Raw AI response containing JSON analysis
            complexity: Analysis complexity level
            sentence: Original German sentence being analyzed
            target_word: Word to focus analysis on

        Returns:
            Parsed and validated analysis result
        """
        try:
            # Extract JSON from response
            json_data = self._extract_json(ai_response)
            if not json_data:
                logger.warning("No JSON found in response, using fallback")
                return self._create_fallback_response(sentence)

            # Validate and normalize comprehensive analysis
            return self._validate_and_normalize_comprehensive(json_data, sentence)

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            return self._create_fallback_response(sentence)
        except Exception as e:
            logger.error(f"Response parsing failed: {e}")
            return self._create_fallback_response(sentence)

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

    def _validate_and_normalize_comprehensive(self, data: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """
        Validate and normalize comprehensive German grammar analysis.

        Args:
            data: Raw parsed JSON data
            original_text: Original text for validation

        Returns:
            Normalized analysis result
        """
        # Extract and validate words
        words = self._validate_words(data.get('words', []), original_text)

        # Extract and validate sentences
        sentences = self._validate_sentences(data.get('sentences', []))

        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(words, sentences)

        # Build analysis metadata
        analysis_metadata = self._build_analysis_metadata(data.get('analysis_metadata', {}))

        # Create elements dictionary grouped by grammatical role (like Spanish gold standard)
        elements = {}
        for word_data in words:
            role = (word_data.get('grammatical_roles') or
                   word_data.get('grammatical_role') or
                   word_data.get('role', 'other'))
            if isinstance(role, list):
                role = role[-1] if role else 'other'

            # Map role using config for standardization
            standard_role = role  # Could enhance with self.config.get_grammatical_roles(complexity)
            if standard_role not in elements:
                elements[standard_role] = []
            elements[standard_role].append(word_data)

        # Ensure word explanations follow the required format
        for word_data in words:
            meaning = word_data.get('meaning', '')
            word = word_data.get('word', '')
            role = word_data.get('grammatical_role', '')

            # Check if meaning has repetition (word appears twice) and fix it
            # Apply selective repetition removal based on grammatical role
            if meaning.count(word) > 1:
                if role == 'other':
                    # For 'other' roles, keep detailed explanations but remove redundant prefixes
                    # Look for pattern: "word (other): word (other): detailed explanation"
                    # Convert to: "word (other): detailed explanation"
                    other_pattern = f"{word} ({role}): {word} ({role}): "
                    if other_pattern in meaning:
                        parts = meaning.split(other_pattern, 1)
                        if len(parts) == 2 and parts[1].strip():
                            word_data['meaning'] = f"{word} ({role}): {parts[1].strip()}"
                    else:
                        # Try alternative pattern: "word (other): word (article): explanation"
                        alt_pattern = f"{word} ({role}): {word} "
                        if alt_pattern in meaning:
                            parts = meaning.split(alt_pattern, 1)
                            if len(parts) == 2 and parts[1].strip():
                                word_data['meaning'] = f"{word} ({role}): {parts[1].strip()}"
                else:
                    # For standard roles, remove all repetition
                    patterns_to_check = [
                        f"{word} ({role}): {word} ({role}): ",  # exact match
                        f"{word} ({role}): {word} ({role})",    # without trailing space
                    ]

                    for pattern in patterns_to_check:
                        if pattern in meaning:
                            # Split on the pattern and take everything after it
                            parts = meaning.split(pattern, 1)
                            if len(parts) == 2 and parts[1].strip():
                                # Reconstruct as: word (role): explanation
                                word_data['meaning'] = f"{word} ({role}): {parts[1].strip()}"
                                break

                    # Additional check: if we still have repetition like "word (role): word (role): ..."
                    # but with different formatting
                    if meaning.count(word) > 1 and f"{word} ({role}):" in meaning:
                        # Find all occurrences of the prefix
                        prefix = f"{word} ({role}):"
                        prefix_count = meaning.count(prefix)

                        if prefix_count >= 2:
                            # Split by the prefix and reconstruct
                            parts = meaning.split(prefix, prefix_count)
                            if len(parts) > 1:
                                # Take the last part (the actual explanation)
                                explanation = parts[-1].strip()
                                if explanation and not explanation.startswith(f"{word} ("):
                                    word_data['meaning'] = f"{word} ({role}): {explanation}"
                        else:
                            # Try to extract just the explanation part after the first occurrence
                            first_occurrence = f"{word} ({role}): "
                            if first_occurrence in meaning:
                                parts = meaning.split(first_occurrence, 1)
                                if len(parts) == 2 and parts[1].startswith(f"{word} ("):
                                    # Find the second occurrence and take everything after it
                                    second_pattern = f"{word} ("
                                    second_pos = parts[1].find(second_pattern)
                                    if second_pos != -1:
                                        # Find the closing ): and take everything after
                                        after_second = parts[1][second_pos:]
                                        close_pos = after_second.find("): ")
                                        if close_pos != -1:
                                            explanation = after_second[close_pos + 3:]
                                            word_data['meaning'] = f"{word} ({role}): {explanation}"

        return {
            'words': words,
            'sentences': sentences,
            'overall_confidence': overall_confidence,
            'analysis_metadata': analysis_metadata,
            'elements': elements,  # Now properly grouped by grammatical role
            'explanations': data.get('overall_analysis', {}),  # Add explanations for GrammarAnalysis compatibility
            'confidence': overall_confidence,  # Add confidence for GrammarAnalysis compatibility
            'errors': [],
            'warnings': []
        }

    def parse_batch_response(self, ai_response: str, sentences: List[str], complexity: str, target_word: str = "") -> List[Dict[str, Any]]:
        """
        Parse batch AI response for German grammar analysis.
        Handles multiple German sentences efficiently with case/gender analysis.
        """
        logger.info(f"Parsing batch German response for {len(sentences)} sentences")
        logger.debug(f"AI response length: {len(ai_response)}")
        logger.debug(f"AI response preview: {ai_response[:500]}...")
        try:
            # Extract JSON using robust method
            json_data = self._extract_json(ai_response)
            if not json_data:
                logger.warning("No JSON found in batch response, using fallbacks")
                return [self._create_fallback_response(s) for s in sentences]

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
                                    'individual_meaning': analysis_item.get('individual_meaning', ''),
                                    'grammatical_case': analysis_item.get('grammatical_case', ''),
                                    'gender': analysis_item.get('gender', '')
                                }
                                words_data.append(word_data)

                        # Create validated_data structure for _validate_and_normalize_comprehensive
                        temp_data = {
                            'words': words_data,
                            'overall_analysis': result_data.get('explanations', {}),
                            'analysis_metadata': result_data.get('analysis_metadata', {})
                        }

                        # Validate German-specific patterns
                        validated_data = self._validate_and_normalize_comprehensive(temp_data, sentence)

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
                        results.append(self._create_fallback_response(sentences[i]))
                else:
                    results.append(self._create_fallback_response(sentences[i]))

            # Ensure we have results for all sentences
            while len(results) < len(sentences):
                results.append(self._create_fallback_response(sentences[len(results)]))

            return results

        except Exception as e:
            logger.error(f"Batch parsing failed: {e}")
            return [self._create_fallback_response(s) for s in sentences]

    def _validate_words(self, words_data: List[Dict[str, Any]], original_text: str) -> List[Dict[str, Any]]:
        """Validate and normalize word analysis data."""
        validated_words = []
        original_words = original_text.split()

        for i, word_data in enumerate(words_data):
            if not isinstance(word_data, dict):
                continue

            # Ensure word matches original text
            word = word_data.get('word', '')
            if i < len(original_words) and word != original_words[i]:
                # Try to match by position or use original
                word = original_words[i] if i < len(original_words) else word

            # Extract simplified grammatical role for coloring
            detailed_role = word_data.get('grammatical_role', 'unknown')
            individual_meaning = word_data.get('individual_meaning', '')
            simplified_role = self._extract_simplified_role(detailed_role, word, individual_meaning)

            validated_word = {
                'word': word,
                'lemma': word_data.get('lemma', word),
                'pos': self._normalize_pos(word_data.get('pos', 'unknown')),
                'grammatical_role': simplified_role,  # Use simplified role for coloring
                'detailed_grammatical_role': detailed_role,  # Keep detailed role for explanations
                'grammatical_case': self._normalize_case(word_data.get('grammatical_case') or word_data.get('case')),
                'gender': self._normalize_gender(word_data.get('gender')),
                'number': word_data.get('number'),
                'person': word_data.get('person'),
                'tense': word_data.get('tense'),
                'mood': word_data.get('mood'),
                'declension_type': word_data.get('declension_type'),
                'preposition_case': word_data.get('preposition_case'),
                'confidence': float(word_data.get('confidence', 0.5)),
                'features': word_data.get('features', {}),
                'morphological_info': word_data.get('morphological_info', {})
            }

            # Format the meaning field for display, similar to Spanish analyzer
            individual_meaning = word_data.get('individual_meaning', '')
            simplified_role = validated_word['grammatical_role']
            detailed_role = word_data.get('grammatical_role', simplified_role)
            if individual_meaning:
                # Use the detailed role for the explanation text, but simplified role for coloring
                validated_word['meaning'] = f"{word} ({simplified_role}): {individual_meaning}"
            else:
                # Fallback format
                validated_word['meaning'] = f"{word} ({simplified_role}): {word}; word in sentence"

            validated_words.append(validated_word)

        return validated_words

    def _validate_sentences(self, sentences_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and normalize sentence analysis data."""
        validated_sentences = []

        for sentence_data in sentences_data:
            if not isinstance(sentence_data, dict):
                continue

            validated_sentence = {
                'text': sentence_data.get('text', ''),
                'word_order_type': sentence_data.get('word_order_type', 'unknown'),
                'clause_structure': sentence_data.get('clause_structure', 'unknown'),
                'verb_position': sentence_data.get('verb_position', 'unknown'),
                'complex_constructions': sentence_data.get('complex_constructions', []),
                'case_assignments': sentence_data.get('case_assignments', {})
            }

            validated_sentences.append(validated_sentence)

        return validated_sentences

    def _normalize_pos(self, pos: str) -> str:
        """Normalize part of speech to standard values."""
        pos_mapping = {
            'noun': 'noun',
            'verb': 'verb',
            'adjective': 'adjective',
            'adverb': 'adverb',
            'article': 'article',
            'pronoun': 'pronoun',
            'preposition': 'preposition',
            'conjunction': 'conjunction',
            'numeral': 'numeral',
            'interjection': 'interjection'
        }
        return pos_mapping.get(pos.lower(), 'unknown')

    def _normalize_case(self, case: Optional[str]) -> Optional[str]:
        """Normalize case to standard German case names."""
        if not case or case.lower() in ['null', 'none', '']:
            return None

        case_mapping = {
            'nominative': 'nominative',
            'nominativ': 'nominative',
            'nom': 'nominative',
            'accusative': 'accusative',
            'akkusativ': 'accusative',
            'acc': 'accusative',
            'dative': 'dative',
            'dativ': 'dative',
            'dat': 'dative',
            'genitive': 'genitive',
            'genitiv': 'genitive',
            'gen': 'genitive'
        }
        return case_mapping.get(case.lower())

    def _normalize_gender(self, gender: Optional[str]) -> Optional[str]:
        """Normalize gender to standard German gender names."""
        if not gender or gender.lower() in ['null', 'none', '']:
            return None

        gender_mapping = {
            'masculine': 'masculine',
            'masc': 'masculine',
            'männlich': 'masculine',
            'maskulin': 'masculine',
            'feminine': 'feminine',
            'fem': 'feminine',
            'weiblich': 'feminine',
            'feminin': 'feminine',
            'neuter': 'neuter',
            'neut': 'neuter',
            'sächlich': 'neuter',
            'neutrum': 'neuter'
        }
        return gender_mapping.get(gender.lower())

    def _extract_simplified_role(self, detailed_role: str, word: str = "", meaning: str = "") -> str:
        """Extract simplified grammatical role for color mapping."""
        detailed_lower = detailed_role.lower()
        meaning_lower = meaning.lower() if meaning else ""

        # Map detailed roles to simplified color scheme keys
        role_mappings = {
            'article': ['definite article', 'indefinite article', 'article', 'demonstrative article'],
            'noun': ['noun', 'substantiv', 'nomen', 'proper noun', 'common noun'],
            'verb': ['verb', 'copular verb', 'auxiliary verb', 'modal verb', 'transitive verb', 'intransitive verb', 'reflexive verb', 'main verb'],
            'adjective': ['adjective', 'predicate adjective', 'attributive adjective', 'comparative adjective', 'superlative adjective'],
            'pronoun': ['pronoun', 'personal pronoun', 'reflexive pronoun', 'demonstrative pronoun', 'possessive pronoun', 'impersonal pronoun', 'relative pronoun'],
            'preposition': ['preposition', 'postposition', 'two-way preposition', 'accusative preposition', 'dative preposition', 'genitive preposition'],
            'conjunction': ['conjunction', 'subordinating conjunction', 'coordinating conjunction'],
            'auxiliary': ['auxiliary', 'auxiliary verb', 'perfect auxiliary', 'future auxiliary'],
            'modal': ['modal', 'modal verb', 'modal auxiliary'],
            'particle': ['particle', 'separable particle', 'infinitive particle', 'negation particle', 'adverbial particle'],
            'adverb': ['adverb', 'negation adverb', 'sentence adverb', 'manner adverb', 'temporal adverb', 'local adverb']
        }

        for simplified_role, keywords in role_mappings.items():
            if any(keyword in detailed_lower for keyword in keywords):
                return simplified_role

        # Special case mappings based on meaning text analysis
        word_lower = word.lower()
        if word_lower == 'nicht' and ('adverb' in meaning_lower or 'negat' in meaning_lower):
            return 'adverb'
        if word_lower == 'zu' and ('particle' in meaning_lower or 'infinitive' in meaning_lower):
            return 'particle'

        # Additional meaning-based corrections
        if 'adverb' in meaning_lower and 'negat' in meaning_lower:
            return 'adverb'
        if 'particle' in meaning_lower and ('infinitive' in meaning_lower or 'introducing' in meaning_lower):
            return 'particle'

        # Default fallback
        return 'other'

    def _calculate_overall_confidence(self, words: List[Dict], sentences: List[Dict]) -> float:
        """Calculate overall analysis confidence."""
        if not words:
            return 0.0

        word_confidences = [w.get('confidence', 0.5) for w in words]
        avg_word_confidence = sum(word_confidences) / len(word_confidences)

        # Boost confidence if we have sentence analysis
        sentence_boost = 0.1 if sentences else 0.0

        # Boost confidence for recognized German features
        german_features_boost = 0.0
        for word in words:
            if word.get('case') or word.get('gender'):
                german_features_boost = 0.2
                break

        confidence = min(1.0, avg_word_confidence + sentence_boost + german_features_boost)
        return round(confidence, 2)

    def _build_analysis_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive analysis metadata."""
        return {
            'case_system_recognized': metadata.get('case_system_recognized', False),
            'gender_agreement_checked': metadata.get('gender_agreement_checked', False),
            'verb_conjugation_analyzed': metadata.get('verb_conjugation_analyzed', False),
            'word_order_validated': metadata.get('word_order_validated', False),
            'complex_constructions_detected': metadata.get('complex_constructions_detected', []),
            'morphological_analysis_performed': metadata.get('morphological_analysis_performed', False),
            'fallback_used': False
        }

    def _create_fallback_response(self, original_text: str) -> Dict[str, Any]:
        """Create fallback response when parsing fails."""
        words = []
        for word in original_text.split():
            words.append({
                'word': word,
                'lemma': word,
                'pos': 'unknown',
                'grammatical_role': 'unknown',
                'case': None,
                'gender': None,
                'number': None,
                'person': None,
                'tense': None,
                'mood': None,
                'declension_type': None,
                'preposition_case': None,
                'confidence': 0.0,
                'features': {},
                'morphological_info': {}
            })

        return {
            'words': words,
            'sentences': [{
                'text': original_text,
                'word_order_type': 'unknown',
                'clause_structure': 'unknown',
                'verb_position': 'unknown',
                'complex_constructions': [],
                'case_assignments': {}
            }],
            'overall_confidence': 0.0,
            'analysis_metadata': {
                'case_system_recognized': False,
                'gender_agreement_checked': False,
                'verb_conjugation_analyzed': False,
                'word_order_validated': False,
                'complex_constructions_detected': [],
                'morphological_analysis_performed': False,
                'fallback_used': True
            },
            'elements': words,  # Add elements for GrammarAnalysis compatibility
            'explanations': {
                'sentence_structure': 'Fallback analysis - parsing failed',
                'key_features': 'Basic word identification only'
            },  # Add explanations for GrammarAnalysis compatibility
            'confidence': 0.3,  # Add confidence for GrammarAnalysis compatibility
            'errors': ['JSON parsing failed'],
            'warnings': ['Using fallback analysis']
        }
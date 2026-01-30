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
            words_data = result_data.get('words') or result_data.get('analysis', [])
            explanations = result_data.get('explanations', {})

            # Process word explanations with RTL consideration
            word_explanations = self._process_word_explanations(words_data, complexity, sentence)

            # Create elements dictionary grouped by grammatical role
            elements = {}
            for word_data in words_data:
                # Handle both old format and new AI format
                role = (word_data.get('grammatical_roles') or 
                       word_data.get('grammatical_role') or
                       word_data.get('role', 'other'))
                if isinstance(role, list):
                    role = role[-1] if role else 'other'
                
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
            logger.info(f"DEBUG: Cleaned response starts with: {cleaned_response[:100]}")

            # Try to extract JSON if it's wrapped in markdown code blocks or other text
            if not cleaned_response.startswith(('{', '[')):
                logger.info("DEBUG: Response doesn't start with JSON, looking for code blocks")
                # Look for JSON code blocks
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group(1)
                    logger.info("DEBUG: Found JSON in code block")
                else:
                    # Look for JSON between curly braces
                    brace_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                    if brace_match:
                        cleaned_response = brace_match.group(0)
                        logger.info("DEBUG: Found JSON between braces")

            logger.info(f"DEBUG: Final cleaned response: {cleaned_response[:200]}")
            
            # Parse JSON response
            json_data = json.loads(cleaned_response)
            logger.info(f"DEBUG: Successfully parsed JSON, type: {type(json_data)}")

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
                        words_data = result_data.get('words') or result_data.get('analysis', [])
                        
                        # Normalize word data format (handle both single and batch response formats)
                        normalized_words_data = []
                        for word_data in words_data:
                            normalized_word = self._normalize_word_data(word_data)
                            normalized_words_data.append(normalized_word)
                        
                        word_explanations = self._process_word_explanations(normalized_words_data, complexity, sentence)
                        
                        explanations = result_data.get('explanations', {})
                        
                        # Create elements dictionary grouped by grammatical role
                        elements = {}
                        for word_data in words_data:
                            # Handle both single role and role array formats
                            grammatical_roles = word_data.get('grammatical_roles') or word_data.get('grammatical_role')
                            if isinstance(grammatical_roles, list):
                                role = grammatical_roles[-1] if grammatical_roles else 'other'
                            else:
                                role = grammatical_roles or 'other'
                            
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

    def _normalize_word_data(self, word_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize word data from different AI response formats to a consistent format.
        
        Handles both single response format (grammatical_role, meaning) and 
        batch response format (role, features) and new detailed format.
        """
        normalized = dict(word_data)  # Copy the original
        
        # Handle AI responses that use "other" field instead of "meaning"
        if 'other' in word_data and 'meaning' not in word_data:
            normalized['meaning'] = word_data['other']
            
        # If it's already in the expected format (has grammatical_role), return as-is
        if 'grammatical_role' in word_data:
            return normalized
            
        # Convert batch format to single format
        if 'role' in word_data:
            normalized['grammatical_role'] = word_data['role']
            
        # Generate meaning from role and features if not present
        if 'meaning' not in word_data:
            # If we have detailed AI fields, use them to construct detailed meaning
            if any(key in word_data for key in ['type', 'person', 'number', 'case']):
                normalized['meaning'] = self._construct_meaning_from_ai_fields(word_data)
            elif 'role' in word_data:
                # Fallback to basic meaning from role and features
                features = word_data.get('features', [])
                role = word_data['role']
                meaning_parts = [f"{role}"]
                if features:
                    meaning_parts.append(f"with features: {', '.join(features)}")
                normalized['meaning'] = " - ".join(meaning_parts)
            
        return normalized

    def _construct_meaning_from_ai_fields(self, word_data: Dict[str, Any]) -> str:
        """
        Construct detailed Arabic grammar explanation from AI analysis fields.
        Uses the structured data from AI to create specific, educational explanations.
        """
        # First check if we already have a contextual meaning in the new format
        meaning = word_data.get('meaning', '')
        if meaning and isinstance(meaning, str):
            # Check if it matches the new format: "WORD (GRAMMATICAL_ROLE): contextual meaning and grammatical function"
            if re.match(r'^[^\s]+\s*\([^)]+\):\s*.+', meaning.strip()):
                logger.debug(f"Using pre-formatted contextual meaning: {meaning}")
                return meaning.strip()
        
        # Handle "other" field from AI responses
        other = word_data.get('other', '')
        if other and isinstance(other, str):
            word = word_data.get('word', '')
            role = word_data.get('grammatical_role', 'other')
            # Convert generic "other" descriptions to contextual format
            if word and role:
                contextual_meaning = f"{word} ({role}): {other} — grammatical function in sentence"
                logger.debug(f"Converting 'other' field to contextual format: {contextual_meaning}")
                return contextual_meaning
        
        # Fall back to constructing from individual fields
        grammatical_role = word_data.get('grammatical_role', '')
        if grammatical_role is None:
            grammatical_role = ''
        word_type = word_data.get('type', '')
        if word_type is None:
            word_type = ''
        person = word_data.get('person', '')
        if person is None:
            person = ''
        number = word_data.get('number', '')
        if number is None:
            number = ''
        case = word_data.get('case', '')
        if case is None:
            case = ''
        target_word = word_data.get('target_word', False)
        
        logger.debug(f"Constructing meaning from fields for word_data: {word_data}")
        
        # Build explanation based on grammatical role
        if grammatical_role == 'pronoun':
            if word_type == 'independent personal pronoun':
                explanation = f"Independent personal pronoun ({person} person, {number})"
                if case:
                    explanation += f" in {case} case"
                if target_word:
                    explanation += " - the main word being analyzed"
                return explanation
            else:
                return f"Personal pronoun ({person} person, {number}) in {case} case"
                
        elif grammatical_role == 'verb':
            if word_type == 'imperfect_verb':
                explanation = f"Imperfect verb ({person} person, {number})"
                if case:
                    explanation += f" in {case} case"
                explanation += " - indicates ongoing, habitual, or future action"
                return explanation
            elif word_type == 'perfect_verb':
                explanation = f"Perfect verb ({person} person, {number})"
                if case:
                    explanation += f" in {case} case" 
                explanation += " - indicates completed action in the past"
                return explanation
            else:
                return f"Verb ({person} person, {number}) in {case} case"
                
        elif grammatical_role == 'noun':
            explanation = f"Noun ({number})"
            if case:
                case_explanation = {
                    'nominative': 'مرفوع (nominative) - subject case',
                    'accusative': 'منصوب (accusative) - object case', 
                    'genitive': 'مجرور (genitive) - possessive case'
                }.get(case, f'{case} case')
                explanation += f" in {case_explanation}"
            return explanation
            
        elif grammatical_role == 'other':
            if word_type == 'adverb of time':
                return "Adverb of time - indicates when an action occurs"
            else:
                return "Grammatical particle with specific function in the sentence"
        
        # Fallback if no specific construction
        return ""

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

    def _get_role_display_name(self, grammatical_role: str) -> str:
        """Get display name for grammatical role"""
        role_display_map = {
            'imperfect_verb': 'verb (imperfect)',
            'noun': 'noun',
            'preposition': 'preposition',
            'conjunction': 'conjunction',
            'other': 'particle',
            'verb': 'verb',
            'adjective': 'adjective'
        }
        return role_display_map.get(grammatical_role.lower(), grammatical_role)

    def _generate_meaning_from_role_and_features(self, role: str, features: List[str]) -> str:
        """Generate detailed meaning from grammatical role and linguistic features"""
        role = role.lower()
        features_set = set(f.lower() for f in features)
        
        # Enhanced meanings for different roles
        role_meanings = {
            'pronoun': 'a word that replaces a noun to avoid repetition',
            'noun': 'a word that names a person, place, thing, or idea',
            'verb': 'a word that expresses an action, occurrence, or state of being',
            'imperfect_verb': 'a verb form indicating ongoing, habitual, or future action',
            'perfect_verb': 'a verb form indicating completed action in the past',
            'adjective': 'a word that describes or modifies a noun',
            'preposition': 'a word that shows the relationship between a noun and other words',
            'conjunction': 'a word that connects clauses, sentences, or words',
            'particle': 'a short word that expresses grammatical relationships or emphasis',
            'interrogative': 'a word used to form questions',
            'negation': 'a word that expresses denial, absence, or opposition',
            'definite_article': 'a word that marks a noun as specific or known',
            'other': 'a grammatical element with specific function'
        }
        
        base_meaning = role_meanings.get(role, f'{role.replace("_", " ")}')
        
        # Build detailed description from features
        descriptions = []
        
        # Person features
        if 'first_person' in features_set:
            descriptions.append('speaker reference')
        elif 'second_person' in features_set:
            descriptions.append('listener reference') 
        elif 'third_person' in features_set:
            descriptions.append('third party reference')
        
        # Number features
        if 'singular' in features_set:
            descriptions.append('single entity')
        elif 'plural' in features_set:
            descriptions.append('multiple entities')
        elif 'dual' in features_set:
            descriptions.append('exactly two entities')
        
        # Gender features
        if 'masculine' in features_set:
            descriptions.append('masculine gender')
        elif 'feminine' in features_set:
            descriptions.append('feminine gender')
        
        # Case features (Arabic i'rab)
        if 'nominative' in features_set:
            descriptions.append('subject case')
        elif 'accusative' in features_set:
            descriptions.append('object case')
        elif 'genitive' in features_set:
            descriptions.append('possessive case')
        
        # Function features
        if 'subject' in features_set:
            descriptions.append('sentence subject')
        elif 'object' in features_set:
            descriptions.append('direct object')
        elif 'predicate' in features_set:
            descriptions.append('sentence predicate')
        
        # Add any remaining features
        remaining_features = [f for f in features if f.lower() not in {
            'first_person', 'second_person', 'third_person', 'singular', 'plural', 'dual',
            'masculine', 'feminine', 'nominative', 'accusative', 'genitive', 
            'subject', 'object', 'predicate'
        }]
        descriptions.extend(remaining_features)
        
        if descriptions:
            return f"{base_meaning} ({'; '.join(descriptions)})"
        
        return base_meaning

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

        try:
            for word_data in words_data:
                word = word_data.get('word', '')
        
                # Handle both old format (grammatical_role) and new AI format (role)
                role_key = (word_data.get('grammatical_roles') or 
                       word_data.get('grammatical_role') or
                       word_data.get('role', 'other'))
                if role_key is None:
                    role_key = 'other'
                if isinstance(role_key, list):
                    # Pick the most specific role (usually the last one is most specific)
                    role_key = role_key[-1] if role_key else 'other'

                # Check for structured role components
                grammatical_role = word_data.get('grammatical_role', role_key)
                specific_type = word_data.get('specific_type', '')
        
                # Combine for role_key if we have structured components
                if grammatical_role and specific_type and grammatical_role != role_key:
                    role_key = f"{grammatical_role.lower()}_{specific_type.lower().replace('-', '_')}"
        
                meaning = word_data.get('meaning', '')  # Try meaning first (new detailed format)
                if meaning is None:
                    meaning = ''
                morphological_notes = word_data.get('morphological_notes', '')
                if morphological_notes is None:
                    morphological_notes = ''
        
                # Check if meaning is in our simple contextual format: "WORD (ROLE): meaning — function"
                contextual_regex = r'^[^\s]+\s*\([^)]+\):\s*.+—\s*.+'
                if meaning and re.match(contextual_regex, meaning.strip()):
                    # Clean up duplicated word/role pattern: "WORD (role): WORD (specific_role): meaning"
                    # Replace with: "WORD (specific_role): meaning"
                    duplicate_pattern = r'^([^\s]+)\s*\(([^)]+)\):\s*\1\s*\(([^)]+)\):\s*(.+)$'
                    if re.match(duplicate_pattern, meaning.strip()):
                        # Extract the specific role and the rest of the meaning
                        match = re.match(duplicate_pattern, meaning.strip())
                        if match:
                            word_part, general_role, specific_role, rest_meaning = match.groups()
                            cleaned_meaning = f"{word_part} ({specific_role}): {rest_meaning}"
                            logger.debug(f"Cleaned duplicated role in meaning: '{meaning}' -> '{cleaned_meaning}'")
                            meaning = cleaned_meaning
                    
                    # This is our desired simple contextual format - use it directly
                    logger.debug(f"REGEX MATCH: Using simple contextual meaning format: {meaning}")
                    pass  # Continue with the rest of processing but keep this meaning
                elif meaning and len(meaning.strip()) > 50 and any(keyword in meaning.lower() for keyword in [
                    "case", "مرفوع", "منصوب", "مجرور", "فاعل", "مفعول", "root", "form", "subject", "object"
                ]):
                    # AI provided detailed explanation - use it as-is
                    pass
                else:
                    # Try to construct from available components or use fallback
                    logger.debug(f"REGEX NO MATCH: meaning='{meaning}', will construct detailed explanation")
                    meaning = self._construct_meaning_from_ai_fields(word_data)
                    logger.debug(f"Constructed meaning for '{word}': '{meaning}'")
        
                # If no meaning, try individual_meaning (legacy)
                if not meaning:
                    meaning = word_data.get('individual_meaning', '')
        
                # Normalize role key
                normalized_role = self._normalize_grammatical_role(role_key)

                # Apply complexity-based role filtering
                if not self.config.should_show_role(normalized_role, complexity):
                    # Use parent role for lower complexity levels
                    display_role = self.config.get_parent_role(normalized_role)
                else:
                    display_role = normalized_role

                # Get color for role - use parent role for color inheritance
                parent_role = self.config.get_parent_role(normalized_role)
                color = color_scheme.get(parent_role, color_scheme.get('other', '#708090'))

                # Get display name for role
                role_display = grammatical_roles.get(display_role, display_role)

                # Update meaning to use display_role instead of original AI role
                if meaning and '(' in meaning and ')' in meaning:
                    # Extract the role from the meaning: "WORD (original_role): ..."
                    role_pattern = r'^([^\s]+)\s*\(([^)]+)\):\s*(.+)$'
                    match = re.match(role_pattern, meaning.strip())
                    if match:
                        word_part, original_role, rest_meaning = match.groups()
                        # Replace with display_role
                        updated_meaning = f"{word_part} ({display_role}): {rest_meaning}"
                        logger.debug(f"Updated meaning role: '{meaning}' -> '{updated_meaning}'")
                        meaning = updated_meaning

                # Enhance meaning with root analysis for advanced complexity
                enhanced_meaning = self._enhance_with_root_analysis(word, meaning, complexity)

                # Create explanation tuple: [word, role_display, color, meaning]
                explanation = [word, role_display, color, enhanced_meaning]
                processed_explanations.append(explanation)

            # CRITICAL: For Arabic (RTL), explanations should be in the SAME order as words appear in sentence
            # Do NOT reverse - explanations should follow reading order (right to left)
            # processed_explanations.reverse()  # REMOVED: This was causing wrong order

            return processed_explanations

        except Exception as e:
            logger.error(f"Error in _process_word_explanations: {e}")
            return self._create_basic_word_explanations(sentence, complexity)

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
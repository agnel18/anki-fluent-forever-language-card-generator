# languages/LANGUAGE_PLACEHOLDER/domain/LANG_CODE_PLACEHOLDER_response_parser.py
"""
LANGUAGE_NAME_PLACEHOLDER Response Parser - Domain Component

GOLD STANDARD RESPONSE PARSING:
This component handles AI response parsing with robust error handling.
It converts raw AI responses into standardized analysis format.

RESPONSIBILITIES:
1. Parse JSON responses from AI models
2. Validate response structure and content
3. Handle malformed responses gracefully
4. Calculate confidence scores
5. Provide fallback parsing for errors
6. CRITICAL: Ensure role consistency in word explanations (Arabic analyzer innovation)

ROLE CONSISTENCY PROCESSING (Arabic Analyzer Pattern):
- Apply complexity-based role filtering using role hierarchy
- Ensure meaning text matches display role to eliminate grammatical repetition
- Use parent roles for color inheritance while showing specific roles in explanations
- Follow standardized word explanation format: "WORD (DISPLAY_ROLE): meaning — function"

PARSING FEATURES:
- JSON extraction and validation
- Confidence score calculation
- Fallback parsing for non-JSON responses
- Language-specific validation
- Error recovery and logging
- Role hierarchy processing for educational depth
- Color inheritance for visual consistency

INTEGRATION:
- Called by main analyzer after AI response
- Uses configuration for validation rules
- Returns standardized result format
"""
# type: ignore  # Template file with placeholders - ignore type checking

import json
import re
from typing import Dict, Any, List, Optional, Tuple


class LanguageResponseParser:
    """
    Parses and validates AI responses for LANGUAGE_NAME_PLACEHOLDER grammatical analysis.

    GOLD STANDARD PARSING APPROACH:
    - Robust JSON extraction from AI responses
    - Multiple fallback strategies for malformed responses
    - Confidence scoring based on multiple factors
    - Language-specific validation rules
    - Comprehensive error handling and recovery
    """

    def __init__(self, config):
        """
        Initialize with configuration.

        TEMPLATE INITIALIZATION:
        1. Store config reference for validation rules
        2. Set up JSON parsing patterns
        3. Initialize fallback strategies
        4. Configure error handling
        """
        self.config = config

        # JSON extraction patterns
        self.json_pattern = re.compile(r'\{.*\}', re.DOTALL)
        self.array_pattern = re.compile(r'\[.*\]', re.DOTALL)

    def parse_response(self, response_text: str, complexity: str, sentence: str, target_word: str = None) -> Dict[str, Any]:
        """
        Parse AI response into standardized format.

        Args:
            response_text: Raw AI response text
            sentence: Original sentence being analyzed
            complexity: Analysis complexity level

        Returns:
            Standardized analysis result dictionary
        """
        try:
            # Primary parsing: Extract and parse JSON
            parsed_data = self._extract_json(response_text)

            if parsed_data:
                return self._process_parsed_data(parsed_data, sentence, complexity)

            # Fallback 1: Try to extract array format
            array_data = self._extract_array(response_text)
            if array_data:
                return self._process_array_data(array_data, sentence, complexity)

            # Fallback 2: Basic text parsing
            return self._fallback_text_parse(response_text, sentence, complexity)

        except Exception as e:
            # Ultimate fallback: Basic word analysis
            return self._emergency_fallback(sentence, complexity, str(e))

    def parse_batch_response(self, response_text: str, sentences: List[str], complexity: str, target_word: str = None) -> List[Dict[str, Any]]:
        """
        Parse batch AI response into per-sentence standardized format with fallbacks.

        Args:
            response_text: Raw AI batch response text
            sentences: Original sentences being analyzed
            complexity: Analysis complexity level
            target_word: Optional target word for analysis

        Returns:
            List of standardized analysis results
        """
        try:
            parsed_data = self._extract_json(response_text)

            if not parsed_data:
                raise ValueError("No JSON found in batch response")

            if isinstance(parsed_data, list):
                batch_results = parsed_data
            else:
                batch_results = parsed_data.get('batch_results', [])

            if not batch_results:
                raise ValueError("No batch_results found in response")

            results = []
            for i, item in enumerate(batch_results):
                if i < len(sentences):
                    try:
                        results.append(self._parse_batch_item(item, sentences[i], complexity, target_word))
                    except Exception:
                        results.append(self._emergency_fallback(sentences[i], complexity, "Batch item parse error"))
                else:
                    results.append(self._emergency_fallback(sentences[i], complexity, "Missing batch item"))

            while len(results) < len(sentences):
                results.append(self._emergency_fallback(sentences[len(results)], complexity, "Missing batch item"))

            return results
        except Exception as e:
            return [self._emergency_fallback(sentence, complexity, str(e)) for sentence in sentences]

    def _parse_batch_item(self, item: Dict[str, Any], sentence: str, complexity: str, target_word: str = None) -> Dict[str, Any]:
        """Parse a single batch item into standardized format."""
        if 'batch_results' in item and item['batch_results']:
            item = item['batch_results'][0]

        if 'word_explanations' in item:
            return self._process_word_explanations_format(item, sentence, complexity)

        if 'words' in item:
            return self._process_words_format(item, sentence, complexity)

        return self._emergency_fallback(sentence, complexity, "Unknown batch item format")

    def _extract_json(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract and parse JSON from response text"""
        try:
            # Find JSON object in response
            json_match = self.json_pattern.search(response_text)
            if not json_match:
                return None

            json_str = json_match.group()
            return json.loads(json_str)

        except (json.JSONDecodeError, AttributeError):
            return None

    def _extract_array(self, response_text: str) -> Optional[List]:
        """Extract and parse array from response text"""
        try:
            array_match = self.array_pattern.search(response_text)
            if not array_match:
                return None

            array_str = array_match.group()
            return json.loads(array_str)

        except (json.JSONDecodeError, AttributeError):
            return None

    def _process_parsed_data(self, data: Dict[str, Any], sentence: str, complexity: str) -> Dict[str, Any]:
        """Process successfully parsed JSON data"""
        try:
            # Handle different response formats
            if 'word_explanations' in data:
                return self._process_word_explanations_format(data, sentence, complexity)
            elif 'words' in data:
                return self._process_words_format(data, sentence, complexity)
            elif 'batch_results' in data:
                # Handle batch format (take first result)
                if data['batch_results'] and len(data['batch_results']) > 0:
                    return self._process_parsed_data(data['batch_results'][0], sentence, complexity)
                else:
                    return self._emergency_fallback(sentence, complexity, "Empty batch results")

            # Unknown format
            return self._emergency_fallback(sentence, complexity, f"Unknown response format: {list(data.keys())}")

        except Exception as e:
            return self._emergency_fallback(sentence, complexity, f"Processing error: {str(e)}")

    def _process_word_explanations_format(self, data: Dict[str, Any], sentence: str, complexity: str) -> Dict[str, Any]:
        """Process word_explanations format (preferred)"""
        word_explanations = data.get('word_explanations', [])
        elements = data.get('elements', {})
        explanations = data.get('explanations', {})
        confidence = data.get('confidence', 0.8)

        # Validate and standardize word explanations
        standardized_explanations = self._standardize_word_explanations(word_explanations, complexity)

        # Process elements
        standardized_elements = self._standardize_elements(elements)

        # Process explanations
        standardized_explanations_text = self._standardize_explanations(explanations)

        # Calculate final confidence
        final_confidence = self._calculate_confidence(standardized_explanations, sentence, confidence)

        return {
            'word_explanations': standardized_explanations,
            'elements': standardized_elements,
            'explanations': standardized_explanations_text,
            'confidence_score': final_confidence,
            'sentence': sentence,
            'complexity': complexity,
            'parsing_method': 'word_explanations_format'
        }

    def _process_words_format(self, data: Dict[str, Any], sentence: str, complexity: str) -> Dict[str, Any]:
        """Process words format (alternative)"""
        words_data = data.get('words', [])
        explanations = data.get('explanations', {})

        # Convert words format to word_explanations format
        word_explanations = []
        colors = self.config.get_color_scheme(complexity)

        for word_info in words_data:
            word = word_info.get('word', '')
            role = word_info.get('grammatical_role', '')
            meaning = word_info.get('meaning', '')

            color = colors.get(role, '#808080')
            word_explanations.append([word, role, color, meaning])

        # Process explanations
        standardized_explanations = self._standardize_explanations(explanations)

        # Calculate confidence
        confidence = self._calculate_confidence(word_explanations, sentence, 0.7)

        return {
            'word_explanations': word_explanations,
            'elements': {},  # Not provided in this format
            'explanations': standardized_explanations,
            'confidence_score': confidence,
            'sentence': sentence,
            'complexity': complexity,
            'parsing_method': 'words_format'
        }

    def _process_array_data(self, array_data: List, sentence: str, complexity: str) -> Dict[str, Any]:
        """Process array format responses"""
        if not array_data:
            return self._emergency_fallback(sentence, complexity, "Empty array response")

        # Assume it's word explanations array
        word_explanations = array_data
        colors = self.config.get_color_scheme(complexity)

        # Standardize format
        standardized_explanations = []
        for item in word_explanations:
            if isinstance(item, list) and len(item) >= 2:
                word, role = item[0], item[1]
                color = item[2] if len(item) > 2 else colors.get(role, '#808080')
                meaning = item[3] if len(item) > 3 else f"Basic {role} analysis"
                standardized_explanations.append([word, role, color, meaning])
            elif isinstance(item, dict):
                word = item.get('word', '')
                role = item.get('grammatical_role', '')
                color = colors.get(role, '#808080')
                meaning = item.get('meaning', f"Basic {role} analysis")
                standardized_explanations.append([word, role, color, meaning])

        confidence = self._calculate_confidence(standardized_explanations, sentence, 0.6)

        return {
            'word_explanations': standardized_explanations,
            'elements': {},
            'explanations': {
                'overall_structure': 'Array format analysis',
                'key_features': 'Basic grammatical breakdown'
            },
            'confidence_score': confidence,
            'sentence': sentence,
            'complexity': complexity,
            'parsing_method': 'array_format'
        }

    def _fallback_text_parse(self, response_text: str, sentence: str, complexity: str) -> Dict[str, Any]:
        """Fallback parsing for plain text responses"""
        # Extract word-role pairs from text
        word_explanations = []
        colors = self.config.get_color_scheme(complexity)

        # Simple pattern matching for word: role format
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line and len(line.split(':')) == 2:
                word, role = line.split(':', 1)
                word = word.strip()
                role = role.strip().lower()

                # Validate role
                if role in self.config.get_grammatical_roles(complexity):
                    color = colors.get(role, '#808080')
                    meaning = f"Text-parsed {role}"
                    word_explanations.append([word, role, color, meaning])

        if word_explanations:
            confidence = self._calculate_confidence(word_explanations, sentence, 0.5)
            return {
                'word_explanations': word_explanations,
                'elements': {},
                'explanations': {
                    'overall_structure': 'Text-parsed analysis',
                    'key_features': 'Basic role identification from text'
                },
                'confidence_score': confidence,
                'sentence': sentence,
                'complexity': complexity,
                'parsing_method': 'text_fallback'
            }

        # If no structured data found, use emergency fallback
        return self._emergency_fallback(sentence, complexity, "No parseable structure found")

    def _emergency_fallback(self, sentence: str, complexity: str, error_reason: str) -> Dict[str, Any]:
        """Emergency fallback: Basic word-by-word analysis"""
        words = sentence.split()
        colors = self.config.get_color_scheme(complexity)

        word_explanations = []
        for word in words:
            role = self._guess_basic_role(word)
            color = colors.get(role, '#808080')
            meaning = f"Emergency fallback: {role.replace('_', ' ')}"
            word_explanations.append([word, role, color, meaning])

        return {
            'word_explanations': word_explanations,
            'elements': {},
            'explanations': {
                'overall_structure': f'Emergency fallback analysis: {error_reason}',
                'key_features': 'Basic word-level grammatical identification'
            },
            'confidence_score': 0.3,
            'sentence': sentence,
            'complexity': complexity,
            'parsing_method': 'emergency_fallback',
            'error': error_reason
        }

    def _standardize_word_explanations(self, explanations: List, complexity: str) -> List[List]:
        """Standardize word explanations to consistent format"""
        standardized = []
        colors = self.config.get_color_scheme(complexity)
        valid_roles = set(self.config.get_grammatical_roles(complexity).keys())

        for item in explanations:
            if isinstance(item, list) and len(item) >= 2:
                word, role = item[0], item[1]
                color = item[2] if len(item) > 2 else colors.get(role, '#808080')
                meaning = item[3] if len(item) > 3 else f"Standardized {role} analysis"

                # Validate role
                if role not in valid_roles:
                    role = self._guess_basic_role(word)

                standardized.append([word, role, color, meaning])

            elif isinstance(item, dict):
                word = item.get('word', '')
                role = item.get('grammatical_role', '')
                color = item.get('color', colors.get(role, '#808080'))
                meaning = item.get('meaning', f"Standardized {role} analysis")

                # Validate role
                if role not in valid_roles:
                    role = self._guess_basic_role(word)

                standardized.append([word, role, color, meaning])

        return standardized

    def _standardize_elements(self, elements: Dict) -> Dict:
        """Standardize elements section"""
        standardized = {}
        for category, items in elements.items():
            if isinstance(items, list):
                standardized[category] = items
            else:
                standardized[category] = []
        return standardized

    def _standardize_explanations(self, explanations: Dict) -> Dict:
        """Standardize explanations section"""
        return {
            'overall_structure': explanations.get('overall_structure', 'Analysis completed'),
            'key_features': explanations.get('key_features', 'Grammatical features identified')
        }

    def _calculate_confidence(self, word_explanations: List, sentence: str, base_confidence: float) -> float:
        """Calculate confidence score for analysis"""
        if not word_explanations:
            return 0.0

        # Word coverage factor
        sentence_words = len(sentence.split())
        analyzed_words = len(word_explanations)
        coverage_ratio = min(analyzed_words / sentence_words, 1.0) if sentence_words > 0 else 0

        # Role validity factor
        valid_roles = set(self.config.get_grammatical_roles('advanced').keys())
        valid_count = sum(1 for item in word_explanations if len(item) > 1 and item[1] in valid_roles)
        validity_ratio = valid_count / analyzed_words if analyzed_words > 0 else 0

        # Explanation completeness factor
        complete_count = sum(1 for item in word_explanations if len(item) > 3 and item[3].strip())
        completeness_ratio = complete_count / analyzed_words if analyzed_words > 0 else 0

        # Weighted confidence calculation
        confidence = (
            base_confidence * 0.4 +      # Base AI confidence
            coverage_ratio * 0.3 +       # Word coverage
            validity_ratio * 0.2 +       # Role validity
            completeness_ratio * 0.1     # Explanation completeness
        )

        return round(confidence, 2)

    def _guess_basic_role(self, word: str) -> str:
        """Guess basic grammatical role for fallback"""
        word_lower = word.lower().strip('.,!?')

        # Language-specific patterns (customize for your language)
        patterns = {
            'noun': [],  # Add common noun patterns
            'verb': [],  # Add common verb endings/patterns
            'adjective': [],  # Add common adjective patterns
            'adverb': [],  # Add common adverb patterns
            'pronoun': [],  # Add common pronouns
            'preposition': [],  # Add common prepositions
            'conjunction': [],  # Add common conjunctions
            'determiner': []  # Add common determiners/articles
        }

        # Check patterns
        for role, role_patterns in patterns.items():
            if any(pattern in word_lower for pattern in role_patterns):
                return role

        # Default to noun (most common fallback)
        return 'noun'

    def _process_word_explanations_with_role_consistency(self, words_data: List[Dict], complexity: str) -> List[List]:
        """
        Process word explanations with role consistency (Arabic Analyzer Innovation)
        
        CRITICAL FEATURES:
        - Apply complexity-based role filtering using role hierarchy
        - Ensure meaning text matches display role to eliminate grammatical repetition
        - Use parent roles for color inheritance while showing specific roles in explanations
        - Follow standardized format: "WORD (DISPLAY_ROLE): meaning — function"
        """
        processed_explanations = []
        
        # Get color scheme for complexity level
        color_scheme = self.config.get_color_scheme(complexity)
        grammatical_roles = self.config.get_grammatical_roles(complexity)
        
        for word_data in words_data:
            word = word_data.get('word', '')
            
            # Handle both old format (grammatical_role) and new AI format (role)
            role_key = (word_data.get('grammatical_roles') or 
                       word_data.get('grammatical_role') or
                       word_data.get('role', 'other'))
            if role_key is None:
                role_key = 'other'
            if isinstance(role_key, list):
                role_key = role_key[-1] if role_key else 'other'
            
            meaning = word_data.get('meaning', '')
            
            # Normalize role key
            normalized_role = self._normalize_grammatical_role(role_key)
            
            # Apply complexity-based role filtering
            if not self.config.should_show_role(normalized_role, complexity):
                display_role = self.config.get_parent_role(normalized_role)
            else:
                display_role = normalized_role
            
            # Get color for role - use parent role for color inheritance
            parent_role = self.config.get_parent_role(normalized_role)
            color = color_scheme.get(parent_role, color_scheme.get('other', '#708090'))
            
            # Get display name for role
            role_display = grammatical_roles.get(display_role, display_role)
            
            # CRITICAL: Update meaning to use display_role instead of original AI role
            if meaning and '(' in meaning and ')' in meaning:
                import re
                role_pattern = r'^([^\s]+)\s*\(([^)]+)\):\s*(.+)$'
                match = re.match(role_pattern, meaning.strip())
                if match:
                    word_part, original_role, rest_meaning = match.groups()
                    # Replace with display_role to eliminate repetition
                    updated_meaning = f"{word_part} ({display_role}): {rest_meaning}"
                    meaning = updated_meaning
            
            # Create explanation tuple: [word, role_display, color, meaning]
            explanation = [word, role_display, color, meaning]
            processed_explanations.append(explanation)
        
        return processed_explanations

    def _normalize_grammatical_role(self, role: str) -> str:
        """Normalize grammatical role to standard format"""
        if not role:
            return 'other'
        
        # Convert to lowercase and replace spaces/hyphens with underscores
        normalized = role.lower().replace(' ', '_').replace('-', '_')
        
        # Map common variations to standard roles
        role_mappings = {
            'noun_phrase': 'noun',
            'verb_phrase': 'verb',
            'adjective_phrase': 'adjective',
            'adverb_phrase': 'adverb',
            'prepositional_phrase': 'preposition',
            'conj': 'conjunction',
            'prep': 'preposition',
            'adv': 'adverb',
            'adj': 'adjective',
            'n': 'noun',
            'v': 'verb',
            'pron': 'pronoun',
            'det': 'determiner',
            'art': 'article'
        }
        
        return role_mappings.get(normalized, normalized)
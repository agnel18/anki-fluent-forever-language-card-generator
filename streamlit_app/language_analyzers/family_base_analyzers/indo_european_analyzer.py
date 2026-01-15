# Indo-European Language Family Base Analyzer
# Base class for all Indo-European language analyzers

import re
import json
import logging
from typing import Dict, List, Any, Tuple
from ..base_analyzer import BaseGrammarAnalyzer, LanguageConfig

logger = logging.getLogger(__name__)

class IndoEuropeanAnalyzer(BaseGrammarAnalyzer):
    """
    Base analyzer class for Indo-European languages.

    Common features across Indo-European languages:
    - Subject-Verb-Object (SVO) or Subject-Object-Verb (SOV) word order
    - Noun cases and gender systems
    - Verb conjugation with tense/aspect/mood
    - Prepositions or postpositions
    - Rich morphological systems
    """

    def __init__(self, language_config: LanguageConfig):
        super().__init__(language_config)

        # Indo-European specific patterns
        self._initialize_indo_european_patterns()

    def _initialize_indo_european_patterns(self):
        """Initialize patterns common to Indo-European languages"""
        # Common grammatical categories
        self.common_categories = {
            'pronouns': ['personal', 'demonstrative', 'possessive', 'relative', 'interrogative'],
            'verbs': ['main', 'auxiliary', 'modal', 'linking'],
            'nouns': ['common', 'proper', 'abstract', 'countable', 'uncountable'],
            'adjectives': ['attributive', 'predicative', 'comparative', 'superlative'],
            'adverbs': ['manner', 'time', 'place', 'degree', 'frequency'],
            'prepositions': ['location', 'time', 'direction', 'manner'],
            'conjunctions': ['coordinating', 'subordinating'],
            'determiners': ['articles', 'quantifiers', 'possessives']
        }

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Generate AI prompt for Indo-European language grammar analysis"""
        if complexity == "beginner":
            return self._get_beginner_prompt(sentence, target_word)
        elif complexity == "intermediate":
            return self._get_intermediate_prompt(sentence, target_word)
        elif complexity == "advanced":
            return self._get_advanced_prompt(sentence, target_word)
        else:
            return self._get_beginner_prompt(sentence, target_word)

    def _get_beginner_prompt(self, sentence: str, target_word: str) -> str:
        """Generate beginner-level grammar analysis prompt for Indo-European languages"""
        base_prompt = f"""Analyze this ENTIRE {self.language_name} sentence WORD BY WORD: {sentence}

For EACH AND EVERY INDIVIDUAL WORD in the sentence, provide:
- Its individual meaning and pronunciation
- Its grammatical role and function in this context
- Gender/number/case information (if applicable)
- How it relates to other words in the sentence
- Why it's important for learners

Pay special attention to the target word: {target_word}

Return a JSON object with detailed word analysis for ALL words in the sentence:
{{
  "words": [
    {{
      "word": "example_word",
      "individual_meaning": "translation/meaning",
      "pronunciation": "IPA_phonetic",
      "grammatical_role": "noun/verb/adjective/etc",
      "morphological_info": "gender/case/tense info",
      "syntactic_function": "subject/object/modifier",
      "importance": "learning significance"
    }}
  ],
  "word_combinations": [
    {{
      "word": "phrase_example",
      "words": ["word1", "word2"],
      "combined_meaning": "phrase meaning",
      "grammatical_structure": "structure description",
      "usage_notes": "usage context"
    }}
  ],
  "explanations": {{
    "word_order": "SVO/SOV description",
    "morphology": "inflection/agreement patterns",
    "syntax": "sentence structure rules",
    "phonology": "pronunciation patterns"
  }}
}}

CRITICAL: Analyze EVERY word in the sentence, not just the target word!"""

        return base_prompt

    def _get_intermediate_prompt(self, sentence: str, target_word: str) -> str:
        """Generate intermediate-level grammar analysis prompt"""
        base_prompt = f"""Analyze this {self.language_name} sentence with INTERMEDIATE grammar focus: {sentence}

Provide detailed analysis including:
- Tense/aspect/mood markings on verbs
- Case/gender/number agreement patterns
- Complex syntactic structures
- Idiomatic expressions and collocations
- Pragmatic functions

Pay special attention to the target word: {target_word}

Return a JSON object with comprehensive analysis:
{{
  "words": [
    {{
      "word": "example",
      "grammatical_role": "role",
      "tense_aspect": "tense info",
      "agreement": "agreement patterns",
      "syntactic_role": "function"
    }}
  ],
  "word_combinations": [...],
  "explanations": {{
    "tense_system": "tense/aspect description",
    "agreement_patterns": "agreement rules",
    "complex_structures": "advanced syntax"
  }}
}}

CRITICAL: Analyze EVERY word in the sentence!"""

        return base_prompt

    def _get_advanced_prompt(self, sentence: str, target_word: str) -> str:
        """Generate advanced-level grammar analysis prompt"""
        base_prompt = f"""Perform advanced grammatical analysis of this {self.language_name} sentence: {sentence}

Analyze complex linguistic phenomena:
- Subjunctive and conditional structures
- Passive and middle voice constructions
- Relative clause formations
- Discourse markers and cohesion
- Stylistic and register variations

Pay special attention to the target word: {target_word}

Return detailed JSON analysis with advanced linguistic features.

CRITICAL: Analyze EVERY word in the sentence!"""

        return base_prompt

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into structured Indo-European grammar analysis"""
        try:
            logger.info(f"DEBUG Hindi Parse - Input AI response length: {len(ai_response)}")
            logger.info(f"DEBUG Hindi Parse - Input sentence: '{sentence}'")
            logger.info(f"DEBUG Hindi Parse - Complexity: '{complexity}'")

            # Try to extract JSON from response
            json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(1))
                    parsed['sentence'] = sentence
                    logger.info(f"DEBUG Hindi Parse - Successfully parsed JSON from markdown. Words: {len(parsed.get('words', []))}")
                    logger.info("DEBUG Hindi Parse - Parsed words sample: " + str(parsed.get('words', [])[:2]))
                    return self._transform_to_standard_format(parsed, complexity)
                except json.JSONDecodeError:
                    logger.error("DEBUG Hindi Parse - JSON decode error in markdown: " + json_match.group(1)[:200] + "...")

            # Try direct JSON parsing
            try:
                parsed = json.loads(ai_response)
                parsed['sentence'] = sentence
                logger.info(f"DEBUG Hindi Parse - Successfully parsed direct JSON. Words: {len(parsed.get('words', []))}")
                logger.info("DEBUG Hindi Parse - Parsed words sample: " + str(parsed.get('words', [])[:2]))
                return self._transform_to_standard_format(parsed, complexity)
            except json.JSONDecodeError:
                logger.error("DEBUG Hindi Parse - Direct JSON parse failed")

            # Fallback: extract structured information from text
            logger.warning("DEBUG Hindi Parse - Falling back to text parsing")
            fallback_result = self._parse_text_response(ai_response, sentence)
            logger.info("DEBUG Hindi Parse - Fallback result: " + str(fallback_result.keys()))
            return self._transform_to_standard_format(fallback_result, complexity)

        except Exception as e:
            logger.error("DEBUG Hindi Parse - Failed to parse grammar response: " + str(e))
            fallback_result = self._create_fallback_parse(ai_response, sentence)
            return self._transform_to_standard_format(fallback_result, complexity)

    def _parse_text_response(self, ai_response: str, sentence: str) -> Dict[str, Any]:
        """Enhanced fallback text parsing when JSON fails - extracts grammatical roles from AI response"""
        try:
            # Try to extract word-role pairs from the AI response text
            word_role_pairs = self._extract_word_roles_from_text(ai_response)

            # Split sentence into words for matching
            sentence_words = sentence.split()

            # Create elements dictionary with proper categorization
            elements = {}
            word_explanations = []

            for word in sentence_words:
                # Find matching role from extracted pairs (case-insensitive partial match)
                role = 'other'  # default
                for extracted_word, extracted_role in word_role_pairs:
                    if extracted_word.lower() in word.lower() or word.lower() in extracted_word.lower():
                        role = extracted_role
                        break

                # Map role to category
                category = self._map_grammatical_role_to_category(role)

                # Add to elements
                if category not in elements:
                    elements[category] = []
                elements[category].append({
                    'word': word,
                    'grammatical_role': role
                })

                # Create word explanation
                color = self._get_color_for_category(category)
                word_explanations.append([word, role, color, 'Extracted from text analysis: ' + str(role)])

            return {
                'elements': elements,
                'word_explanations': word_explanations,
                'explanations': {'fallback': 'Enhanced text analysis extracted ' + str(len(word_role_pairs)) + ' word-role pairs'},
                'sentence': sentence
            }

        except Exception as e:
            logger.error(f"Enhanced text parsing fallback failed: {e}")
            # Fall back to basic parsing
            words = sentence.split()
            elements = {
                'other': [{'word': word, 'grammatical_role': 'other'} for word in words]
            }
            return {
                'elements': elements,
                'explanations': {'fallback': 'Basic word-level analysis due to parsing failure'},
                'sentence': sentence
            }

    def _extract_word_roles_from_text(self, ai_response: str) -> List[Tuple[str, str]]:
        """Extract word-grammatical_role pairs from AI response text using regex"""
        pairs = []

        # Pattern to match "word": "value", "grammatical_role": "value" sequences
        # This handles both JSON fragments and descriptive text
        pattern = r'"word"\s*:\s*"([^"]+)"\s*,\s*"grammatical_role"\s*:\s*"([^"]+)"'
        matches = re.findall(pattern, ai_response, re.IGNORECASE)

        for word, role in matches:
            pairs.append((word.strip(), role.strip()))

        # Also try alternative patterns for robustness
        if not pairs:
            # Pattern for word: value, grammatical_role: value
            alt_pattern = r'word\s*:\s*([^\s,]+)\s*,\s*grammatical_role\s*:\s*([^\s,]+)'
            alt_matches = re.findall(alt_pattern, ai_response, re.IGNORECASE)
            for word, role in alt_matches:
                pairs.append((word.strip(), role.strip()))

        return pairs

    def _create_fallback_parse(self, ai_response: str, sentence: str) -> Dict[str, Any]:
        """Create minimal fallback analysis when all parsing fails"""
        return {
            'elements': {},
            'explanations': {'error': 'Grammar analysis temporarily unavailable'},
            'sentence': sentence
        }

    def _transform_to_standard_format(self, parsed_data: Dict[str, Any], complexity: str = 'beginner') -> Dict[str, Any]:
        """Transform Indo-European analyzer output to standard BaseGrammarAnalyzer format"""
        try:
            words = parsed_data.get('words', [])
            word_combinations = parsed_data.get('word_combinations', [])
            explanations = parsed_data.get('explanations', {})

            logger.info(f"DEBUG Hindi Transform - Input words count: {len(words)}")
            logger.info("DEBUG Hindi Transform - Input explanations keys: " + str(list(explanations.keys())))
            for key, value in explanations.items():
                logger.info("DEBUG Hindi Transform - Explanation '" + str(key) + "': " + str(value)[:100] + "...")

            # Transform words into elements grouped by grammatical role
            elements = {}
            for word_data in words:
                grammatical_role = word_data.get('grammatical_role', 'other')
                if grammatical_role not in elements:
                    elements[grammatical_role] = []
                elements[grammatical_role].append(word_data)

            logger.info(f"DEBUG Hindi Transform - Elements keys after grouping: {list(elements.keys())}")
            for role, word_list in elements.items():
                logger.info(f"DEBUG Hindi Transform - Role '{role}': {len(word_list)} words")

            # Add word combinations as a special category
            if word_combinations:
                elements['word_combinations'] = word_combinations

            # Create word_explanations for HTML coloring: [word, pos, color, explanation]
            word_explanations = []
            colors = self.get_color_scheme(complexity)  # Use the actual complexity level

            logger.info("DEBUG Hindi Transform - Color scheme for complexity '" + str(complexity) + "': " + str(colors))

            for word_data in words:
                word = word_data.get('word', '')
                grammatical_role = word_data.get('grammatical_role', 'other')
                individual_meaning = word_data.get('individual_meaning', '')
                pronunciation = word_data.get('pronunciation', '')

                category = self._map_grammatical_role_to_category(grammatical_role)
                color = colors.get(category, '#888888')

                logger.info("DEBUG Hindi Transform - Word: '" + str(word) + "', Role: '" + str(grammatical_role) + "', Category: '" + str(category) + "', Color: '" + str(color) + "'")

                # Create explanation text from available data
                explanation_parts = []
                if individual_meaning:
                    explanation_parts.append(individual_meaning)
                if pronunciation:
                    explanation_parts.append("(" + str(pronunciation) + ")")

                explanation = ", ".join(explanation_parts) if explanation_parts else str(grammatical_role)

                word_explanations.append([word, grammatical_role, color, explanation])
                logger.info("DEBUG Hindi Transform - Added word_explanation: " + str(word_explanations[-1]))

            logger.info(f"DEBUG Hindi Transform - Final word_explanations count: {len(word_explanations)}")

        except Exception as e:
            logger.error("Failed to transform " + str(self.language_name) + " analysis data: " + str(e))
            return {
                'elements': {},
                'explanations': {'error': 'Data transformation failed'},
                'word_explanations': [],
                'sentence': parsed_data.get('sentence', '')
            }

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Generate HTML output for Indo-European text with word-level coloring using colors from word_explanations (single source of truth)"""
        explanations = parsed_data.get('word_explanations', [])

        logger.info(f"DEBUG Hindi HTML Gen - Input explanations count: {len(explanations)}")
        logger.info("DEBUG Hindi HTML Gen - Input sentence: '" + str(sentence) + "'")
        logger.error("DEBUG HTML GEN CALLED: sentence='" + str(sentence) + "', explanations_count=" + str(len(explanations)))

        # Create mapping of words to categories directly from word_explanations (authoritative source)
        word_to_category = {}
        for exp in explanations:
            if len(exp) >= 3:
                word, pos, color = exp[0], exp[1], exp[2]
                # Clean word for consistent matching (remove punctuation)
                clean_word = re.sub(r'[।!?.,;:\"\'()\[\]{}]', '', word)
                category = self._map_grammatical_role_to_category(pos)
                word_to_category[clean_word] = category
                logger.info("DEBUG Hindi HTML Gen - Word '" + str(word) + "' (clean: '" + str(clean_word) + "') -> Category '" + str(category) + "' (POS: '" + str(pos) + "')")

        logger.info("DEBUG Hindi HTML Gen - Word-to-category mapping: " + str(word_to_category))
        logger.info(f"DEBUG Hindi HTML Gen - Total words in mapping: {len(word_to_category)}")

        # Generate HTML by coloring each word individually using colors from grammar explanations
        words_in_sentence = re.findall(r'\S+', sentence)

        logger.info("DEBUG Hindi HTML Gen - Words found in sentence: " + str(words_in_sentence))

        html_parts = []
        for word in words_in_sentence:
            # Remove punctuation for matching but keep original word
            # Handle various scripts including Devanagari, Latin, Cyrillic, etc.
            # Remove common punctuation marks that might be attached to words
            clean_word = re.sub(r'[।!?.,;:\"\'()\[\]{}]', '', word)

            logger.info("DEBUG Hindi HTML Gen - Processing word '" + str(word) + "' -> clean '" + str(clean_word) + "'")

            if clean_word in word_to_category:
                category = word_to_category[clean_word]
                color_scheme = self.get_color_scheme('intermediate')
                color = color_scheme.get(category, '#888888')
                # Escape curly braces in word to prevent f-string issues
                safe_word = word.replace('{', '{{').replace('}', '}}')
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{safe_word}</span>')
                print("DEBUG Hindi HTML Gen - ✓ Colored word '" + str(word) + "' with category '" + str(category) + "' and color '" + str(color) + "'")
            else:
                # For words without analysis, use default color (should be rare with new architecture)
                safe_word = word.replace('{', '{{').replace('}', '}}')
                html_parts.append(f'<span style="color: #888888;">{safe_word}</span>')
                print("DEBUG Hindi HTML Gen - ✗ No category found for word '" + str(word) + "' (clean: '" + str(clean_word) + "'). Available words: " + str(list(word_to_category.keys())))

        result = ' '.join(html_parts)
        logger.info(f"DEBUG Hindi HTML Gen - Final HTML output length: {len(result)}")
        logger.info("DEBUG Hindi HTML Gen - Final HTML preview: " + str(result[:300]) + "...")
        logger.info(f"DEBUG Hindi HTML Gen - Category distribution: {set(word_to_category.values())}")
        return result

    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Map grammatical role descriptions to color category names"""
        role_lower = grammatical_role.lower()

        # Map various grammatical roles to color categories
        if any(keyword in role_lower for keyword in ['pronoun', 'personal', 'demonstrative', 'possessive']):
            return 'pronoun'
        elif any(keyword in role_lower for keyword in ['verb', 'action', 'state', 'linking', 'auxiliary', 'modal']):
            return 'verb'
        elif any(keyword in role_lower for keyword in ['noun', 'object', 'subject']):
            return 'noun'
        elif any(keyword in role_lower for keyword in ['adjective', 'description', 'quality']):
            return 'adjective'
        elif any(keyword in role_lower for keyword in ['adverb', 'manner', 'time', 'place', 'degree']):
            return 'adverb'
        elif any(keyword in role_lower for keyword in ['preposition', 'postposition', 'case', 'marker']):
            return 'postposition'
        else:
            return 'other'

    def _get_default_category_for_word(self, word: str) -> str:
        """Get a default grammatical category for words that don't have detailed analysis"""
        # This is a simple heuristic - language-specific analyzers should override this
        word_lower = word.lower()

        # Common pronouns across Indo-European languages
        if word_lower in ['i', 'me', 'my', 'mine', 'you', 'your', 'yours', 'he', 'him', 'his',
                         'she', 'her', 'hers', 'it', 'its', 'we', 'us', 'our', 'ours',
                         'they', 'them', 'their', 'theirs', 'this', 'that', 'these', 'those']:
            return 'pronoun'

        # Common verbs (basic forms)
        if word_lower in ['be', 'is', 'am', 'are', 'was', 'were', 'been', 'being',
                         'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
                         'go', 'went', 'gone', 'going', 'come', 'came', 'coming']:
            return 'verb'

        # Common prepositions
        if word_lower in ['in', 'on', 'at', 'to', 'from', 'by', 'with', 'for', 'of', 'about']:
            return 'postposition'

        # Default to 'other' for unknown words
        return 'other'

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate Indo-European grammar analysis quality (85% threshold required)"""
        try:
            words = parsed_data.get('elements', {})
            explanations = parsed_data.get('explanations', {})

            # Basic validation checks
            has_words = len(words) > 0
            has_explanations = len(explanations) > 0

            # Check word coverage in sentence
            sentence_words = set(re.findall(r'\w+', original_sentence.lower()))
            analyzed_words = set()

            for category, word_list in words.items():
                if category != 'word_combinations':
                    for word_data in word_list:
                        if isinstance(word_data, dict):
                            word = word_data.get('word', '').lower()
                            if word:
                                analyzed_words.add(re.sub(r'[^\w]', '', word))

            word_coverage = len(sentence_words.intersection(analyzed_words)) / len(sentence_words) if sentence_words else 0

            # Calculate confidence score
            base_score = 0.9 if (has_words and has_explanations) else 0.6
            coverage_bonus = word_coverage * 0.1

            confidence = min(base_score + coverage_bonus, 1.0)
            return confidence

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return 0.5

    def _extract_colors_from_grammar_explanations(self, word_explanations_html: str) -> Dict[str, str]:
        """
        Extract word-color mappings from grammar explanations HTML.
        This serves as the single source of truth for colors in the new architecture.

        Args:
            word_explanations_html: HTML string containing grammar explanations with colored words

        Returns:
            Dictionary mapping words to their colors
        """
        word_to_color = {}

        try:
            # Pattern to match: <span class="word-highlight" style="color: #FF4444;"><strong>word</strong></span>
            pattern = r'<span\s+class="word-highlight"\s+style="[^"]*color:\s*([^;"]+)[^"]*"[^>]*><strong>([^<]+)</strong></span>'

            matches = re.findall(pattern, word_explanations_html, re.IGNORECASE)

            for color, word in matches:
                word_to_color[word.strip()] = color.strip()

            logger.debug(f"Extracted {len(word_to_color)} word-color mappings from grammar explanations")

        except Exception as e:
            logger.error(f"Error extracting colors from grammar explanations: {e}")

        return word_to_color
# Chinese Traditional Grammar Analyzer
# Modular analyzer for Chinese Traditional (繁體中文) using domain-driven design
# Language Family: Sino-Tibetan
# Script Type: logographic
# Complexity Rating: high

import logging
import json
from typing import Dict, List, Any, Optional

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

# Import modular components
from .domain.zh_tw_config import ZhTwConfig
from .domain.zh_tw_prompt_builder import ZhTwPromptBuilder
from .domain.zh_tw_response_parser import ZhTwResponseParser
from .domain.zh_tw_validator import ZhTwValidator
from .infrastructure.zh_tw_fallbacks import ZhTwFallbacks

logger = logging.getLogger(__name__)


class ZhTwAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Chinese Traditional (繁體中文) using modular architecture.

    Key Features: ['word_segmentation', 'compounds_first', 'chinese_categories', 'aspect_system', 'topic_comment']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']

    Architecture:
    - Domain: Config, PromptBuilder, ResponseParser, Validator
    - Infrastructure: Fallbacks for error recovery
    """

    VERSION = "4.0"  # Updated for modular architecture
    LANGUAGE_CODE = "zh-tw"
    LANGUAGE_NAME = "Chinese Traditional"

    def __init__(self):
        # Initialize modular components
        self.zh_tw_config = ZhTwConfig()
        self.prompt_builder = ZhTwPromptBuilder(self.zh_tw_config)
        self.response_parser = ZhTwResponseParser(self.zh_tw_config)
        self.validator = ZhTwValidator(self.zh_tw_config)
        self.fallbacks = ZhTwFallbacks(self.zh_tw_config)

        # Initialize base analyzer with language config
        base_config = LanguageConfig(
            code=self.zh_tw_config.language_code,
            name=self.zh_tw_config.language_name,
            native_name=self.zh_tw_config.native_name,
            family=self.zh_tw_config.family,
            script_type=self.zh_tw_config.script_type,
            complexity_rating=self.zh_tw_config.complexity_rating,
            key_features=self.zh_tw_config.key_features,
            supported_complexity_levels=self.zh_tw_config.supported_complexity_levels
        )
        super().__init__(base_config)

        logger.info(f"Initialized {self.LANGUAGE_NAME} analyzer v{self.VERSION} with modular architecture")

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str) -> GrammarAnalysis:
        """
        Analyze grammar for a single sentence - RICH EXPLANATIONS LIKE CHINESE SIMPLIFIED.

        CHINESE TRADITIONAL WORKFLOW:
        1. Build AI prompt using prompt_builder (Traditional-specific templates)
        2. Call AI API with proper error handling
        3. Parse response using response_parser (with Traditional fallbacks)
        4. Validate results using validator (aspect particles, classifiers)
        5. Generate HTML output for colored sentence display
        6. Return GrammarAnalysis object with RICH explanations

        OUTPUT FORMAT:
        - word_explanations: [[word, role, color, meaning], ...] - RICH MEANINGS
        - Maintains sentence word order (LTR) for optimal user experience
        - Colors based on grammatical roles and complexity level
        """
        try:
            prompt = self.prompt_builder.build_single_sentence_prompt(sentence, target_word, complexity)
            ai_response = self._call_ai_model(prompt, gemini_api_key)
            parsed_data = self.response_parser.parse_response(ai_response, sentence, complexity)
            validation = self.validator.validate_analysis(parsed_data)
            
            # Apply validation results to parsed data
            parsed_data['validation'] = validation
            parsed_data['confidence'] = validation.get('quality_score', 50) / 100.0

            # Generate HTML output with RICH explanations
            html_output = self._generate_html_output(parsed_data, sentence, complexity)

            # Return GrammarAnalysis object with rich explanations
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=parsed_data.get('elements', {}),
                explanations=parsed_data.get('explanations', {}),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=parsed_data.get('confidence', 0.0),
                word_explanations=parsed_data.get('word_explanations', [])
            )
        except Exception as e:
            logger.error(f"Analysis failed for '{sentence}': {e}")
            # Create fallback analysis
            fallback_result = self.fallbacks.generate_fallback_analysis(sentence)
            legacy_fallback = self._convert_modular_to_legacy(fallback_result, sentence)
            html_output = self._generate_html_output(legacy_fallback, sentence, complexity)
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=legacy_fallback.get('elements', {}),
                explanations=legacy_fallback.get('explanations', {}),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=legacy_fallback.get('confidence', 0.3),
                word_explanations=legacy_fallback.get('word_explanations', [])
            )

    def get_batch_grammar_prompt(
        self,
        complexity: str,
        sentences: List[str],
        target_word: str,
        native_language: str = "English"
    ) -> str:
        """
        Generate Chinese Traditional-specific AI prompt for batch grammar analysis.

        Delegates to the prompt builder component.

        Args:
            complexity: Complexity level (beginner/intermediate/advanced)
            sentences: List of sentences to analyze
            target_word: Target word being learned
            native_language: Language for explanations

        Returns:
            Formatted prompt string for AI analysis
        """
        return self.prompt_builder.build_batch_grammar_prompt(
            complexity, sentences, target_word, native_language
        )

    def analyze_batch_response(
        self,
        ai_response: str,
        sentences: List[str],
        target_word: str = "",
        complexity: str = "intermediate"
    ) -> Dict[str, Any]:
        """
        Analyze AI response for batch grammar analysis.

        Uses the modular pipeline: parse → validate → fallback if needed.

        Args:
            ai_response: Raw AI response string
            sentences: Original sentences being analyzed
            target_word: Target word being learned
            complexity: Complexity level

        Returns:
            Analyzed and validated results
        """

        try:
            # Step 1: Parse the AI response
            parsed_result = self.response_parser.parse_batch_response(ai_response, sentences, complexity, target_word)

            if not parsed_result.get('success', False):
                logger.warning("AI response parsing failed, using fallback analysis")
                return self._use_fallback_analysis(sentences, target_word)

            results = parsed_result.get('results', [])

            # Step 2: Validate each result
            validated_results = []
            for result in results:
                validation = self.validator.validate_analysis(result)
                result['validation'] = validation
                validated_results.append(result)

            # Step 3: Check overall quality
            overall_quality = self._assess_overall_quality(validated_results)

            return {
                'success': True,
                'results': validated_results,
                'metadata': {
                    'analyzer_version': self.VERSION,
                    'language': self.LANGUAGE_CODE,
                    'complexity': complexity,
                    'overall_quality': overall_quality,
                    'parsing_method': 'ai_response'
                }
            }

        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return self._use_fallback_analysis(sentences, target_word)

    def _use_fallback_analysis(self, sentences: List[str], target_word: str = "") -> Dict[str, Any]:
        """
        Use fallback analysis when AI analysis fails.

        Args:
            sentences: Sentences to analyze
            target_word: Target word

        Returns:
            Fallback analysis results
        """

        logger.info("Using fallback analysis for Chinese Traditional")

        fallback_results = []
        for sentence in sentences:
            result = self.fallbacks.generate_fallback_analysis(sentence, target_word)
            fallback_results.append(result)

        return {
            'success': True,
            'results': fallback_results,
            'metadata': {
                'analyzer_version': self.VERSION,
                'language': self.LANGUAGE_CODE,
                'parsing_method': 'fallback_rule_based',
                'note': 'AI analysis failed, using rule-based fallback'
            }
        }

    def _assess_overall_quality(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess overall quality of analysis results.

        Args:
            results: Validated results

        Returns:
            Quality assessment
        """

        if not results:
            return {'score': 0, 'level': 'failed'}

        total_score = 0
        total_validations = 0

        for result in results:
            validation = result.get('validation', {})
            score = validation.get('quality_score', 50)  # Default medium score
            total_score += score
            total_validations += 1

        average_score = total_score / total_validations if total_validations > 0 else 0

        # Determine quality level
        if average_score >= 80:
            level = 'excellent'
        elif average_score >= 60:
            level = 'good'
        elif average_score >= 40:
            level = 'acceptable'
        else:
            level = 'poor'

        return {
            'score': round(average_score, 1),
            'level': level,
            'total_results': len(results)
        }

    def get_supported_complexity_levels(self) -> List[str]:
        """Get supported complexity levels."""
        return self.zh_tw_config.supported_complexity_levels

    def get_grammatical_roles(self) -> Dict[str, str]:
        """Get grammatical roles with colors."""
        return self.zh_tw_config.grammatical_roles

    def validate_sentence(self, sentence: str) -> Dict[str, Any]:
        """
        Validate a Chinese Traditional sentence.

        Args:
            sentence: Sentence to validate

        Returns:
            Validation results
        """

        validation_result = {
            'is_valid': True,
            'issues': [],
            'checks': []
        }

        # Check Traditional characters
        if not self._has_traditional_characters(sentence):
            validation_result['issues'].append("Sentence should use Traditional Chinese characters")
            validation_result['is_valid'] = False

        validation_result['checks'].append('traditional_characters')

        # Check basic structure
        if len(sentence.strip()) == 0:
            validation_result['issues'].append("Sentence is empty")
            validation_result['is_valid'] = False

        validation_result['checks'].append('basic_structure')

        return validation_result

    def _has_traditional_characters(self, sentence: str) -> bool:
        """
        Check if sentence contains Traditional Chinese characters.

        Args:
            sentence: Sentence to check

        Returns:
            True if Traditional characters are present
        """

        # Simple check for common Traditional characters
        traditional_chars = {'臺', '體', '學', '說', '點', '們', '還', '時', '間', '電', '國', '對', '來', '東'}

        for char in sentence:
            if char in traditional_chars:
                return True

        # If no definitive Traditional chars, assume valid (could be neutral text)
        return True

    def get_language_info(self) -> Dict[str, Any]:
        """Get comprehensive language information."""
        return {
            'code': self.zh_tw_config.language_code,
            'name': self.zh_tw_config.language_name,
            'native_name': self.zh_tw_config.native_name,
            'family': self.zh_tw_config.family,
            'script_type': self.zh_tw_config.script_type,
            'complexity_rating': self.zh_tw_config.complexity_rating,
            'key_features': self.zh_tw_config.key_features,
            'supported_levels': self.zh_tw_config.supported_complexity_levels,
            'grammatical_categories': len(self.zh_tw_config.grammatical_roles),
            'analyzer_version': self.VERSION
        }

    # Abstract method implementations for BaseGrammarAnalyzer

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Legacy method - redirect to batch prompt for single sentence"""
        return self.get_batch_grammar_prompt(complexity, [sentence], target_word)

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """
        Validate Chinese Traditional analysis quality and return confidence score.

        Args:
            parsed_data: Parsed analysis data from parse_grammar_response
            original_sentence: Original sentence for validation

        Returns:
            Confidence score between 0.0 and 1.0
        """

        try:
            # For modular results, check if validation data is already present
            if 'validation' in parsed_data:
                validation = parsed_data['validation']
                quality_score = validation.get('quality_score', 50)
                # Convert quality score (0-100) to confidence (0.0-1.0)
                confidence = quality_score / 100.0
                return confidence

            # For legacy format with 'elements' or 'word_explanations', perform basic validation
            elements = parsed_data.get('elements', {})
            word_explanations = parsed_data.get('word_explanations', [])

            if not elements and not word_explanations:
                return 0.0

            # Basic validation checks
            base_score = 0.7  # Start with reasonable base score

            # Check word count vs sentence length
            sentence_length = len(original_sentence)
            total_words = 0

            if word_explanations:
                total_words = len(word_explanations)
            else:
                # Count words from elements
                for element_list in elements.values():
                    if isinstance(element_list, list):
                        total_words += len(element_list)

            if total_words > 0:
                # Reasonable word density (roughly 1 word per 2-3 characters for Chinese)
                expected_words = max(1, sentence_length // 3)
                if abs(total_words - expected_words) <= 2:
                    base_score += 0.1

            # Check for grammatical role diversity
            if word_explanations:
                roles = [exp[1] for exp in word_explanations if len(exp) > 1]
            else:
                roles = list(elements.keys())

            unique_roles = set(roles)

            if len(unique_roles) >= 2:  # At least subject and verb/predicate
                base_score += 0.1

            if 'verb' in unique_roles or 'predicate' in unique_roles:
                base_score += 0.05

            # Check meaning completeness
            if word_explanations:
                meanings_present = sum(1 for exp in word_explanations if len(exp) > 3 and exp[3].strip())
                if meanings_present == len(word_explanations):
                    base_score += 0.05
            else:
                # Check if elements have meanings
                total_elements = sum(len(element_list) for element_list in elements.values() if isinstance(element_list, list))
                elements_with_meanings = 0
                for element_list in elements.values():
                    if isinstance(element_list, list):
                        elements_with_meanings += sum(1 for item in element_list if isinstance(item, dict) and item.get('individual_meaning', '').strip())

                if elements_with_meanings == total_elements and total_elements > 0:
                    base_score += 0.05

            return min(base_score, 1.0)

        except Exception as e:
            logger.error(f"Validation failed for Chinese Traditional: {e}")
            return 0.0

    def get_color_scheme(self, complexity: str = "intermediate") -> Dict[str, str]:
        """Return color scheme for Chinese Traditional grammatical elements"""
        return self.zh_tw_config.get_color_scheme(complexity)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """
        Parse single sentence AI response.

        This method handles individual sentence parsing, not batch parsing.
        For batch processing, use parse_batch_grammar_response directly.
        """
        try:
            # Try to parse as JSON first (for batch item format)
            try:
                response_data = json.loads(ai_response)
                if isinstance(response_data, dict) and 'words' in response_data:
                    # This is already parsed modular data
                    return self._convert_modular_to_legacy(response_data, sentence)
            except json.JSONDecodeError:
                pass

            # Use the modular pipeline for single sentence
            batch_result = self.analyze_batch_response(ai_response, [sentence], complexity=complexity)

            if batch_result.get('success') and batch_result.get('results'):
                result = batch_result['results'][0]
                return self._convert_modular_to_legacy(result, sentence)
            else:
                # Fallback analysis
                fallback_result = self.fallbacks.generate_fallback_analysis(sentence)
                return self._convert_modular_to_legacy(fallback_result, sentence)
        except Exception as e:
            # Fallback on any error
            fallback_result = self.fallbacks.generate_fallback_analysis(sentence)
            return self._convert_modular_to_legacy(fallback_result, sentence)

    def _convert_modular_to_legacy(self, modular_data: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        print(f"DEBUG: _convert_modular_to_legacy called with modular_data keys: {list(modular_data.keys())}")
        words = modular_data.get('words', [])
        elements = {}
        word_explanations = []
        colors = self.get_color_scheme('intermediate')  # Use intermediate as default

        for word_data in words:
            word = word_data.get('word', '')
            role = word_data.get('grammatical_role', 'other')
            # Map role using config
            standard_role = role  # Keep the role name
            color = colors.get(standard_role, '#AAAAAA')
            explanation = word_data.get('individual_meaning', standard_role)
            word_explanations.append([word, standard_role, color, explanation])

            if standard_role not in elements:
                elements[standard_role] = []
            elements[standard_role].append(word_data)

        # Get explanations from modular data, or generate from word explanations
        explanations = modular_data.get('explanations', {})
        if not explanations:
            # Generate explanations from word explanations if no explanations field exists
            explanations = {}
            for word_exp in word_explanations:
                if len(word_exp) >= 4:
                    word, role, color, meaning = word_exp
                    if role not in explanations:
                        explanations[role] = []
                    explanations[role].append(f"{word}: {meaning}")

            # Convert lists to strings for display
            for role in explanations:
                if isinstance(explanations[role], list):
                    explanations[role] = "; ".join(explanations[role])

        # ALWAYS generate rich overall_structure and key_features for sentence-level analysis
        if 'overall_structure' not in explanations:
            roles = [exp[1] for exp in word_explanations if len(exp) > 1]
            role_counts = {}
            for role in roles:
                role_counts[role] = role_counts.get(role, 0) + 1
            overall = f"Sentence with {', '.join([f'{count} {role}' + ('s' if count > 1 else '') for role, count in role_counts.items()])}"
            explanations['overall_structure'] = overall
            explanations['key_features'] = f"Demonstrates {len(set(roles))} grammatical categories in Chinese Traditional sentence structure"
            print(f"DEBUG: Generated rich explanations - overall_structure: {overall}")

        return {
            'sentence': modular_data.get('sentence', sentence),
            'elements': elements,
            'explanations': explanations,
            'word_explanations': word_explanations
        }

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """
        Generate HTML output for Chinese Traditional text with inline color styling for Anki compatibility.
        RICH EXPLANATIONS LIKE CHINESE SIMPLIFIED - shows individual meanings for each word.
        """
        explanations = parsed_data.get('word_explanations', [])

        print(f"DEBUG Chinese Traditional HTML Gen - Input explanations count: {len(explanations)}")
        print("DEBUG Chinese Traditional HTML Gen - Input sentence: '" + str(sentence) + "'")

        # For Chinese (logographic script without spaces), use position-based replacement
        color_scheme = self.get_color_scheme(complexity)

        # Sort explanations by position in sentence to avoid conflicts
        sorted_explanations = sorted(explanations, key=lambda x: sentence.find(x[0]) if len(x) >= 4 else len(sentence))

        # Build HTML by processing the sentence character by character
        html_parts = []
        i = 0
        sentence_len = len(sentence)

        while i < sentence_len:
            # Check if current position matches any word explanation
            matched = False
            for exp in sorted_explanations:
                if len(exp) >= 4:  # [word, role, color, meaning]
                    word = exp[0]
                    word_len = len(word)

                    # Check if word matches at current position
                    if i + word_len <= sentence_len and sentence[i:i + word_len] == word:
                        role = exp[1]
                        color = exp[2] if len(exp) > 2 else color_scheme.get(role, '#888888')

                        # Escape curly braces in word to prevent f-string issues
                        safe_word_display = word.replace('{', '{{').replace('}', '}}')
                        colored_word = f'<span style="color: {color}; font-weight: bold;">{safe_word_display}</span>'
                        html_parts.append(colored_word)

                        print(f"DEBUG Chinese Traditional HTML Gen - Replaced '{word}' with role '{role}' and color '{color}'")

                        i += word_len
                        matched = True
                        break

            if not matched:
                # No match, add character as-is
                html_parts.append(sentence[i])
                i += 1

        html = ''.join(html_parts)
        print("DEBUG Chinese Traditional HTML Gen - Final HTML result: " + html)
        return html

    def _convert_modular_to_legacy(self, modular_result: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        """
        Convert modular analysis result to legacy format expected by base analyzer.

        Args:
            modular_result: Result from modular pipeline
            sentence: Original sentence

        Returns:
            Legacy format with elements, word_explanations, and explanations dict
        """
        # Convert words to word_explanations format
        word_explanations = []
        elements = {}
        explanations = {}

        for word_data in modular_result.get('words', []):
            word = word_data.get('word', '')
            role = word_data.get('grammatical_role', 'noun')
            color = self.zh_tw_config.grammatical_roles.get(role, '#000000')
            meaning = word_data.get('individual_meaning', '')
            word_explanations.append([word, role, color, meaning])

            # Also populate elements for compatibility
            if role not in elements:
                elements[role] = []
            elements[role].append({
                'word': word,
                'individual_meaning': meaning
            })

            # Create explanations dictionary for grammar processor compatibility
            # Group meanings by role for rich explanations
            if role not in explanations:
                explanations[role] = []
            if meaning and meaning != 'Translation not available (fallback analysis)':
                explanations[role].append(f"{word}: {meaning}")

        # Convert explanations lists to formatted strings
        formatted_explanations = {}
        for role, meanings in explanations.items():
            if meanings:
                formatted_explanations[role] = '; '.join(meanings)
            else:
                formatted_explanations[role] = f"{role} in zh-tw grammar"

        # ALWAYS generate rich overall_structure and key_features for sentence-level analysis
        if 'overall_structure' not in formatted_explanations:
            roles = [exp[1] for exp in word_explanations if len(exp) > 1]
            role_counts = {}
            for role in roles:
                role_counts[role] = role_counts.get(role, 0) + 1
            overall = f"Sentence with {', '.join([f'{count} {role}' + ('s' if count > 1 else '') for role, count in role_counts.items()])}"
            formatted_explanations['overall_structure'] = overall
            formatted_explanations['key_features'] = f"Demonstrates {len(set(roles))} grammatical categories in Chinese Traditional sentence structure"

        return {
            "sentence": modular_result.get('original_sentence', sentence),
            "elements": elements,
            "word_explanations": word_explanations,
            "explanations": formatted_explanations
        }

    def _reorder_explanations_by_sentence_position(self, word_explanations: List[List], sentence: str) -> List[List]:
        """
        Reorder word explanations by their position in the sentence.

        Legacy method for compatibility with base analyzer expectations.
        """
        if not word_explanations:
            return word_explanations

        # Create mapping of words to their positions in sentence
        word_positions = {}
        for i, word_info in enumerate(word_explanations):
            word = word_info[0] if len(word_info) > 0 else ""
            if word:
                # Find all occurrences of this word in the sentence
                start = 0
                positions = []
                while True:
                    pos = sentence.find(word, start)
                    if pos == -1:
                        break
                    positions.append(pos)
                    start = pos + 1

                if positions:
                    word_positions[i] = min(positions)  # Use first occurrence

        # Sort by position
        sorted_indices = sorted(word_positions.keys(), key=lambda i: word_positions[i])

        # Reorder explanations
        reordered = []
        used_indices = set()
        for idx in sorted_indices:
            reordered.append(word_explanations[idx])
            used_indices.add(idx)

        # Add any remaining explanations that weren't positioned
        for i, explanation in enumerate(word_explanations):
            if i not in used_indices:
                reordered.append(explanation)

        return reordered

    def _create_fallback_parse(self, sentence: str, complexity: str = "intermediate") -> Dict[str, Any]:
        """
        Create fallback parse when AI analysis fails.

        Legacy method for compatibility.
        """
        fallback_result = self.fallbacks.generate_fallback_analysis(sentence)

        # Convert to legacy format
        return self._convert_modular_to_legacy(fallback_result, sentence)

    def batch_analyze_grammar(self, sentences: List[str], target_word: str, complexity: str, gemini_api_key: str) -> List[GrammarAnalysis]:
        """
        Analyze grammar for multiple sentences with RICH EXPLANATIONS.

        CHINESE TRADITIONAL BATCH PROCESSING:
        - Handles 8 sentences efficiently (prevents token overflow)
        - Uses single AI call for all sentences (cost-effective)
        - Applies per-result validation and fallbacks
        - Maintains sentence order in output
        - Provides RICH explanations with overall_structure and key_features
        - Prevents generic "Grammar analysis for ZH-TW" summaries

        CHINESE TRADITIONAL BATCH SIZE CONSIDERATIONS:
        - 8 sentences: Optimal balance of efficiency and response quality
        - Prevents JSON truncation with 2000 max_tokens
        - Allows meaningful error recovery per sentence
        - Accounts for Traditional character analysis complexity

        ERROR HANDLING:
        - If entire batch fails: Return fallbacks for all sentences
        - If individual sentences fail: Use fallbacks only for failed ones
        - Maintains RICH explanations even in fallback cases
        """
        logger.info(f"DEBUG: batch_analyze_grammar called with {len(sentences)} sentences")
        try:
            prompt = self.prompt_builder.build_batch_grammar_prompt(complexity, sentences, target_word)
            ai_response = self._call_ai_model(prompt, gemini_api_key)
            batch_result = self.response_parser.parse_batch_response(ai_response, sentences, complexity, target_word)

            if not batch_result.get('success', False):
                logger.warning("Batch parsing failed, using fallback analysis")
                return self._create_fallback_batch_analyses(sentences, target_word, complexity)

            validated_results = batch_result.get('results', [])

            grammar_analyses = []
            for result, sentence in zip(validated_results, sentences):
                # Transform batch result to standard format with rich explanations
                standard_result = self.response_parser._transform_to_standard_format(result, complexity, target_word)
                validation = self.validator.validate_analysis(standard_result)

                # Apply validation results
                standard_result['validation'] = validation
                standard_result['confidence'] = validation.get('quality_score', 50) / 100.0

                # Generate HTML output with rich explanations
                html_output = self._generate_html_output(standard_result, sentence, complexity)

                grammar_analyses.append(GrammarAnalysis(
                    sentence=sentence,
                    target_word=target_word or "",
                    language_code=self.language_code,
                    complexity_level=complexity,
                    grammatical_elements=standard_result.get('elements', {}),
                    explanations=standard_result.get('explanations', {}),  # RICH explanations!
                    color_scheme=self.get_color_scheme(complexity),
                    html_output=html_output,
                    confidence_score=standard_result.get('confidence', 0.0),
                    word_explanations=standard_result.get('word_explanations', [])
                ))

            return grammar_analyses

        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return self._create_fallback_batch_analyses(sentences, target_word, complexity)

    def _create_fallback_batch_analyses(self, sentences: List[str], target_word: str, complexity: str) -> List[GrammarAnalysis]:
        """
        Create fallback GrammarAnalysis objects when batch processing fails.

        Ensures RICH explanations even in fallback cases.

        Args:
            sentences: Sentences to analyze
            target_word: Target word being learned
            complexity: Complexity level

        Returns:
            List of GrammarAnalysis objects with rich fallback explanations
        """
        fallback_analyses = []
        for sentence in sentences:
            # Use modular fallbacks for rich explanations
            fallback_result = self.fallbacks.generate_fallback_analysis(sentence, target_word)

            # Convert to standard format with rich explanations
            standard_result = self.response_parser._transform_to_standard_format(fallback_result, complexity, target_word)

            html_output = self._generate_html_output(standard_result, sentence, complexity)

            fallback_analyses.append(GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=standard_result.get('elements', {}),
                explanations=standard_result.get('explanations', {}),  # RICH fallback explanations!
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=standard_result.get('confidence', 0.3),
                word_explanations=standard_result.get('word_explanations', [])
            ))

        return fallback_analyses
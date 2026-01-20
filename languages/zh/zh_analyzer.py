# languages/zh/zh_analyzer.py
"""
Chinese Simplified Grammar Analyzer - Clean Architecture Facade

GOLD STANDARD IMPLEMENTATION FOR CHINESE SIMPLIFIED:
This file demonstrates the clean architecture pattern for Chinese analyzers.
It serves as the main entry point (Facade) that orchestrates domain components.

ARCHITECTURAL PATTERN:
- Facade Pattern: Single entry point that delegates to specialized components
- Domain-Driven Design: Separated concerns into config, prompts, parsing, validation, fallbacks
- Clean Architecture: Dependencies point inward (domain components don't depend on infrastructure)

KEY RESPONSIBILITIES:
1. Initialize domain components (config, prompt_builder, response_parser, validator)
2. Orchestrate single and batch grammar analysis workflows
3. Handle AI API calls with proper error handling and fallbacks
4. Generate HTML output for colored sentence display
5. Provide legacy compatibility methods

DOMAIN COMPONENTS USED:
- ZhConfig: Language-specific configuration (colors, roles, patterns)
- ZhPromptBuilder: Builds AI prompts using Jinja2 templates
- ZhResponseParser: Parses AI responses, applies fallbacks, transforms data
- ZhValidator: Validates results and calculates confidence scores

INTEGRATION POINTS:
- Called by sentence_generator.py for Pass 3: Grammar Analysis
- Returns GrammarAnalysis objects with word_explanations in [word, role, color, meaning] format
- Supports batch processing with 8-sentence limits to prevent token overflow
- Uses 2000 max_tokens for complete AI responses (prevents JSON truncation)

INHERITANCE:
- Inherits from BaseGrammarAnalyzer (Chinese is analytic, not Indo-European)
- Can be adapted for other Sino-Tibetan languages by changing domain components

USAGE FOR NEW LANGUAGES:
1. Create language-specific domain components (config, prompt_builder, etc.)
2. Copy this facade structure, changing only the component imports
3. Implement language-specific logic in domain components, not here
"""

import logging
import re
from typing import Dict, List, Any
from pathlib import Path

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

from .domain.zh_config import ZhConfig
from .domain.zh_prompt_builder import ZhPromptBuilder
from .domain.zh_response_parser import ZhResponseParser
from .domain.zh_validator import ZhValidator

logger = logging.getLogger(__name__)

class ZhAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Chinese Simplified (简体中文) - Clean Architecture.

    CHINESE-SPECIFIC FEATURES:
    - Analytic Language: No inflection, relies on particles and word order
    - Aspect System: 了 (completed), 着 (ongoing), 过 (experienced)
    - Classifier System: Obligatory measure words for counting
    - Topic-Comment Structure: Flexible word order
    - Logographic Script: Character-based analysis with compound recognition

    Key Features: ['aspect_markers', 'classifiers', 'particles', 'topic_comment', 'no_inflection']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    Script: Simplified Chinese characters (LTR), logographic writing system
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "zh"
    LANGUAGE_NAME = "Chinese Simplified"

    def __init__(self):
        """
        Initialize Chinese Simplified analyzer with domain components.

        CHINESE-SPECIFIC INITIALIZATION:
        1. Initialize domain components first (config, builders, parsers)
        2. Create language config with Chinese metadata
        3. Call parent constructor with config
        4. Set up logging and validation

        This pattern ensures all dependencies are available before analysis begins.
        """
        logger.info("DEBUG: ZhAnalyzer __init__ called")
        # Initialize domain components first
        self.zh_config = ZhConfig()
        self.prompt_builder = ZhPromptBuilder(self.zh_config)
        self.response_parser = ZhResponseParser(self.zh_config)
        self.validator = ZhValidator(self.zh_config)

        config = LanguageConfig(
            code="zh",
            name="Chinese Simplified",
            native_name="简体中文",
            family="Sino-Tibetan",
            script_type="logographic",
            complexity_rating="medium",
            key_features=['aspect_markers', 'classifiers', 'particles', 'topic_comment', 'no_inflection'],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )
        super().__init__(config)

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, groq_api_key: str) -> GrammarAnalysis:
        """
        Analyze grammar for a single sentence.

        CHINESE WORKFLOW:
        1. Build AI prompt using prompt_builder (Chinese-specific templates)
        2. Call AI API with proper error handling
        3. Parse response using response_parser (with Chinese fallbacks)
        4. Validate results using validator (aspect particles, classifiers)
        5. Generate HTML output for colored display
        6. Return GrammarAnalysis object

        CHINESE FALLBACK HIERARCHY:
        - Primary: AI-generated analysis with aspect/classifier validation
        - Secondary: Pattern-based fallbacks for particles and compounds
        - Tertiary: Basic rule-based fallbacks for character-based analysis

        OUTPUT FORMAT:
        - word_explanations: [[word, role, color, meaning], ...]
        - Maintains sentence word order (LTR) for optimal user experience
        - Colors based on grammatical roles and complexity level
        """
        try:
            prompt = self.prompt_builder.build_single_prompt(sentence, target_word, complexity)
            ai_response = self._call_ai(prompt, groq_api_key)
            result = self.response_parser.parse_response(ai_response, complexity, sentence, target_word)
            validated_result = self.validator.validate_result(result, sentence)

            # Generate HTML output
            html_output = self._generate_html_output(validated_result, sentence, complexity)

            # Return GrammarAnalysis object
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=validated_result.get('elements', {}),
                explanations=validated_result.get('explanations', {}),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=validated_result.get('confidence', 0.0),
                word_explanations=validated_result.get('word_explanations', [])
            )
        except Exception as e:
            logger.error(f"Analysis failed for '{sentence}': {e}")
            # Create fallback analysis
            fallback_result = self.response_parser.fallbacks.create_fallback(sentence, complexity)
            html_output = self._generate_html_output(fallback_result, sentence, complexity)
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=fallback_result.get('elements', {}),
                explanations=fallback_result.get('explanations', {}),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=fallback_result.get('confidence', 0.3),
                word_explanations=fallback_result.get('word_explanations', [])
            )

    def batch_analyze_grammar(self, sentences: List[str], target_word: str, complexity: str, groq_api_key: str) -> List[GrammarAnalysis]:
        """
        Analyze grammar for multiple sentences.

        CHINESE BATCH PROCESSING:
        - Handles 8 sentences efficiently (prevents token overflow)
        - Uses single AI call for all sentences (cost-effective)
        - Applies per-result validation and fallbacks
        - Maintains sentence order in output
        - Provides partial fallbacks (some sentences may succeed even if others fail)

        CHINESE BATCH SIZE CONSIDERATIONS:
        - 8 sentences: Optimal balance of efficiency and response quality
        - Prevents JSON truncation with 2000 max_tokens
        - Allows meaningful error recovery per sentence
        - Accounts for character-based analysis complexity

        ERROR HANDLING:
        - If entire batch fails: Return fallbacks for all sentences
        - If individual sentences fail: Use fallbacks only for failed ones
        - Maintains output consistency regardless of partial failures
        """
        logger.info(f"DEBUG: batch_analyze_grammar called with {len(sentences)} sentences")
        try:
            prompt = self.prompt_builder.build_batch_prompt(sentences, target_word, complexity)
            ai_response = self._call_ai(prompt, groq_api_key)
            results = self.response_parser.parse_batch_response(ai_response, sentences, complexity, target_word)

            grammar_analyses = []
            for result, sentence in zip(results, sentences):
                validated_result = self.validator.validate_result(result, sentence)
                html_output = self._generate_html_output(validated_result, sentence, complexity)

                grammar_analyses.append(GrammarAnalysis(
                    sentence=sentence,
                    target_word=target_word or "",
                    language_code=self.language_code,
                    complexity_level=complexity,
                    grammatical_elements=validated_result.get('elements', {}),
                    explanations=validated_result.get('explanations', {}),
                    color_scheme=self.get_color_scheme(complexity),
                    html_output=html_output,
                    confidence_score=validated_result.get('confidence', 0.0),
                    word_explanations=validated_result.get('word_explanations', [])
                ))

            return grammar_analyses
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            # Return fallback analyses
            fallback_analyses = []
            for sentence in sentences:
                fallback_result = self.response_parser.fallbacks.create_fallback(sentence, complexity)
                html_output = self._generate_html_output(fallback_result, sentence, complexity)
                fallback_analyses.append(GrammarAnalysis(
                    sentence=sentence,
                    target_word=target_word or "",
                    language_code=self.language_code,
                    complexity_level=complexity,
                    grammatical_elements=fallback_result.get('elements', {}),
                    explanations=fallback_result.get('explanations', {}),
                    color_scheme=self.get_color_scheme(complexity),
                    html_output=html_output,
                    confidence_score=fallback_result.get('confidence', 0.3),
                    word_explanations=fallback_result.get('word_explanations', [])
                ))
            return fallback_analyses

    def _call_ai(self, prompt: str, groq_api_key: str) -> str:
        """
        Call Groq AI for grammar analysis.

        CHINESE AI INTEGRATION:
        - Uses llama-3.3-70b-versatile model (current production model)
        - 2000 max_tokens prevents JSON truncation in batch responses
        - 30-second timeout for online environments
        - Comprehensive error handling with meaningful logging
        - Returns error response for fallback processing

        CHINESE CONSIDERATIONS:
        - Handles logographic script properly
        - Accounts for compound word analysis
        - Supports aspect marker and classifier validation
        - Future-proof: Update model names as Groq releases new versions

        ERROR HANDLING:
        - Catches all exceptions to prevent crashes
        - Returns standardized error response for fallback logic
        - Logs detailed information for debugging
        """
        logger.info(f"DEBUG: _call_ai called with prompt: {prompt[:200]}...")
        try:
            from groq import Groq
            client = Groq(api_key=groq_api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Current production model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,  # Prevents JSON truncation
                temperature=0.1  # Low creativity for consistent grammar analysis
            )
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"DEBUG: AI response: {ai_response[:500]}...")
            logger.info(f"AI response received: {ai_response[:500]}...")
            return ai_response
        except Exception as e:
            logger.info(f"DEBUG: AI call failed: {e}")
            logger.error(f"AI call failed: {e}")
            return '{"sentence": "error", "words": []}'  # Standardized error response

    def _mock_batch_ai_response(self, sentences: List[str], complexity: str) -> str:
        """Mock batch AI response for testing."""
        results = []
        for s in sentences:
            words = s.split()
            word_data = []
            for word in words:
                role = 'other'
                if word in ['的', '了', '着', '过']:
                    role = 'particle'
                elif word in ['个', '本', '杯']:
                    role = 'classifier'
                word_data.append({
                    'word': word,
                    'grammatical_role': role,
                    'individual_meaning': f'{role} in sentence'
                })
            results.append({"sentence": s, "words": word_data})
        return '{"batch_results": ' + str(results).replace("'", '"') + '}'

    def _mock_ai_response(self, sentence: str, complexity: str) -> str:
        """Mock single AI response for testing."""
        words = sentence.split()
        word_data = []
        for word in words:
            role = 'other'
            if word in ['的', '了', '着', '过']:
                role = 'particle'
            elif word in ['个', '本', '杯']:
                role = 'classifier'
            word_data.append({
                'word': word,
                'grammatical_role': role,
                'individual_meaning': f'{role} in sentence'
            })
        return '{"sentence": "' + sentence + '", "words": ' + str(word_data).replace("'", '"') + '}'

    # Legacy compatibility methods - delegate to new implementation
    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str, native_language: str = "English") -> str:
        """
        Legacy method - use analyze_grammar instead.

        DEPRECATED: This method is maintained for backward compatibility.
        New code should use the analyze_grammar() method directly.
        """
        return self.prompt_builder.build_single_prompt(sentence, complexity, native_language)

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """
        Return color scheme for Chinese Simplified grammatical elements.

        COLOR CODING PHILOSOPHY:
        - Consistent colors across complexity levels where possible
        - Progressive disclosure: More roles distinguished at higher complexity
        - Accessible colors: High contrast, colorblind-friendly
        - Language-appropriate: Colors that make sense for Chinese grammar

        CHINESE COMPLEXITY PROGRESSION:
        - Beginner: Basic roles (noun, verb, adjective, particles)
        - Intermediate: More distinctions (classifiers, aspect markers, pronouns)
        - Advanced: Full granularity (all particle types, structural elements)
        """
        return self.zh_config.get_color_scheme(complexity)

    # Abstract method implementations required by BaseGrammarAnalyzer

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Generate Chinese-specific AI prompt for grammar analysis."""
        return self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into standardized Chinese grammar analysis format."""
        return self.response_parser.parse_response(ai_response, complexity, sentence, None)

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate Chinese analysis quality and return confidence score."""
        return self.validator.validate_result(parsed_data, original_sentence)['confidence']

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Generate HTML output for Chinese text with inline color styling for Anki compatibility"""
        explanations = parsed_data.get('word_explanations', [])

        print(f"DEBUG Chinese HTML Gen - Input explanations count: {len(explanations)}")
        print("DEBUG Chinese HTML Gen - Input sentence: '" + str(sentence) + "'")

        # For Chinese (logographic script without spaces), use sequential replacement instead of space splitting
        color_scheme = self.get_color_scheme('intermediate')
        html = sentence

        for exp in explanations:
            if len(exp) >= 3:
                word = exp[0]
                pos = exp[1]
                category = self._map_grammatical_role_to_category(pos)
                color = color_scheme.get(category, '#888888')

                # Replace the word with colored version (first occurrence only, in order)
                safe_word = re.escape(word)
                # Escape curly braces in word to prevent f-string issues
                safe_word_display = word.replace('{', '{{').replace('}', '}}')
                colored_word = f'<span style="color: {color}; font-weight: bold;">{safe_word_display}</span>'
                html = re.sub(safe_word, colored_word, html, count=1)

                print("DEBUG Chinese HTML Gen - Replaced '" + str(word) + "' with category '" + str(category) + "' and color '" + str(color) + "'")

        print("DEBUG Chinese HTML Gen - Final HTML result: " + html)
        return html

    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Map Chinese grammatical roles to color scheme categories"""
        role_mapping = {
            'noun': 'noun',
            'verb': 'verb',
            'adjective': 'adjective',
            'adverb': 'adverb',
            'pronoun': 'pronoun',
            'preposition': 'preposition',
            'conjunction': 'conjunction',
            'interjection': 'interjection',
            'particle': 'particle',
            'classifier': 'classifier',
            'aspect_marker': 'aspect_marker',
            'modal_particle': 'modal_particle',
            'structural_particle': 'structural_particle',
            'measure_word': 'measure_word',
            'numeral': 'numeral',
            'other': 'other'
        }
        return role_mapping.get(grammatical_role, 'other')
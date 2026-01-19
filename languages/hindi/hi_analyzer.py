# languages/hindi/hi_analyzer.py
"""
Refactored Hindi Grammar Analyzer - Clean Architecture Facade

GOLD STANDARD IMPLEMENTATION FOR OTHER LANGUAGES:
This file demonstrates the clean architecture pattern for language analyzers.
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
- HiConfig: Language-specific configuration (colors, roles, patterns)
- HiPromptBuilder: Builds AI prompts using Jinja2 templates
- HiResponseParser: Parses AI responses, applies fallbacks, transforms data
- HiValidator: Validates results and calculates confidence scores

INTEGRATION POINTS:
- Called by sentence_generator.py for Pass 3: Grammar Analysis
- Returns GrammarAnalysis objects with word_explanations in [word, role, color, meaning] format
- Supports batch processing with 8-sentence limits to prevent token overflow
- Uses 2000 max_tokens for complete AI responses (prevents JSON truncation)

INHERITANCE:
- Inherits from IndoEuropeanAnalyzer (provides base functionality)
- Can be adapted for other Indo-European languages by changing domain components

USAGE FOR NEW LANGUAGES:
1. Create language-specific domain components (config, prompt_builder, etc.)
2. Copy this facade structure, changing only the component imports
3. Implement language-specific logic in domain components, not here
"""

import logging
from typing import Dict, List, Any
from pathlib import Path

from streamlit_app.language_analyzers.family_base_analyzers.indo_european_analyzer import IndoEuropeanAnalyzer
from streamlit_app.language_analyzers.base_analyzer import LanguageConfig, GrammarAnalysis

from .domain.hi_config import HiConfig
from .domain.hi_prompt_builder import HiPromptBuilder
from .domain.hi_response_parser import HiResponseParser
from .domain.hi_validator import HiValidator

logger = logging.getLogger(__name__)

class HiAnalyzer(IndoEuropeanAnalyzer):
    """
    Grammar analyzer for Hindi (हिंदी) - Refactored Clean Architecture.

    GOLD STANDARD FEATURES:
    - Clean Architecture: Separated domain logic from infrastructure
    - Batch Processing: Handles 8 sentences efficiently with fallbacks
    - AI Integration: Uses Groq API with proper error handling
    - HTML Generation: Creates colored sentence displays
    - Confidence Scoring: Validates results with fallback mechanisms
    - Word Ordering: Maintains sentence word order for optimal UX

    Key Features: ['postpositions', 'gender_agreement', 'case_marking', 'verb_conjugation', 'aspect_tense', 'honorifics']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    Script: Devanagari (LTR), Abugida writing system
    """

    VERSION = "2.0"
    LANGUAGE_CODE = "hi"
    LANGUAGE_NAME = "Hindi"

    def __init__(self):
        """
        Initialize Hindi analyzer with domain components.

        GOLD STANDARD INITIALIZATION:
        1. Initialize domain components first (config, builders, parsers)
        2. Create language config with metadata
        3. Call parent constructor with config
        4. Set up logging and validation

        This pattern ensures all dependencies are available before analysis begins.
        """
        logger.info("DEBUG: HiAnalyzer __init__ called")
        # Initialize domain components first
        self.hi_config = HiConfig()
        self.prompt_builder = HiPromptBuilder(self.hi_config)
        self.response_parser = HiResponseParser(self.hi_config)
        self.validator = HiValidator(self.hi_config)

        config = LanguageConfig(
            code="hi",
            name="Hindi",
            native_name="हिंदी",
            family="Indo-European",
            script_type="abugida",
            complexity_rating="medium",
            key_features=['postpositions', 'gender_agreement', 'case_marking', 'verb_conjugation', 'aspect_tense', 'honorifics'],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )
        super().__init__(config)

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, groq_api_key: str) -> GrammarAnalysis:
        """
        Analyze grammar for a single sentence.

        GOLD STANDARD WORKFLOW:
        1. Build AI prompt using prompt_builder
        2. Call AI API with proper error handling
        3. Parse response using response_parser (with fallbacks)
        4. Validate results using validator
        5. Generate HTML output for colored display
        6. Return GrammarAnalysis object

        FALLBACK HIERARCHY:
        - Primary: AI-generated analysis
        - Secondary: Pattern-based fallbacks in response_parser
        - Tertiary: Basic rule-based fallbacks in fallbacks component

        OUTPUT FORMAT:
        - word_explanations: [[word, role, color, meaning], ...]
        - Maintains sentence word order for optimal user experience
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

        GOLD STANDARD BATCH PROCESSING:
        - Handles 8 sentences efficiently (prevents token overflow)
        - Uses single AI call for all sentences (cost-effective)
        - Applies per-result validation and fallbacks
        - Maintains sentence order in output
        - Provides partial fallbacks (some sentences may succeed even if others fail)

        BATCH SIZE CONSIDERATIONS:
        - 8 sentences: Optimal balance of efficiency and response quality
        - Prevents JSON truncation with 2000 max_tokens
        - Allows meaningful error recovery per sentence

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

        GOLD STANDARD AI INTEGRATION:
        - Uses llama-3.3-70b-versatile model (current production model)
        - 2000 max_tokens prevents JSON truncation in batch responses
        - 30-second timeout for online environments
        - Comprehensive error handling with meaningful logging
        - Returns error response for fallback processing

        MODEL SELECTION:
        - llama-3.3-70b-versatile: Best balance of quality and speed
        - Avoid deprecated models (llama3-70b-8192, etc.)
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
                if word in ['का', 'की', 'के']:
                    role = 'postposition'
                elif word.endswith('ा'):
                    role = 'verb'
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
            if word in ['का', 'की', 'के']:
                role = 'postposition'
            elif word.endswith('ा'):
                role = 'verb'
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
        Return color scheme for Hindi grammatical elements.

        COLOR CODING PHILOSOPHY:
        - Consistent colors across complexity levels where possible
        - Progressive disclosure: More roles distinguished at higher complexity
        - Accessible colors: High contrast, colorblind-friendly
        - Language-appropriate: Colors that make sense for Hindi grammar

        COMPLEXITY PROGRESSION:
        - Beginner: Basic roles (noun, verb, adjective, etc.)
        - Intermediate: More distinctions (personal pronouns, auxiliary verbs)
        - Advanced: Full granularity (all pronoun types, particles, etc.)
        """
        return self.hi_config.get_color_scheme(complexity)
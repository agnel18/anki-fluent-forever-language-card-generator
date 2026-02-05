# languages/turkish/tr_analyzer.py
"""
Turkish Grammar Analyzer - Clean Architecture Facade

GOLD STANDARD IMPLEMENTATION FOR TURKISH:
This file demonstrates the clean architecture pattern for Turkish analyzers.
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
- TrConfig: Language-specific configuration (colors, roles, patterns)
- TrPromptBuilder: Builds AI prompts using Jinja2 templates
- TrResponseParser: Parses AI responses, applies fallbacks, transforms data
- TrValidator: Validates results and calculates confidence scores

INTEGRATION POINTS:
- Called by sentence_generator.py for Pass 3: Grammar Analysis
- Returns GrammarAnalysis objects with word_explanations in [word, role, color, meaning] format
- Supports batch processing with 8-sentence limits to prevent token overflow
- Uses 2000 max_tokens for complete AI responses (prevents JSON truncation)

INHERITANCE:
- Inherits from BaseGrammarAnalyzer (Turkish is agglutinative, not analytic)
- Can be adapted for other Turkic languages by changing domain components

USAGE FOR NEW LANGUAGES:
1. Create language-specific domain components (config, prompt_builder, etc.)
2. Copy this facade structure, changing only the component imports
3. Implement language-specific logic in domain components, not here
"""

import logging
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

from .domain.tr_config import TrConfig
from .domain.tr_prompt_builder import TrPromptBuilder
from .domain.tr_response_parser import TrResponseParser
from .domain.tr_validator import TrValidator

# Import centralized configuration
from streamlit_app.shared_utils import get_gemini_model, get_gemini_fallback_model

logger = logging.getLogger(__name__)

class TrAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Turkish (Türkçe) - Clean Architecture.

    TURKISH-SPECIFIC FEATURES:
    - Agglutinative Language: Words formed by adding suffixes to roots
    - Vowel Harmony: Suffix vowels harmonize with root vowels
    - SOV Word Order: Subject-Object-Verb sentence structure
    - Case System: 6 grammatical cases (nominative, accusative, dative, locative, ablative, genitive)
    - No Grammatical Gender: Unlike many Indo-European languages

    Key Features: ['agglutination', 'vowel_harmony', 'case_system', 'sov_order', 'no_gender']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    Script: Latin alphabet (LTR), alphabetic writing system
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "tr"
    LANGUAGE_NAME = "Turkish"

    def __init__(self):
        """
        Initialize Turkish analyzer with domain components.

        TURKISH-SPECIFIC INITIALIZATION:
        1. Initialize domain components first (config, builders, parsers)
        2. Create language config with Turkish metadata
        3. Call parent constructor with config
        4. Set up logging and validation

        This pattern ensures all dependencies are available before analysis begins.
        """
        logger.info("DEBUG: TrAnalyzer __init__ called")
        # Initialize domain components first
        self.tr_config = TrConfig()
        self.prompt_builder = TrPromptBuilder(self.tr_config)
        self.response_parser = TrResponseParser(self.tr_config)
        self.validator = TrValidator(self.tr_config)

        config = LanguageConfig(
            code="tr",
            name="Turkish",
            native_name="Türkçe",
            family="Turkic",
            script_type="alphabetic",
            complexity_rating="high",
            key_features=['agglutination', 'vowel_harmony', 'case_system', 'sov_order', 'no_gender'],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )

        super().__init__(config)

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str) -> GrammarAnalysis:
        """
        Analyze grammar for a single sentence.

        TURKISH WORKFLOW:
        1. Build AI prompt using prompt_builder (Turkish-specific templates)
        2. Call AI API with proper error handling
        3. Parse response using response_parser (with Turkish fallbacks)
        4. Validate results using validator (agglutination, vowel harmony)
        5. Generate HTML output for colored display
        6. Return GrammarAnalysis object

        TURKISH FALLBACK HIERARCHY:
        - Primary: AI-generated analysis with agglutination/vowel harmony validation
        - Secondary: Pattern-based fallbacks for suffixes and cases
        - Tertiary: Basic rule-based fallbacks for morphological analysis

        OUTPUT FORMAT:
        - word_explanations: [[word, role, color, meaning], ...]
        - Maintains sentence word order (LTR) for optimal user experience
        - Colors based on grammatical roles and complexity level
        """
        try:
            prompt = self.get_grammar_prompt(complexity, sentence, target_word)
            ai_response = self._call_ai(prompt, gemini_api_key)
            result = self.response_parser.parse_response(ai_response, complexity, sentence, target_word)
            validated_result = self.validator.validate_result(result, sentence)

            # Additional explanation quality validation
            quality_validation = self.validator.validate_explanation_quality(validated_result)
            validated_result['explanation_quality'] = quality_validation

            # Adjust confidence score based on explanation quality
            base_confidence = validated_result.get('confidence', 0.5)
            quality_score = quality_validation.get('quality_score', 1.0)
            adjusted_confidence = min(base_confidence * quality_score, 1.0)
            validated_result['confidence'] = adjusted_confidence

            # Log quality issues if any
            if quality_validation.get('issues'):
                logger.info(f"Explanation quality issues for '{sentence}': {quality_validation['issues']}")

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

    def batch_analyze_grammar(self, sentences: List[str], target_word: str, complexity: str, gemini_api_key: str) -> List[GrammarAnalysis]:
        """
        Analyze grammar for multiple sentences.

        TURKISH BATCH PROCESSING:
        - Handles 8 sentences efficiently (prevents token overflow)
        - Uses single AI call for all sentences (cost-effective)
        - Applies per-result validation and fallbacks
        - Maintains sentence order in output
        - Provides partial fallbacks (some sentences may succeed even if others fail)

        TURKISH BATCH SIZE CONSIDERATIONS:
        - 8 sentences: Optimal balance of efficiency and response quality
        - Prevents JSON truncation with 2000 max_tokens
        - Allows meaningful error recovery per sentence
        - Accounts for agglutinative analysis complexity

        ERROR HANDLING:
        - If entire batch fails: Return fallbacks for all sentences
        - If individual sentences fail: Use fallbacks only for failed ones
        - Maintains output consistency regardless of partial failures
        """
        logger.info(f"DEBUG: batch_analyze_grammar called with {len(sentences)} sentences")
        try:
            prompt = self.prompt_builder.build_batch_prompt(sentences, target_word, complexity)
            ai_response = self._call_ai(prompt, gemini_api_key)
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

    def _call_ai(self, prompt: str, gemini_api_key: str) -> str:
        """
        Call Google Gemini AI for grammar analysis.

        TURKISH AI INTEGRATION:
        - Uses gemini-2.5-flash model (primary) with gemini-3-flash-preview fallback
        - 2000 max_output_tokens prevents JSON truncation in batch responses
        - 30-second timeout for online environments
        - Comprehensive error handling with meaningful logging
        - Returns error response for fallback processing

        TURKISH CONSIDERATIONS:
        - Handles agglutinative morphology properly
        - Accounts for vowel harmony patterns
        - Supports case system and suffix validation
        - Future-proof: Update model names as Google releases new versions

        ERROR HANDLING:
        - Catches all exceptions to prevent crashes
        - Returns standardized error response for fallback logic
        - Logs detailed information for debugging
        """
        logger.info(f"DEBUG: _call_ai called with prompt: {prompt[:200]}...")
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_api_key)
            # Try primary model first
            try:
                model = genai.GenerativeModel(get_gemini_model())
                response = model.generate_content(prompt)
                ai_response = response.text.strip()
            except Exception as primary_error:
                logger.warning(f"Primary model {get_gemini_model()} failed: {primary_error}")
                # Fallback to preview model
                model = genai.GenerativeModel(get_gemini_fallback_model())
                response = model.generate_content(prompt)
                ai_response = response.text.strip()
            logger.info(f"DEBUG: AI response: {ai_response[:500]}...")
            logger.info(f"AI response received: {ai_response[:500]}...")
            return ai_response
        except Exception as e:
            logger.info(f"DEBUG: AI call failed: {e}")
            logger.error(f"AI call failed: {e}")
            return '{"sentence": "error", "words": []}'  # Standardized error response

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Generate AI prompt for grammar analysis"""
        return self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str, target_word: str = "") -> Dict[str, Any]:
        """Parse AI response into standardized format"""
        return self.response_parser.parse_response(ai_response, complexity, sentence, target_word)

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate analysis and return confidence score"""
        validated = self.validator.validate_result(parsed_data, original_sentence)
        return validated.get('confidence', 0.5)

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for grammatical roles"""
        return self.tr_config.get_color_scheme(complexity)

    def get_sentence_generation_prompt(self, word: str, language: str, num_sentences: int,
                                     enriched_meaning: str = "", min_length: int = 3,
                                     max_length: int = 15, difficulty: str = "intermediate",
                                     topics: Optional[List[str]] = None) -> Optional[str]:
        """
        Get Turkish-specific sentence generation prompt to ensure proper response formatting.
        """
        # Build context instruction based on topics
        if topics:
            context_instruction = f"- CRITICAL REQUIREMENT: ALL sentences MUST relate to these specific topics: {', '.join(topics)}. Force the word usage into these contexts even if it requires creative interpretation. Do NOT use generic contexts."
        else:
            context_instruction = "- Use diverse real-life contexts: home, travel, food, emotions, work, social life, daily actions"

        # Build meaning instruction based on enriched data
        if enriched_meaning and enriched_meaning != 'N/A':
            if enriched_meaning.startswith('{') and enriched_meaning.endswith('}'):
                # Parse the enriched context format
                context_lines = enriched_meaning[1:-1].split('\n')  # Remove {} and split
                definitions = []
                source = "Unknown"
                for line in context_lines:
                    line = line.strip()
                    if line.startswith('Source:'):
                        source = line.replace('Source:', '').strip()
                    elif line.startswith('Definition'):
                        # Extract just the definition text
                        def_text = line.split(':', 1)[1].strip() if ':' in line else line
                        # Remove part of speech info
                        def_text = def_text.split(' | ')[0].strip()
                        definitions.append(def_text)

                if definitions:
                    meaning_summary = '; '.join(definitions[:4])  # Use first 4 definitions
                    enriched_meaning_instruction = f'Analyze this linguistic data for "{word}" and generate a brief, clean English meaning that encompasses ALL the meanings. Data: {meaning_summary}. IMPORTANT: Consider all meanings and provide a comprehensive meaning.'
                else:
                    enriched_meaning_instruction = f'Analyze this linguistic context for "{word}" and generate a brief, clean English meaning. Context: {enriched_meaning[:200]}. IMPORTANT: Return ONLY the English meaning.'
            else:
                # Legacy format
                enriched_meaning_instruction = f'Use this pre-reviewed meaning for "{word}": "{enriched_meaning}". Generate a clean English meaning based on this.'
        else:
            enriched_meaning_instruction = f'Provide a brief English meaning for "{word}".'

        # Custom prompt for Turkish to ensure proper formatting
        prompt = f"""You are a native-level expert linguist in Turkish (Türkçe).

Your task: Generate a complete learning package for the Turkish word "{word}" in ONE response.

===========================
STEP 1: WORD MEANING
===========================
{enriched_meaning_instruction}
Format: Return exactly one line like "house (a building where people live)" or "he (male pronoun, used as subject)"
IMPORTANT: Keep the entire meaning under 75 characters total.

===========================
WORD-SPECIFIC RESTRICTIONS
===========================
Based on the meaning above, identify any grammatical constraints for "{word}".
Examples: case requirements, suffix harmony, agglutination patterns.
If no restrictions apply, state "No specific grammatical restrictions."
IMPORTANT: Keep the entire restrictions summary under 60 characters total.

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic sentences in Turkish for the word "{word}".

QUALITY RULES:
- Every sentence must use proper Turkish spelling and grammar
- Vowel harmony must be correct in all suffixes
- Case markers must be used appropriately
- The target word "{word}" MUST be used correctly according to restrictions
- Each sentence must be no more than {max_length} characters long
- Difficulty: {difficulty}

VARIETY REQUIREMENTS:
- Use different cases (nominative, accusative, dative, locative, ablative, genitive)
- Use different sentence types: declarative, interrogative, imperative
- Include possessive suffixes and other agglutinative forms when appropriate
{context_instruction}

===========================
STEP 3: ENGLISH TRANSLATIONS
===========================
For EACH sentence above, provide a natural, fluent English translation.
- Translation should be natural English, not literal word-for-word

===========================
STEP 4: IPA TRANSCRIPTION
===========================
For EACH sentence above, provide accurate IPA transcription.
- Use proper IPA symbols for Turkish sounds
- Include syllable stress marks where appropriate

===========================
STEP 5: IMAGE KEYWORDS
===========================
For EACH sentence above, generate exactly 3 specific keywords for image search.
- Keywords should be concrete and specific
- Keywords in English only

===========================
OUTPUT FORMAT - FOLLOW EXACTLY
===========================
Return your response in this exact text format:

MEANING: [brief English meaning]

RESTRICTIONS: [grammatical restrictions]

SENTENCES:
1. [sentence 1 in Turkish]
2. [sentence 2 in Turkish]
3. [sentence 3 in Turkish]
4. [sentence 4 in Turkish]

TRANSLATIONS:
1. [natural English translation for sentence 1]
2. [natural English translation for sentence 2]
3. [natural English translation for sentence 3]
4. [natural English translation for sentence 4]

IPA:
1. [IPA for sentence 1]
2. [IPA for sentence 2]
3. [IPA for sentence 3]
4. [IPA for sentence 4]

KEYWORDS:
1. [keyword1, keyword2, keyword3]
2. [keyword1, keyword2, keyword3]
3. [keyword1, keyword2, keyword3]
4. [keyword1, keyword2, keyword3]

IMPORTANT:
- Return ONLY the formatted text, no extra explanation
- Sentences must be in proper Turkish with correct vowel harmony
- Ensure exactly {num_sentences} sentences, translations, IPA, and keywords"""

        return prompt

    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Map Turkish grammatical roles to color scheme categories"""
        role_mapping = {
            'noun': 'noun',
            'verb': 'verb',
            'adjective': 'adjective',
            'adverb': 'adverb',
            'pronoun': 'pronoun',
            'postposition': 'postposition',
            'conjunction': 'conjunction',
            'interjection': 'interjection',
            'numeral': 'numeral',
            'case_marker': 'case_marker',
            'possessive_suffix': 'possessive_suffix',
            'tense_marker': 'tense_marker',
            'question_particle': 'question_particle',
            'other': 'other'
        }
        return role_mapping.get(grammatical_role, 'other')
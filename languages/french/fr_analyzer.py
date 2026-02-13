# languages/french/fr_analyzer.py
"""
French Grammar Analyzer - Clean Architecture Facade

FRENCH ANALYZER IMPLEMENTATION:
This file implements the French grammar analyzer following the Chinese Simplified gold standard.
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
- FrConfig: French-specific configuration (colors, roles, patterns)
- FrPromptBuilder: Builds AI prompts using Jinja2 templates
- FrResponseParser: Parses AI responses, applies fallbacks, transforms data
- FrValidator: Validates results and calculates confidence scores

INTEGRATION POINTS:
- Called by sentence_generator.py for Pass 3: Grammar Analysis
- Returns GrammarAnalysis objects with word_explanations in [word, role, color, meaning] format
- Supports batch processing with 8-sentence limits to prevent token overflow
- Uses 2000 max_tokens for complete AI responses (prevents JSON truncation)

INHERITANCE:
- Inherits from BaseGrammarAnalyzer (French is fusional, Indo-European)
- Can be adapted for other Romance languages by changing domain components

USAGE FOR FRENCH:
1. Create French-specific domain components (config, prompt_builder, etc.)
2. Copy this facade structure, changing only the component imports
3. Implement French-specific logic in domain components, not here
"""

import logging
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

from .domain.fr_config import FrConfig
from .domain.fr_prompt_builder import FrPromptBuilder
from .domain.fr_response_parser import FrResponseParser
from .domain.fr_fallbacks import FrFallbacks
from .domain.fr_validator import FrValidator

# Import centralized configuration
from streamlit_app.shared_utils import get_gemini_model, get_gemini_fallback_model, get_gemini_api

logger = logging.getLogger(__name__)

class FrAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for French - Clean Architecture.

    FRENCH-SPECIFIC FEATURES:
    - Fusional Language: Complex inflection with multiple grammatical features
    - Gender System: Grammatical gender (masculine/feminine) affecting agreement
    - Verb Conjugation: Three main groups with irregular forms and stem changes
    - Agreement Cascade: Adjectives, pronouns, past participles agree with nouns
    - Complex Prepositions: Multiple translations for single English prepositions
    - Partitive Articles: du/de la/de l'/des for partial quantities

    Key Features: ['gender_agreement', 'verb_conjugation', 'complex_prepositions', 'partitive_articles', 'fusional_morphology']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    Script: Latin alphabet with diacritics (LTR), alphabetic writing system
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "fr"
    LANGUAGE_NAME = "French"

    def __init__(self):
        """
        Initialize French analyzer with domain components.

        FRENCH-SPECIFIC INITIALIZATION:
        1. Initialize domain components first (config, builders, parsers)
        2. Create language config with French metadata
        3. Call parent constructor with config
        4. Set up logging and validation

        This pattern ensures all dependencies are available before analysis begins.
        """
        logger.info("DEBUG: FrAnalyzer __init__ called")
        # Initialize domain components first
        self.fr_config = FrConfig()
        self.fr_fallbacks = FrFallbacks(self.fr_config)
        self.prompt_builder = FrPromptBuilder(self.fr_config)
        self.response_parser = FrResponseParser(self.fr_config, self.fr_fallbacks)
        self.validator = FrValidator(self.fr_config)

        config = LanguageConfig(
            code="fr",
            name="French",
            native_name="Français",
            family="Indo-European",
            script_type="alphabetic",
            complexity_rating="high",
            key_features=['gender_agreement', 'verb_conjugation', 'complex_prepositions', 'partitive_articles', 'fusional_morphology'],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )
        super().__init__(config)

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str) -> GrammarAnalysis:
        """
        Analyze grammar for a single French sentence.

        FRENCH WORKFLOW:
        1. Build AI prompt using prompt_builder (French-specific templates)
        2. Call AI API with proper error handling
        3. Parse response using response_parser (with French fallbacks)
        4. Validate results using validator (gender agreement, conjugation)
        5. Generate HTML output for colored display
        6. Return GrammarAnalysis object

        FRENCH FALLBACK HIERARCHY:
        - Primary: AI-generated analysis with agreement and conjugation validation
        - Secondary: Pattern-based fallbacks for gender detection and verb forms
        - Tertiary: Basic rule-based fallbacks for morphological analysis

        OUTPUT FORMAT:
        - word_explanations: [[word, role, color, meaning], ...]
        - Maintains sentence word order (LTR) for optimal user experience
        - Colors based on grammatical roles and complexity level
        """
        try:
            prompt = self.prompt_builder.build_single_prompt(sentence, target_word, complexity)
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
        Analyze grammar for multiple French sentences.

        FRENCH BATCH PROCESSING:
        - Handles 8 sentences efficiently (prevents token overflow)
        - Uses single AI call for all sentences (cost-effective)
        - Applies per-result validation and fallbacks
        - Maintains sentence order in output
        - Provides partial fallbacks (some sentences may succeed even if others fail)

        FRENCH BATCH SIZE CONSIDERATIONS:
        - 8 sentences: Optimal balance of efficiency and response quality
        - Prevents JSON truncation with 2000 max_tokens
        - Allows meaningful error recovery per sentence
        - Accounts for fusional morphology analysis complexity

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
        Call Google Gemini AI for French grammar analysis.

        FRENCH AI INTEGRATION:
        - Uses gemini-2.5-flash model (primary) with gemini-3-flash-preview fallback
        - 2000 max_output_tokens prevents JSON truncation in batch responses
        - 30-second timeout for online environments
        - Comprehensive error handling with meaningful logging
        - Returns error response for fallback processing

        FRENCH CONSIDERATIONS:
        - Handles diacritics and elision properly
        - Accounts for fusional morphology analysis
        - Supports gender agreement and conjugation validation
        - Future-proof: Update model names as Google releases new versions

        ERROR HANDLING:
        - Catches all exceptions to prevent crashes
        - Returns standardized error response for fallback logic
        - Logs detailed information for debugging
        """
        logger.info(f"DEBUG: _call_ai called with prompt: {prompt[:200]}...")
        try:
            api = get_gemini_api()
            api.configure(api_key=gemini_api_key)
            # Try primary model first
            try:
                response = api.generate_content(
                    model=get_gemini_model(),
                    contents=prompt,
                    config={'max_output_tokens': 4000}
                )
                ai_response = response.text.strip()
            except Exception as primary_error:
                logger.warning(f"Primary model {get_gemini_model()} failed: {primary_error}")
                # Fallback to preview model
                response = api.generate_content(
                    model=get_gemini_fallback_model(),
                    contents=prompt,
                    config={'max_output_tokens': 4000}
                )
                ai_response = response.text.strip()
            logger.info(f"DEBUG: AI response: {ai_response[:500]}...")
            logger.info(f"AI response received: {ai_response[:500]}...")
            return ai_response
        except Exception as e:
            logger.info(f"DEBUG: AI call failed: {e}")
            logger.error(f"AI call failed: {e}")
            return '{"sentence": "error", "words": []}'  # Standardized error response

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """
        Return color scheme for French grammatical elements.

        COLOR CODING PHILOSOPHY:
        - Consistent colors across complexity levels where possible
        - Progressive disclosure: More roles distinguished at higher complexity
        - Accessible colors: High contrast, colorblind-friendly
        - Language-appropriate: Colors that make sense for French grammar

        FRENCH COMPLEXITY PROGRESSION:
        - Beginner: Basic roles (noun, verb, adjective, determiners)
        - Intermediate: More distinctions (pronoun types, verb auxiliaries, prepositions)
        - Advanced: Full granularity (all pronoun subtypes, verb moods, complex determiners)
        """
        return self.fr_config.get_color_scheme(complexity)

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """
        Generate HTML output for French text with inline color styling for Anki compatibility.

        FRENCH HTML GENERATION:
        - Handles spaces between words (alphabetic script)
        - Preserves diacritics and elision
        - Uses position-based replacement for accuracy
        - Maintains word boundaries for proper coloring
        """
        explanations = parsed_data.get('word_explanations', [])

        print(f"DEBUG French HTML Gen - Input explanations count: {len(explanations)}")
        print(f"DEBUG French HTML Gen - Input sentence: '{sentence}'")

        # For French (alphabetic script with spaces), split by spaces but handle elision
        color_scheme = self.get_color_scheme(complexity)

        # Sort explanations by position in sentence to avoid conflicts
        sorted_explanations = sorted(explanations, key=lambda x: sentence.find(x[0]) if len(x) >= 3 else len(sentence))

        # Build HTML by processing the sentence word by word
        html_parts = []
        words_in_sentence = sentence.split()
        i = 0

        for word_in_sentence in words_in_sentence:
            # Find matching explanation
            matched = False
            for exp in sorted_explanations:
                if len(exp) >= 3:
                    word = exp[0]
                    # Handle elision matching (e.g., "l'" matches "le" or "la")
                    if self._words_match(word_in_sentence, word):
                        pos = exp[1]
                        category = self._map_grammatical_role_to_category(pos)
                        color = color_scheme.get(category, '#888888')

                        # Escape curly braces in word to prevent f-string issues
                        safe_word_display = word_in_sentence.replace('{', '{{').replace('}', '}}')
                        colored_word = f'<span style="color: {color}; font-weight: bold;">{safe_word_display}</span>'
                        html_parts.append(colored_word)

                        print(f"DEBUG French HTML Gen - Replaced '{word_in_sentence}' with category '{category}' and color '{color}'")

                        matched = True
                        break

            if not matched:
                # No match, add word with default styling
                default_color = color_scheme.get('default', '#000000')
                safe_word_display = word_in_sentence.replace('{', '{{').replace('}', '}}')
                html_parts.append(f'<span style="color: {default_color}; font-weight: bold;">{safe_word_display}</span>')

            # Add space between words (except for last word)
            if i < len(words_in_sentence) - 1:
                html_parts.append(' ')
            i += 1

        html = ''.join(html_parts)
        print(f"DEBUG French HTML Gen - Final HTML result: {html}")
        return html

    def _words_match(self, word_in_sentence: str, explanation_word: str) -> bool:
        """Check if words match, handling elision cases."""
        # Direct match
        if word_in_sentence == explanation_word:
            return True

        # Handle elision: if sentence has "l'" and explanation has "le/la"
        if word_in_sentence == "l'" and explanation_word in ["le", "la"]:
            return True

        # Handle elision: if sentence has "d'" and explanation has "de"
        if word_in_sentence == "d'" and explanation_word == "de":
            return True

        # Handle other common elisions
        elision_pairs = [
            ("s'", "se"),
            ("c'", "ce"),
            ("j'", "je"),
            ("m'", "me"),
            ("t'", "te"),
            ("n'", "ne"),
            ("qu'", "que"),
            ("jusqu'", "jusque"),
            ("lorsqu'", "lorsque"),
            ("puisqu'", "puisque"),
            ("quoiqu'", "quoique")
        ]

        for elided, full in elision_pairs:
            if word_in_sentence == elided and explanation_word == full:
                return True

        return False

    def _map_grammatical_role_to_category(self, role: str) -> str:
        """Map detailed grammatical roles to color categories."""
        # Use the role hierarchy from config
        hierarchy = self.fr_config.grammatical_roles.get('role_hierarchy', {})
        return hierarchy.get(role, role)

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """
        Generate French-specific AI prompt for grammar analysis.

        FRENCH PROMPT GENERATION:
        - Delegates to prompt_builder for complexity-aware prompt building
        - Uses French-specific templates with gender agreement and conjugation logic
        - Handles fusional morphology analysis requirements
        - Supports all three complexity levels (beginner, intermediate, advanced)
        """
        return self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """
        Parse AI response into standardized French grammar analysis format.

        FRENCH RESPONSE PARSING:
        - Delegates to response_parser for robust JSON extraction
        - Applies French-specific fallbacks for gender detection and verb forms
        - Transforms data to standard format with agreement validation
        - Handles elision and liaison processing
        """
        return self.response_parser.parse_response(ai_response, complexity, sentence, None)

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """
        Validate French analysis quality and return confidence score.

        FRENCH VALIDATION:
        - Delegates to validator for comprehensive quality assessment
        - Checks gender agreement patterns and verb conjugation accuracy
        - Validates partitive article usage and adjective placement
        - Returns confidence score (0.0-1.0) with explanation quality factors
        """
        validation_result = self.validator.validate_result(parsed_data, original_sentence)
        return validation_result.get('confidence', 0.0)

    def get_sentence_generation_prompt(self, word: str, language: str, num_sentences: int,
                                     enriched_meaning: str = "", min_length: int = 3,
                                     max_length: int = 15, difficulty: str = "intermediate",
                                     topics: Optional[List[str]] = None) -> Optional[str]:
        """
        Get French-specific sentence generation prompt to ensure proper response formatting.

        FRENCH SENTENCE GENERATION:
        - Enforces character limits (75 chars for meanings, 60 for restrictions)
        - Includes French-specific grammar requirements
        - Handles gender agreement and verb conjugations
        - Supports elision and liaison contexts
        """
        # Build context instruction based on topics
        if topics:
            context_instruction = f"- CRITICAL REQUIREMENT: ALL sentences MUST relate to these specific topics: {', '.join(topics)}. Force the word usage into these contexts even if it requires creative interpretation. Do NOT use generic contexts."
        else:
            context_instruction = "- Use diverse real-life contexts: home, travel, food, emotions, work, social life, daily actions, cultural experiences"

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

        # French-specific prompt with character limits and grammar requirements
        prompt = f"""You are a native-level expert linguist in French (Français).

Your task: Generate a complete learning package for the French word "{word}" in ONE response.

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
Examples: gender requirements (masculine/feminine), agreement patterns, conjugation groups, preposition requirements
If no restrictions apply, state "No specific grammatical restrictions."
IMPORTANT: Keep the entire restrictions summary under 60 characters total.

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic sentences in French for the word "{word}".

QUALITY RULES:
- Every sentence must sound like native French
- Grammar, syntax, spelling, and French-specific features must be correct
- The target word "{word}" MUST be used correctly according to restrictions
- Each sentence must be between {min_length} and {max_length} words long
- COUNT words precisely; if outside the range, regenerate internally
- Difficulty: {difficulty}

FRENCH-SPECIFIC REQUIREMENTS:
- Use proper gender agreement (masculine/feminine)
- Apply correct verb conjugations (person, number, tense, mood)
- Include appropriate determiners and pronouns
- Handle elision and liaison where natural
- Use varied sentence structures (declarative, interrogative, negative)

VARIETY REQUIREMENTS:
- Use different verb tenses and moods when applicable
- Include different pronoun types (personal, possessive, demonstrative)
- Use various determiners (definite, indefinite, partitive)
- Include prepositional phrases with different prepositions
- Use both simple and complex sentence structures
{context_instruction}

===========================
STEP 3: ENGLISH TRANSLATIONS
===========================
For EACH sentence above, provide a natural, fluent English translation.
- Translation should be natural English, not literal word-for-word

===========================
STEP 4: IPA TRANSCRIPTION
===========================
For EACH sentence above, provide IPA phonetic transcription.
- Use standard IPA symbols for French pronunciation
- Include liaison and elision markers where applicable
- Show stress and intonation patterns

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
1. [sentence 1 in French]
2. [sentence 2 in French]
3. [sentence 3 in French]
4. [sentence 4 in French]

TRANSLATIONS:
1. [natural English translation for sentence 1]
2. [natural English translation for sentence 2]
3. [natural English translation for sentence 3]
4. [natural English translation for sentence 4]

IPA:
1. [IPA transcription for sentence 1]
2. [IPA transcription for sentence 2]
3. [IPA transcription for sentence 3]
4. [IPA transcription for sentence 4]

KEYWORDS:
1. [keyword1, keyword2, keyword3]
2. [keyword1, keyword2, keyword3]
3. [keyword1, keyword2, keyword3]
4. [keyword1, keyword2, keyword3]

IMPORTANT:
- Return ONLY the formatted text, no extra explanation
- Sentences must be in French only
- Ensure exactly {num_sentences} sentences, translations, IPA transcriptions, and keywords
- Respect character limits for meaning and restrictions"""

        return prompt
# languages/chinese_simplified/zh_analyzer.py
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
from typing import Dict, List, Any, Optional
from pathlib import Path

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

from .domain.zh_config import ZhConfig
from .domain.zh_prompt_builder import ZhPromptBuilder
from .domain.zh_response_parser import ZhResponseParser
from .domain.zh_validator import ZhValidator

# Import centralized configuration — lazy import in _call_ai() to support test mocking

logger = logging.getLogger(__name__)

class ZhAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Chinese Simplified (ç®€ä½“ä¸­æ–‡) - Clean Architecture.

    CHINESE-SPECIFIC FEATURES:
    - Analytic Language: No inflection, relies on particles and word order
    - Aspect System: äº† (completed), ç€ (ongoing), è¿‡ (experienced)
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
            native_name="ç®€ä½“ä¸­æ–‡",
            family="Sino-Tibetan",
            script_type="logographic",
            complexity_rating="medium",
            key_features=['aspect_markers', 'classifiers', 'particles', 'topic_comment', 'no_inflection'],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )
        super().__init__(config)

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str) -> GrammarAnalysis:
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

        CHINESE AI INTEGRATION:
        - Uses gemini-2.5-flash model (primary) with gemini-3-flash-preview fallback
        - 2000 max_output_tokens prevents JSON truncation in batch responses
        - 30-second timeout for online environments
        - Comprehensive error handling with meaningful logging
        - Returns error response for fallback processing

        CHINESE CONSIDERATIONS:
        - Handles logographic script properly
        - Accounts for compound word analysis
        - Supports aspect marker and classifier validation
        - Future-proof: Update model names as Google releases new versions

        ERROR HANDLING:
        - Catches all exceptions to prevent crashes
        - Returns standardized error response for fallback logic
        - Logs detailed information for debugging
        """
        logger.info(f"DEBUG: _call_ai called with prompt: {prompt[:200]}...")
        try:
            from streamlit_app.shared_utils import get_gemini_model, get_gemini_fallback_model, get_gemini_api
            api = get_gemini_api()
            api.configure(api_key=gemini_api_key)
            # Try primary model first
            try:
                response = api.generate_content(
                    model=get_gemini_model(),
                    contents=prompt,
                    config={'max_output_tokens': 20000}
                )
                ai_response = response.text.strip()
            except Exception as primary_error:
                logger.warning(f"Primary model {get_gemini_model()} failed: {primary_error}")
                # Fallback to preview model
                response = api.generate_content(
                    model=get_gemini_fallback_model(),
                    contents=prompt,
                    config={'max_output_tokens': 20000}
                )
                ai_response = response.text.strip()
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
                if word in ['çš„', 'äº†', 'ç€', 'è¿‡']:
                    role = 'particle'
                elif word in ['ä¸ª', 'æœ¬', 'æ¯']:
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
            if word in ['çš„', 'äº†', 'ç€', 'è¿‡']:
                role = 'particle'
            elif word in ['ä¸ª', 'æœ¬', 'æ¯']:
                role = 'classifier'
            word_data.append({
                'word': word,
                'grammatical_role': role,
                'individual_meaning': f'{role} in sentence'
            })
        return '{"sentence": "' + sentence + '", "words": ' + str(word_data).replace("'", '"') + '}'

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Gold-standard: Delegate to prompt builder (soft guidance + complexity-aware)."""
        return self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

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

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into standardized Chinese grammar analysis format."""
        return self.response_parser.parse_response(ai_response, complexity, sentence, None)

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate Chinese analysis quality and return confidence score."""
        return self.validator.validate_result(parsed_data, original_sentence)['confidence']

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Gold-standard HTML generator: complexity-aware + prefers pre-computed color."""
        explanations = parsed_data.get('word_explanations', [])

        print(f"DEBUG Chinese HTML Gen - Input explanations count: {len(explanations)}")
        print(f"DEBUG Chinese HTML Gen - Input sentence: '{sentence}'")
        print(f"DEBUG Chinese HTML Gen - Complexity level: {complexity}")

        # Use the ACTUAL complexity level the user chose
        color_scheme = self.get_color_scheme(complexity)

        # Sort explanations by position in sentence to avoid conflicts
        sorted_explanations = sorted(explanations, key=lambda x: sentence.find(x[0]) if len(x) >= 3 else len(sentence))

        html_parts = []
        i = 0
        sentence_len = len(sentence)

        while i < sentence_len:
            matched = False
            for exp in sorted_explanations:
                if len(exp) >= 3:
                    word = exp[0]
                    word_len = len(word)

                    if i + word_len <= sentence_len and sentence[i:i + word_len] == word:
                        # Prefer color already computed by the parser (best)
                        if len(exp) >= 3 and isinstance(exp[2], str) and exp[2].startswith('#'):
                            color = exp[2]
                        else:
                            pos = exp[1]
                            category = self._map_grammatical_role_to_category(pos)
                            color = color_scheme.get(category, '#888888')

                        safe_word_display = word.replace('{', '{{').replace('}', '}}')
                        colored_word = f'<span style="color: {color}; font-weight: bold;">{safe_word_display}</span>'
                        html_parts.append(colored_word)

                        print(f"DEBUG Chinese HTML Gen - Replaced '{word}' with color '{color}' (role: {exp[1]})")

                        i += word_len
                        matched = True
                        break

            if not matched:
                default_color = color_scheme.get('default', '#000000')
                html_parts.append(f'<span style="color: {default_color}; font-weight: bold;">{sentence[i]}</span>')
                i += 1

        html = ''.join(html_parts)
        print("DEBUG Chinese HTML Gen - Final HTML result: " + html)
        return html

    def get_sentence_generation_prompt(self, word: str, language: str, num_sentences: int,
                                     enriched_meaning: str = "", min_length: int = 3,
                                     max_length: int = 15, difficulty: str = "intermediate",
                                     topics: Optional[List[str]] = None) -> Optional[str]:
        """
        Get Chinese Simplified-specific sentence generation prompt to ensure proper response formatting.
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

        # Custom prompt for Chinese Simplified to ensure proper formatting
        prompt = f"""You are a native-level expert linguist in Simplified Chinese (ç®€ä½“ä¸­æ–‡).

Your task: Generate a complete learning package for the Simplified Chinese word "{word}" in ONE response.

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
Examples: particles only (çš„/äº†/å—), specific measure words required, character-based restrictions.
If no restrictions apply, state "No specific grammatical restrictions."
IMPORTANT: Keep the entire restrictions summary under 60 characters total.

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic sentences in Simplified Chinese for the word "{word}".

QUALITY RULES:
- Every sentence must use proper Simplified Chinese characters (ç®€ä½“å­—)
- Grammar, syntax, and character usage must be correct
- The target word "{word}" MUST be used correctly according to restrictions
- Each sentence must be between {min_length} and {max_length} words long; if no spaces, treat characters as words
- COUNT precisely; if outside the range, regenerate internally
- Difficulty: {difficulty}

VARIETY REQUIREMENTS:
- Use different aspect particles (äº†, ç€, è¿‡) and sentence structures if applicable
- Use different sentence types: declarative, interrogative, imperative
- Include appropriate measure words/classifiers when needed
{context_instruction}

===========================
STEP 3: ENGLISH TRANSLATIONS
===========================
For EACH sentence above, provide a natural, fluent English translation.
- Translation should be natural English, not literal word-for-word

===========================
STEP 4: PINYIN TRANSCRIPTION
===========================
For EACH sentence above, provide accurate Pinyin transcription with tone marks.
- Use proper tone marks (Ä, Ã¡, ÇŽ, Ã , Ä“, Ã©, Ä›, Ã¨, etc.)
- Include spaces between words for readability

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
1. [sentence 1 in Simplified Chinese]
2. [sentence 2 in Simplified Chinese]
3. [sentence 3 in Simplified Chinese]
4. [sentence 4 in Simplified Chinese]

TRANSLATIONS:
1. [natural English translation for sentence 1]
2. [natural English translation for sentence 2]
3. [natural English translation for sentence 3]
4. [natural English translation for sentence 4]

PINYIN:
1. [Pinyin for sentence 1]
2. [Pinyin for sentence 2]
3. [Pinyin for sentence 3]
4. [Pinyin for sentence 4]

KEYWORDS:
1. [keyword1, keyword2, keyword3]
2. [keyword1, keyword2, keyword3]
3. [keyword1, keyword2, keyword3]
4. [keyword1, keyword2, keyword3]

IMPORTANT:
- Return ONLY the formatted text, no extra explanation
- Sentences must be in Simplified Chinese characters only
- Ensure exactly {num_sentences} sentences, translations, Pinyin, and keywords"""

        return prompt

    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Robust mapping that handles beginner-level verbose roles after soft guidance."""
        if not grammatical_role:
            return 'other'
        
        role = grammatical_role.lower().strip()
        # Strip all parentheticals (e.g. "Adverb (negation marker)" → "adverb")
        role = re.sub(r'\s*\([^)]*\)', '', role).strip()

        # Most specific first
        if 'pronoun' in role or 'demonstrative' in role:
            return 'pronoun'
        elif any(x in role for x in ['classifier', 'measure word', 'measure']):
            return 'classifier'
        elif 'noun' in role:
            return 'noun'
        elif any(x in role for x in ['adverb', 'negation']):
            return 'adverb'
        elif 'verb' in role or 'copula' in role:
            return 'verb'
        elif 'adjective' in role:
            return 'adjective'
        elif any(x in role for x in ['particle', 'structural']):
            return 'particle'
        elif 'aspect' in role:
            return 'aspect_marker'
        elif 'modal' in role:
            return 'modal_particle'
        elif any(x in role for x in ['numeral', 'number']):
            return 'numeral'
        else:
            return 'other'

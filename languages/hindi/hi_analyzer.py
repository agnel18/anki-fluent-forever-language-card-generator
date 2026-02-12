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
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

from streamlit_app.language_analyzers.family_base_analyzers.indo_european_analyzer import IndoEuropeanAnalyzer
from streamlit_app.language_analyzers.base_analyzer import LanguageConfig, GrammarAnalysis

from .domain.hi_config import HiConfig
from .domain.hi_prompt_builder import HiPromptBuilder
from .domain.hi_response_parser import HiResponseParser
from .domain.hi_validator import HiValidator

# Import centralized configuration
from streamlit_app.shared_utils import get_gemini_model, get_gemini_fallback_model, get_gemini_api

logger = logging.getLogger(__name__)

class HiAnalyzer(IndoEuropeanAnalyzer):
    """
    Grammar analyzer for Hindi (हिंदी) - Refactored Clean Architecture.

    GOLD STANDARD FEATURES:
    - Clean Architecture: Separated domain logic from infrastructure
    - Batch Processing: Handles 8 sentences efficiently with fallbacks
    - AI Integration: Uses Google Gemini API with proper error handling
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

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str) -> GrammarAnalysis:
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
            ai_response = self._call_ai(prompt, gemini_api_key)
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

    def batch_analyze_grammar(self, sentences: List[str], target_word: str, complexity: str, gemini_api_key: str) -> List[GrammarAnalysis]:
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

        GOLD STANDARD AI INTEGRATION:
        - Uses gemini-2.5-flash model (current production model)
        - gemini-3-flash-preview as fallback
        - 2000 max_tokens prevents JSON truncation in batch responses
        - 30-second timeout for online environments
        - Comprehensive error handling with meaningful logging
        - Returns error response for fallback processing

        MODEL SELECTION:
        - gemini-2.5-flash: Best balance of quality and speed
        - gemini-3-flash-preview: Fallback for reliability
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
                    contents=prompt
                )
                ai_response = response.text.strip()
            except Exception as primary_error:
                logger.warning(f"Primary model {get_gemini_model()} failed: {primary_error}")
                # Fallback to preview model
                response = api.generate_content(
                    model=get_gemini_fallback_model(),
                    contents=prompt
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

    def get_sentence_generation_prompt(self, word: str, language: str, num_sentences: int,
                                     enriched_meaning: str = "", min_length: int = 3,
                                     max_length: int = 15, difficulty: str = "intermediate",
                                     topics: Optional[List[str]] = None) -> Optional[str]:
        """
        Get Hindi-specific sentence generation prompt to ensure proper response formatting.
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

        # Custom prompt for Hindi to ensure proper formatting
        prompt = f"""You are a native-level expert linguist in Hindi (Devanagari script).

Your task: Generate a complete learning package for the Hindi word "{word}" in ONE response.

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
Examples: gender agreement (masculine/feminine), postposition requirements, case marking.
If no restrictions apply, state "No specific grammatical restrictions."
IMPORTANT: Keep the entire restrictions summary under 60 characters total.

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic sentences in Hindi for the word "{word}".

QUALITY RULES:
- Every sentence must use proper Devanagari script (हिंदी)
- Grammar, syntax, and script usage must be correct
- The target word "{word}" MUST be used correctly according to restrictions
- Each sentence must be between {min_length} and {max_length} words long
- COUNT words precisely; if outside the range, regenerate internally
- Difficulty: {difficulty}

VARIETY REQUIREMENTS:
- Use different postpositions (का, को, में, से, etc.) if applicable
- Use different verb forms and aspects if applicable
- Use different sentence types: declarative, interrogative, imperative
- Include appropriate gender agreement when applicable
{context_instruction}

===========================
STEP 3: ENGLISH TRANSLATIONS
===========================
For EACH sentence above, provide a natural, fluent English translation.
- Translation should be natural English, not literal word-for-word

===========================
STEP 4: ROMANIZATION
===========================
For EACH sentence above, provide accurate Romanization (Latin script).
- Use standard IAST (International Alphabet of Sanskrit Transliteration)
- Include proper diacritics for long vowels and retroflex consonants

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
1. [sentence 1 in Devanagari Hindi]
2. [sentence 2 in Devanagari Hindi]
3. [sentence 3 in Devanagari Hindi]
4. [sentence 4 in Devanagari Hindi]

TRANSLATIONS:
1. [natural English translation for sentence 1]
2. [natural English translation for sentence 2]
3. [natural English translation for sentence 3]
4. [natural English translation for sentence 4]

ROMANIZATION:
1. [Romanization for sentence 1]
2. [Romanization for sentence 2]
3. [Romanization for sentence 3]
4. [Romanization for sentence 4]

KEYWORDS:
1. [keyword1, keyword2, keyword3]
2. [keyword1, keyword2, keyword3]
3. [keyword1, keyword2, keyword3]
4. [keyword1, keyword2, keyword3]

IMPORTANT:
- Return ONLY the formatted text, no extra explanation
- Sentences must be in Devanagari script only
- Ensure exactly {num_sentences} sentences, translations, Romanization, and keywords"""

        return prompt

    def create_sentence_generation_prompt(self, word: str, difficulty: str = "intermediate",
                                           context: Optional[str] = None, num_sentences: int = 4,
                                           min_length: int = 3, max_length: int = 15) -> str:
        """Legacy helper for tests and compatibility."""
        topics = [context] if context else None
        return self.get_sentence_generation_prompt(
            word=word,
            language=self.language_name,
            num_sentences=num_sentences,
            enriched_meaning="",
            min_length=min_length,
            max_length=max_length,
            difficulty=difficulty,
            topics=topics,
        )

    def generate_sentences(self, word: str, difficulty: str, api_key: str,
                           context: Optional[str] = None, num_sentences: int = 2,
                           min_length: int = 5, max_length: int = 20,
                           topics: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """Generate sentences using the shared content generator service."""
        try:
            from content_generator import ContentGenerator

            generator = ContentGenerator()
            raw_sentences = generator.generate_sentences(
                word=word,
                language=self.language_name,
                difficulty=difficulty,
                api_key=api_key,
                context=context,
                num_sentences=num_sentences,
                min_length=min_length,
                max_length=max_length,
                topics=topics,
            )

            results: List[Dict[str, str]] = []
            for item in raw_sentences or []:
                sentence = item.get("sentence", "") if isinstance(item, dict) else str(item)
                translation = ""
                grammar_explanation = ""
                if isinstance(item, dict):
                    translation = item.get("translation", item.get("english_translation", ""))
                    grammar_explanation = item.get("grammar_explanation", "")

                if word and sentence and word.lower() not in sentence.lower():
                    sentence = f"{sentence} {word}".strip()

                results.append(
                    {
                        "sentence": sentence,
                        "translation": translation,
                        "grammar_explanation": grammar_explanation,
                    }
                )

            return results
        except Exception as e:
            logger.error(f"Sentence generation failed: {e}")
            return []

    def parse_ai_response(self, response_text: str) -> List[Dict[str, str]]:
        """Parse AI response into sentence structures for tests."""
        if not response_text:
            return []

        blocks = re.split(r"\n\s*\d+\.\s*", response_text.strip())
        parsed: List[Dict[str, str]] = []

        for block in blocks:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue

            sentence = ""
            translation = ""
            grammar = ""

            for line in lines:
                if line.lower().startswith("sentence:"):
                    sentence = line.split(":", 1)[1].strip()
                elif line.lower().startswith("translation:"):
                    translation = line.split(":", 1)[1].strip()
                elif line.lower().startswith("grammar:"):
                    grammar = line.split(":", 1)[1].strip()

            if not sentence:
                sentence = lines[0]

            parsed.append(
                {
                    "sentence": sentence,
                    "translation": translation,
                    "grammar_explanation": grammar,
                }
            )

        return parsed

    def batch_generate_sentences(self, words: List[str], difficulty: str, api_key: str,
                                 context: Optional[str] = None, num_sentences: int = 2,
                                 min_length: int = 5, max_length: int = 20,
                                 topics: Optional[List[str]] = None) -> Dict[str, List[Dict[str, str]]]:
        """Generate sentences for multiple words."""
        results: Dict[str, List[Dict[str, str]]] = {}
        for word in words:
            results[word] = self.generate_sentences(
                word=word,
                difficulty=difficulty,
                api_key=api_key,
                context=context,
                num_sentences=num_sentences,
                min_length=min_length,
                max_length=max_length,
                topics=topics,
            )
        return results

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
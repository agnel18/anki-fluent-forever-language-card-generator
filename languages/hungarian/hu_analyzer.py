# languages/hungarian/hu_analyzer.py
"""
Hungarian Grammar Analyzer - Clean Architecture Facade

Implements the Hungarian grammar analyzer following the French v2.0 gold standard.
Orchestrates domain components for grammar analysis of Hungarian text.

HUNGARIAN-SPECIFIC FEATURES:
- Agglutinative morphology: extensive suffixing with vowel harmony
- 18 grammatical cases expressed by suffixes on nouns
- Definite vs indefinite verb conjugation (two paradigms)
- Preverbs (igekötők): meg-, el-, ki-, be-, fel-, le-, vissza-, össze-
- Postpositions instead of prepositions
- Possessive suffixes on nouns
- Flexible word order with topic-focus structure
- No grammatical gender
"""

import logging
import re
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

from .domain.hu_config import HuConfig
from .domain.hu_prompt_builder import HuPromptBuilder
from .domain.hu_response_parser import HuResponseParser
from .domain.hu_validator import HuValidator
from .infrastructure.hu_fallbacks import HuFallbacks

logger = logging.getLogger(__name__)


class HuAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Hungarian — Clean Architecture.

    Hungarian is agglutinative (Uralic/Finno-Ugric family) with SVO default order,
    Latin script with diacritics, and extensive case suffixing with vowel harmony.
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "hu"
    LANGUAGE_NAME = "Hungarian"

    def __init__(self):
        self.hu_config = HuConfig()
        self.hu_fallbacks = HuFallbacks(self.hu_config)
        self.prompt_builder = HuPromptBuilder(self.hu_config)
        self.response_parser = HuResponseParser(self.hu_config, self.hu_fallbacks)
        self.validator = HuValidator(self.hu_config)

        config = LanguageConfig(
            code="hu",
            name="Hungarian",
            native_name="magyar",
            family="Uralic",
            script_type="latin_extended",
            complexity_rating="high",
            key_features=[
                'agglutinative_morphology', 'vowel_harmony', '18_grammatical_cases',
                'definite_indefinite_conjugation', 'preverbs', 'postpositions',
                'possessive_suffixes', 'topic_focus_structure', 'no_grammatical_gender'
            ],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )
        super().__init__(config)

    def analyze_grammar(self, sentence: str, target_word: str, complexity: str, gemini_api_key: str) -> GrammarAnalysis:
        """Analyze grammar for a single Hungarian sentence."""
        try:
            start_time = time.time()

            logger.info(f"Hungarian Analysis: Starting for '{sentence[:50]}...' (complexity: {complexity})")

            prompt = self.prompt_builder.build_single_prompt(sentence, target_word, complexity)
            ai_response = self._call_ai(prompt, gemini_api_key)
            result = self.response_parser.parse_response(ai_response, complexity, sentence, target_word)
            validated_result = self.validator.validate_result(result, sentence)

            # Explanation quality check
            quality_validation = self.validator.validate_explanation_quality(validated_result)
            validated_result['explanation_quality'] = quality_validation

            base_confidence = validated_result.get('confidence', 0.5)
            quality_score = quality_validation.get('quality_score', 1.0)
            adjusted_confidence = min(base_confidence * quality_score, 1.0)
            validated_result['confidence'] = adjusted_confidence

            html_output = self._generate_html_output(validated_result, sentence, complexity)

            analysis_result = GrammarAnalysis(
                sentence=sentence,
                target_word=target_word,
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=validated_result.get('elements', {}),
                explanations=validated_result.get('explanations', {}),
                word_explanations=validated_result.get('word_explanations', []),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=adjusted_confidence
            )

            processing_time = time.time() - start_time
            logger.info(f"Hungarian Analysis: Completed in {processing_time:.2f}s, confidence: {adjusted_confidence:.2f}")

            return analysis_result

        except Exception as e:
            logger.error(f"Analysis failed for '{sentence}': {e}")
            fallback_result = self.hu_fallbacks.create_fallback(sentence, complexity)
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
        """Analyze grammar for multiple Hungarian sentences."""
        logger.info(f"Batch analyze: {len(sentences)} sentences")
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
            fallback_analyses = []
            for sentence in sentences:
                fallback_result = self.hu_fallbacks.create_fallback(sentence, complexity)
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
        """Call Google Gemini AI for Hungarian grammar analysis."""
        # LAZY IMPORT — critical for analyzer registry discovery
        from streamlit_app.shared_utils import get_gemini_model, get_gemini_fallback_model, get_gemini_api

        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                api = get_gemini_api()
                api.configure(api_key=gemini_api_key)

                try:
                    response = api.generate_content(
                        model=get_gemini_model(),
                        contents=prompt,
                        config={'max_output_tokens': 20000, 'temperature': 0.1}
                    )
                    return response.text.strip()

                except Exception as primary_error:
                    logger.warning(f"Primary model failed (attempt {attempt + 1}): {str(primary_error)[:200]}")
                    try:
                        response = api.generate_content(
                            model=get_gemini_fallback_model(),
                            contents=prompt,
                            config={'max_output_tokens': 20000, 'temperature': 0.1}
                        )
                        return response.text.strip()

                    except Exception as fallback_error:
                        logger.warning(f"Fallback model also failed (attempt {attempt + 1}): {str(fallback_error)[:200]}")
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            time.sleep(delay)
                        else:
                            raise fallback_error

            except Exception as e:
                logger.error(f"All models failed on attempt {attempt + 1}: {str(e)[:200]}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
                else:
                    return '{"error": "AI service unavailable", "sentence": "error"}'

        return '{"error": "AI service unavailable", "sentence": "error"}'

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for Hungarian grammatical elements."""
        return self.hu_config.get_color_scheme(complexity)

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Generate Hungarian-specific AI prompt for grammar analysis."""
        return self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into standardized grammar analysis format."""
        return self.response_parser.parse_response(ai_response, complexity, sentence)

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate analysis quality and return confidence score."""
        result = self.validator.validate_result(parsed_data, original_sentence)
        return result.get('confidence', 0.0)

    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """
        Generate HTML output for Hungarian text with inline color styling for Anki.

        Hungarian uses spaces between words, so we color each word based on
        the word_explanations from AI analysis.
        """
        explanations = parsed_data.get('word_explanations', [])
        color_scheme = self.get_color_scheme(complexity)

        if not explanations:
            return sentence

        # Build HTML by iterating through word explanations in order
        html_parts = []
        covered = 0  # Track position in original sentence

        for exp in explanations:
            if len(exp) < 3:
                continue

            word = exp[0]
            role = exp[1]
            category = self._map_grammatical_role_to_category(role)
            color = color_scheme.get(category, color_scheme.get('other', '#AAAAAA'))

            # Find word in sentence starting from current position
            idx = sentence.find(word, covered)
            if idx == -1:
                idx = sentence.find(word)

            if idx != -1:
                # Add any uncovered characters before this word (spaces, etc.)
                if idx > covered:
                    uncovered = sentence[covered:idx]
                    html_parts.append(uncovered)

                # Add the colored word
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{word}</span>')
                covered = idx + len(word)
            else:
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{word}</span>')

        # Add any remaining characters
        if covered < len(sentence):
            remaining = sentence[covered:]
            html_parts.append(remaining)

        return ''.join(html_parts)

    def _map_grammatical_role_to_category(self, role: str) -> str:
        """Map specific grammatical roles to color categories."""
        hierarchy = self.hu_config.grammatical_roles.get('role_hierarchy', {})
        return hierarchy.get(role, role)

    def get_sentence_generation_prompt(self, word: str, language: str, num_sentences: int,
                                       enriched_meaning: str = "", min_length: int = 3,
                                       max_length: int = 15, difficulty: str = "intermediate",
                                       topics: Optional[List[str]] = None) -> Optional[str]:
        """
        Get Hungarian-specific sentence generation prompt to ensure proper response formatting.

        HUNGARIAN SENTENCE GENERATION:
        - Enforces character limits (75 chars for meanings, 60 for restrictions)
        - Includes Hungarian-specific grammar requirements
        - Handles vowel harmony, case suffixes, and definite/indefinite conjugation
        - Supports agglutinative morphology and verb prefix (igekötő) contexts
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

        # Hungarian-specific prompt with character limits and grammar requirements
        prompt = f"""You are a native-level expert linguist in Hungarian (Magyar).

Your task: Generate a complete learning package for the Hungarian word "{word}" in ONE response.

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
Examples: case suffix requirements, vowel harmony class (front/back), verb conjugation type, definite/indefinite usage
If no restrictions apply, state "No specific grammatical restrictions."
IMPORTANT: Keep the entire restrictions summary under 60 characters total.

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic sentences in Hungarian for the word "{word}".

QUALITY RULES:
- Every sentence must sound like native Hungarian
- Grammar, syntax, spelling, and Hungarian-specific features must be correct
- The target word "{word}" MUST be used correctly according to restrictions
- Each sentence must be between {min_length} and {max_length} words long
- COUNT words precisely; if outside the range, regenerate internally
- Difficulty: {difficulty}

HUNGARIAN-SPECIFIC REQUIREMENTS:
- Apply vowel harmony (front vs. back) consistently across suffixes — front: e, é, i, í, ö, ő, ü, ű; back: a, á, o, ó, u, ú
- Use the agglutinative case system — 18+ cases marked by suffixes (nominative-Ø, accusative -t, dative -nak/-nek, instrumental -val/-vel, illative -ba/-be, inessive -ban/-ben, elative -ból/-ből, sublative -ra/-re, superessive -n/-on/-en/-ön, delative -ról/-ről, allative -hoz/-hez/-höz, adessive -nál/-nél, ablative -tól/-től, terminative -ig, causal-final -ért, translative -vá/-vé, etc.)
- Distinguish definite vs. indefinite verb conjugation (látom = "I see it [definite]" vs. látok = "I see [indefinite]")
- Apply possessive suffixes correctly (házam = my house, házad = your house, háza = his/her house)
- Use the article a/az correctly (az before vowel-initial words, a before consonants)
- Hungarian has NO grammatical gender — pronouns ő = he/she
- Use appropriate verb prefixes (igekötők: meg-, el-, fel-, le-, be-, ki-, etc.) for aspect and direction
- Apply correct word order — Hungarian is topic-prominent; the focus position is immediately before the verb
- Diacritics: á, é, í, ó, ö, ő, ú, ü, ű (long ő and ű are unique to Hungarian)

VARIETY REQUIREMENTS:
- Use different verb tenses and moods when applicable
- Include different pronoun types (personal, possessive, demonstrative)
- Use various determiners (definite, indefinite)
- Include postpositional phrases with different postpositions
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
- Use standard IPA symbols for Hungarian pronunciation
- Reflect vowel length distinctions (short vs. long vowels) and consonant gemination
- Show stress (primary stress always on the first syllable in Hungarian)

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
1. [sentence 1 in Hungarian]
2. [sentence 2 in Hungarian]
3. [sentence 3 in Hungarian]
4. [sentence 4 in Hungarian]

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
- Sentences must be in Hungarian only
- Ensure exactly {num_sentences} sentences, translations, IPA transcriptions, and keywords
- Respect character limits for meaning and restrictions"""

        return prompt

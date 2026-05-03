# languages/latvian/lv_analyzer.py
"""
Latvian Grammar Analyzer — Facade

Implements BaseGrammarAnalyzer for the Latvian language.
Orchestrates domain components: config, prompt_builder, response_parser, validator, fallbacks.

Lazy imports inside _call_ai() follow the required pattern to support test mocking
and avoid cross-test contamination (see CLAUDE.md — Analyzer import patterns).

Class name: LvAnalyzer  (auto-discovered by analyzer_registry.py)
"""

import logging
import time
from typing import Any, Dict, List, Optional

from streamlit_app.language_analyzers.base_analyzer import (
    BaseGrammarAnalyzer,
    GrammarAnalysis,
    LanguageConfig,
)

from .domain.lv_config import LvConfig
from .domain.lv_prompt_builder import LvPromptBuilder
from .domain.lv_response_parser import LvResponseParser
from .domain.lv_fallbacks import LvFallbacks
from .domain.lv_validator import LvValidator

logger = logging.getLogger(__name__)


class LvAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Latvian (Latviešu valoda).

    Latvian — Indo-European, Baltic branch.
    Key features: 7 cases, 2 genders (masc/fem), definite/indefinite adjective forms,
    debitive mood (jā- + verb), reflexive verbs (-ties), 4 participle types, SVO order.

    Script: Latin with diacritics (LTR).
    Complexity levels: beginner, intermediate, advanced.
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "lv"
    LANGUAGE_NAME = "Latvian"

    def __init__(self):
        # Initialise domain components
        self.lv_config = LvConfig()
        self.lv_fallbacks = LvFallbacks(self.lv_config)
        self.prompt_builder = LvPromptBuilder(self.lv_config)
        self.response_parser = LvResponseParser(self.lv_config, self.lv_fallbacks)
        self.validator = LvValidator(self.lv_config)

        config = LanguageConfig(
            code="lv",
            name="Latvian",
            native_name="Latviešu",
            family="Indo-European",
            script_type="alphabetic",
            complexity_rating="high",
            key_features=[
                "case_system",
                "grammatical_gender",
                "definite_adjective",
                "debitive_mood",
                "reflexive_verbs",
                "participial_system",
                "free_word_order",
            ],
            supported_complexity_levels=["beginner", "intermediate", "advanced"],
        )
        super().__init__(config)

    # ------------------------------------------------------------------
    # BaseGrammarAnalyzer abstract methods
    # ------------------------------------------------------------------

    def get_grammar_prompt(
        self, complexity: str, sentence: str, target_word: str
    ) -> str:
        return self.prompt_builder.build_single_prompt(sentence, target_word, complexity)

    def parse_grammar_response(
        self, ai_response: str, complexity: str, sentence: str
    ) -> Dict[str, Any]:
        return self.response_parser.parse_response(
            ai_response, complexity, sentence
        )

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        return self.lv_config.get_color_scheme(complexity)

    def validate_analysis(
        self, parsed_data: Dict[str, Any], original_sentence: str
    ) -> float:
        result = self.validator.validate_result(parsed_data, original_sentence)
        return result.get("confidence", 0.0)

    # ------------------------------------------------------------------
    # Single sentence analysis
    # ------------------------------------------------------------------

    def analyze_grammar(
        self,
        sentence: str,
        target_word: str,
        complexity: str,
        gemini_api_key: str,
    ) -> GrammarAnalysis:
        """Analyse grammar for a single Latvian sentence."""
        try:
            start = time.time()
            prompt = self.prompt_builder.build_single_prompt(
                sentence, target_word, complexity
            )
            ai_response = self._call_ai(prompt, gemini_api_key)
            result = self.response_parser.parse_response(
                ai_response, complexity, sentence, target_word
            )
            validated = self.validator.validate_result(result, sentence)

            quality = self.validator.validate_explanation_quality(validated)
            base_conf = validated.get("confidence", 0.5)
            quality_score = quality.get("quality_score", 1.0)
            confidence = min(base_conf * quality_score, 1.0)
            validated["confidence"] = confidence

            html_output = self._generate_html_output(validated, sentence, complexity)
            elapsed = time.time() - start
            logger.info(
                f"Latvian analysis done in {elapsed:.2f}s, confidence={confidence:.2f}"
            )
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=validated.get("elements", {}),
                explanations=validated.get("explanations", {}),
                word_explanations=self._format_word_explanations(validated.get("word_explanations", [])),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=confidence,
            )
        except Exception as exc:
            logger.error(f"Latvian analysis failed: {exc}")
            fallback = self.lv_fallbacks.create_fallback(sentence, complexity)
            html_output = self._generate_html_output(fallback, sentence, complexity)
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=fallback.get("elements", {}),
                explanations=fallback.get("explanations", {}),
                word_explanations=self._format_word_explanations(fallback.get("word_explanations", [])),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=fallback.get("confidence", 0.3),
            )

    # ------------------------------------------------------------------
    # Batch analysis — matches Japanese ja_analyzer.py pattern exactly
    # ------------------------------------------------------------------

    def batch_analyze_grammar(
        self,
        sentences: List[str],
        target_word: str,
        complexity: str,
        gemini_api_key: str,
    ) -> List[GrammarAnalysis]:
        """Analyse grammar for multiple Latvian sentences in one AI call."""
        logger.info(f"Batch analyse: {len(sentences)} sentences, complexity={complexity}")
        try:
            prompt = self.prompt_builder.build_batch_prompt(
                sentences, target_word, complexity
            )
            ai_response = self._call_ai(prompt, gemini_api_key)
            results = self.response_parser.parse_batch_response(
                ai_response, sentences, complexity, target_word
            )

            grammar_analyses = []
            for result, sentence in zip(results, sentences):
                validated = self.validator.validate_result(result, sentence)
                html_output = self._generate_html_output(validated, sentence, complexity)
                grammar_analyses.append(
                    GrammarAnalysis(
                        sentence=sentence,
                        target_word=target_word or "",
                        language_code=self.language_code,
                        complexity_level=complexity,
                        grammatical_elements=validated.get("elements", {}),
                        explanations=validated.get("explanations", {}),
                        color_scheme=self.get_color_scheme(complexity),
                        html_output=html_output,
                        confidence_score=validated.get("confidence", 0.0),
                        word_explanations=self._format_word_explanations(validated.get("word_explanations", [])),
                    )
                )
            return grammar_analyses

        except Exception as exc:
            logger.error(f"Batch analysis failed: {exc}")
            fallback_analyses = []
            for sentence in sentences:
                fallback = self.lv_fallbacks.create_fallback(sentence, complexity)
                html_output = self._generate_html_output(fallback, sentence, complexity)
                fallback_analyses.append(
                    GrammarAnalysis(
                        sentence=sentence,
                        target_word=target_word or "",
                        language_code=self.language_code,
                        complexity_level=complexity,
                        grammatical_elements=fallback.get("elements", {}),
                        explanations=fallback.get("explanations", {}),
                        color_scheme=self.get_color_scheme(complexity),
                        html_output=html_output,
                        confidence_score=fallback.get("confidence", 0.3),
                        word_explanations=self._format_word_explanations(fallback.get("word_explanations", [])),
                    )
                )
            return fallback_analyses

    # ------------------------------------------------------------------
    # AI call — lazy import to support test mocking (per CLAUDE.md)
    # ------------------------------------------------------------------

    def _call_ai(self, prompt: str, gemini_api_key: str) -> str:
        """Call Gemini AI for Latvian grammar analysis. Lazy imports required."""
        from streamlit_app.shared_utils import (
            get_gemini_api,
            get_gemini_fallback_model,
            get_gemini_model,
        )

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
                        config={"max_output_tokens": 20000, "temperature": 0.1},
                    )
                    return response.text.strip()

                except Exception as primary_error:
                    logger.warning(
                        f"Primary model failed (attempt {attempt+1}): "
                        f"{str(primary_error)[:200]}"
                    )
                    try:
                        response = api.generate_content(
                            model=get_gemini_fallback_model(),
                            contents=prompt,
                            config={"max_output_tokens": 20000, "temperature": 0.1},
                        )
                        return response.text.strip()
                    except Exception as fallback_error:
                        logger.warning(
                            f"Fallback model also failed (attempt {attempt+1}): "
                            f"{str(fallback_error)[:200]}"
                        )
                        if attempt < max_retries - 1:
                            time.sleep(base_delay * (2 ** attempt))
                        else:
                            raise fallback_error

            except Exception as exc:
                logger.error(f"All models failed on attempt {attempt+1}: {str(exc)[:200]}")
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                else:
                    return '{"error": "AI service unavailable", "sentence": "error"}'

        return '{"error": "AI service unavailable", "sentence": "error"}'

    # ------------------------------------------------------------------
    # HTML output generation
    # ------------------------------------------------------------------

    def _format_word_explanations(self, raw: list) -> list:
        """Convert word_explanations to [word, role, color, meaning] list format."""
        result = []
        for item in raw:
            if isinstance(item, dict):
                result.append([
                    item.get("word", ""),
                    item.get("role", "other"),
                    item.get("color", "#CCCCCC"),
                    item.get("meaning", item.get("word", "")),
                ])
            elif isinstance(item, (list, tuple)) and len(item) >= 4:
                result.append(list(item))
        return result

    def _generate_html_output(
        self,
        parsed_data: Dict[str, Any],
        sentence: str,
        complexity: str,
    ) -> str:
        """Generate HTML with inline color styling for Anki display."""
        explanations = parsed_data.get("word_explanations", [])
        if not explanations:
            return f'<span style="color:#CCCCCC">{sentence}</span>'

        parts = []
        for item in explanations:
            if not isinstance(item, dict):
                continue
            word = item.get("word", "")
            color = item.get("color", "#CCCCCC")
            meaning = item.get("meaning", word)
            role = item.get("role", "other")
            tooltip = f"{role}: {meaning}"
            parts.append(
                f'<span style="color:{color}" title="{tooltip}">{word}</span>'
            )

        return " ".join(parts)

    def _map_grammatical_role_to_category(self, role: str) -> str:
        """Map a Latvian role label to a broad category (for legacy callers)."""
        mapping = {
            "noun": "noun",
            "verb": "verb",
            "adjective": "adjective",
            "adjective_definite": "adjective",
            "adjective_indefinite": "adjective",
            "pronoun": "pronoun",
            "personal_pronoun": "pronoun",
            "reflexive_pronoun": "pronoun",
            "demonstrative": "pronoun",
            "relative_pronoun": "pronoun",
            "indefinite_pronoun": "pronoun",
            "preposition": "preposition",
            "conjunction": "conjunction",
            "subordinating_conjunction": "conjunction",
            "adverb": "adverb",
            "auxiliary": "auxiliary",
            "reflexive_verb": "verb",
            "participle": "participle",
            "debitive": "debitive",
            "numeral": "numeral",
            "particle": "particle",
            "interjection": "interjection",
            "verbal_noun": "noun",
            "other": "other",
        }
        return mapping.get(role, "other")

    # ------------------------------------------------------------------
    # Sentence generation prompt
    # ------------------------------------------------------------------

    def get_sentence_generation_prompt(self, word: str, language: str, num_sentences: int,
                                     enriched_meaning: str = "", min_length: int = 3,
                                     max_length: int = 15, difficulty: str = "intermediate",
                                     topics: Optional[List[str]] = None) -> Optional[str]:
        """
        Get Latvian-specific sentence generation prompt to ensure proper response formatting.

        LATVIAN SENTENCE GENERATION:
        - Enforces character limits (75 chars for meanings, 60 for restrictions)
        - Includes Latvian-specific grammar requirements
        - Handles case marking and verb conjugations
        - Supports reflexive verbs and debitive mood contexts
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

        # Latvian-specific prompt with character limits and grammar requirements
        prompt = f"""You are a native-level expert linguist in Latvian (Latviešu valoda).

Your task: Generate a complete learning package for the Latvian word "{word}" in ONE response.

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
Generate exactly {num_sentences} highly natural, idiomatic sentences in Latvian for the word "{word}".

QUALITY RULES:
- Every sentence must sound like native Latvian
- Grammar, syntax, spelling, and Latvian-specific features must be correct
- The target word "{word}" MUST be used correctly according to restrictions
- Each sentence must be between {min_length} and {max_length} words long
- COUNT words precisely; if outside the range, regenerate internally
- Difficulty: {difficulty}

LATVIAN-SPECIFIC REQUIREMENTS:
- Apply correct case marking — Latvian has 7 cases: nominative, genitive, dative, accusative, instrumental, locative, vocative
- Use proper gender agreement (masculine ends in -s/-š/-is, feminine ends in -a/-e/-s)
- Distinguish definite vs. indefinite adjective forms (-ais/-ā for definite vs. -s/-a for indefinite)
- Apply correct verb conjugation by person (1st/2nd/3rd) and number (singular/plural)
- Use appropriate moods: indicative, conditional (-tu ending), debitive (jā- prefix for "must"), imperative
- Include reflexive verbs where natural (-ies/-ās ending: mācīties, runāt vs. runāties)
- Use prepositions with their required cases (ar + instrumental, no + genitive, uz + accusative/locative)
- Apply proper diacritics: ā, ē, ī, ū (long vowels); č, š, ž (palatals); ķ, ļ, ņ, ģ (palatalized)

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
1. [sentence 1 in Latvian]
2. [sentence 2 in Latvian]
3. [sentence 3 in Latvian]
4. [sentence 4 in Latvian]

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
- Sentences must be in Latvian only
- Ensure exactly {num_sentences} sentences, translations, IPA transcriptions, and keywords
- Respect character limits for meaning and restrictions"""

        return prompt

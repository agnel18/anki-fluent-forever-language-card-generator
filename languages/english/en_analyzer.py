# languages/english/en_analyzer.py
"""
English Grammar Analyzer — Facade

Implements BaseGrammarAnalyzer for the English language.
Orchestrates domain components: config, prompt_builder, response_parser, validator, fallbacks.

Lazy imports inside _call_ai() follow the required pattern to support test mocking
and avoid cross-test contamination (see CLAUDE.md — Analyzer import patterns).

Class name: EnAnalyzer  (auto-discovered by analyzer_registry.py)
"""

import logging
import time
from typing import Any, Dict, List, Optional

from streamlit_app.language_analyzers.base_analyzer import (
    BaseGrammarAnalyzer,
    GrammarAnalysis,
    LanguageConfig,
)

from .domain.en_config import EnConfig
from .domain.en_prompt_builder import EnPromptBuilder
from .domain.en_response_parser import EnResponseParser
from .domain.en_fallbacks import EnFallbacks
from .domain.en_validator import EnValidator

logger = logging.getLogger(__name__)


class EnAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for English.

    English — West Germanic, Indo-European family.
    Key features: analytic morphology, strict SVO word order, auxiliary verb system,
    minimal inflection, phrasal verbs, categorical ambiguity (to / -ing / -ed / that).

    Script: Latin (LTR).
    Complexity levels: beginner, intermediate, advanced.
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "en"
    LANGUAGE_NAME = "English"

    def __init__(self):
        # Initialise domain components
        self.en_config = EnConfig()
        self.en_fallbacks = EnFallbacks(self.en_config)
        self.prompt_builder = EnPromptBuilder(self.en_config)
        self.response_parser = EnResponseParser(self.en_config, self.en_fallbacks)
        self.validator = EnValidator(self.en_config)

        config = LanguageConfig(
            code="en",
            name="English",
            native_name="English",
            family="Indo-European",
            script_type="alphabetic",
            complexity_rating="medium",
            key_features=[
                "analytic_morphology",
                "auxiliary_stack",
                "strict_svo",
                "minimal_inflection",
                "phrasal_verbs",
                "do_support",
                "categorical_ambiguity",
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
        return self.response_parser.parse_response(ai_response, complexity, sentence)

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        return self.en_config.get_color_scheme(complexity)

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
        """Analyse grammar for a single English sentence."""
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

            # Quality multiplier — only applies to non-fallback paths since
            # validator already capped fallback at 0.3.
            if not validated.get("is_fallback", False):
                quality = self.validator.validate_explanation_quality(validated)
                base_conf = validated.get("confidence", 0.5)
                quality_score = quality.get("quality_score", 1.0)
                confidence = min(base_conf * quality_score, 1.0)
                validated["confidence"] = confidence
            else:
                confidence = validated.get("confidence", 0.3)

            html_output = self._generate_html_output(validated, sentence, complexity)
            elapsed = time.time() - start
            logger.info(
                f"English analysis done in {elapsed:.2f}s, confidence={confidence:.2f}"
            )
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=validated.get("elements", {}),
                explanations=validated.get("explanations", {}),
                word_explanations=self._format_word_explanations(
                    validated.get("word_explanations", [])
                ),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=confidence,
            )
        except Exception as exc:
            logger.error(f"English analysis failed: {exc}")
            fallback = self.en_fallbacks.create_fallback(sentence, complexity)
            html_output = self._generate_html_output(fallback, sentence, complexity)
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=fallback.get("elements", {}),
                explanations=fallback.get("explanations", {}),
                word_explanations=self._format_word_explanations(
                    fallback.get("word_explanations", [])
                ),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=fallback.get("confidence", 0.3),
            )

    # ------------------------------------------------------------------
    # Batch analysis — matches Japanese ja_analyzer.py / Latvian pattern
    # ------------------------------------------------------------------

    def batch_analyze_grammar(
        self,
        sentences: List[str],
        target_word: str,
        complexity: str,
        gemini_api_key: str,
    ) -> List[GrammarAnalysis]:
        """Analyse grammar for multiple English sentences in one AI call."""
        logger.info(
            f"Batch analyse: {len(sentences)} sentences, complexity={complexity}"
        )
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
                        word_explanations=self._format_word_explanations(
                            validated.get("word_explanations", [])
                        ),
                    )
                )
            return grammar_analyses

        except Exception as exc:
            logger.error(f"Batch analysis failed: {exc}")
            fallback_analyses = []
            for sentence in sentences:
                fallback = self.en_fallbacks.create_fallback(sentence, complexity)
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
                        word_explanations=self._format_word_explanations(
                            fallback.get("word_explanations", [])
                        ),
                    )
                )
            return fallback_analyses

    # ------------------------------------------------------------------
    # AI call — lazy import to support test mocking (per CLAUDE.md)
    # ------------------------------------------------------------------

    def _call_ai(self, prompt: str, gemini_api_key: str) -> str:
        """Call Gemini AI for English grammar analysis. Lazy imports required."""
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
                    return self._extract_response_text(response)

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
                        return self._extract_response_text(response)
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

    @staticmethod
    def _extract_response_text(response) -> str:
        """Pull .text from a Gemini response, raising if it's missing.

        Gemini can return a 200 OK with `response.text = None` when the
        completion is blocked by a safety filter or hits the max-tokens cap.
        Letting `.strip()` raise AttributeError surfaces that as a confusing
        crash; raising a clean RuntimeError instead lets the retry/fallback
        layer above this method swap models.
        """
        text = getattr(response, "text", None)
        if not text or not str(text).strip():
            raise RuntimeError(
                "Gemini returned empty .text (likely safety filter or max-tokens hit)"
            )
        return str(text).strip()

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
        """Map an English role label to a broad category (for legacy callers)."""
        mapping = {
            "noun": "noun",
            "verb": "verb",
            "adjective": "adjective",
            "adverb": "adverb",
            "pronoun": "pronoun",
            "personal_pronoun": "pronoun",
            "reflexive_pronoun": "pronoun",
            "demonstrative": "pronoun",
            "relative_pronoun": "pronoun",
            "indefinite_pronoun": "pronoun",
            "interrogative_pronoun": "pronoun",
            "possessive_pronoun": "pronoun",
            "possessive_determiner": "determiner",
            "preposition": "preposition",
            "conjunction": "conjunction",
            "subordinating_conjunction": "conjunction",
            "coordinating_conjunction": "conjunction",
            "auxiliary": "auxiliary",
            "modal_verb": "auxiliary",
            "article": "article",
            "determiner": "determiner",
            "particle": "particle",
            "phrasal_verb_particle": "particle",
            "phrasal_verb": "verb",
            "infinitive_marker": "particle",
            "infinitive": "verb",
            "gerund": "noun",
            "present_participle": "verb",
            "past_participle": "verb",
            "comparative": "adjective",
            "superlative": "adjective",
            "numeral": "numeral",
            "interjection": "interjection",
            "other": "other",
        }
        return mapping.get(role, "other")

    # ------------------------------------------------------------------
    # Sentence generation prompt
    # ------------------------------------------------------------------

    def get_sentence_generation_prompt(
        self,
        word: str,
        language: str,
        num_sentences: int,
        enriched_meaning: str = "",
        min_length: int = 3,
        max_length: int = 15,
        difficulty: str = "intermediate",
        topics: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Get English-specific sentence generation prompt."""
        # Build context instruction based on topics
        if topics:
            context_instruction = (
                f"- CRITICAL REQUIREMENT: ALL sentences MUST relate to these specific topics: "
                f"{', '.join(topics)}. Force the word usage into these contexts even if it requires "
                f"creative interpretation. Do NOT use generic contexts."
            )
        else:
            context_instruction = (
                "- Use diverse real-life contexts: home, travel, food, emotions, work, "
                "social life, daily actions, cultural experiences"
            )

        # Build meaning instruction based on enriched data
        if enriched_meaning and enriched_meaning != "N/A":
            if enriched_meaning.startswith("{") and enriched_meaning.endswith("}"):
                context_lines = enriched_meaning[1:-1].split("\n")
                definitions = []
                for line in context_lines:
                    line = line.strip()
                    if line.startswith("Definition"):
                        def_text = line.split(":", 1)[1].strip() if ":" in line else line
                        def_text = def_text.split(" | ")[0].strip()
                        definitions.append(def_text)
                if definitions:
                    meaning_summary = "; ".join(definitions[:4])
                    enriched_meaning_instruction = (
                        f'Analyze this linguistic data for "{word}" and generate a brief, clean '
                        f"English meaning that encompasses ALL the meanings. Data: {meaning_summary}. "
                        f"IMPORTANT: Consider all meanings and provide a comprehensive meaning."
                    )
                else:
                    enriched_meaning_instruction = (
                        f'Analyze this linguistic context for "{word}" and generate a brief, '
                        f"clean English meaning. Context: {enriched_meaning[:200]}. "
                        f"IMPORTANT: Return ONLY the English meaning."
                    )
            else:
                enriched_meaning_instruction = (
                    f'Use this pre-reviewed meaning for "{word}": "{enriched_meaning}". '
                    f"Generate a clean English meaning based on this."
                )
        else:
            enriched_meaning_instruction = f'Provide a brief English meaning for "{word}".'

        prompt = f"""You are a native-level expert linguist in English.

Your task: Generate a complete learning package for the English word "{word}" in ONE response.

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
Examples: count vs. mass noun, transitive vs. intransitive verb, irregular plural / past, modal-verb defective paradigm, gerund vs. infinitive complement.
If no restrictions apply, state "No specific grammatical restrictions."
IMPORTANT: Keep the entire restrictions summary under 60 characters total.

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic sentences in English for the word "{word}".

QUALITY RULES:
- Every sentence must sound like native English
- Grammar, syntax, spelling, and punctuation must be correct
- The target word "{word}" MUST be used correctly according to restrictions
- Each sentence must be between {min_length} and {max_length} words long
- COUNT words precisely; if outside the range, regenerate internally
- Difficulty: {difficulty}

ENGLISH-SPECIFIC REQUIREMENTS:
- Apply correct verb agreement (3sg -s on present-tense lexical verbs)
- Use proper article choice (a/an/the/Ø) — be sensitive to count vs. mass nouns
- Use auxiliary verbs correctly (be for progressive/passive, have for perfect, do for negation/inversion in lexical-verb clauses)
- Use modal verbs with bare-infinitive complement (no "to": can swim, NOT can to swim — except `ought to`)
- Apply correct pronoun case (I/me, he/him, who/whom)
- Use phrasal verbs idiomatically when natural

VARIETY REQUIREMENTS:
- Use different tenses and aspects (simple / progressive / perfect)
- Use different sentence types: declarative, interrogative, imperative
- Include both active and passive voice when appropriate
- Vary sentence subjects (don't always start with "I" or "the")
{context_instruction}

===========================
STEP 3: NATIVE-LANGUAGE TRANSLATIONS
===========================
For EACH sentence above, provide a natural, fluent translation into the user's native language.
- Translation should be natural, not literal word-for-word

===========================
STEP 4: IPA TRANSCRIPTION
===========================
For EACH sentence above, provide IPA phonetic transcription.
- Use standard IPA symbols for English pronunciation (General American or RP)
- Show stress markers
- Reduce unstressed vowels to schwa where appropriate

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
1. [sentence 1 in English]
2. [sentence 2 in English]
3. [sentence 3 in English]
4. [sentence 4 in English]

TRANSLATIONS:
1. [natural translation for sentence 1]
2. [natural translation for sentence 2]
3. [natural translation for sentence 3]
4. [natural translation for sentence 4]

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
- Sentences must be in English only
- Ensure exactly {num_sentences} sentences, translations, IPA transcriptions, and keywords
- Respect character limits for meaning and restrictions"""

        return prompt

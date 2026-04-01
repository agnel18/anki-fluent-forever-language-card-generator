"""
Content Generator Service

Handles AI-powered content generation using Google Gemini API.
Extracted from sentence_generator.py for better separation of concerns.
"""

import json
import logging
import re
import time
import warnings
from typing import Optional, List, Dict, Any, Tuple, Union

# Suppress FutureWarnings from dependencies
warnings.filterwarnings("ignore", category=FutureWarning)

# Import centralized configuration
from streamlit_app.shared_utils import get_gemini_model, get_gemini_fallback_model, cached_api_call, retry_with_exponential_backoff, with_fallback, get_gemini_api

from streamlit_app.shared_utils import LANGUAGE_NAME_TO_CODE, CONTENT_LANGUAGE_MAP
from streamlit_app.language_analyzers.analyzer_registry import get_analyzer
from streamlit_app.generation_utils import validate_ipa_output

logger = logging.getLogger(__name__)


class ContentGenerator:
    """
    Service for generating educational content using Google Gemini AI.
    """

    def __init__(self):
        self.client = None

    def _get_client(self, api_key: str):
        """Configure Google GenAI client wrapper."""
        api = get_gemini_api()
        api.configure(api_key=api_key)
        return api

    def generate_word_meaning_sentences_and_keywords(
        self,
        word: str,
        language: str,
        num_sentences: int,
        gemini_api_key: str,
        enriched_meaning: str = "",
        min_length: int = 3,
        max_length: int = 15,
        difficulty: str = "intermediate",
        topics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate word meaning, sentences, IPA, and keywords in one optimized API call.

        Args:
            word: Target word to generate content for
            language: Language name (e.g., "Hindi", "Spanish")
            num_sentences: Number of sentences to generate
            gemini_api_key: Google Gemini API key for AI calls
            enriched_meaning: Pre-enriched meaning data (optional)
            min_length: Minimum sentence length in words
            max_length: Maximum sentence length in words
            difficulty: Difficulty level (beginner/intermediate/advanced)
            topics: Specific topics to focus on (optional)

        Returns:
            Dict containing:
            - meaning: English meaning string
            - restrictions: Grammatical restrictions string
            - sentences: List of generated sentences
            - ipa: List of IPA transcriptions
            - keywords: List of keyword strings (one per sentence)
        """
        if not gemini_api_key:
            raise ValueError("Google Gemini API key required")

        # Validate API key format
        if not gemini_api_key.startswith('AIza'):
            logger.error(f"Invalid API key format: does not start with 'AIza'")
            raise ValueError("Invalid Google Gemini API key format")
        
        if len(gemini_api_key) < 20:
            logger.error(f"API key too short: {len(gemini_api_key)} characters")
            raise ValueError("Google Gemini API key too short")

        logger.info(f"Content generation called with word='{word}', language='{language}', num_sentences={num_sentences}")

        # Sanitize user input to prevent prompt injection
        import json as _json
        safe_word = word.strip()[:100]  # Limit length
        safe_word = ''.join(c for c in safe_word if c.isprintable())  # Remove control chars

        # Map language name for AI compatibility
        ai_language = CONTENT_LANGUAGE_MAP.get(language, language)
        if ai_language != language:
            logger.info(f"Mapped language '{language}' to '{ai_language}' for AI compatibility")

        try:
            client = self._get_client(gemini_api_key)
            logger.info("Google Gemini client configured successfully")
            
            # Skip connectivity test in online environments as it may not work
            # and could cause delays

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
                        enriched_meaning_instruction = f'Analyze this linguistic data for "{safe_word}" and generate a brief, clean English meaning that encompasses ALL the meanings. Data: {meaning_summary}. IMPORTANT: Consider all meanings (letter, deity, etc.) and provide a comprehensive meaning like "letter (seventh letter of Hindi alphabet); deity (Vishnu)" - do NOT focus on just one meaning.'
                    else:
                        enriched_meaning_instruction = f'Analyze this linguistic context for "{safe_word}" and generate a brief, clean English meaning. Context: {enriched_meaning[:200]}. IMPORTANT: Return ONLY the English meaning in format like "house (a building where people live)" - do NOT include any raw linguistic data in your response.'
                else:
                    # Legacy format
                    enriched_meaning_instruction = f'Use this pre-reviewed meaning for "{safe_word}": "{enriched_meaning}". Generate a clean English meaning based on this. IMPORTANT: Return ONLY the English meaning in format like "house (a building where people live)" - do NOT include the original text in your response.'
            else:
                enriched_meaning_instruction = f'Provide a brief English meaning for "{safe_word}".'

            # Check if language is Chinese for Pinyin instead of IPA
            is_chinese = language in ["Chinese Simplified", "Chinese Traditional", "Chinese (Simplified)", "Chinese (Traditional)"]
            pronunciation_label = "PINYIN" if is_chinese else "IPA"
            pronunciation_instruction = "MANDATORY Pinyin romanization (with tone marks) for EVERY word in the sentence - including particles, function words, grammatical markers, and single characters. DO NOT skip any words." if is_chinese else "official IPA symbols only (not pinyin, not romanization, not any non-IPA symbols)"

            # Check for language-specific sentence generation prompt
            language_code = LANGUAGE_NAME_TO_CODE.get(language, language.lower()[:2])
            analyzer = get_analyzer(language_code)
            custom_prompt = None
            if analyzer:
                try:
                    custom_prompt = analyzer.get_sentence_generation_prompt(
                        word=word,
                        language=language,
                        num_sentences=num_sentences,
                        enriched_meaning=enriched_meaning,
                        min_length=min_length,
                        max_length=max_length,
                        difficulty=difficulty,
                        topics=topics
                    )
                    if custom_prompt:
                        logger.info(f"Using language-specific sentence generation prompt for {language}")
                        prompt = custom_prompt
                    else:
                        logger.info(f"No custom prompt available for {language}, using generic prompt")
                except Exception as e:
                    logger.warning(f"Failed to get custom prompt for {language}: {e}, falling back to generic")
            else:
                logger.info(f"No analyzer available for {language} ({language_code}), using generic prompt")

            # Build generic prompt if no custom prompt was found
            if not custom_prompt:
                prompt = f"""You are a native-level expert linguist in {ai_language} with professional experience teaching it to non-native learners.

Your task: Generate a complete learning package for the {ai_language} word "{safe_word}" in ONE response.

===========================
STEP 1: WORD MEANING
===========================
{enriched_meaning_instruction}
Format: Return exactly one line like "house (a building where people live)" or "he (male pronoun, used as subject)"
IMPORTANT: Keep the entire meaning under 75 characters total.

===========================
WORD-SPECIFIC RESTRICTIONS
===========================
Based on the meaning above, identify any grammatical constraints, mood, person, or context restrictions for "{safe_word}".
Examples:
- Imperatives (commands): ONLY use in direct commands, never in statements
- Restricted moods: ONLY use in specific grammatical contexts (e.g., subjunctive for doubts)
- Person/number restrictions: ONLY use in certain persons (e.g., formal pronouns)
- Contextual restrictions: ONLY use in specific situations (e.g., directional verbs)

If no restrictions apply, state "No specific grammatical restrictions."
IMPORTANT: Keep the entire restrictions summary under 60 characters total.

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic, culturally appropriate sentences in {ai_language} for the word "{safe_word}".

QUALITY RULES (STRICT):
- Every sentence must sound like it was written by an educated native speaker
- Absolutely no unnatural, robotic, or literal-translation phrasing
- Grammar, syntax, spelling, diacritics, gender agreement, case, politeness level, and punctuation must all be correct
- The target word "{safe_word}" MUST be used correctly in context according to its grammatical restrictions
- Ensure EVERY sentence matches the EXACT meaning and follows the WORD-SPECIFIC RESTRICTIONS above
- If the word cannot be used naturally within restrictions, use related forms and note it (e.g., base form instead of imperative)
- E.g., for imperatives: ONLY in commands like "Come here!"; for restricted moods: DO NOT force – use alternatives like base form
- Avoid rare or archaic vocabulary (unless difficulty="advanced")
- All sentences must be semantically meaningful (no filler templates)
- No repeated sentence structures or patterns — each sentence must be unique
- Each sentence must be between {min_length} and {max_length} words long. COUNT words precisely; if outside the range, it's INVALID – regenerate internally
- Difficulty: {difficulty}
  - beginner: Use only simple vocabulary and grammar, mostly present tense
  - intermediate: Use mixed tenses, richer but still natural language
  - advanced: Use complex structures, nuanced vocabulary, and advanced grammar

VARIETY REQUIREMENTS:
- Use different tenses (if applicable to {ai_language})
- Use different sentence types: declarative, interrogative, imperative
- Use the target word in different grammatical roles if possible
{context_instruction}

===========================
STEP 3: ENGLISH TRANSLATIONS
===========================
For EACH sentence above, provide a natural, fluent English translation.
- Translation should be natural English, not literal word-for-word
- Maintain the same meaning and nuance as the original sentence
- Use appropriate English grammar and idioms

===========================
STEP 4: IMAGE KEYWORDS
===========================
For EACH sentence above, generate exactly 3 diverse and specific keywords for image search.
- Keywords MUST be SPECIFIC/concrete (e.g., 'red apple on wooden table' not 'fruit'); avoid generics like 'language' or 'learning'
- Focus on concrete objects, actions, or scenes that represent the sentence
- Keywords should be in English only

===========================
OUTPUT FORMAT
===========================
Return your response in this exact text format:

MEANING: [brief English meaning]

RESTRICTIONS: [grammatical restrictions identified]

SENTENCES:
1. [sentence 1 in {language}]
2. [sentence 2 in {language}]
3. [sentence 3 in {language}]

TRANSLATIONS:
1. [natural English translation for sentence 1]
2. [natural English translation for sentence 2]
3. [natural English translation for sentence 3]

{pronunciation_label}:
1. [{pronunciation_instruction} for sentence 1 - REQUIRED: provide Pinyin even for particles and function words like '的', '了', '嗎']
2. [{pronunciation_instruction} for sentence 2 - REQUIRED: provide Pinyin even for particles and function words like '的', '了', '嗎']
3. [{pronunciation_instruction} for sentence 3 - REQUIRED: provide Pinyin even for particles and function words like '的', '了', '嗎']

KEYWORDS:
1. [keyword1, keyword2, keyword3]
2. [keyword1, keyword2, keyword3]
3. [keyword1, keyword2, keyword3]

IMPORTANT:
- Return ONLY the formatted text, no extra explanation
- Sentences must be in {language} only
- Translations must be natural, fluent English
- {pronunciation_label} must use {pronunciation_instruction}
- Keywords must be comma-separated
- Ensure exactly {num_sentences} sentences, translations, and keywords"""

            # Try Gemini models with fallback - using recommended models for Anki generation accuracy
            # Best for Anki generation accuracy
            models_to_try = [get_gemini_model(), get_gemini_fallback_model()]
            
            response = None
            last_error = None
            
            for model_name in models_to_try:
                try:
                    logger.info(f"Attempting API call with model: {model_name}")
                    response = client.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=client.genai.types.GenerateContentConfig(
                            temperature=0.7,  # Creativity for sentence variety
                            max_output_tokens=20000,  # Increased for Arabic and complex responses
                        )
                    )
                    logger.info(f"API call successful with model: {model_name}")
                    break
                except Exception as model_e:
                    logger.warning(f"Model {model_name} failed: {str(model_e)}")
                    last_error = model_e
                    continue
            
            if response is None:
                raise last_error or Exception("All models failed")

            logger.info("API call completed successfully")
            response_text = response.text.strip()
            logger.info(f"Content generation raw response length: {len(response_text)}")
            logger.debug(f"Content generation raw response: {response_text[:500]}...")

            # Parse the response
            result = self._parse_generation_response(response_text, word, language, num_sentences, min_length, max_length)
            
            # Debug: log parsing results
            parsed_sentences = len(result.get('sentences', []))
            if parsed_sentences == 0:
                logger.warning(f"Failed to parse sentences from response. Raw response: {response_text}")

            # Attempt AI repair when validation failures are present
            critical_failures = [w for w in result.get('validation_warnings', []) if not w.get('is_valid', True)]
            if critical_failures:
                logger.info(f"Attempting AI repair for {len(critical_failures)} validation failure(s)")
                repaired_result = self._repair_with_ai(
                    client=client,
                    models_to_try=models_to_try,
                    original_prompt=prompt,
                    failed_response=response_text,
                    critical_failures=critical_failures,
                    word=word,
                    language=language,
                    num_sentences=num_sentences,
                    min_length=min_length,
                    max_length=max_length,
                    pronunciation_label=pronunciation_label,
                    restrictions=result.get('restrictions', 'No specific grammatical restrictions.'),
                    difficulty=difficulty,
                )
                if repaired_result is not None:
                    return repaired_result

            return result

        except Exception as e:
            logger.error(f"Content generation failed for word '{word}': {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Try to provide more specific error information
            error_msg = str(e).lower()
            if "timeout" in error_msg:
                logger.error("API call timed out - possible network issue in online environment")
            elif "connection" in error_msg:
                logger.error("Connection error - possible network/firewall issue")
            elif "rate limit" in error_msg or "429" in error_msg:
                logger.error(
                    "Quota/rate limit exceeded (HTTP 429). "
                    "Rate limit or daily free-tier limit reached. "
                    "Set a per-minute rate limit in Google Cloud Console "
                    "(APIs & Services → Generative Language API → Quotas & System Limits "
                    "→ 'GenerateContent requests per minute') to prevent unexpected charges."
                )
            elif "unauthorized" in error_msg or "401" in error_msg:
                logger.error("API key invalid or unauthorized")
            elif "forbidden" in error_msg or "403" in error_msg:
                logger.error("API access forbidden")
            else:
                logger.error(f"Unknown API error: {str(e)}")
            
            # Return fallback structure with error indication
            return self._create_fallback_response(word, num_sentences)

    def _parse_generation_response(self, response_text: str, word: str, language: str, num_sentences: int, min_length: int, max_length: int) -> Dict[str, Any]:
        """Parse the AI response into structured data."""
        meaning = ""
        restrictions = ""
        sentences = []
        ipa_list = []
        keywords = []

        is_chinese = language in ["Chinese Simplified", "Chinese Traditional", "Chinese (Simplified)", "Chinese (Traditional)"]
        pronunciation_section = "PINYIN:" if is_chinese else "IPA:"
        if not is_chinese and "ROMANIZATION:" in response_text:
            pronunciation_section = "ROMANIZATION:"

        # Extract meaning
        if "MEANING:" in response_text:
            meaning_part = response_text.split("MEANING:")[1].split("RESTRICTIONS:")[0].strip()
            meaning = meaning_part.strip()

        # Extract restrictions
        if "RESTRICTIONS:" in response_text:
            restrictions_part = response_text.split("RESTRICTIONS:")[1].split("SENTENCES:")[0].strip()
            restrictions = restrictions_part.strip()

        # Extract sentences
        if "SENTENCES:" in response_text and "TRANSLATIONS:" in response_text:
            sentences_part = response_text.split("SENTENCES:")[1].split("TRANSLATIONS:")[0].strip()
            for line in sentences_part.split("\n"):
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, num_sentences + 1)):
                    sentence = line.split(".", 1)[1].strip() if "." in line else line
                    if sentence:
                        sentences.append(sentence)
        elif "SENTENCES:" in response_text:
            # Handle case where response is truncated and missing TRANSLATIONS section
            sentences_part = response_text.split("SENTENCES:")[1].strip()
            for line in sentences_part.split("\n"):
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, num_sentences + 1)):
                    sentence = line.split(".", 1)[1].strip() if "." in line else line
                    if sentence:
                        sentences.append(sentence)

        # Extract translations
        translations = []
        if "TRANSLATIONS:" in response_text and pronunciation_section in response_text:
            translations_part = response_text.split("TRANSLATIONS:")[1].split(pronunciation_section)[0].strip()
            for line in translations_part.split("\n"):
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, num_sentences + 1)):
                    translation = line.split(".", 1)[1].strip() if "." in line else line
                    if translation:
                        translations.append(translation)

        # Extract IPA/Pinyin
        if pronunciation_section in response_text and "KEYWORDS:" in response_text:
            ipa_part = response_text.split(pronunciation_section)[1].split("KEYWORDS:")[0].strip()
            for line in ipa_part.split("\n"):
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, num_sentences + 1)):
                    ipa = line.split(".", 1)[1].strip() if "." in line else line
                    if ipa:
                        # Validate IPA/Pinyin output
                        # Normalize language name for lookup (convert to lowercase, replace spaces with underscores)
                        normalized_language = language.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('（', '').replace('）', '')
                        language_code = LANGUAGE_NAME_TO_CODE.get(normalized_language, "en")
                        is_valid, validated_ipa = validate_ipa_output(ipa, language_code)
                        if is_valid:
                            ipa_list.append(validated_ipa)
                            logger.debug(f"Valid {'Pinyin' if is_chinese else 'IPA'}: {validated_ipa}")
                        else:
                            # Use AI-generated content even if validation fails - better than blank
                            logger.warning(f"Invalid {'Pinyin' if is_chinese else 'IPA'} rejected: {validated_ipa}, using AI-generated content anyway")
                            ipa_list.append(ipa)  # Use the original AI-generated content

        # Extract keywords
        if "KEYWORDS:" in response_text:
            keywords_part = response_text.split("KEYWORDS:")[1].strip()
            for line in keywords_part.split("\n"):
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, num_sentences + 1)):
                    kw = line.split(".", 1)[1].strip() if "." in line else line
                    if kw:
                        keywords.append(kw)

        logger.info(f"Parsed: meaning='{meaning}', restrictions='{restrictions}', sentences={len(sentences)}, translations={len(translations)}, {'pinyin' if is_chinese else 'ipa'}={len(ipa_list)}, keywords={len(keywords)}")

        # Debug: log parsing results
        if len(sentences) == 0:
            logger.warning(f"Failed to parse sentences from response. Raw response: {response_text}")

        # Validate and create fallbacks
        validated_sentences, validated_translations, validated_ipa, validated_keywords, validation_warnings = self._validate_and_create_fallbacks(
            sentences, translations, ipa_list, keywords, word, restrictions, num_sentences, min_length, max_length
        )

        return {
            'meaning': meaning,
            'restrictions': restrictions,
            'sentences': validated_sentences,
            'translations': validated_translations,
            'ipa': validated_ipa,
            'keywords': validated_keywords,
            'validation_warnings': validation_warnings
        }

    def _validate_and_create_fallbacks(self, sentences: List[str], translations: List[str], ipa_list: List[str], keywords: List[str],
                                      word: str, restrictions: str, num_sentences: int, min_length: int, max_length: int) -> Tuple[List[str], List[str], List[str], List[str], List[Dict[str, Any]]]:
        """Validate content and create validation warnings instead of fallbacks."""

        # Create fallback templates based on restrictions
        if "imperative" in restrictions.lower() or "command" in restrictions.lower():
            fallback_templates = [
                f"{word} here and sit down!",
                f"{word} and eat your food!",
                f"{word} and listen to me!",
                f"{word} and introduce yourself!",
                f"{word} quickly!",
                f"Please {word} now!",
                f"{word} immediately!",
                f"You should {word} right away!",
                f"Don't wait, {word}!",
                f"{word} without delay!"
            ]
            fallback_keywords = [
                f"{word}, person walking, chair",
                f"{word}, food plate, dining",
                f"{word}, listening, advice",
                f"{word}, introduction, handshake",
                f"{word}, hurry, speed",
                f"{word}, request, now",
                f"{word}, urgent, immediate",
                f"{word}, should, right away",
                f"{word}, wait, delay",
                f"{word}, time, delay"
            ]
        else:
            fallback_templates = [
                f"This is a sample sentence with {word}.",
                f"Here is an example using {word}.",
                f"Look at this sentence containing {word}.",
                f"Consider this phrase with {word}.",
                f"Observe how {word} is used here.",
                f"Note this example featuring {word}.",
                f"See this sentence including {word}.",
                f"Examine this phrase with {word}.",
                f"Study this example using {word}.",
                f"Review this sentence with {word}."
            ]
            fallback_keywords = [
                f"{word}, example, usage",
                f"{word}, illustration, scene",
                f"{word}, instance, application",
                f"{word}, scenario, situation",
                f"{word}, model, sentence",
                f"{word}, pattern, structure",
                f"{word}, template, form",
                f"{word}, reference, guide",
                f"{word}, practice, exercise",
                f"{word}, tutorial, lesson"
            ]

        validated_sentences = []
        validated_translations = []
        validated_ipa = []
        validated_keywords = []
        validation_warnings = []

        generic_terms = ['language', 'learning', 'word', 'text', 'communication', 'study']

        def strip_arabic_diacritics(text: str) -> str:
            return re.sub(r"[\u064B-\u065F\u0670\u06D6-\u06ED]", "", text)

        def is_target_word_present(target: str, value: str) -> bool:
            if target in value:
                return True

            # Arabic: allow diacritic-insensitive matching.
            if any('\u0600' <= ch <= '\u06FF' for ch in target):
                stripped = strip_arabic_diacritics(value)
                if target in stripped:
                    return True

            # Devanagari: allow infinitive stem matching (e.g., होना -> हो/होगा/होते).
            if any('\u0900' <= ch <= '\u097F' for ch in target) and target.endswith("ना"):
                stem = target[:-2]
                if stem and stem in value:
                    return True

            return False

        for i, sentence in enumerate(sentences[:num_sentences]):
            normalized_sentence = sentence
            if any('\u0600' <= ch <= '\u06FF' for ch in word):
                if word not in sentence:
                    stripped = strip_arabic_diacritics(sentence)
                    if word in stripped:
                        normalized_sentence = stripped

            sentence = normalized_sentence
            word_missing = not is_target_word_present(word, sentence)
            word_count = self._count_sentence_units(sentence)

            # Always use the AI-generated sentence, but collect validation warnings
            validated_sentences.append(sentences[i])  # Use original sentence, not normalized
            validated_translations.append(translations[i] if i < len(translations) and translations[i] else f"This is a sample sentence with {word}.")
            validated_ipa.append(ipa_list[i] if i < len(ipa_list) else "")
            candidate_keywords = keywords[i] if i < len(keywords) else fallback_keywords[i % len(fallback_keywords)]
            keyword_items = [kw.strip().lower() for kw in candidate_keywords.split(',')]
            if any(any(term in kw for term in generic_terms) for kw in keyword_items):
                candidate_keywords = fallback_keywords[i % len(fallback_keywords)]
            validated_keywords.append(candidate_keywords)

            # Collect validation warnings for this sentence
            warnings = []
            if word_missing:
                warnings.append(f"Missing target word '{word}'")
                logger.warning(f"Sentence {i+1} missing target word '{word}'. Keeping sentence with warning.")

            if not (min_length <= word_count <= max_length):
                warnings.append(f"Word count: {word_count} (required: {min_length}-{max_length})")
                logger.warning(f"Sentence {i+1} has {word_count} words, outside {min_length}-{max_length}. Keeping sentence with warning.")

            validation_warnings.append({
                'sentence_index': i + 1,
                'issues': warnings,
                'is_valid': len(warnings) == 0
            })

        # Ensure correct number of items (use fallbacks only as absolute last resort)
        while len(validated_sentences) < num_sentences:
            validated_sentences.append(f"This is a sample sentence with {word}.")
            validated_translations.append(f"This is a sample sentence with {word}.")
            validated_ipa.append("")
            validated_keywords.append(fallback_keywords[len(validated_sentences) % len(fallback_keywords)])
            validation_warnings.append({
                'sentence_index': len(validation_warnings) + 1,
                'issues': ['Used fallback sentence - AI generation failed'],
                'is_valid': False
            })

        return validated_sentences, validated_translations, validated_ipa, validated_keywords, validation_warnings

        return validated_sentences[:num_sentences], validated_translations[:num_sentences], validated_ipa[:num_sentences], validated_keywords[:num_sentences]

    def _count_sentence_units(self, sentence: str) -> int:
        """Count words or character units for scripts that do not use spaces."""
        tokens = [t for t in sentence.split() if t]
        if len(tokens) > 1:
            return len(tokens)

        cjk_count = sum(1 for ch in sentence if '\u4e00' <= ch <= '\u9fff')
        kana_count = sum(1 for ch in sentence if '\u3040' <= ch <= '\u309f' or '\u30a0' <= ch <= '\u30ff' or '\u31f0' <= ch <= '\u31ff')
        hangul_count = sum(1 for ch in sentence if '\uac00' <= ch <= '\ud7af')
        thai_count = sum(1 for ch in sentence if '\u0e00' <= ch <= '\u0e7f')

        if cjk_count or kana_count or hangul_count or thai_count:
            return cjk_count + kana_count + hangul_count + thai_count

        return len(tokens)

    def _repair_with_ai(
        self,
        client,
        models_to_try: List[str],
        original_prompt: str,
        failed_response: str,
        critical_failures: List[Dict],
        word: str,
        language: str,
        num_sentences: int,
        min_length: int,
        max_length: int,
        pronunciation_label: str,
        restrictions: str,
        difficulty: str,
    ) -> Optional[Dict[str, Any]]:
        """Use AI to repair a failed/invalid generation response."""
        try:
            fix_prompt = self._build_fix_prompt(
                original_prompt=original_prompt,
                failed_response=failed_response,
                critical_failures=critical_failures,
                word=word,
                language=language,
                num_sentences=num_sentences,
                min_length=min_length,
                max_length=max_length,
                pronunciation_label=pronunciation_label,
                restrictions=restrictions,
                difficulty=difficulty,
            )
            for model_name in models_to_try:
                try:
                    repaired_response = client.generate_content(
                        model=model_name,
                        contents=fix_prompt,
                        config=client.genai.types.GenerateContentConfig(
                            temperature=0.4,  # Lower temperature for deterministic repair
                            max_output_tokens=20000,
                        ),
                    )
                    if repaired_response:
                        repaired_text = repaired_response.text.strip()
                        repaired_result = self._parse_generation_response(
                            repaired_text, word, language, num_sentences, min_length, max_length
                        )
                        repaired_failures = [
                            w for w in repaired_result.get('validation_warnings', [])
                            if not w.get('is_valid', True)
                        ]
                        if len(repaired_failures) < len(critical_failures):
                            logger.info(
                                f"AI repair improved content: {len(critical_failures)} -> "
                                f"{len(repaired_failures)} failure(s)"
                            )
                            return repaired_result
                        else:
                            logger.info("AI repair did not reduce failures; keeping original result")
                    break
                except Exception as repair_e:
                    logger.warning(f"Repair attempt with model {model_name} failed: {repair_e}")
                    continue
        except Exception as e:
            logger.warning(f"AI repair failed: {e}")
        return None

    def _build_fix_prompt(
        self,
        original_prompt: str,
        failed_response: str,
        critical_failures: List[Dict],
        word: str,
        language: str,
        num_sentences: int,
        min_length: int,
        max_length: int,
        pronunciation_label: str,
        restrictions: str,
        difficulty: str,
    ) -> str:
        """Build the repair prompt for a failed AI generation response."""
        num_failing = len(critical_failures)
        error_description = f"{num_failing} sentence(s) failed validation"
        specific_failures = "; ".join(
            f"Sentence {w['sentence_index']}: {', '.join(w['issues'])}"
            for w in critical_failures
            if w.get('issues')
        )

        return (
            "You are an expert AI content editor specializing in fixing and improving "
            "language learning content generated by Google Gemini. Your task is to take "
            "a failed Gemini response and transform it into high-quality, properly formatted "
            "content that meets all specified criteria.\n\n"
            "## ORIGINAL GENERATION CRITERIA\n"
            f"{original_prompt}\n\n"
            "## FAILED GEMINI RESPONSE\n"
            f"{failed_response}\n\n"
            "## FAILURE DETAILS\n"
            f"Error Type: VALIDATION_FAILURE\n"
            f"Error Description: {error_description}\n"
            f"Specific Issues: {specific_failures}\n\n"
            "## FIXING PRIORITIES\n\n"
            "### PRIORITY 1: FORMAT COMPLIANCE (CRITICAL)\n"
            "- Response must follow EXACT output format from original criteria\n"
            f"- ALL sections must be present: MEANING, RESTRICTIONS, SENTENCES, TRANSLATIONS, {pronunciation_label}, KEYWORDS\n"
            "- Section headers must be in ALL CAPS with colons\n"
            "- Numbering must be sequential starting from 1\n"
            f"- Each section must have exactly {num_sentences} items\n"
            "- Keywords must be comma-separated in format: keyword1, keyword2, keyword3\n\n"
            "### PRIORITY 2: CONTENT VALIDATION (CRITICAL)\n"
            f"- Every sentence must be between {min_length} and {max_length} words (count precisely)\n"
            f"- Target word \"{word}\" must be used correctly in ALL sentences according to grammatical restrictions\n"
            f"- Content must be in specified language \"{language}\" only\n"
            f"- Sentences must follow restrictions: {restrictions}\n"
            f"- Difficulty level must be maintained: {difficulty}\n"
            "- All content must be semantically meaningful and educationally valuable\n\n"
            "### PRIORITY 3: QUALITY IMPROVEMENT\n"
            "- Fix any truncated or incomplete content from token limits\n"
            "- Correct grammatical errors, unnatural phrasing, or literal translations\n"
            "- Ensure cultural appropriateness and natural native speaker language\n"
            "- Maintain consistency across all sentences and translations\n"
            "- Improve clarity while preserving educational intent\n"
            "- Fix IPA pronunciation formatting and accuracy\n\n"
            "### PRIORITY 4: STRUCTURAL INTEGRITY\n"
            "- Repair any parsing or JSON structure issues\n"
            "- Correct section ordering and separation\n"
            "- Fix encoding issues or malformed characters\n"
            "- Ensure proper data types and formatting\n\n"
            "## OUTPUT REQUIREMENTS\n"
            "Return ONLY the corrected response in the exact format specified in the original criteria. "
            "Do not include explanations, comments, or text outside the required structure. "
            "The output must be parseable by the existing codebase validation logic.\n\n"
            "## CORRECTED RESPONSE:"
        )

    def _create_fallback_response(self, word: str, num_sentences: int) -> Dict[str, Any]:
        """Create fallback response when generation fails."""
        # Provide basic fallback IPA/Pinyin - better than empty strings
        basic_pronunciation = f"[{word}]"  # Basic fallback in brackets

        return {
            'meaning': word,
            'restrictions': 'No specific grammatical restrictions.',
            'sentences': [f"This is a sample sentence with {word}."] * num_sentences,
            'translations': [f"This is a sample sentence with {word}."] * num_sentences,
            'ipa': [basic_pronunciation] * num_sentences,  # Use basic pronunciation instead of empty strings
            'keywords': [f"{word}, language, learning"] * num_sentences
        }


# Global instance for backward compatibility
_content_generator = None

def get_content_generator() -> ContentGenerator:
    """Get global content generator instance."""
    global _content_generator
    if _content_generator is None:
        _content_generator = ContentGenerator()
    return _content_generator
"""
Content Generator Service

Handles AI-powered content generation using Google Gemini API.
Extracted from sentence_generator.py for better separation of concerns.
"""

import json
import logging
import time
from typing import Optional, List, Dict, Any, Tuple, Union
import google.generativeai as genai

# Import centralized configuration
from streamlit_app.shared_utils import get_gemini_model, get_gemini_fallback_model, cached_api_call, retry_with_exponential_backoff, with_fallback

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
        """Configure Google Generative AI client."""
        genai.configure(api_key=api_key)
        return genai

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
        logger.info(f"API key provided: {'YES' if gemini_api_key else 'NO'} (length: {len(gemini_api_key) if gemini_api_key else 0})")
        if gemini_api_key:
            logger.info(f"API key starts with: {gemini_api_key[:10]}... (ends with: ...{gemini_api_key[-10:] if len(gemini_api_key) > 10 else gemini_api_key})")

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
                        enriched_meaning_instruction = f'Analyze this linguistic data for "{word}" and generate a brief, clean English meaning that encompasses ALL the meanings. Data: {meaning_summary}. IMPORTANT: Consider all meanings (letter, deity, etc.) and provide a comprehensive meaning like "letter (seventh letter of Hindi alphabet); deity (Vishnu)" - do NOT focus on just one meaning.'
                    else:
                        enriched_meaning_instruction = f'Analyze this linguistic context for "{word}" and generate a brief, clean English meaning. Context: {enriched_meaning[:200]}. IMPORTANT: Return ONLY the English meaning in format like "house (a building where people live)" - do NOT include any raw linguistic data in your response.'
                else:
                    # Legacy format
                    enriched_meaning_instruction = f'Use this pre-reviewed meaning for "{word}": "{enriched_meaning}". Generate a clean English meaning based on this. IMPORTANT: Return ONLY the English meaning in format like "house (a building where people live)" - do NOT include the original text in your response.'
            else:
                enriched_meaning_instruction = f'Provide a brief English meaning for "{word}".'

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

Your task: Generate a complete learning package for the {ai_language} word "{word}" in ONE response.

===========================
STEP 1: WORD MEANING
===========================
{enriched_meaning_instruction}
Format: Return exactly one line like "house (a building where people live)" or "he (male pronoun, used as subject)"
IMPORTANT: Keep the entire meaning under 75 characters total.

===========================
WORD-SPECIFIC RESTRICTIONS
===========================
Based on the meaning above, identify any grammatical constraints, mood, person, or context restrictions for "{word}".
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
Generate exactly {num_sentences} highly natural, idiomatic, culturally appropriate sentences in {ai_language} for the word "{word}".

QUALITY RULES (STRICT):
- Every sentence must sound like it was written by an educated native speaker
- Absolutely no unnatural, robotic, or literal-translation phrasing
- Grammar, syntax, spelling, diacritics, gender agreement, case, politeness level, and punctuation must all be correct
- The target word "{word}" MUST be used correctly in context according to its grammatical restrictions
- Ensure EVERY sentence matches the EXACT meaning and follows the WORD-SPECIFIC RESTRICTIONS above
- If the word cannot be used naturally within restrictions, use related forms and note it (e.g., base form instead of imperative)
- E.g., for imperatives: ONLY in commands like "Come here!"; for restricted moods: DO NOT force – use alternatives like base form
- Avoid rare or archaic vocabulary (unless difficulty="advanced")
- All sentences must be semantically meaningful (no filler templates)
- No repeated sentence structures or patterns — each sentence must be unique
- Each sentence must be no more than {max_length} words long. COUNT words precisely; if >{max_length}, it's INVALID – regenerate internally
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
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.7,  # Creativity for sentence variety
                            max_output_tokens=4000,  # Increased for Arabic and complex responses
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
            result = self._parse_generation_response(response_text, word, language, num_sentences, max_length)
            
            # Debug: log parsing results
            parsed_sentences = len(result.get('sentences', []))
            if parsed_sentences == 0:
                logger.warning(f"Failed to parse sentences from response. Raw response: {response_text}")
            
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
                logger.error("Rate limit exceeded")
            elif "unauthorized" in error_msg or "401" in error_msg:
                logger.error("API key invalid or unauthorized")
            elif "forbidden" in error_msg or "403" in error_msg:
                logger.error("API access forbidden")
            else:
                logger.error(f"Unknown API error: {str(e)}")
            
            # Return fallback structure with error indication
            return self._create_fallback_response(word, num_sentences)

    def _parse_generation_response(self, response_text: str, word: str, language: str, num_sentences: int, max_length: int) -> Dict[str, Any]:
        """Parse the AI response into structured data."""
        meaning = ""
        restrictions = ""
        sentences = []
        ipa_list = []
        keywords = []

        is_chinese = language in ["Chinese Simplified", "Chinese Traditional", "Chinese (Simplified)", "Chinese (Traditional)"]
        pronunciation_section = "PINYIN:" if is_chinese else "IPA:"

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
        validated_sentences, validated_translations, validated_ipa, validated_keywords = self._validate_and_create_fallbacks(
            sentences, translations, ipa_list, keywords, word, restrictions, num_sentences, max_length
        )

        return {
            'meaning': meaning,
            'restrictions': restrictions,
            'sentences': validated_sentences,
            'translations': validated_translations,
            'ipa': validated_ipa,
            'keywords': validated_keywords
        }

    def _validate_and_create_fallbacks(self, sentences: List[str], translations: List[str], ipa_list: List[str], keywords: List[str],
                                      word: str, restrictions: str, num_sentences: int, max_length: int) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Validate content and create fallbacks for invalid items."""

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
                f"{word}, demonstration, context",
                f"{word}, illustration, usage",
                f"{word}, instance, application",
                f"{word}, case, study",
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

        for i, sentence in enumerate(sentences[:num_sentences]):
            word_count = len(sentence.split())

            if word_count <= max_length:
                validated_sentences.append(sentence)
                validated_translations.append(translations[i] if i < len(translations) and translations[i] else f"This is a sample sentence with {word}.")
                validated_ipa.append(ipa_list[i] if i < len(ipa_list) else "")
                validated_keywords.append(keywords[i] if i < len(keywords) else fallback_keywords[i % len(fallback_keywords)])
            else:
                logger.warning(f"Sentence {i+1} has {word_count} words, exceeds maximum {max_length}. Using fallback.")
                fallback_idx = i % len(fallback_templates)
                validated_sentences.append(fallback_templates[fallback_idx])
                validated_translations.append(f"This is a sample sentence with {word}.")
                validated_ipa.append("")
                validated_keywords.append(fallback_keywords[fallback_idx])

        # Ensure correct number of items
        while len(validated_sentences) < num_sentences:
            validated_sentences.append(f"This is a sample sentence with {word}.")
        while len(validated_translations) < len(validated_sentences):
            validated_translations.append(f"This is a sample sentence with {word}.")
        while len(validated_ipa) < len(validated_sentences):
            validated_ipa.append("")
        while len(validated_keywords) < len(validated_sentences):
            validated_keywords.append(f"{word}, language, learning")

        return validated_sentences[:num_sentences], validated_translations[:num_sentences], validated_ipa[:num_sentences], validated_keywords[:num_sentences]

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
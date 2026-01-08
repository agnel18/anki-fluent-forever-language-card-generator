# Sentence generation module
# Extracted from core_functions.py for better separation of concerns

import json
import logging
import time
from typing import Optional, List, Dict, Any, Tuple
from groq import Groq

# Import cache manager and error recovery
from cache_manager import cached_api_call
from error_recovery import resilient_groq_call, with_fallback

# Import the new grammar analyzer system
from language_analyzers.analyzer_registry import get_analyzer

logger = logging.getLogger(__name__)

# Language name to ISO code mapping for analyzer registry
LANGUAGE_NAME_TO_CODE = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese (Simplified)": "zh",
    "Chinese (Traditional)": "zh",
    "Arabic": "ar",
    "Hindi": "hi",
    "Bengali": "bn",
    "Telugu": "te",
    "Tamil": "ta",
    "Dutch": "nl",
    "Swedish": "sv",
    "Norwegian": "no",
    "Danish": "da",
    "Finnish": "fi",
    "Polish": "pl",
    "Czech": "cs",
    "Slovak": "sk",
    "Hungarian": "hu",
    "Romanian": "ro",
    "Bulgarian": "bg",
    "Greek": "el",
    "Turkish": "tr",
    "Hebrew": "he",
    "Thai": "th",
    "Vietnamese": "vi",
    "Indonesian": "id",
    "Malay": "ms",
    "Filipino": "fil",
    "Swahili": "sw",
    "Amharic": "am",
    "Hausa": "ha",
    "Yoruba": "yo",
    "Igbo": "ig",
    "Zulu": "zu",
    "Xhosa": "xh",
    "Afrikaans": "af",
    "Albanian": "sq",
    "Armenian": "hy",
    "Azerbaijani": "az",
    "Basque": "eu",
    "Belarusian": "be",
    "Bosnian": "bs",
    "Catalan": "ca",
    "Croatian": "hr",
    "Estonian": "et",
    "Galician": "gl",
    "Georgian": "ka",
    "Icelandic": "is",
    "Irish": "ga",
    "Kazakh": "kk",
    "Latvian": "lv",
    "Lithuanian": "lt",
    "Macedonian": "mk",
    "Maltese": "mt",
    "Mongolian": "mn",
    "Serbian": "sr",
    "Slovenian": "sl",
    "Ukrainian": "uk",
    "Welsh": "cy",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa",
    "Urdu": "ur",
    "Persian": "fa",
    "Pashto": "ps",
    "Sindhi": "sd",
    "Nepali": "ne",
    "Sinhala": "si",
    "Burmese": "my",
    "Khmer": "km",
    "Lao": "lo",
    "Tibetan": "bo",
    "Dzongkha": "dz",
    "Uzbek": "uz",
    "Kyrgyz": "ky",
    "Tajik": "tg",
    "Turkmen": "tk",
    "Kazakh": "kk",
    "Mongolian": "mn",
    "Cantonese": "zh",  # Map to same as Simplified Chinese
    "Mandarin Chinese": "zh",  # Map to same as Simplified Chinese
    "Moroccan Arabic": "ar",  # Map to Arabic
}

# ============================================================================
# IPA GENERATION (Using Epitran)
# ============================================================================
def generate_ipa_hybrid(text: str, language: str, ai_ipa: str = "") -> str:
    """
    Generate IPA using Epitran library for accurate phonetic transcription.
    Falls back to AI-generated IPA if Epitran fails or language not supported.
    Ensures output is official IPA only (no Pinyin, romanization).
    """
    if not text:
        return ""
    
    try:
        import epitran
        
        # Map language names to Epitran codes (IPA-focused)
        language_map = {
            "Chinese (Simplified)": "cmn-Hans",  # Mandarin IPA (not Pinyin)
            "Chinese (Traditional)": "cmn-Hant", 
            "Mandarin Chinese": "cmn-Hans",
            "English": "eng-Latn",
            "Spanish": "spa-Latn",
            "French": "fra-Latn",
            "German": "deu-Latn",
            "Italian": "ita-Latn",
            "Portuguese": "por-Latn",
            "Russian": "rus-Cyrl",
            "Japanese": "jpn-Hrgn",  # Hepburn romanization to IPA
            "Korean": "kor-Hang",   # Hangul to IPA
            "Hindi": "hin-Deva",
            "Arabic": "ara-Arab",
        }
        
        epi_code = language_map.get(language)
        if epi_code:
            epi = epitran.Epitran(epi_code)
            ipa = epi.transliterate(text)
            if ipa and ipa != text:
                # Use the comprehensive validation from generation_utils
                from generation_utils import validate_ipa_output
                is_valid, _ = validate_ipa_output(ipa, language)
                if is_valid:
                    return ipa

        # Fallback to AI IPA if Epitran fails or validation fails
        if ai_ipa:
            from generation_utils import validate_ipa_output
            is_valid, _ = validate_ipa_output(ai_ipa, language)
            if is_valid:
                return ai_ipa

        # If no valid IPA, return empty (will be handled upstream)
        return ""

    except Exception as e:
        logger.warning(f"Epitran IPA generation failed for '{text}' in {language}: {e}")
        # Try AI fallback if available and valid
        if ai_ipa:
            from generation_utils import validate_ipa_output
            is_valid, _ = validate_ipa_output(ai_ipa, language)
            if is_valid:
                return ai_ipa
        return ""

# ============================================================================
# WORD MEANING GENERATION (Groq)
# ============================================================================
@cached_api_call("groq_meaning", ttl_seconds=86400)  # Cache for 24 hours
@resilient_groq_call(max_retries=3)
@with_fallback(fallback_value=lambda word, **kwargs: word)  # Fallback to word itself
def generate_word_meaning(
    word: str,
    language: str,
    groq_api_key: str = None,
) -> str:
    """
    Generate English meaning and brief explanation for a word.

    Args:
        word: Target language word
        language: Language name (e.g., "Spanish", "Hindi")
        groq_api_key: Groq API key

    Returns:
        String with meaning and brief explanation (e.g., "he (male pronoun, used as subject)")
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")

    client = Groq(api_key=groq_api_key)

    prompt = f"""Provide a brief English meaning for the {language} word \"{word}\".

Format: Return ONLY a single line with the meaning and a brief explanation in parentheses.
Example: \"house (a building where people live)\" or \"he (male pronoun, used as subject)\"

IMPORTANT: Return ONLY the meaning line, nothing else. No markdown, no explanation, no JSON."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temperature for consistency
            max_tokens=100,
        )
        # --- API USAGE TRACKING ---
        try:
            import streamlit as st
            if "groq_api_calls" not in st.session_state:
                st.session_state.groq_api_calls = 0
            if "groq_tokens_used" not in st.session_state:
                st.session_state.groq_tokens_used = 0
            st.session_state.groq_api_calls += 1
            # Estimate tokens used (prompt+completion)
            st.session_state.groq_tokens_used += 100  # rough estimate, adjust if needed
        except Exception:
            pass
        # -------------------------
        meaning = response.choices[0].message.content.strip()

        # Clean up any quotes
        meaning = meaning.strip('"\'')
        logger.info(f"Generated meaning for '{word}': {meaning}")
        
        # Rate limiting: wait 5 seconds between API calls to respect per-minute limits
        time.sleep(5)
        
        return meaning if meaning else word

    except Exception as e:
        logger.error(f"Error generating meaning for '{word}': {e}")
        return word  # Fallback to word itself

# ============================================================================
# COMBINED PASS 1: Word Meaning + Sentences + Keywords (Single API Call)
# ============================================================================

def generate_word_meaning_sentences_and_keywords(
    word: str,
    language: str,
    num_sentences: int = 10,
    min_length: int = 5,
    max_length: int = 20,
    difficulty: str = "intermediate",
    groq_api_key: str = None,
    topics: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    COMBINED PASS 1: Generate word meaning, sentences, AND keywords in ONE efficient API call.
    This reduces API calls from 3 separate calls to 1 combined call.

    Args:
        word: Target language word
        language: Language name (e.g., "Spanish", "Hindi")
        num_sentences: Number of sentences to generate (1-20)
        min_length: Minimum sentence length in words
        max_length: Maximum sentence length in words
        difficulty: "beginner", "intermediate", "advanced"
        groq_api_key: Groq API key
        topics: List of topics to focus sentence generation around (optional)

    Returns:
        Dict with keys:
        - meaning: English meaning string
        - sentences: List of generated sentences
        - keywords: List of keyword strings (one per sentence)
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")

    logger.info(f"PASS 1 called with word='{word}', language='{language}', num_sentences={num_sentences}, min_length={min_length}, max_length={max_length}, difficulty='{difficulty}', topics={topics}")

    try:
        client = Groq(api_key=groq_api_key)

        # Build context instruction based on topics
        if topics:
            context_instruction = f"- CRITICAL REQUIREMENT: ALL sentences MUST relate to these specific topics: {', '.join(topics)}. Force the word usage into these contexts even if it requires creative interpretation. Do NOT use generic contexts."
        else:
            context_instruction = "- Use diverse real-life contexts: home, travel, food, emotions, work, social life, daily actions"

        prompt = f"""You are a native-level expert linguist in {language} with professional experience teaching it to non-native learners.

Your task: Generate a complete learning package for the {language} word "{word}" in ONE response.

===========================
STEP 1: WORD MEANING
===========================
Provide a brief English meaning for "{word}".
Format: Return exactly one line like "house (a building where people live)" or "he (male pronoun, used as subject)"

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

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic, culturally appropriate sentences in {language} for the word "{word}".

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
- Use different tenses (if applicable to {language})
- Use different sentence types: declarative, interrogative, imperative
- Use the target word in different grammatical roles if possible
{context_instruction}

===========================
STEP 3: IMAGE KEYWORDS
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

IPA:
1. [IPA transcription for sentence 1]
2. [IPA transcription for sentence 2]
3. [IPA transcription for sentence 3]

KEYWORDS:
1. [keyword1, keyword2, keyword3]
2. [keyword1, keyword2, keyword3]
3. [keyword1, keyword2, keyword3]

IMPORTANT:
- Return ONLY the formatted text, no extra explanation
- Sentences must be in {language} only
- IPA must use official IPA symbols only (not pinyin, not romanization, not any non-IPA symbols)
- Keywords must be comma-separated
- Ensure exactly {num_sentences} sentences and keywords"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,  # Creativity for sentence variety
            max_tokens=2000,  # Enough for meaning + sentences + keywords
        )

        response_text = response.choices[0].message.content.strip()
        logger.info(f"PASS 1 raw response: {response_text}")

        # Parse text format
        meaning = ""
        restrictions = ""
        sentences = []
        ipa_list = []
        keywords = []

        # Extract meaning
        if "MEANING:" in response_text:
            meaning_part = response_text.split("MEANING:")[1].split("RESTRICTIONS:")[0].strip()
            meaning = meaning_part.strip()

        # Extract restrictions
        if "RESTRICTIONS:" in response_text:
            restrictions_part = response_text.split("RESTRICTIONS:")[1].split("SENTENCES:")[0].strip()
            restrictions = restrictions_part.strip()

        # Extract sentences
        if "SENTENCES:" in response_text and "IPA:" in response_text:
            sentences_part = response_text.split("SENTENCES:")[1].split("IPA:")[0].strip()
            # Split by numbered lines
            for line in sentences_part.split("\n"):
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, num_sentences + 1)):
                    # Remove the number prefix
                    sentence = line.split(".", 1)[1].strip() if "." in line else line
                    if sentence:
                        sentences.append(sentence)

        # Extract IPA
        if "IPA:" in response_text and "KEYWORDS:" in response_text:
            ipa_part = response_text.split("IPA:")[1].split("KEYWORDS:")[0].strip()
            for line in ipa_part.split("\n"):
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, num_sentences + 1)):
                    # Remove the number prefix
                    ipa = line.split(".", 1)[1].strip() if "." in line else line
                    if ipa:
                        # Validate IPA output to reject Pinyin and non-IPA romanizations
                        from generation_utils import validate_ipa_output
                        language_code = LANGUAGE_NAME_TO_CODE.get(language, "en")
                        is_valid, validated_ipa = validate_ipa_output(ipa, language_code)
                        if is_valid:
                            ipa_list.append(validated_ipa)
                            logger.debug(f"Valid IPA: {validated_ipa}")
                        else:
                            logger.warning(f"Invalid IPA rejected: {validated_ipa}")
                            ipa_list.append("")  # Use empty string for invalid IPA

        # Extract keywords
        if "KEYWORDS:" in response_text:
            keywords_part = response_text.split("KEYWORDS:")[1].strip()
            for line in keywords_part.split("\n"):
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, num_sentences + 1)):
                    # Remove the number prefix
                    kw = line.split(".", 1)[1].strip() if "." in line else line
                    if kw:
                        keywords.append(kw)

        logger.info(f"PASS 1 parsed: meaning='{meaning}', restrictions='{restrictions}', sentences={len(sentences)}, ipa={len(ipa_list)}, keywords={len(keywords)}")

        # Validate sentence lengths and reject/re-pad if necessary
        validated_sentences = []
        validated_ipa = []
        validated_keywords = []
        
        # Prepare varied fallbacks that incorporate word meaning when possible
        if "imperative" in restrictions.lower() or "command" in restrictions.lower():
            # For imperatives, create command-based fallbacks
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
            # Generic fallbacks for other word types
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
        
        for i, sentence in enumerate(sentences[:num_sentences]):
            word_count = len(sentence.split())
            
            # Only enforce maximum length - allow any reasonable sentence length
            if word_count <= max_length:
                validated_sentences.append(sentence)
                validated_ipa.append(ipa_list[i] if i < len(ipa_list) else "")
                validated_keywords.append(keywords[i] if i < len(keywords) else fallback_keywords[i % len(fallback_keywords)])
            else:
                logger.warning(f"Sentence {i+1} has {word_count} words, exceeds maximum {max_length}. Rejecting and using varied fallback.")
                # Use varied fallback for rejected sentences
                fallback_idx = i % len(fallback_templates)
                validated_sentences.append(fallback_templates[fallback_idx])
                validated_ipa.append("")
                validated_keywords.append(fallback_keywords[fallback_idx])

        # Ensure we have the right number of items
        sentences = validated_sentences[:num_sentences]
        ipa_list = validated_ipa[:num_sentences]
        keywords = validated_keywords[:num_sentences]

        # Pad if necessary (though validation should prevent this)
        while len(sentences) < num_sentences:
            sentences.append(f"This is a sample sentence with {word}.")
        while len(ipa_list) < len(sentences):
            ipa_list.append("")
        while len(keywords) < len(sentences):
            keywords.append(f"{word}, language, learning")

        # Rate limiting: wait 5 seconds between API calls to respect per-minute limits
        time.sleep(5)

        return {
            'meaning': meaning,
            'restrictions': restrictions,
            'sentences': sentences,
            'ipa': ipa_list,
            'keywords': keywords
        }

    except Exception as e:
        logger.error(f"Error in combined generation: {e}")
        # Fallback: return basic structure
        return {
            'meaning': word,
            'sentences': [f"This is a sample sentence with {word}."] * num_sentences,
            'keywords': [f"{word}, language, learning"] * num_sentences
        }

# ============================================================================
# SENTENCE GENERATION (Groq)
# ============================================================================
def generate_sentences(
    word: str,
    language: str,
    num_sentences: int = 10,
    min_length: int = 5,
    max_length: int = 20,
    difficulty: str = "intermediate",
    groq_api_key: str = None,
    topics: Optional[List[str]] = None,
    native_language: str = "English",
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Generate sentences using optimized 3-pass architecture with COMBINED first pass:
    1. COMBINED PASS 1: Generate word meaning + raw sentences + keywords in ONE API call
    2. PASS 2: Batch validate + enrich ALL sentences in ONE API call
    3. PASS 3: Batch grammar analysis and coloring

    This approach reduces API calls from 5 to 3 per word while maintaining quality.

    Args:
        word: Target language word
        language: Language name (e.g., "Spanish", "Hindi")
        num_sentences: Number of sentences to generate (1-20)
        min_length: Minimum sentence length in words
        max_length: Maximum sentence length in words
        difficulty: "beginner", "intermediate", "advanced"
        groq_api_key: Groq API key
        topics: List of topics to focus sentence generation around (optional)
        native_language: User's native language for explanations (default: "English")

    Returns:
        Tuple of (meaning, sentences_list) where sentences_list contains dicts with keys:
        sentence, english_translation, ipa, context, image_keywords, role_of_word, word, meaning
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")

    try:
        # COMBINED PASS 1: Generate meaning + sentences + keywords in ONE call
        logger.info(f"COMBINED PASS 1: Generating meaning, {num_sentences} sentences, and keywords for '{word}' ({language})...")
        combined_result = generate_word_meaning_sentences_and_keywords(
            word=word,
            language=language,
            num_sentences=num_sentences,
            min_length=min_length,
            max_length=max_length,
            difficulty=difficulty,
            groq_api_key=groq_api_key,
            topics=topics,
        )

        meaning = combined_result['meaning']
        raw_sentences = combined_result['sentences']
        raw_ipa = combined_result.get('ipa', [])
        raw_keywords = combined_result['keywords']

        logger.info(f"Generated meaning: {meaning}")
        logger.info(f"Generated {len(raw_sentences)} sentences with {len(raw_keywords)} keyword sets")

        # PASS 2: Batch validate + enrich all sentences in ONE call
        logger.info(f"PASS 2: Batch validating + enriching {len(raw_sentences)} sentences...")
        enriched_results = _validate_and_enrich_batch_pass2(
            sentences=raw_sentences,
            word=word,
            language=language,
            groq_api_key=groq_api_key,
        )

        # Initialize final_sentences from enriched results
        final_sentences = []
        for i, result in enumerate(enriched_results):
            # Use keywords from combined pass 1, but allow override from pass 2 if better
            image_keywords = raw_keywords[i] if i < len(raw_keywords) else result.get("image_keywords", "")

            final_sentences.append({
                "sentence": result.get("sentence", ""),
                "english_translation": result.get("english_translation", ""),
                "context": result.get("context", "general"),
                "ipa": result.get("ipa", ""),
                "image_keywords": image_keywords,  # Use keywords from combined pass
                "role_of_word": result.get("role_of_word", ""),
                "word": word,
                "meaning": meaning,
                # Initialize grammar fields (will be updated in PASS 3)
                "colored_sentence": result.get("sentence", ""),
                "word_explanations": [],
                "grammar_summary": "",
            })

        # PASS 3: Batch grammar analysis and coloring for ALL sentences
        logger.info(f"PASS 3: Batch analyzing grammar for {len(final_sentences)} sentences...")
        try:
            # Extract sentences for batch processing
            sentences_to_analyze = [s["sentence"] for s in final_sentences if s["sentence"]]

            if sentences_to_analyze:
                # Batch analyze grammar for all sentences at once
                batch_grammar_results = _batch_analyze_grammar_and_color(
                    sentences=sentences_to_analyze,
                    word=word,
                    language=language,
                    groq_api_key=groq_api_key,
                    complexity_level=difficulty,  # Map difficulty to complexity level
                    native_language=native_language,
                )

                # Update final_sentences with batch results
                for i, grammar_result in enumerate(batch_grammar_results):
                    if i < len(final_sentences):
                        # Handle different analyzer output formats
                        colored_sentence = grammar_result.get("colored_sentence", final_sentences[i]["sentence"])
                        grammar_summary = grammar_result.get("grammar_summary", "")

                        # Convert character-based analysis to word_explanations format
                        # Check if analyzer already provided word_explanations (preferred)
                        if "word_explanations" in grammar_result and grammar_result["word_explanations"]:
                            word_explanations = grammar_result["word_explanations"]
                            logger.info(f"DEBUG Color Flow - Using analyzer's word_explanations directly: {len(word_explanations)} items")
                        else:
                            # Fallback to conversion function
                            word_explanations = _convert_analyzer_output_to_explanations(grammar_result, language)
                            logger.info(f"DEBUG Color Flow - Using converted word_explanations: {len(word_explanations)} items")

                        final_sentences[i].update({
                            "colored_sentence": colored_sentence,
                            "word_explanations": word_explanations,
                            "grammar_summary": grammar_summary,
                        })
            else:
                logger.warning("No valid sentences to analyze grammar for")

        except Exception as e:
            logger.warning(f"Batch grammar analysis failed, falling back to individual analysis: {e}")
            # Fallback: Try individual analysis for each sentence (less efficient but more likely to succeed)
            for i, sentence_data in enumerate(final_sentences):
                if sentence_data["sentence"]:
                    try:
                        # Use basic fallback for grammar analysis
                        sentence_data["colored_sentence"] = sentence_data["sentence"]
                        sentence_data["word_explanations"] = []
                        sentence_data["grammar_summary"] = "Analysis failed"
                    except Exception as inner_e:
                        logger.error(f"Individual grammar analysis failed for sentence {i}: {inner_e}")

        return meaning, final_sentences
    except Exception as exc:
        logger.error(f"3-pass sentence generation error: {exc}")
        return word, []  # Return word as fallback meaning, empty sentences list

# ============================================================================
# PASS 1: SENTENCE GENERATION (Raw sentences, no JSON)
# ============================================================================
def _generate_sentences_pass1(
    word: str,
    meaning: str,
    language: str,
    num_sentences: int = 10,
    min_length: int = 5,
    max_length: int = 20,
    difficulty: str = "intermediate",
    groq_api_key: Optional[str] = None,
    topics: Optional[List[str]] = None,
) -> List[str]:

    try:
        client = Groq(api_key=groq_api_key)

        # Build topic section if topics are provided
        topic_section = ""
        if topics:
            topic_section = """===========================
TOPIC FOCUS
===========================
Focus the sentences around these topics: """ + ', '.join(topics) + """
Ensure the sentences are relevant to these topics while maintaining natural language use.
"""

        prompt = f"""
You are a native-level expert linguist in {language} with professional experience teaching it to non-native learners.

Your task:
Generate exactly {num_sentences} highly natural, idiomatic, culturally appropriate sentences in {language} for the word \"{word}\" ({meaning}).

{topic_section}===========================
QUALITY RULES (STRICT)
===========================
- Every sentence must sound like it was written by an educated native speaker. Native speakers should NOT cringe at the sentence.
- Absolutely no unnatural, robotic, or literal-translation phrasing.
- Grammar, syntax, spelling, diacritics, gender agreement, case, politeness level, and punctuation must all be correct.
- The target word \"{word}\" MUST:
    * be used correctly in context,
    * match its real meaning,
    * NOT be forced into an unnatural construction.
- If the word cannot be used naturally, do NOT use it. Instead, create a sentence that clearly conveys the meaning of \"{word}\" in context, even if the word itself isn't used.
- Avoid rare or archaic vocabulary (unless difficulty=\"advanced\").
- All sentences must be semantically meaningful (no filler templates).
- No repeated sentence structures or patterns — each sentence must be unique.

- Each sentence must be no more than {max_length} words long.
- Difficulty: {difficulty}
    - beginner: Use only simple vocabulary and grammar, mostly present tense.
    - intermediate: Use mixed tenses, richer but still natural language.
    - advanced: Use complex structures, nuanced vocabulary, and advanced grammar.

===========================
VARIETY REQUIREMENTS
===========================
Across the {num_sentences} sentences:
- Use different tenses (if applicable to {language}).
- Use different sentence types: declarative, interrogative, imperative.
- Use the target word in different grammatical roles if possible.
- Use diverse real-life contexts: home, travel, food, emotions, work, social life, daily actions.

===========================
IMPORTANT
===========================
- RETURN ONLY the {language} sentences, one per line.
- NO English translation.
- NO explanation.
- NO JSON.
- NO numbering.
- NO extra text.
- Each line = ONE sentence only.
"""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200,
        )
        response_text = response.choices[0].message.content.strip()
        logger.info(f"PASS 1 raw response: {response_text}")
        # Split by newlines and filter empty lines
        sentences = [s.strip() for s in response_text.split("\n") if s.strip()]
        logger.info(f"PASS 1 parsed sentences: {sentences}")
        
        # Rate limiting: wait 5 seconds between API calls to respect per-minute limits
        time.sleep(5)
        
        return sentences[:num_sentences]
    except Exception as e:
        logger.error(f"PASS 1 (sentence generation) error: {e}")
        return []

# ============================================================================
# PASS 2: BATCH VALIDATION + ENRICHMENT (All sentences in one call)
# ============================================================================
@cached_api_call("groq_sentences_pass2", ttl_seconds=86400)  # Cache for 24 hours
@resilient_groq_call(max_retries=3)
@with_fallback(fallback_value=lambda sentences, **kwargs: [
    {
        "sentence": s,
        "valid": True,  # Assume valid if API fails
        "english_translation": "",
        "ipa": "",
        "context": "general",
        "image_keywords": "",
        "role_of_word": "",
    } for s in sentences
])
def _validate_and_enrich_batch_pass2(
    sentences: List[str],
    word: str,
    language: str,
    groq_api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    PASS 2: Validate and enrich ALL sentences in a single batched API call.
    This is 5× more efficient than separate validation + enrichment per sentence.

    Args:
        sentences: List of raw sentences from Pass 1
        word: Target word used in sentences
        language: Language name
        groq_api_key: Groq API key

    Returns:
        List of dicts, each with keys: sentence, valid, english_translation, ipa, context, image_keywords, role_of_word
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")

    client = Groq(api_key=groq_api_key)

    # Build numbered sentence list for prompt
    sentences_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])

    prompt = f"""You are a native linguist for {language}.

Task: For each sentence below, validate it and provide enrichment data.

Sentences:
{sentences_text}

For EACH sentence, check:
- Is it natural and grammatically correct?
- Is "{word}" used correctly?
- Are spelling/accents/diacritics correct?
- Is it culturally appropriate?

Return a JSON array with one object per sentence (in order):

[
  {{
    "sentence": "corrected sentence if needed, otherwise original",
    "valid": true/false,
    "english_translation": "natural English translation",
    "ipa": "full IPA transcription using correct symbols",
    "context": "one short phrase (e.g., office, family, travel)",
    "image_keywords": "2-3 concrete nouns or actions for images (in English only)",
    "role_of_word": "grammatical role of '{word}' (subject, verb, adjective, etc.)"
  }},
  ...
]

IMPORTANT:
- Return ONLY valid JSON array, no markdown, no explanation.
- IPA must use official IPA symbols only.
- Image keywords must be visually representable.
- If sentence is valid, keep it unchanged in "sentence" field.
- If invalid, provide corrected version in "sentence" field."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=2000,  # Enough for 10 sentences with full enrichment
        )

        response_text = response.choices[0].message.content.strip()

        # Extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        results = json.loads(response_text)

        # Validate structure
        if not isinstance(results, list):
            logger.error("PASS 2 batch: Expected JSON array")
            return []

        # Ensure we have the right number of results
        validated_results = []
        for i, result in enumerate(results[:len(sentences)]):
            if isinstance(result, dict):
                validated_results.append({
                    "sentence": result.get("sentence", sentences[i]),
                    "valid": result.get("valid", False),
                    "english_translation": result.get("english_translation", ""),
                    "ipa": result.get("ipa", ""),
                    "context": result.get("context", "general"),
                    "image_keywords": result.get("image_keywords", ""),
                    "role_of_word": result.get("role_of_word", ""),
                })

        # Rate limiting: wait 5 seconds between API calls to respect per-minute limits
        time.sleep(5)

        return validated_results

    except json.JSONDecodeError as e:
        logger.error(f"PASS 2 batch JSON parse error: {e}")
        # Return fallback data
        return [{
            "sentence": s,
            "valid": False,
            "english_translation": "",
            "ipa": "",
            "context": "general",
            "image_keywords": "",
            "role_of_word": "",
        } for s in sentences]
    except Exception as e:
        logger.error(f"PASS 2 batch error: {e}")
        return [{
            "sentence": s,
            "valid": False,
            "english_translation": "",
            "ipa": "",
            "context": "general",
            "image_keywords": "",
            "role_of_word": "",
        } for s in sentences]

# ============================================================================
# PASS 3: GRAMMATICAL ANALYSIS (AI-powered POS tagging and coloring)
# ============================================================================
@cached_api_call("groq_grammar_analysis", ttl_seconds=2592000)  # Cache for 30 days (permanent)
@resilient_groq_call(max_retries=3)
@with_fallback(fallback_func=lambda sentence, word, language, groq_api_key=None, **kwargs: {
    "colored_sentence": sentence,
    "word_explanations": [],
    "grammar_summary": "Analysis unavailable"
})
def analyze_grammar_and_color(
    sentence: str,
    word: str,
    language: str,
    groq_api_key: str = None,
) -> Dict[str, Any]:
    """
    PASS 3: Analyze sentence grammar and assign colors to words based on POS.
    Provides educational coloring for language learning cards.

    Uses the new grammar analyzer system for language-specific analysis.

    Args:
        sentence: The sentence to analyze
        word: Target word being learned
        language: Language name (e.g., "Spanish", "Hindi")
        groq_api_key: Groq API key

    Returns:
        Dict with keys:
        - colored_sentence: HTML with color-coded words
        - word_explanations: List of [word, pos, color, explanation] tuples
        - grammar_summary: Brief grammar explanation
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")

    # Get language code for analyzer registry
    language_code = LANGUAGE_NAME_TO_CODE.get(language)
    if not language_code:
        logger.warning(f"No language code mapping found for '{language}', falling back to generic analysis")
        language_code = None

    # Try to get language-specific analyzer
    analyzer = None
    if language_code:
        analyzer = get_analyzer(language_code)

    if analyzer:
        # Use the new analyzer system
        logger.info(f"Using {language_code} analyzer for grammar analysis")
        try:
            # Determine complexity level (default to intermediate for now)
            complexity = "intermediate"

            # Analyze grammar using the language-specific analyzer
            analysis_result = analyzer.analyze_grammar(
                sentence=sentence,
                target_word=word,
                complexity=complexity,
                groq_api_key=groq_api_key
            )

            # DEBUG: Log the complete analysis result structure
            logger.info(f"DEBUG Hindi Color Flow - Analysis Result Type: {type(analysis_result)}")
            logger.info(f"DEBUG Hindi Color Flow - Analysis Result Keys: {analysis_result.__dict__.keys() if hasattr(analysis_result, '__dict__') else 'No __dict__'}")
            logger.info(f"DEBUG Hindi Color Flow - HTML Output: {analysis_result.html_output[:200]}...")
            logger.info(f"DEBUG Hindi Color Flow - Grammatical Elements: {analysis_result.grammatical_elements}")
            logger.info(f"DEBUG Hindi Color Flow - Explanations: {analysis_result.explanations}")
            logger.info(f"DEBUG Hindi Color Flow - Color Scheme: {analysis_result.color_scheme}")
            logger.info(f"DEBUG Hindi Color Flow - Confidence: {analysis_result.confidence_score}")

            # Convert analyzer result to expected format
            colored_sentence = analysis_result.html_output
            word_explanations = []

            # DEBUG: Log what we're extracting
            logger.info(f"DEBUG Hindi Color Flow - Raw HTML Output Length: {len(colored_sentence)}")
            logger.info(f"DEBUG Hindi Color Flow - Grammatical Elements Keys: {list(analysis_result.grammatical_elements.keys())}")

            # Combine grammatical elements and explanations
            elements = analysis_result.grammatical_elements
            explanations = analysis_result.explanations

            # DEBUG: Check if explanations contain HTML with colors
            for exp_key, exp_value in explanations.items():
                logger.info(f"DEBUG Hindi Color Flow - Explanation '{exp_key}': {str(exp_value)[:100]}...")

            # Build word explanations list - THIS IS THE PROBLEM AREA
            logger.info(f"DEBUG Hindi Color Flow - Building word_explanations from grammatical_elements...")
            for element_type, element_list in elements.items():
                logger.info(f"DEBUG Hindi Color Flow - Processing element_type '{element_type}' with {len(element_list)} elements")
                for element in element_list:
                    word = element.get('word', '')
                    if word:
                        # Find corresponding explanation
                        explanation = explanations.get(element_type, f"{element_type} in {analysis_result.language_code} grammar")
                        color = analysis_result.color_scheme.get(element_type, '#CCCCCC')

                        logger.info(f"DEBUG Hindi Color Flow - Word: '{word}', Type: '{element_type}', Color: '{color}', Explanation: '{explanation[:50]}...'")
                        word_explanations.append([word, element_type, color, explanation])

            logger.info(f"DEBUG Hindi Color Flow - Final word_explanations count: {len(word_explanations)}")
            for i, exp in enumerate(word_explanations[:3]):  # Log first 3
                logger.info(f"DEBUG Hindi Color Flow - word_explanations[{i}]: {exp}")

            # Create grammar summary
            grammar_summary = f"Grammar analysis for {analysis_result.language_code.upper()} ({analysis_result.complexity_level} level)"
            if explanations:
                # Use the most relevant explanation as summary
                main_explanation = list(explanations.values())[0] if explanations else ""
                if main_explanation:
                    grammar_summary = main_explanation

            logger.info(f"DEBUG Hindi Color Flow - Final colored_sentence: {colored_sentence[:100]}...")
            logger.info(f"DEBUG Hindi Color Flow - Final grammar_summary: {grammar_summary[:100]}...")

            result = {
                "colored_sentence": colored_sentence,
                "word_explanations": word_explanations,
                "grammar_summary": grammar_summary
            }

            # --- API USAGE TRACKING ---
            try:
                import streamlit as st
                if "groq_api_calls" not in st.session_state:
                    st.session_state.groq_api_calls = 0
                if "groq_tokens_used" not in st.session_state:
                    st.session_state.groq_tokens_used = 0
                st.session_state.groq_api_calls += 1
                # Estimate tokens used for grammar analysis
                st.session_state.groq_tokens_used += 150
            except Exception:
                pass
            # -------------------------

            logger.info(f"✓ Grammar analysis completed using {language_code} analyzer for sentence: {sentence[:50]}...")
            return result

        except Exception as e:
            logger.warning(f"Language-specific analyzer failed for {language_code}: {e}, falling back to generic analysis")

    # Fallback to generic analysis if no analyzer available or analyzer failed
    logger.info(f"Using generic grammar analysis for {language}")
    return _analyze_grammar_generic(sentence, word, language, groq_api_key)


def _analyze_grammar_generic(
    sentence: str,
    word: str,
    language: str,
    groq_api_key: str,
) -> Dict[str, Any]:
    """
    Generic grammar analysis fallback when no language-specific analyzer is available.
    """
    client = Groq(api_key=groq_api_key)

    # Color mapping for different POS categories
    color_map = {
        "noun": "#FF6B6B",        # Red - things/objects
        "verb": "#4ECDC4",        # Teal - actions
        "adjective": "#45B7D1",   # Blue - descriptions
        "adverb": "#96CEB4",      # Green - how/when/where
        "pronoun": "#FFEAA7",     # Yellow - replacements
        "preposition": "#DDA0DD", # Plum - relationships
        "conjunction": "#98D8C8", # Mint - connections
        "article": "#F7DC6F",     # Light yellow - determiners
        "interjection": "#FF9999", # Light red - exclamations
        "other": "#CCCCCC"        # Gray - other parts
    }

    prompt = f"""You are a linguistics expert specializing in {language} grammar analysis for language learners.

TASK: Analyze this {language} sentence and provide grammatical coloring information.

SENTENCE: "{sentence}"
TARGET WORD: "{word}"

INSTRUCTIONS:
1. Break down the sentence into individual words/tokens
2. For each word, identify its part of speech (POS) category
3. Assign an appropriate color based on POS
4. Provide a brief explanation for each word's grammatical role

COLOR CATEGORIES (use these exact names):
- noun (red): people, places, things, ideas
- verb (teal): actions, states, occurrences
- adjective (blue): descriptions of nouns
- adverb (green): modify verbs, adjectives, other adverbs
- pronoun (yellow): replace nouns (he, she, it, they, etc.)
- preposition (plum): show relationships (in, on, at, with, etc.)
- conjunction (mint): connect clauses (and, but, or, because, etc.)
- article (light yellow): determiners (the, a, an)
- interjection (light red): exclamations (oh, wow, hey)
- other (gray): numbers, punctuation, unclassified words

OUTPUT FORMAT: Return ONLY a valid JSON object with this exact structure:
{{
  "colored_sentence": "<span style='color: #COLOR1'>word1</span> <span style='color: #COLOR2'>word2</span> ...",
  "word_explanations": [
    ["word1", "pos_category", "#COLOR1", "brief explanation of grammatical role"],
    ["word2", "pos_category", "#COLOR2", "brief explanation of grammatical role"],
    ...
  ],
  "grammar_summary": "Brief 1-2 sentence summary of the sentence's grammatical structure"
}}

IMPORTANT:
- Use the exact color hex codes from the categories above
- colored_sentence must be valid HTML with inline styles
- Each word explanation should be educational and helpful for learners
- Maintain original sentence structure and punctuation
- Target word should be clearly identified in explanations
- Return ONLY the JSON object, no markdown or extra text"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,  # Low temperature for consistency
            max_tokens=1500,
        )

        response_text = response.choices[0].message.content.strip()

        # Extract JSON if wrapped in markdown - be more robust
        if "```json" in response_text:
            json_part = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_part = response_text.split("```")[1].split("```")[0].strip()
        else:
            # Try to find JSON object directly
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_part = response_text[start_idx:end_idx+1]
            else:
                json_part = response_text

        # Clean up any trailing content after JSON
        json_part = json_part.strip()
        if json_part.endswith('}'):
            # Find the last complete JSON object
            brace_count = 0
            last_valid_pos = -1
            for i, char in enumerate(json_part):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        last_valid_pos = i
            if last_valid_pos != -1:
                json_part = json_part[:last_valid_pos+1]

        # Try to parse JSON, with fallback attempts
        try:
            result = json.loads(json_part)
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parse failed: {e}, attempting cleanup...")
            # Try to clean up common issues
            json_part = json_part.replace('\n', ' ').replace('\r', ' ')
            json_part = ' '.join(json_part.split())  # normalize whitespace
            try:
                result = json.loads(json_part)
            except json.JSONDecodeError:
                # Last resort: try to extract just the core content
                logger.error(f"Failed to parse grammar analysis JSON after cleanup, using fallback. Raw response: {response_text[:200]}...")
                raise

        # Validate required fields
        if not all(key in result for key in ["colored_sentence", "word_explanations", "grammar_summary"]):
            raise ValueError("Missing required fields in grammar analysis response")

        # --- API USAGE TRACKING ---
        try:
            import streamlit as st
            if "groq_api_calls" not in st.session_state:
                st.session_state.groq_api_calls = 0
            if "groq_tokens_used" not in st.session_state:
                st.session_state.groq_tokens_used = 0
            st.session_state.groq_api_calls += 1
            # Estimate tokens used (prompt + response)
            st.session_state.groq_tokens_used += 150  # rough estimate for grammar analysis
        except Exception:
            pass
        # -------------------------

        logger.info(f"✓ Generic grammar analysis completed for sentence: {sentence[:50]}...")
        
        # Rate limiting: wait 5 seconds between API calls to respect per-minute limits
        time.sleep(5)
        
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Grammar analysis JSON parse error: {e}")
        # Return fallback
        return {
            "colored_sentence": sentence,
            "word_explanations": [],
            "grammar_summary": "Grammar analysis unavailable"
        }
    except Exception as e:
        logger.error(f"Grammar analysis error: {e}")
        return {
            "colored_sentence": sentence,
            "word_explanations": [],
            "grammar_summary": "Grammar analysis unavailable"
        }


def _batch_analyze_grammar_and_color(
    sentences: List[str],
    word: str,
    language: str,
    groq_api_key: str = None,
    complexity_level: str = "beginner",
    native_language: str = "English",
) -> List[Dict[str, Any]]:
    """
    PASS 3 (Batched): Analyze grammar and assign colors for MULTIPLE sentences in ONE API call.
    Much more efficient than individual calls - saves API quota and reduces latency.

    NOW INTEGRATED: Uses language-specific analyzers when available for authentic grammar analysis.

    Args:
        sentences: List of sentences to analyze
        word: Target word being learned
        language: Language name (e.g., "Spanish", "Hindi")
        groq_api_key: Groq API key
        complexity_level: Complexity level ('beginner', 'intermediate', 'advanced')
        native_language: User's native language for explanations (default: "English")

    Returns:
        List of dicts, each with keys:
        - colored_sentence: HTML with color-coded words
        - word_explanations: List of [word, pos, color, explanation] tuples
        - grammar_summary: Brief grammar explanation
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")

    if not sentences:
        return []

    client = Groq(api_key=groq_api_key)

    # Get language code for analyzer registry
    language_code = LANGUAGE_NAME_TO_CODE.get(language)
    if not language_code:
        logger.warning(f"No language code mapping found for '{language}', falling back to generic analysis")
        language_code = None

    # Try to get language-specific analyzer
    analyzer = None
    if language_code:
        analyzer = get_analyzer(language_code)

    # Build numbered sentence list for prompt
    sentences_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])

    if analyzer:
        # ✅ LANGUAGE-SPECIFIC ANALYZER INTEGRATION WITH 8-SENTENCE BATCHING (Phase 5.6)
        logger.info(f"Using {language_code} analyzer for 8-sentence batch grammar analysis of {len(sentences)} sentences")

        # PHASE 5.6: 8-Sentence Batch Processing for Pass 3
        # Group sentences into batches of 8 to reduce API calls by 87%
        # Each batch of 8 sentences = 1 API call instead of 8 individual calls
        BATCH_SIZE = 8
        processed_results = []

        # Process sentences in batches of 8
        for batch_start in range(0, len(sentences), BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, len(sentences))
            batch_sentences = sentences[batch_start:batch_end]
            batch_indices = list(range(batch_start, batch_end))

            logger.info(f"Processing batch {batch_start//BATCH_SIZE + 1}: sentences {batch_start+1}-{batch_end} of {len(sentences)}")

            try:
                # Create batch prompt for 8 sentences
                batch_prompt = _create_8sentence_batch_prompt(
                    analyzer=analyzer,
                    sentences=batch_sentences,
                    word=word,
                    complexity_level=complexity_level,
                    language_code=language_code,
                    native_language=native_language
                )

                # Single API call for the entire batch of 8 sentences
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": batch_prompt}],
                    temperature=0.3,
                    max_tokens=2000,  # Increased for batch processing
                )

                response_text = response.choices[0].message.content.strip()
                logger.info(f"Batch API response received for sentences {batch_start+1}-{batch_end}")

                # Parse batch response and process each sentence in the batch
                batch_results = _parse_8sentence_batch_response(
                    response_text=response_text,
                    batch_sentences=batch_sentences,
                    analyzer=analyzer,
                    complexity_level=complexity_level,
                    language_code=language_code
                )

                # Add batch results to processed results
                processed_results.extend(batch_results)

                # Rate limiting between batches (not individual sentences)
                if batch_end < len(sentences):  # Don't delay after last batch
                    time.sleep(5)  # 5 second delay between batches

            except Exception as e:
                logger.error(f"Batch processing failed for sentences {batch_start+1}-{batch_end}: {e}")
                # Fallback: Process sentences individually in this batch
                logger.info(f"Falling back to individual processing for failed batch")

                for i, sentence in enumerate(batch_sentences):
                    try:
                        # Individual processing as fallback
                        prompt = analyzer.get_grammar_prompt(complexity_level, sentence, word)

                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.3,
                            max_tokens=2000,
                        )

                        response_text = response.choices[0].message.content.strip()
                        parsed_data = analyzer.parse_grammar_response(response_text, complexity_level, sentence)
                        colored_sentence = analyzer._generate_html_output(parsed_data, sentence, complexity_level)

                        # Convert to word_explanations format
                        if "word_explanations" in parsed_data and parsed_data["word_explanations"]:
                            word_explanations = parsed_data["word_explanations"]
                        else:
                            word_explanations = _convert_analyzer_output_to_explanations(parsed_data, language)

                        grammar_summary = parsed_data.get('explanations', {}).get('sentence_structure',
                            f"This sentence uses {language_code} grammatical structures appropriate for {complexity_level} learners.")

                        processed_results.append({
                            "colored_sentence": colored_sentence,
                            "word_explanations": word_explanations,
                            "grammar_summary": grammar_summary,
                        })

                        # Rate limiting between individual fallback calls
                        if i < len(batch_sentences) - 1:
                            time.sleep(5)

                    except Exception as inner_e:
                        logger.error(f"Individual fallback failed for sentence {batch_start + i + 1}: {inner_e}")
                        processed_results.append({
                            "colored_sentence": sentence,
                            "word_explanations": [],
                            "grammar_summary": f"Analysis failed for {language_code} sentence",
                        })

        return processed_results

    else:
        # Fallback to generic batch analysis
        logger.info(f"Using generic batch grammar analysis for {language} ({len(sentences)} sentences)")

        prompt = f"""Analyze the grammar of these {language} sentences and provide color-coded HTML output.

Sentences:
{sentences_text}

For EACH sentence, return analysis in this exact JSON format:

[
  {{
    "sentence_index": 1,
    "colored_sentence": "<span style='color: #FF6B6B'>Subject</span> <span style='color: #4ECDC4'>verb</span> <span style='color: #45B7D1'>object</span>",
    "word_explanations": [
      ["word1", "noun", "#FF6B6B", "explanation in {native_language}"],
      ["word2", "verb", "#4ECDC4", "explanation in {native_language}"]
    ],
    "grammar_summary": "Brief explanation of sentence grammar structure in {native_language}"
  }},
  ...
]

Color codes to use:
- #FF6B6B: nouns (red)
- #4ECDC4: verbs (teal)
- #45B7D1: adjectives/adverbs (blue)
- #96CEB4: prepositions/conjunctions (green)
- #FFEAA7: pronouns/articles (yellow)
- #CCCCCC: other (gray)

Provide explanations in {native_language}. Return ONLY the JSON array, no additional text."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Consistent analysis
            max_tokens=3000,  # Enough for detailed analysis of multiple sentences
        )

        response_text = response.choices[0].message.content.strip()
        logger.info(f"PASS 3 raw response: {response_text[:500]}...")  # Log first 500 chars

        # Extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        results = json.loads(response_text)

        # Validate structure
        if not isinstance(results, list):
            logger.error("PASS 3 batch: Expected JSON array")
            raise ValueError("Invalid response format")

        # Process results and ensure we have the right number
        processed_results = []
        for i, result in enumerate(results[:len(sentences)]):
            if isinstance(result, dict):
                processed_results.append({
                    "colored_sentence": result.get("colored_sentence", sentences[i]),
                    "word_explanations": result.get("word_explanations", []),
                    "grammar_summary": result.get("grammar_summary", ""),
                })
            else:
                # Fallback for malformed result
                processed_results.append({
                    "colored_sentence": sentences[i],
                    "word_explanations": [],
                    "grammar_summary": "Analysis failed",
                })

        # Ensure we have results for all sentences
        while len(processed_results) < len(sentences):
            processed_results.append({
                "colored_sentence": sentences[len(processed_results)],
                "word_explanations": [],
                "grammar_summary": "Analysis failed",
            })

        # --- API USAGE TRACKING ---
        try:
            import streamlit as st
            if "groq_api_calls" not in st.session_state:
                st.session_state.groq_api_calls = 0
            if "groq_tokens_used" not in st.session_state:
                st.session_state.groq_tokens_used = 0
            st.session_state.groq_api_calls += 1
            # Estimate tokens used for batch analysis (more efficient than individual calls)
            estimated_tokens = len(sentences) * 200  # Rough estimate per sentence
            st.session_state.groq_tokens_used += estimated_tokens
        except Exception:
            pass
        # -------------------------

        logger.info(f"✓ Batch grammar analysis completed for {len(sentences)} sentences")
        
        # Rate limiting: wait 5 seconds between API calls to respect per-minute limits
        time.sleep(5)
        
        return processed_results

    except Exception as e:
        logger.error(f"Batch grammar analysis failed: {e}")
        # Return fallback results for all sentences
        return [{
            "colored_sentence": sentence,
            "word_explanations": [],
            "grammar_summary": "Grammar analysis unavailable"
        } for sentence in sentences]


def _convert_analyzer_output_to_explanations(grammar_result: Dict[str, Any], language: str) -> List[List[Any]]:
    """
    Convert analyzer output to word_explanations format [word, pos, color, explanation].
    Handles both traditional word-based and new character-based analysis formats.
    """
    explanations = []

    # Check if this is character-based analysis (Chinese analyzer)
    if 'characters' in grammar_result:
        # Character-based analysis (Chinese)
        characters = grammar_result.get('characters', [])
        word_combinations = grammar_result.get('word_combinations', [])

        # Add individual character explanations
        for char_data in characters:
            char = char_data.get('character', '')
            meaning = char_data.get('individual_meaning', '')
            role = char_data.get('grammatical_role', '')
            pronunciation = char_data.get('pronunciation', '')

            if char:
                # Map grammatical role to color category
                color_category = _map_grammatical_role_to_color_category(role)
                color = _get_color_for_category(color_category, language)

                explanation = f"{meaning}"
                if pronunciation and pronunciation != 'unknown':
                    explanation += f" ({pronunciation})"
                if role:
                    explanation += f" - {role}"

                explanations.append([char, role, color, explanation])

        # Add word combination explanations
        for combo_data in word_combinations:
            word = combo_data.get('word', '')
            meaning = combo_data.get('combined_meaning', '')
            structure = combo_data.get('grammatical_structure', '')

            if word and len(word) > 1:  # Only for actual combinations
                color_category = _map_grammatical_role_to_color_category(structure)
                color = _get_color_for_category(color_category, language)

                explanation = f"{meaning} - {structure}"
                explanations.append([word, structure, color, explanation])

    elif 'elements' in grammar_result:
        # New analyzer format with elements and explanations
        elements = grammar_result.get('elements', {})
        element_explanations = grammar_result.get('explanations', {})

        # Process each grammatical element category
        for element_type, word_list in elements.items():
            if element_type == 'word_combinations':
                # Handle word combinations specially
                for combo_data in word_list:
                    word = combo_data.get('word', '')
                    meaning = combo_data.get('combined_meaning', '')
                    structure = combo_data.get('grammatical_structure', '')

                    if word:
                        color_category = _map_grammatical_role_to_color_category(element_type)
                        color = _get_color_for_category(color_category, language)

                        explanation = f"{meaning}"
                        if structure:
                            explanation += f" - {structure}"

                        explanations.append([word, element_type, color, explanation])
            else:
                # Handle individual words
                for word_data in word_list:
                    word = word_data.get('word', '')
                    meaning = word_data.get('individual_meaning', '')
                    pronunciation = word_data.get('pronunciation', '')
                    role = word_data.get('grammatical_role', element_type)

                    if word:
                        color_category = _map_grammatical_role_to_color_category(role)
                        color = _get_color_for_category(color_category, language)

                        explanation = f"{meaning}"
                        if pronunciation and pronunciation != 'unknown':
                            explanation += f" ({pronunciation})"
                        if role and role != element_type:
                            explanation += f" - {role}"

                        explanations.append([word, role, color, explanation])

        # If no elements but we have explanations, add a general explanation
        if not explanations and element_explanations:
            for exp_type, exp_text in element_explanations.items():
                color = _get_color_for_category(exp_type, language)
                explanations.append(['', exp_type, color, exp_text])

    else:
        # Traditional word-based analysis
        word_explanations = grammar_result.get('word_explanations', [])
        explanations.extend(word_explanations)


# PHASE 5.6: 8-Sentence Batch Processing Helper Functions

def _create_8sentence_batch_prompt(
    analyzer,
    sentences: List[str],
    word: str,
    complexity_level: str,
    language_code: str,
    native_language: str = "English"
) -> str:
    """
    Create a batch prompt for analyzing 8 sentences together in one API call.
    This reduces API calls by 87% compared to individual sentence processing.
    """
    # Get the base prompt structure from the analyzer
    base_prompt = analyzer.get_grammar_prompt(complexity_level, sentences[0], word)

    # Extract the core analysis instructions from the base prompt
    # Remove sentence-specific parts and adapt for batch processing
    batch_instructions = f"""
Analyze ALL {len(sentences)} sentences below as a batch. For each sentence, provide complete grammatical analysis including word-by-word breakdown, grammatical roles, and color coding.

Target word: "{word}"
Language: {language_code}
Complexity level: {complexity_level}
Analysis should be in {native_language}

Sentences to analyze:
"""

    # Add numbered sentences
    for i, sentence in enumerate(sentences, 1):
        batch_instructions += f"{i}. {sentence}\n"

    # Add batch output format requirements
    batch_instructions += f"""

Return your analysis in this exact JSON format:
{{
  "batch_analysis": [
    {{
      "sentence_index": 1,
      "sentence": "{sentences[0] if sentences else ''}",
      "grammatical_analysis": {{
        "words": [
          {{
            "word": "example",
            "grammatical_role": "noun",
            "category": "noun",
            "explanation": "Explanation in {native_language}"
          }}
        ],
        "sentence_structure": "Brief grammatical summary in {native_language}",
        "complexity_notes": "Notes about {complexity_level} level structures used"
      }}
    }},
    {{
      "sentence_index": 2,
      "sentence": "{sentences[1] if len(sentences) > 1 else ''}",
      "grammatical_analysis": {{
        "words": [
          {{
            "word": "example",
            "grammatical_role": "verb",
            "category": "verb",
            "explanation": "Explanation in {native_language}"
          }}
        ],
        "sentence_structure": "Brief grammatical summary in {native_language}",
        "complexity_notes": "Notes about {complexity_level} level structures used"
      }}
    }}
  ]
}}

IMPORTANT:
- Analyze ALL {len(sentences)} sentences in this single response
- Each sentence must have complete word-by-word grammatical analysis
- Use language-specific grammatical categories appropriate for {language_code}
- Provide explanations in {native_language}
- Return ONLY the JSON object, no additional text or markdown formatting
"""

    return batch_instructions


def _parse_8sentence_batch_response(
    response_text: str,
    batch_sentences: List[str],
    analyzer,
    complexity_level: str,
    language_code: str
) -> List[Dict[str, Any]]:
    """
    Parse the batch response from the 8-sentence analysis and convert to individual sentence results.
    Includes automatic fallback to individual processing if batch parsing fails.
    """
    try:
        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        batch_data = json.loads(response_text)

        if not isinstance(batch_data, dict) or "batch_analysis" not in batch_data:
            raise ValueError("Invalid batch response format")

        batch_results = batch_data["batch_analysis"]

        if not isinstance(batch_results, list) or len(batch_results) != len(batch_sentences):
            raise ValueError(f"Expected {len(batch_sentences)} results, got {len(batch_results) if isinstance(batch_results, list) else 'non-list'}")

        processed_results = []

        for i, sentence_result in enumerate(batch_results):
            if not isinstance(sentence_result, dict):
                raise ValueError(f"Invalid sentence result format at index {i}")

            sentence_index = sentence_result.get("sentence_index", i + 1)
            grammatical_analysis = sentence_result.get("grammatical_analysis", {})

            # Convert batch format to analyzer-compatible format
            parsed_data = {
                "words": grammatical_analysis.get("words", []),
                "explanations": {
                    "sentence_structure": grammatical_analysis.get("sentence_structure", ""),
                    "complexity_notes": grammatical_analysis.get("complexity_notes", "")
                }
            }

            # Generate HTML output using analyzer
            sentence = batch_sentences[i]
            colored_sentence = analyzer._generate_html_output(parsed_data, sentence, complexity_level)

            # Convert to word_explanations format
            if "word_explanations" in parsed_data and parsed_data["word_explanations"]:
                word_explanations = parsed_data["word_explanations"]
            else:
                word_explanations = _convert_analyzer_output_to_explanations(parsed_data, f"{language_code} ({sentence_index})")

            # Create grammar summary
            grammar_summary = grammatical_analysis.get("sentence_structure",
                f"This sentence uses {language_code} grammatical structures appropriate for {complexity_level} learners.")

            processed_results.append({
                "colored_sentence": colored_sentence,
                "word_explanations": word_explanations,
                "grammar_summary": grammar_summary,
            })

        logger.info(f"Successfully parsed batch response for {len(processed_results)} sentences")
        return processed_results

    except Exception as e:
        logger.error(f"Failed to parse batch response: {e}")
        logger.info("Batch parsing failed, individual processing will be used as fallback")
        raise  # Re-raise to trigger fallback in calling function

    return explanations


def _map_grammatical_role_to_color_category(role: str) -> str:
    """Map grammatical role to color category"""
    role_lower = role.lower()

    if any(kw in role_lower for kw in ['pronoun', 'demonstrative']):
        return 'pronouns'
    elif any(kw in role_lower for kw in ['verb', 'linking', 'action']):
        return 'verbs'
    elif any(kw in role_lower for kw in ['particle', 'marker']):
        return 'particles'
    elif any(kw in role_lower for kw in ['noun', 'object', 'subject']):
        return 'nouns'
    elif any(kw in role_lower for kw in ['adjective', 'description']):
        return 'adjectives'
    elif any(kw in role_lower for kw in ['adverb', 'manner']):
        return 'adverbs'
    else:
        return 'other'


def _get_color_for_category(category: str, language: str) -> str:
    """Get color for grammatical category based on language"""
    # Use the analyzer's color scheme if available
    analyzer = get_analyzer(LANGUAGE_NAME_TO_CODE.get(language))
    if analyzer:
        color_scheme = analyzer.get_color_scheme('beginner')  # Default to beginner
        return color_scheme.get(category, '#CCCCCC')

    # Fallback colors
    fallback_colors = {
        'pronouns': '#FF4444',
        'verbs': '#44FF44',
        'particles': '#4444FF',
        'nouns': '#FFAA00',
        'adjectives': '#FF44FF',
        'adverbs': '#44FFFF',
        'other': '#888888'
    }
    return fallback_colors.get(category, '#CCCCCC')
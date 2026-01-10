# Word Data Fetcher Module
# Fetches enriched word data from Wiktionary API with Google Translate fallback

import requests
import logging
import time
import re
from typing import Dict, Optional, Any, List
from translate import Translator
from bs4 import BeautifulSoup
from circuit_breaker import WIKTIONARY_BREAKER, GOOGLE_TRANSLATE_BREAKER, call_with_circuit_breaker, CircuitBreakerOpenException
from persistent_cache import WIKTIONARY_CACHE, TRANSLATION_CACHE, get_cached_response

logger = logging.getLogger(__name__)

# ============================================================================
# WIKTIONARY API FUNCTIONS
# ============================================================================

def parse_hindi_wiktionary_html(word: str) -> List[Dict[str, Any]]:
    """
    Parse Hindi Wiktionary HTML page to extract comprehensive definitions.

    Args:
        word: The word to look up

    Returns:
        List of definition dictionaries with part_of_speech and definition
    """
    def _fetch_html():
        url = f"https://hi.wiktionary.org/wiki/{word}"
        headers = {
            'User-Agent': 'LanguageLearningApp/1.0 (https://github.com/your-repo)'
        }

        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        definitions = []

        # Find the main content area
        content = soup.find('div', {'id': 'mw-content-text'})
        if not content:
            return definitions

        # Look for definition paragraphs (Hindi Wiktionary uses paragraphs for definitions)
        paragraphs = content.find_all('p')

        for para in paragraphs:
            text = para.get_text().strip()

            # Clean up the text
            # Remove reference markers like [1], [2], etc.
            text = re.sub(r'\[\d+\]', '', text)
            # Remove extra whitespace
            text = ' '.join(text.split())

            # Skip very short paragraphs or those that are just navigation/symbols
            if len(text) > 10 and not re.match(r'^[\d\s\.\-\(\)\[\]]+$', text):
                # Try to determine part of speech from the text
                pos = 'unknown'

                # Check for part of speech indicators in the text
                if 'संज्ञा' in text or 'संज्ञा' in text:
                    pos = 'Noun'
                elif 'क्रिया' in text:
                    pos = 'Verb'
                elif 'विशेषण' in text:
                    pos = 'Adjective'
                elif 'अव्यय' in text or 'अव्य॰' in text:
                    pos = 'Adverb'
                elif 'सर्वनाम' in text:
                    pos = 'Pronoun'
                elif 'पूर्वसर्ग' in text:
                    pos = 'Preposition'
                elif 'उपसर्ग' in text:
                    pos = 'Prefix'

                # Extract the main definition text (remove the part-of-speech prefix if present)
                definition_text = text
                # Remove common prefixes like "प्रति ^१ अव्य॰ [सं॰]", "प्रति ^२ संज्ञा स्त्री॰", etc.
                definition_text = re.sub(r'^प्रति\s*\^\d+\s*(?:अव्य॰|संज्ञा|स्त्री॰|क्रिया|विशेषण|सर्वनाम|पूर्वसर्ग|उपसर्ग)*\s*(?:\[[^\]]*\]\s*)?', '', definition_text)
                definition_text = re.sub(r'^\^\d+\s*(?:अव्य॰|संज्ञा|स्त्री॰|क्रिया|विशेषण|सर्वनाम|पूर्वसर्ग|उपसर्ग)*\s*(?:\[[^\]]*\]\s*)?', '', definition_text)
                # Also remove "प्रति" at the beginning if it's just repeating the word
                definition_text = re.sub(r'^प्रति\s+', '', definition_text)

                if definition_text and len(definition_text) > 5:
                    definitions.append({
                        'part_of_speech': pos,
                        'definition': definition_text.strip(),
                        'examples': []
                    })

        return definitions

    try:
        return call_with_circuit_breaker(WIKTIONARY_BREAKER, _fetch_html)
    except CircuitBreakerOpenException:
        logger.warning(f"Wiktionary HTML parsing circuit breaker open for word '{word}'")
        return []
    except Exception as e:
        logger.warning(f"Failed to parse Hindi Wiktionary HTML for word '{word}': {e}")
        return []


def fetch_wiktionary_data(word: str, language: str = "Hindi") -> Dict[str, Any]:
    """
    Fetch comprehensive word data from Wiktionary API.

    Args:
        word: The word to look up
        language: Language name (e.g., "Hindi", "Spanish")

    Returns:
        Dict with comprehensive word data including all definitions
    """
    try:
        # Initialize definitions list
        all_definitions = []

        # Map language names to Wiktionary language codes
        lang_codes = {
            "Hindi": "hi",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Chinese": "zh",
            "Japanese": "ja",
            "Korean": "ko",
            "Arabic": "ar",
            "Russian": "ru",
            "Portuguese": "pt"
        }

        lang_code = lang_codes.get(language, "en")

        # For Hindi words, try HTML parsing first to get comprehensive definitions
        if language == "Hindi":
            logger.info(f"Trying HTML parsing first for Hindi word '{word}'")
            html_definitions = parse_hindi_wiktionary_html(word)
            if html_definitions:
                all_definitions = html_definitions
                logger.info(f"HTML parsing found {len(html_definitions)} definitions for '{word}'")

        # If HTML parsing didn't work or not Hindi, try REST API
        if not all_definitions:
            # Try the language-specific page first
            url = f"https://{lang_code}.wiktionary.org/api/rest_v1/page/definition/{word}"

            headers = {
                'User-Agent': 'LanguageLearningApp/1.0 (https://github.com/your-repo)'
            }

            response = requests.get(url, headers=headers, timeout=10)

            # If language-specific page fails, try English Wiktionary
            if response.status_code != 200:
                url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{word}"
                response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Extract ALL definitions for the target language
                if lang_code in data:
                    for definition in data[lang_code]:
                        if 'definitions' in definition:
                            part_of_speech = definition.get('partOfSpeech', 'unknown')
                            for def_item in definition['definitions']:
                                if 'definition' in def_item:
                                    # Clean HTML tags and extract plain text
                                    definition_text = def_item['definition']
                                    # Remove HTML tags
                                    import re
                                    clean_text = re.sub(r'<[^>]+>', '', definition_text)
                                    # Remove extra whitespace
                                    clean_text = ' '.join(clean_text.split())
                                    if clean_text and len(clean_text) > 1:  # Stricter filter to avoid noise
                                        all_definitions.append({
                                            'part_of_speech': part_of_speech,
                                            'definition': clean_text,
                                            'examples': def_item.get('examples', [])
                                        })

                # If no definitions found for target language, try English Wiktionary
                if not all_definitions and lang_code != "en":
                    if "en" in data:
                        for definition in data["en"]:
                            if 'definitions' in definition:
                                part_of_speech = definition.get('partOfSpeech', 'unknown')
                                for def_item in definition['definitions']:
                                    if 'definition' in def_item:
                                        # Look for definitions that mention the target language
                                        definition_text = def_item['definition']
                                        import re
                                        clean_text = re.sub(r'<[^>]+>', '', definition_text)
                                        clean_text = ' '.join(clean_text.split())
                                        if clean_text and len(clean_text) > 1:
                                            all_definitions.append({
                                                'part_of_speech': part_of_speech,
                                                'definition': clean_text,
                                                'examples': def_item.get('examples', [])
                                            })

        if all_definitions:
            # Take first 5 definitions for display, but keep all for processing
            primary_definitions = all_definitions[:5]

            return {
                "word": word,
                "all_definitions": all_definitions,  # Keep all for processing
                "definitions": primary_definitions,  # First 5 for display
                "meaning": "; ".join([d['definition'] for d in primary_definitions]),
                "usages": ["N/A"],  # Wiktionary doesn't provide structured usage data
                "variations": ["N/A"],  # Would need additional parsing
                "source": "Wiktionary",
                "definition_count": len(all_definitions)
            }

    except Exception as e:
        logger.warning(f"Wiktionary API failed for word '{word}': {e}")

    # Try HTML parsing as final fallback for Hindi words
    if language == "Hindi" and not all_definitions:
        logger.info(f"Trying HTML parsing fallback for Hindi word '{word}'")
        html_definitions = parse_hindi_wiktionary_html(word)
        if html_definitions:
            all_definitions = html_definitions
            logger.info(f"HTML parsing found {len(html_definitions)} definitions for '{word}'")

    if all_definitions:
        # Take first 5 definitions for display, but keep all for processing
        primary_definitions = all_definitions[:5]

        return {
            "word": word,
            "all_definitions": all_definitions,  # Keep all for processing
            "definitions": primary_definitions,  # First 5 for display
            "meaning": "; ".join([d['definition'] for d in primary_definitions]),
            "usages": ["N/A"],  # Wiktionary doesn't provide structured usage data
            "variations": ["N/A"],  # Would need additional parsing
            "source": "Wiktionary",
            "definition_count": len(all_definitions)
        }

    # Return N/A if all methods fail
    return {
        "word": word,
        "all_definitions": [],
        "definitions": [],
        "meaning": "N/A",
        "usages": ["N/A"],
        "variations": ["N/A"],
        "source": "N/A",
        "definition_count": 0
    }

# ============================================================================
# GOOGLE TRANSLATE FALLBACK
# ============================================================================

def fetch_google_translate_data(word: str, target_lang: str = "Hindi", source_lang: str = "en") -> Dict[str, Any]:
    """
    Fetch word data using Google Translate as verification.
    Translates the word from the target language to English for verification.

    Args:
        word: The word to translate (in target language)
        target_lang: Target language name
        source_lang: Source language code for translation (usually 'en' for English)

    Returns:
        Dict with translation data for verification
    """
    def _translate_word():
        # Map language names to Google Translate codes
        lang_codes = {
            "Hindi": "hi",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Chinese": "zh-CN",
            "Japanese": "ja",
            "Korean": "ko",
            "Arabic": "ar",
            "Russian": "ru",
            "Portuguese": "pt"
        }

        source_code = lang_codes.get(target_lang, "hi")

        # Use translate library for Google Translate
        # Translate FROM target language TO English for verification
        translator = Translator(from_lang=source_code, to_lang="en")

        # Try to translate the word
        translation = translator.translate(word)

        if translation:
            return {
                "translation": translation,
                "confidence": "high",  # Google Translate is generally reliable
                "source": "Google Translate",
                "verified": True
            }

    try:
        return call_with_circuit_breaker(GOOGLE_TRANSLATE_BREAKER, _translate_word) or {
            "translation": "N/A",
            "confidence": "none",
            "source": "Google Translate",
            "verified": False
        }
    except CircuitBreakerOpenException:
        logger.warning(f"Google Translate circuit breaker open for word '{word}'")
        return {
            "translation": "N/A",
            "confidence": "circuit_open",
            "source": "Google Translate",
            "verified": False
        }
    except Exception as e:
        logger.warning(f"Google Translate failed for word '{word}': {e}")
        return {
            "translation": "N/A",
            "confidence": "none",
            "source": "Google Translate",
            "verified": False
        }

def generate_english_meaning_from_definitions(word: str, definitions: List[Dict], language: str) -> str:
    """
    Generate a consolidated English meaning from multiple definitions using AI.

    Args:
        word: The target word
        definitions: List of definition dictionaries
        language: Source language

    Returns:
        English meaning string
    """
    if not definitions:
        return "Meaning unavailable"

    # Prepare enriched data format similar to sentence_generator
    enriched_data_parts = []
    for i, def_dict in enumerate(definitions[:3]):  # Use first 3 definitions
        pos = def_dict.get('part_of_speech', 'unknown')
        definition = def_dict.get('definition', '')
        enriched_data_parts.append(f"Definition {i+1}: {definition}")
        if pos != 'unknown':
            enriched_data_parts.append(f"Part of Speech: {pos}")

    enriched_data = f"{{Source: Wiktionary\nLanguage: {language}\n" + "\n".join(enriched_data_parts) + "\n}"

    # Use AI to generate English meaning (similar to sentence_generator approach)
    try:
        from sentence_generator import generate_sentences
        import os

        # Generate meaning using the same AI logic
        meaning, _ = generate_sentences(
            word=word,
            language=language,
            num_sentences=1,
            groq_api_key=os.getenv('GROQ_API_KEY'),
            enriched_word_data=enriched_data
        )

        # Clean up the meaning - remove any remaining Hindi text if present
        if meaning and not any(char in meaning for char in '???????????????????????????????????????????'):
            return meaning.strip()
        else:
            # Fallback: extract the most relevant definition and translate it
            primary_def = definitions[0].get('definition', '')
            return translate_meaning_to_english(primary_def, language)

    except Exception as e:
        logger.warning(f"AI meaning generation failed for '{word}': {e}")
        # Fallback to translation
        primary_def = definitions[0].get('definition', '')
        return translate_meaning_to_english(primary_def, language)

def combine_and_verify_definitions(word: str, wiktionary_data: Dict, google_data: Dict, language: str) -> Dict[str, Any]:
    """
    Intelligently combine and verify definitions from multiple sources.

    Args:
        word: The target word
        wiktionary_data: Data from Wiktionary API
        google_data: Data from Google Translate
        language: Language name

    Returns:
        Combined and verified word data
    """
    # Base result structure
    result = {
        "word": word,
        "sources": {
            "wiktionary": wiktionary_data,
            "google_translate": google_data
        },
        "all_definitions": [],
        "definitions": [],  # First 5 for display
        "primary_meaning": "N/A",
        "verification_status": "unverified",
        "meaning": "N/A",
        "usages": ["N/A"],
        "variations": ["N/A"],
        "source": "N/A",
        "definition_count": 0
    }

    # If Wiktionary failed completely, use Google Translate as fallback
    if wiktionary_data.get("definition_count", 0) == 0:
        if google_data.get("verified", False):
            result.update({
                "primary_meaning": google_data.get("translation", "N/A"),
                "meaning": google_data.get("translation", "N/A"),
                "source": "Google Translate (fallback)",
                "verification_status": "fallback_only"
            })
        return result

    # Get all Wiktionary definitions
    all_wiktionary_defs = wiktionary_data.get("all_definitions", [])

    # Verify definitions against Google Translate
    verified_definitions = []
    google_translation = google_data.get("translation", "").lower().strip()

    for i, w_def in enumerate(all_wiktionary_defs):
        definition_text = w_def.get("definition", "").lower().strip()
        part_of_speech = w_def.get("part_of_speech", "unknown")

        # Check if Google Translate matches this definition
        verification_score = 0
        if google_translation:
            # Simple verification: check if key terms match
            google_words = set(google_translation.split())
            def_words = set(definition_text.split())

            # Calculate overlap
            overlap = len(google_words.intersection(def_words))
            if overlap > 0:
                verification_score = min(overlap / len(google_words), 1.0)
            elif google_translation in definition_text or any(word in definition_text for word in google_words):
                verification_score = 0.5  # Partial match

        verified_def = w_def.copy()
        verified_def.update({
            "verification_score": verification_score,
            "verified_by_google": verification_score > 0.3,
            "index": i
        })
        verified_definitions.append(verified_def)

    # Sort by verification score (prioritize verified definitions)
    verified_definitions.sort(key=lambda x: x.get("verification_score", 0), reverse=True)

    # Select primary meaning (highest verified score, or first if none verified)
    if verified_definitions:
        primary_def = verified_definitions[0]
        result["primary_meaning"] = primary_def.get("definition", "N/A")

        # Set verification status
        verified_count = sum(1 for d in verified_definitions if d.get("verified_by_google", False))
        if verified_count > 0:
            result["verification_status"] = f"verified ({verified_count}/{len(verified_definitions)})"
        else:
            result["verification_status"] = "unverified"

    # Prepare display definitions (first 5)
    display_definitions = verified_definitions[:5]

    # Generate consolidated English meaning using AI (similar to sentence_generator approach)
    english_meaning = generate_english_meaning_from_definitions(word, display_definitions, language)

    # Update result
    result.update({
        "all_definitions": verified_definitions,
        "definitions": display_definitions,
        "meaning": english_meaning,
        "source": "Wiktionary",
        "definition_count": len(verified_definitions)
    })

    return result

# ============================================================================
# CARD DATA FUNCTION (English translations for Anki cards)
# ============================================================================

def get_word_data_for_cards(word: str, language: str = "Hindi") -> Dict[str, Any]:
    """
    Get structured word data with ENGLISH TRANSLATIONS for Anki card display.
    This returns clean, formatted English meanings for user-facing cards.

    Args:
        word: The word to enrich
        language: Language name (e.g., "Hindi", "Spanish")

    Returns:
        Structured dictionary with translated "meaning" field for cards
    """
    # Map language codes to full names
    lang_mapping = {
        "hi": "Hindi",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "ar": "Arabic",
        "ru": "Russian",
        "pt": "Portuguese"
    }

    # Convert language code to full name if needed
    if language.lower() in lang_mapping:
        language = lang_mapping[language.lower()]

    logger.info(f"Getting card data for '{word}' in {language}")

    # Fetch from both sources
    wiktionary_data = fetch_wiktionary_data(word, language)
    google_data = fetch_google_translate_data(word, language)

    # Combine and verify definitions (this creates the translated "meaning" field)
    combined_result = combine_and_verify_definitions(word, wiktionary_data, google_data, language)

    return combined_result

def get_word_data_for_cards_batch(words: List[str], language: str = "Hindi") -> Dict[str, Dict[str, Any]]:
    """
    Batch get structured word data with English translations for Anki cards.

    Args:
        words: List of words to get card data for
        language: Language name (e.g., "Hindi", "Spanish")

    Returns:
        Dictionary mapping word to structured card data
    """
    results = {}
    for word in words:
        try:
            results[word] = get_word_data_for_cards(word, language)
        except Exception as e:
            logger.error(f"Failed to get card data for '{word}': {e}")
            results[word] = {
                "word": word,
                "meaning": "Translation failed",
                "source": "Error",
                "definition_count": 0
            }
    return results

# ============================================================================
# MAIN ENRICHMENT FUNCTION
# ============================================================================

def enrich_word_data(word: str, language: str = "Hindi") -> str:
    """
    Enrich word data using multiple APIs and return a SINGLE CONSOLIDATED STRING
    that users can freely edit. This string contains all linguistic information
    in a flexible format that the AI can intelligently parse.

    Args:
        word: The word to enrich
        language: Language name (e.g., "Hindi", "Spanish") or code (e.g., "hi", "es")

    Returns:
        Single consolidated string with all enriched data for user editing
    """
    # Map language codes to full names
    lang_mapping = {
        "hi": "Hindi",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "ar": "Arabic",
        "ru": "Russian",
        "pt": "Portuguese"
    }

    # Convert language code to full name if needed
    if language.lower() in lang_mapping:
        language = lang_mapping[language.lower()]

    logger.info(f"Enriching word data for '{word}' in {language}")

    # Fetch from both sources
    wiktionary_data = fetch_wiktionary_data(word, language)
    google_data = fetch_google_translate_data(word, language)

    # Combine and verify definitions
    combined_result = combine_and_verify_definitions(word, wiktionary_data, google_data, language)

    # Convert structured data to SINGLE CONSOLIDATED STRING
    consolidated_string = _create_consolidated_meaning_string(combined_result, language)

    return consolidated_string

def enrich_word_data_batch(words: List[str], language: str = "Hindi", batch_size: int = 5) -> Dict[str, str]:
    """
    Batch enrich word data for multiple words with optimized processing.

    Processes words in batches to reduce API calls and improve performance.
    Uses parallel processing where possible and smarter caching.

    Args:
        words: List of words to enrich
        language: Language name (e.g., "Hindi", "Spanish") or code (e.g., "hi", "es")
        batch_size: Number of words to process in each batch

    Returns:
        Dictionary mapping word to consolidated enrichment string
    """
    if not words:
        return {}

    # Map language codes to full names
    lang_mapping = {
        "hi": "Hindi",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "ar": "Arabic",
        "ru": "Russian",
        "pt": "Portuguese"
    }

    # Convert language code to full name if needed
    if language.lower() in lang_mapping:
        language = lang_mapping[language.lower()]

    logger.info(f"Batch enriching {len(words)} words in {language}")

    results = {}

    # Process in batches to optimize API usage
    for i in range(0, len(words), batch_size):
        batch_words = words[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(words) + batch_size - 1)//batch_size}: {len(batch_words)} words")

        # Process batch - for now, process sequentially but with optimizations
        # Future: implement parallel processing for independent API calls
        for word in batch_words:
            try:
                consolidated_string = enrich_word_data(word, language)
                results[word] = consolidated_string
            except Exception as e:
                logger.error(f"Failed to enrich word '{word}': {e}")
                results[word] = f"{word} = [Error: {str(e)}]"

    logger.info(f"Batch enrichment completed: {len(results)}/{len(words)} words processed")
    return results

def translate_meaning_to_english(text: str, source_lang: str) -> str:
    """
    Translate a meaning from source language to English with quality metrics and caching.

    Args:
        text: Text to translate
        source_lang: Source language code (e.g., 'hi' for Hindi)

    Returns:
        Translated text or '{translation needed}' if failed
    """
    if not text or text.strip() == "":
        return "{translation needed}"

    # If already English, return as-is
    if source_lang.lower() in ['english', 'en']:
        return text.strip()

    cache_key = f"translate:{source_lang}:{hash(text) % 1000000}"

    def _perform_translation():
        # Clean up the text first - remove extra linguistic details
        clean_text = text.strip()

        # Remove common linguistic prefixes/suffixes that don't help with meaning
        clean_text = re.sub(r'^[^\w]*\^\d+\s*', '', clean_text)  # Remove ^1, ^2 prefixes
        clean_text = re.sub(r'\s*\[.*?\]\s*', ' ', clean_text)  # Remove [brackets]
        clean_text = re.sub(r'\s*\(.*?\)\s*', ' ', clean_text)  # Remove (parentheses)
        clean_text = re.sub(r'\s*—.*$', '', clean_text)  # Remove example citations
        clean_text = re.sub(r'\s*\..*$', '', clean_text)  # Stop at first period
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()  # Clean whitespace

        # Skip if too long or too short
        if len(clean_text) > 200 or len(clean_text) < 3:
            return "{translation needed}"

        # Map language names to codes for Google Translate
        lang_codes = {
            "Hindi": "hi",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Chinese": "zh-CN",
            "Japanese": "ja",
            "Korean": "ko",
            "Arabic": "ar",
            "Russian": "ru",
            "Portuguese": "pt"
        }

        source_code = lang_codes.get(source_lang, source_lang.lower())

        # Use Google Translate
        translator = Translator(from_lang=source_code, to_lang="en")
        translation = translator.translate(clean_text)

        if translation and len(translation.strip()) > 0:
            # Clean up and limit length
            clean_translation = translation.strip()
            # Remove extra punctuation and clean up
            clean_translation = re.sub(r'[^\w\s\-\(\)]', '', clean_translation)
            clean_translation = re.sub(r'\s+', ' ', clean_translation).strip()

            # Quality assessment
            quality_score = assess_translation_quality(clean_text, clean_translation, source_lang)

            # Reject low quality translations
            if quality_score < 0.3:
                logger.warning(f"Low quality translation rejected: '{clean_text}' -> '{clean_translation}' (score: {quality_score})")
                return "{translation needed}"

            if len(clean_translation) > 80:
                clean_translation = clean_translation[:77] + "..."

            # Return with quality metadata (stored in translation for now)
            return clean_translation
        else:
            return "{translation needed}"

    try:
        result = call_with_circuit_breaker(GOOGLE_TRANSLATE_BREAKER, lambda: get_cached_response(TRANSLATION_CACHE, cache_key, _perform_translation))
        return result if result else "{translation needed}"
    except CircuitBreakerOpenException:
        logger.warning(f"Translation circuit breaker open for text: '{text[:50]}...'")
        return "{translation needed}"
    except Exception as e:
        logger.warning(f"Translation failed for '{text[:50]}...': {e}")
        return "{translation needed}"

def assess_translation_quality(original_text: str, translated_text: str, source_lang: str) -> float:
    """
    Assess the quality of a translation based on various heuristics.

    Args:
        original_text: Original text in source language
        translated_text: Translated text in English
        source_lang: Source language

    Returns:
        Quality score between 0.0 and 1.0
    """
    if not translated_text or translated_text == "{translation needed}":
        return 0.0

    score = 0.5  # Base score

    # Length ratio check (translations shouldn't be radically different in length)
    orig_len = len(original_text.split())
    trans_len = len(translated_text.split())

    if orig_len > 0:
        ratio = trans_len / orig_len
        if 0.5 <= ratio <= 2.0:
            score += 0.2
        elif 0.3 <= ratio <= 3.0:
            score += 0.1

    # Check for placeholder text or obvious failures
    failure_indicators = [
        "translate", "translation", "error", "failed",
        original_text.lower(),  # If translation is same as original
        "n/a", "none", ""
    ]

    trans_lower = translated_text.lower().strip()
    if any(indicator in trans_lower for indicator in failure_indicators):
        score -= 0.3

    # Language-specific quality checks
    if source_lang == "Hindi":
        # Hindi translations should not contain Devanagari script if translating to English
        if any('\u0900' <= char <= '\u097F' for char in translated_text):
            score -= 0.2

    # Check for reasonable English structure
    if translated_text[0].isupper() and translated_text[-1] in '.!?':
        score += 0.1

    return max(0.0, min(1.0, score))

# ============================================================================
# CONSOLIDATED STRING CREATION
# ============================================================================

def _create_consolidated_meaning_string(data: Dict[str, Any], language: str) -> str:
    """
    Convert structured word data into a SINGLE CONSOLIDATED STRING
    containing RAW parsed data from API/HTML for AI interpretation,
    encapsulated in {} format. Each definition limited to 200 characters max.

    Args:
        data: Structured word data from combine_and_verify_definitions
        language: Language name

    Returns:
        Single consolidated string with raw data in {} encapsulation for AI
    """
    all_definitions = data.get("all_definitions", [])
    source = data.get("source", "Wiktionary")

    # Build raw context for AI interpretation
    context_parts = []

    # Add source attribution
    context_parts.append(f"Source: {source}")

    # Add language
    context_parts.append(f"Language: {language}")

    # Process raw definitions (no cleaning/translations for AI)
    if all_definitions:
        # Sort by verification score and relevance
        sorted_definitions = sorted(all_definitions,
                                  key=lambda x: (x.get("verification_score", 0),
                                               -len(x.get("definition", ""))),
                                  reverse=True)

        # Take top definitions with raw data, limited to 200 chars each
        for i, definition in enumerate(sorted_definitions[:4]):
            def_text = definition.get("definition", "").strip()
            part_of_speech = definition.get("part_of_speech", "unknown")
            examples = definition.get("examples", [])

            if def_text and len(def_text) > 0:
                # Limit to 200 characters max per definition
                if len(def_text) > 200:
                    def_text = def_text[:197] + "..."

                # Build raw entry for AI
                entry_parts = []
                entry_parts.append(f"Definition {i+1}: {def_text}")
                if part_of_speech != "unknown":
                    entry_parts.append(f"Part of Speech: {part_of_speech}")
                if examples:
                    # Limit examples too
                    limited_examples = []
                    for ex in examples[:2]:
                        if len(ex) > 100:
                            ex = ex[:97] + "..."
                        limited_examples.append(ex)
                    entry_parts.append(f"Examples: {'; '.join(limited_examples)}")

                context_parts.append(" | ".join(entry_parts))

    # Always include Google Translate data if available (not just as fallback)
    google_data = data.get("sources", {}).get("google_translate", {})
    google_translation = google_data.get("translation", "")
    if google_translation and google_translation != "N/A":
        # Limit to 200 characters max
        if len(google_translation) > 200:
            google_translation = google_translation[:197] + "..."
        context_parts.append(f"Google Translate: {google_translation}")
        context_parts.append("Source: Google Translate")

    # Join all context with newlines
    consolidated_string = "\n".join(context_parts)

    # Ensure we have something
    if not consolidated_string.strip():
        consolidated_string = "Source: Unknown\nLanguage: {language}\nBasic Translation: [definition needed]"

    # Encapsulate in {} for AI focus
    return f"{{{consolidated_string}}}"

def _clean_definition_text(text: str) -> str:
    """
    Clean up definition text to extract the core meaning.

    Args:
        text: Raw definition text

    Returns:
        Cleaned definition text or empty string if not usable
    """
    if not text or len(text.strip()) < 3:
        return ""

    clean_text = text.strip()

    # For Hindi and similar languages, try to extract core meanings
    # Remove linguistic annotations and examples
    clean_text = re.sub(r'^[^\w]*\^\d+\s*', '', clean_text, flags=re.UNICODE)  # Remove ^1, ^2 prefixes
    clean_text = re.sub(r'\s*\[.*?\]\s*', ' ', clean_text, flags=re.UNICODE)  # Remove [brackets]
    clean_text = re.sub(r'\s*\(.*?\)\s*', ' ', clean_text, flags=re.UNICODE)  # Remove (parentheses)
    clean_text = re.sub(r'\s*—.*$', '', clean_text, flags=re.UNICODE)  # Remove citations
    clean_text = re.sub(r'\s*\..*$', '', clean_text, flags=re.UNICODE)  # Stop at first period
    # Remove punctuation but keep Unicode letters and spaces
    clean_text = re.sub(r'[^\w\s\u0900-\u097F]', ' ', clean_text, flags=re.UNICODE)  # Keep Devanagari range
    clean_text = re.sub(r'\s+', ' ', clean_text, flags=re.UNICODE).strip()  # Clean whitespace

    # Special handling for noun definitions
    if 'संज्ञा' in clean_text:
        # Extract the noun that follows the grammatical markers
        # Pattern: संज्ञा [gender] [source] actual_noun
        words = clean_text.split()
        noun_candidates = []
        for word in words:
            # Skip grammatical markers and look for the actual noun
            if word in ['ए', 'संज्ञा', 'पुं॰', 'स्त्री॰', 'नपुं॰', 'पुं', 'स्त्री', 'नपुं', '१', '२', '३'] or '॰' in word or '[सं॰]' in word or '[हिं॰]' in word:
                continue
            # Take significant words that are likely the noun
            if len(word) > 1 and word not in ['।']:
                noun_candidates.append(word)
        if noun_candidates:
            clean_text = ' '.join(noun_candidates[:2])  # Take up to 2 words

    # Skip if too short or too long
    if len(clean_text) < 3 or len(clean_text) > 50:
        return ""

    return clean_text

def enrich_words_batch(words: list, language: str = "Hindi", delay: float = 0.5) -> list:
    """
    Enrich multiple words with rate limiting. Returns consolidated strings
    for each word that users can edit.

    Args:
        words: List of words to enrich
        language: Language name
        delay: Delay between API calls in seconds

    Returns:
        List of consolidated meaning strings (one per word)
    """
    results = []

    for word in words:
        result = enrich_word_data(word, language)
        results.append(result)

        # Rate limiting
        if delay > 0:
            time.sleep(delay)

    return results
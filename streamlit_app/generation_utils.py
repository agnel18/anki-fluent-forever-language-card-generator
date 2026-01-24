# Generation utilities module
# Extracted from core_functions.py for better separation of concerns

import logging
import pandas as pd
import re
import time
from typing import List, Dict
import google.generativeai as genai

# Import centralized configuration
from config import get_gemini_model

# Import language registry for consistent language handling
try:
    from language_registry import get_language_registry
except ImportError:
    # Fallback for testing environments
    from .language_registry import get_language_registry

logger = logging.getLogger(__name__)

# IPA validation constants
PINYIN_TONE_MARKS = 'āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ'

# ============================================================================
# IPA VALIDATION SYSTEM (Phase 1: IPA Strict Enforcement)
# ============================================================================

def validate_ipa_output(ipa_text: str, language: str = "zh") -> tuple[bool, str]:
    """
    Validates that the provided text contains only valid IPA symbols and no Pinyin romanization.

    Args:
        ipa_text: The text to validate
        language: Language code (default: "zh" for Chinese)

    Returns:
        tuple: (is_valid: bool, result_message: str)
    """
    if not ipa_text or not ipa_text.strip():
        return False, "Empty IPA text"

    # Clean the text for validation
    clean_text = ipa_text.strip()

    # Check if it's in IPA slashes /text/
    if clean_text.startswith('/') and clean_text.endswith('/'):
        ipa_content = clean_text[1:-1]
        return validate_ipa_slashed(ipa_content, language)

    # Check if it's in IPA brackets [text]
    if clean_text.startswith('[') and clean_text.endswith(']'):
        ipa_content = clean_text[1:-1]
        return validate_ipa_bracketed(ipa_content, language)

    # If not in brackets or slashes, check if it's valid IPA without brackets
    return validate_ipa_unbracketed(clean_text, language)


def validate_ipa_slashed(ipa_content: str, language: str) -> tuple[bool, str]:
    """Validate IPA content within slashes / /."""
    # Same validation as bracketed IPA
    pulmonic_consonants = 'pbtdʈɖcɟkɡgqɢʔɴŋɲɳnɱmʙrʀⱱɾɽɸβfvθðszʃʒʂʐçʝxɣχʁħʕhɦɬɮʋɹɻjɰlɭʎʟʤʧś'
    non_pulmonic = 'ʼʍwɥʜʢʡɕʑɺɧ'
    vowels = 'iyɨʉɯuɪʏʊeøɘəɵɤoɛœɜɞʌɔæɐaɶɑɒɚɝíéáóúãẽĩõũỹɒ̃āīūē'
    diacritics = '̴̴̵̶̷̸̡̢̥̬̤̰̼̝̞̟̠̣̤̥̦̩̪̫̬̭̮̯̰̱̲̳̹̺̻̼̊̽̾̿͡ʰ'
    tones_stress = 'ˈˌːˑʼʲʷʸˠˤ˞̴̵̶̷̸̙̘̗̖̝̞̟̠̜̹̜̹̪̺̻̼̩̯̰̪̫̬̭̮̯̰̱̲̳̹̺̻̼̚꜀꜁꜂꜃꜄꜅꜆꜇꜈꜉꜊꜋꜌꜍꜎꜏꜐꜑꜒꜓꜔꜕꜖ꜗꜘꜙꜚꜛꜜꜝꜞꜟ꜠꜡Ꜣꜣ˥˦˧˨˩̋̌̂᷄᷅᷆᷇᷈᷉'
    other_symbols = '.,;:!?\'"() '

    allowed_chars = pulmonic_consonants + non_pulmonic + vowels + diacritics + tones_stress + other_symbols

    # For Chinese languages, allow Pinyin tone marks as valid transliteration
    if language in ['zh', 'zh-tw']:
        allowed_chars += PINYIN_TONE_MARKS

    # Check for invalid characters
    invalid_chars = []
    for char in ipa_content:
        if char not in allowed_chars:
            invalid_chars.append(char)

    if invalid_chars:
        return False, f"Contains non-IPA characters: {''.join(set(invalid_chars))} in /{ipa_content}/"

    # Check for Pinyin patterns within IPA (shouldn't happen in valid IPA)
    # For Chinese languages, Pinyin with tone marks IS acceptable as transliteration
    if language in ['zh', 'zh-tw']:
        # Allow Pinyin tone marks for Chinese - this is appropriate for learners
        pass  # Don't reject Pinyin for Chinese
    elif any(char in ipa_content for char in PINYIN_TONE_MARKS):
        return False, f"Detected Pinyin tone marks in IPA: /{ipa_content}/"

    return True, ipa_content


def validate_ipa_bracketed(ipa_content: str, language: str) -> tuple[bool, str]:
    """Validate IPA content within brackets [ ]."""
    # Comprehensive IPA character set - includes all official IPA symbols
    pulmonic_consonants = 'pbtdʈɖcɟkɡgqɢʔɴŋɲɳnɱmʙrʀⱱɾɽɸβfvθðszʃʒʂʐçʝxɣχʁħʕhɦɬɮʋɹɻjɰlɭʎʟʤʧś'
    non_pulmonic = 'ʼʍwɥʜʢʡɕʑɺɧ'
    vowels = 'iyɨʉɯuɪʏʊeøɘəɵɤoɛœɜɞʌɔæɐaɶɑɒɚɝíéáóúãẽĩõũỹɒ̃āīūē'
    diacritics = '̴̴̵̶̷̸̡̢̥̬̤̰̼̝̞̟̠̣̤̥̦̩̪̫̬̭̮̯̰̱̲̳̹̺̻̼̊̽̾̿͡ʰ'
    tones_stress = 'ˈˌːˑʼʲʷʸˠˤ˞̴̵̶̷̸̙̘̗̖̝̞̟̠̜̹̜̹̪̺̻̼̩̯̰̪̫̬̭̮̯̰̱̲̳̹̺̻̼̚꜀꜁꜂꜃꜄꜅꜆꜇꜈꜉꜊꜋꜌꜍꜎꜏꜐꜑꜒꜓꜔꜕꜖ꜗꜘꜙꜚꜛꜜꜝꜞꜟ꜠꜡Ꜣꜣ˥˦˧˨˩̋̌̂᷄᷅᷆᷇᷈᷉'
    other_symbols = '.,;:!?\'"() '

    allowed_chars = pulmonic_consonants + non_pulmonic + vowels + diacritics + tones_stress + other_symbols

    # For Chinese languages, allow Pinyin tone marks as valid transliteration
    if language in ['zh', 'zh-tw']:
        allowed_chars += PINYIN_TONE_MARKS

    # Check for invalid characters
    invalid_chars = []
    for char in ipa_content:
        if char not in allowed_chars:
            invalid_chars.append(char)

    if invalid_chars:
        return False, f"Contains non-IPA characters: {''.join(set(invalid_chars))} in [{ipa_content}]"

    # Check for Pinyin patterns within IPA (shouldn't happen in valid IPA)
    # For Chinese languages, Pinyin with tone marks IS acceptable as transliteration
    if language in ['zh', 'zh-tw']:
        # Allow Pinyin tone marks for Chinese - this is appropriate for learners
        pass  # Don't reject Pinyin for Chinese
    elif any(char in ipa_content for char in PINYIN_TONE_MARKS):
        return False, f"Detected Pinyin tone marks in IPA: [{ipa_content}]"

    return True, ipa_content


def validate_ipa_unbracketed(text: str, language: str) -> tuple[bool, str]:
    """Validate IPA text that is not in brackets (likely romanization)."""
    # For unbracketed text, we expect either valid IPA symbols or it should be rejected as romanization

    # First check for Pinyin-specific patterns - be very specific to avoid false positives
    pinyin_patterns = [
        r'\b[a-z]+[1-5]\b',  # Pinyin with numbers (ma1, ni3, etc.) - word boundary required
        r'\b[A-Z][a-z]*[1-5]\b',  # Capitalized Pinyin with numbers
    ]

    # Check for specific Pinyin tone marks that are NOT IPA symbols
    # Pinyin uses macron (¯) and caron (ˇ) diacritics on vowels: āēīōūǖ and ǎěǐǒǔǚ
    has_pinyin_tones = any(char in text for char in PINYIN_TONE_MARKS)

    for pattern in pinyin_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False, f"Detected Pinyin romanization: {text}"

    # If it has Pinyin tone marks, reject it (only for non-Chinese languages)
    # For Chinese, Pinyin with tone marks IS acceptable romanization
    if language not in ['zh', 'zh-tw'] and has_pinyin_tones:
        return False, f"Detected Pinyin tone marks: {text}"

    # For Chinese and other logographic languages, reject plain ASCII words
    # But allow romanization for languages that commonly use it (like Hindi, Arabic, etc.)
    # For Chinese, Pinyin romanization is acceptable
    romanization_allowed_languages = ['hi', 'ar', 'fa', 'ur', 'bn', 'pa', 'gu', 'or', 'ta', 'te', 'kn', 'ml', 'si', 'zh', 'zh-tw']
    
    if language in ['ja', 'ko'] and language not in romanization_allowed_languages:
        # If it contains only ASCII letters and spaces, it's likely romanization/Pinyin
        if re.match(r'^[a-zA-Z\s]+$', text.strip()):
            return False, f"Detected romanization (plain ASCII text): {text}"
    
    # For languages that allow romanization, accept romanized text with common diacritics
    romanization_diacritics = 'āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜñḍṭṅṇṃśṣḥḷḻṛṝṁ'
    if language in romanization_allowed_languages:
        romanization_pattern = r'^[a-zA-Z\s\'' + romanization_diacritics + r'.,;:!?]+$'
        if re.match(romanization_pattern, text.strip()):
            return True, text

    # Check if it contains only valid IPA symbols (unbracketed IPA is also valid)
    pulmonic_consonants = 'pbtdʈɖcɟkɡgqɢʔɴŋɲɳnɱmʙrʀⱱɾɽɸβfvθðszʃʒʂʐçʝxɣχʁħʕhɦɬɮʋɹɻjɰlɭʎʟʤʧś'
    non_pulmonic = 'ʼʍwɥʜʢʡɕʑɺɧ'
    vowels = 'iyɨʉɯuɪʏʊeøɘəɵɤoɛœɜɞʌɔæɐaɶɑɒɚɝíéáóúãẽĩõũỹɒ̃āīūē'
    diacritics = '̴̴̵̶̷̸̡̢̥̬̤̰̼̝̞̟̠̣̤̥̦̩̪̫̬̭̮̯̰̱̲̳̹̺̻̼̊̽̾̿͡ʰ'
    tones_stress = 'ˈˌːˑʼʲʷʸˠˤ˞̴̵̶̷̸̙̘̗̖̝̞̟̠̜̹̜̹̪̺̻̼̩̯̰̪̫̬̭̮̯̰̱̲̳̹̺̻̼̚꜀꜁꜂꜃꜄꜅꜆꜇꜈꜉꜊꜋꜌꜍꜎꜏꜐꜑꜒꜓꜔꜕꜖ꜗꜘꜙꜚꜛꜜꜝꜞꜟ꜠꜡Ꜣꜣ˥˦˧˨˩̋̌̂᷄᷅᷆᷇᷈᷉'
    other_symbols = '.,;:!?\'"() '

    allowed_chars = pulmonic_consonants + non_pulmonic + vowels + diacritics + tones_stress + other_symbols

    # Check for invalid characters
    invalid_chars = []
    for char in text:
        if char not in allowed_chars:
            invalid_chars.append(char)

    if invalid_chars:
        # If it has invalid characters, check if it looks like romanization
        # But be careful not to reject valid IPA that happens to contain letter sequences
        if re.search(r'\b[a-z]{3,}\b', text, re.IGNORECASE) and not any(ipa_char in text for ipa_char in 'ɖʈɖcɟʔŋɲɳɱʙʀⱱɾɽɸβθðʃʒʂʐçʝxɣχʁħʕɦɬɮʋɹɻɰɭʎʟʼʍɥʜʢʡɕʑɺɧɨʉɯɪʏʊøɘɵɤɛœɜɞʌɔæɐɶɑɒɚɝˈˌːˑʼʲʷʸˠˤ˞̴̵̶̷̸̙̘̗̖̝̞̟̠̜̹̜̹̪̺̻̼̩̯̰̪̫̬̭̮̯̰̱̲̳̹̺̻̼̚꜀꜁꜂꜃꜄꜅꜆꜇꜈꜉꜊꜋꜌꜍꜎꜏꜐꜑꜒꜓꜔꜕꜖ꜗꜘꜙꜚꜛꜜꜝꜞꜟ꜠꜡Ꜣꜣ˥˦˧˨˩̋̌̂᷄᷅᷆᷇᷈᷉'):
            return False, f"Detected romanization (non-IPA): {text}"
        else:
            return False, f"Contains non-IPA characters: {''.join(set(invalid_chars))} in {text}"

    return True, text


def generate_ipa_hybrid(sentence: str, language: str, gemini_api_key: str) -> str:
    """
    Generate IPA transliteration with strict validation to ensure IPA-only output.

    Args:
        sentence: The sentence to transliterate
        language: Language code (e.g., 'zh', 'ja', 'ko') or full name
        gemini_api_key: Gemini API key

    Returns:
        Validated IPA transliteration string
    """
    if not gemini_api_key:
        logger.warning("No Gemini API key provided for IPA generation")
        return ""

    # Get language registry and normalize language input
    registry = get_language_registry()
    normalized_lang = registry.normalize_language_input(language)
    full_lang_name = registry.get_full_name(normalized_lang) or language

    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(get_gemini_model())

        # Enhanced prompt for IPA-only output using full language name
        # For some languages, romanization is more useful than strict IPA
        romanization_allowed = ['hi', 'ar', 'fa', 'ur', 'bn', 'pa', 'gu', 'or', 'ta', 'te', 'kn', 'ml', 'si']

        if normalized_lang in romanization_allowed:
            prompt = f"""Transliterate this {full_lang_name} sentence to romanized pronunciation using Latin letters.

Use standard romanization conventions for {full_lang_name}. Show pronunciation clearly with familiar letters.

Sentence: {sentence}

Return ONLY the romanized transliteration, no explanations or additional text."""
        else:
            prompt = f"""Transliterate this {full_lang_name} sentence to IPA (International Phonetic Alphabet) only.

IMPORTANT: Use ONLY official IPA symbols. Do NOT use:
- Pinyin romanization (no āáǎà, no ma1, no zh/ch/sh/r/z/c/s)
- Any non-IPA romanization systems
- Latin letters that aren't IPA symbols
- Any delimiters like / or [ ]

Sentence: {sentence}

Return ONLY the IPA transliteration, no explanations or additional text."""

        response = model.generate_content(prompt)

        ipa_result = response.text.strip()

        # Validate the IPA output using normalized language code
        is_valid, result = validate_ipa_output(ipa_result, normalized_lang)

        if is_valid:
            logger.info(f"Generated valid IPA: {result}")
            return result
        else:
            logger.warning(f"Invalid IPA generated: {result}")
            # Try one more time with stricter instructions
            if normalized_lang in romanization_allowed:
                fallback_prompt = f"""Convert to romanized pronunciation using Latin letters:

{sentence}

Romanization:"""
            else:
                fallback_prompt = f"""Convert to IPA only. NO Pinyin, NO romanization, NO delimiters like / or [ ], ONLY IPA symbols:

{sentence}

IPA:"""

            fallback_response = model.generate_content(fallback_prompt)

            fallback_ipa = fallback_response.text.strip()
            is_valid_fallback, fallback_result = validate_ipa_output(fallback_ipa, normalized_lang)

            if is_valid_fallback:
                logger.info(f"Fallback IPA successful: {fallback_result}")
                return fallback_result
            else:
                logger.error(f"Fallback IPA also invalid: {fallback_result}")
                return ""  # Return empty string to indicate failure

    except Exception as e:
        logger.error(f"IPA generation failed: {e}")
        return ""


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def estimate_api_costs(num_words: int, num_sentences: int = 10) -> dict:
    """
    Estimate API usage for cost calculator (Optimized 2-Pass Architecture).

    Token usage per word:
    - PASS 1 (raw generation): ~200 tokens
    - PASS 2 (batch validation + enrichment): ~200 tokens
    - Total: ~400 tokens per word

    With 100k free tokens:
    - ~250 words/month (10 sentences each = 2,500 sentences)

    Args:
        num_words: Number of words to process
        num_sentences: Sentences per word

    Returns:
        Dict with estimates
    """
    total_sentences = num_words * num_sentences
    avg_chars_per_sentence = 90

    return {
        "total_sentences": total_sentences,
        "total_images": total_sentences,
        "google_search_requests": total_sentences,  # One per sentence
        "gemini_tokens_est": int(num_words * 400),  # 2-pass architecture: ~400 tokens/word
        "google_tts_chars": int(total_sentences * avg_chars_per_sentence),
    }

def parse_csv_upload(file_content: bytes) -> list[dict]:
    """
    Parse uploaded CSV file.

    Args:
        file_content: CSV file bytes

    Returns:
        List of dicts with 'word' and 'meaning' keys
    """
    try:
        df = pd.read_csv(file_content)
        # Expect columns: word, meaning (flexible naming)
        cols = df.columns.str.lower()
        word_col = [c for c in cols if "word" in c][0] if any("word" in c for c in cols) else cols[0]
        meaning_col = [c for c in cols if "meaning" in c or "translation" in c][0] if any("meaning" in c or "translation" in c for c in cols) else cols[1] if len(cols) > 1 else "meaning"

        result = []
        for _, row in df.iterrows():
            result.append({
                "word": str(row[word_col]).strip(),
                "meaning": str(row[meaning_col]).strip(),
            })

        return result
    except Exception as e:
        logger.error(f"CSV parse error: {e}")
        return []


def generate_image_keywords(sentence: str, translation: str, target_word: str, gemini_api_key: str) -> str:
    """
    Generate AI-powered keywords for image search based on sentence content.

    Args:
        sentence: The sentence text
        translation: English translation
        target_word: The target word being learned
        gemini_api_key: Gemini API key

    Returns:
        Comma-separated keywords string
    """
    if not gemini_api_key:
        logger.warning("Gemini API key not available, using fallback keywords")
        return f"{target_word}, language, learning"

    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(get_gemini_model())
        response = model.generate_content(f"Generate exactly 3 diverse and specific keywords for an image that represents the sentence: '{sentence}' with translation: '{translation}'. The sentence is about the word '{target_word}'. Make the keywords unique and visual - avoid generic terms like 'language' or 'learning'. Focus on concrete objects, actions, or scenes. Return only a comma-separated list of 3 keywords, no explanations or formatting.")
        raw_response = response.text.strip()

        # Rate limiting: wait 5 seconds between API calls to respect per-minute limits
        time.sleep(5)
        
        # Extract just the keywords from the response
        # Remove any introductory text and formatting
        lines = raw_response.split('\n')
        keywords_list = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and explanatory text
            if not line or line.startswith(('Here are', 'These keywords', 'The keywords', 'Keywords:')):
                continue
            # Remove numbering like "1. " or "- "
            line = re.sub(r'^\d+\.\s*', '', line)
            line = re.sub(r'^-\s*', '', line)
            # Clean up the line
            line = line.strip()
            if line and not line.startswith(('These', 'The', 'Keywords')):
                keywords_list.append(line)
        
        # If we found numbered/listed keywords, join them
        if keywords_list:
            keywords = ', '.join(keywords_list[:3])  # Limit to 3 keywords
        else:
            # Fallback: try to extract comma-separated keywords
            keywords = re.sub(r'[^\w\s,]', '', raw_response)  # Remove special chars
            keywords = re.sub(r'\s+', ' ', keywords)  # Normalize spaces
            keywords = keywords.strip()
        
        # Ensure we have something useful
        if not keywords or len(keywords.split(',')) < 2:
            keywords = f"{target_word}, language, learning"
            
        return keywords
    except Exception as e:
        logger.error(f"Error generating image keywords: {e}")
        return f"{target_word}, language, learning"


def batch_generate_image_keywords(
    sentences_data: List[Dict[str, str]],
    gemini_api_key: str
) -> List[str]:
    """
    Generate AI-powered keywords for image search for MULTIPLE sentences in ONE API call.
    Much more efficient than individual calls - saves API quota and reduces latency.

    Args:
        sentences_data: List of dicts with keys 'sentence', 'english_translation', 'target_word'
        gemini_api_key: Gemini API key

    Returns:
        List of comma-separated keywords strings, one per sentence
    """
    if not gemini_api_key:
        logger.warning("Gemini API key not available, using fallback keywords")
        return [f"{data['target_word']}, language, learning" for data in sentences_data]

    if not sentences_data:
        return []

    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(get_gemini_model())

        # Build a single prompt for all sentences
        prompt_parts = []
        for i, data in enumerate(sentences_data, 1):
            prompt_parts.append(f"Sentence {i}: '{data['sentence']}' (translation: '{data['english_translation']}', target word: '{data['target_word']}')")

        prompt = f"""Generate exactly 3 diverse and specific keywords for an image that represents each sentence. Make the keywords unique and visual - avoid generic terms like 'language' or 'learning'. Focus on concrete objects, actions, or scenes.

{"".join(prompt_parts)}

Return the results in this exact format:
Sentence 1: keyword1, keyword2, keyword3
Sentence 2: keyword1, keyword2, keyword3
..."""

        response = model.generate_content(prompt)
        raw_response = response.text.strip()

        # Rate limiting: wait 5 seconds between API calls to respect per-minute limits
        time.sleep(5)

        # Parse the response
        results = []
        lines = raw_response.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('Sentence ') and ':' in line:
                # Extract keywords after the colon
                keywords_part = line.split(':', 1)[1].strip()
                # Clean up any extra formatting
                keywords_part = re.sub(r'[^\w\s,]', '', keywords_part)
                keywords_part = re.sub(r'\s+', ' ', keywords_part).strip()

                if keywords_part and len(keywords_part.split(',')) >= 2:
                    results.append(keywords_part)
                else:
                    # Fallback for this sentence
                    sentence_idx = len(results)
                    if sentence_idx < len(sentences_data):
                        target_word = sentences_data[sentence_idx]['target_word']
                        results.append(f"{target_word}, language, learning")

        # Ensure we have results for all sentences
        while len(results) < len(sentences_data):
            target_word = sentences_data[len(results)]['target_word']
            results.append(f"{target_word}, language, learning")

        return results[:len(sentences_data)]  # Don't return more than requested

    except Exception as e:
        logger.error(f"Error in batch image keyword generation: {e}")
        return [f"{data['target_word']}, language, learning" for data in sentences_data]
"""
Core functions for Anki card generation.
Handles: Groq sentences, Edge TTS audio, Pixabay images, TSV export, ZIP creation.
"""

import os
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import pandas as pd
import edge_tts
import requests
from groq import Groq
import logging
import re
from typing import Optional, List
import genanki
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
console.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(console)

# ============================================================================
# IPA GENERATION (HYBRID APPROACH)
# ============================================================================

def generate_ipa_hybrid(text: str, language: str, ai_ipa: str = "") -> str:
    """
    Generate IPA transcription using hybrid approach:
    1. Try AI-generated IPA first
    2. Fall back to epitran library if AI IPA is empty
    
    Args:
        text: Text to transcribe
        language: Language name (e.g., "Spanish", "Arabic")
        ai_ipa: IPA from AI (may be empty)
        
    Returns:
        IPA transcription string
    """
    # If AI provided IPA, use it
    if ai_ipa and ai_ipa.strip():
        return ai_ipa.strip()
    
    # Language code mapping for epitran
    lang_codes = {
        "Spanish": "spa-Latn",
        "French": "fra-Latn",
        "German": "deu-Latn",
        "Italian": "ita-Latn",
        "Portuguese": "por-Latn",
        "Russian": "rus-Cyrl",
        "Arabic": "ara-Arab",
        "Hindi": "hin-Deva",
        "Turkish": "tur-Latn",
        "Polish": "pol-Latn",
        "Dutch": "nld-Latn",
        "Swedish": "swe-Latn",
        "Czech": "ces-Latn",
        "Romanian": "ron-Latn",
        "Vietnamese": "vie-Latn",
        "Indonesian": "ind-Latn",
        "Malay": "msa-Latn",
        "Tagalog": "tgl-Latn",
        "Swahili": "swa-Latn",
        "Uzbek": "uzb-Latn",
        "Amharic": "amh-Ethi",
    }
    
    epitran_code = lang_codes.get(language)
    
    if epitran_code:
        try:
            import epitran
            epi = epitran.Epitran(epitran_code)
            ipa = epi.transliterate(text)
            return ipa if ipa else ""
        except Exception as e:
            logger.warning(f"Epitran failed for {language}: {e}")
            return ""
    
    # If language not supported by epitran, return empty
    logger.warning(f"IPA generation not available for {language}")
    return ""


# ============================================================================
# WORD MEANING GENERATION (Groq)
# ============================================================================

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
    
    prompt = f"""Provide a brief English meaning for the {language} word "{word}".

Format: Return ONLY a single line with the meaning and a brief explanation in parentheses.
Example: "house (a building where people live)" or "he (male pronoun, used as subject)"

IMPORTANT: Return ONLY the meaning line, nothing else. No markdown, no explanation, no JSON."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temperature for consistency
            max_tokens=100,
        )
        
        meaning = response.choices[0].message.content.strip()
        
        # Clean up any quotes
        meaning = meaning.strip('"\'')
        
        return meaning if meaning else word
        
    except Exception as e:
        logger.error(f"Error generating meaning for '{word}': {e}")
        return word  # Fallback to word itself


# ============================================================================
# SENTENCE GENERATION (Groq)
# ============================================================================

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
    groq_api_key: str = None,
) -> list[str]:
    """
    PASS 1: Generate raw sentences using Groq.
    Returns plain text sentences (one per line), no JSON.
    
    Args:
        word: Target language word
        meaning: English meaning
        language: Language name
        num_sentences: Number of sentences
        min_length: Minimum sentence length (words)
        max_length: Maximum sentence length (words)
        difficulty: "beginner", "intermediate", "advanced"
        groq_api_key: Groq API key
        
    Returns:
        List of raw sentence strings
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")
    
    client = Groq(api_key=groq_api_key)
    
    prompt = f"""You are a native-level expert linguist in {language} with professional experience teaching it to non-native learners.

Your task:
Generate exactly {num_sentences} highly natural, idiomatic, culturally appropriate sentences in {language} using the word "{word}" ({meaning}).

===========================
QUALITY RULES (STRICT)
===========================
- Every sentence must sound like it was written by an educated native speaker.
- Absolutely no unnatural, robotic, or literal-translation phrasing.
- Grammar, syntax, spelling, diacritics, gender agreement, case, politeness level, and punctuation must all be correct.
- The target word "{word}" MUST:
  * be used correctly in context,
  * match its real meaning,
  * NOT be forced into an unnatural construction.
- Avoid rare or archaic vocabulary (unless difficulty="advanced").
- All sentences must be semantically meaningful (no filler templates).
- No repeated sentence structures or patterns — each sentence must be unique.

- Each sentence must be {min_length}-{max_length} words long.
- Difficulty level:
  beginner → simple vocabulary, mostly present tense
  intermediate → mixed tenses, richer but still natural
  advanced → complex structures, nuanced vocabulary

===========================
VARIETY REQUIREMENTS
===========================
Across the {num_sentences} sentences:
- Use different tenses (if applicable to {language}).
- Use different sentence types: declarative, interrogative, imperative.
- Use the target word in different grammatical roles.
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
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200,
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Split by newlines and filter empty lines
        sentences = [s.strip() for s in response_text.split("\n") if s.strip()]
        
        return sentences[:num_sentences]
        
    except Exception as e:
        logger.error(f"PASS 1 (sentence generation) error: {e}")
        raise


# ============================================================================
# PASS 2: BATCH VALIDATION + ENRICHMENT (All sentences in one call)
# ============================================================================

def _validate_and_enrich_batch_pass2(
    sentences: list[str],
    word: str,
    language: str,
    groq_api_key: str = None,
) -> list[dict]:
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
    "image_keywords": "2-3 concrete nouns or actions for images",
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
# MAIN: OPTIMIZED 2-PASS SENTENCE GENERATION
# ============================================================================

def generate_sentences(
    word: str,
    meaning: str,
    language: str,
    num_sentences: int = 10,
    min_length: int = 5,
    max_length: int = 20,
    difficulty: str = "intermediate",
    groq_api_key: str = None,
) -> list[dict]:
    """
    Generate sentences using optimized 2-pass architecture:
    1. PASS 1: Generate raw sentences (high quality, plain text, no JSON)
    2. PASS 2: Batch validate + enrich ALL sentences in ONE API call
    
    This approach:
    - Reduces token usage from ~2000 to ~400 per word (5× cheaper than 3-pass)
    - Maintains high quality through separate generation and validation
    - Processes ~250 words/month on 100k free tokens (vs ~50 with 3-pass)
    
    Args:
        word: Target language word
        meaning: English meaning
        language: Language name (e.g., "Spanish", "Hindi")
        num_sentences: Number of sentences to generate (1-20)
        min_length: Minimum sentence length in words
        max_length: Maximum sentence length in words
        difficulty: "beginner", "intermediate", "advanced"
        groq_api_key: Groq API key
        
    Returns:
        List of dicts with keys: sentence, english_translation, ipa, context, image_keywords, role_of_word, word, meaning
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")
    
    try:
        # PASS 1: Generate raw sentences (plain text, no JSON)
        logger.info(f"PASS 1: Generating {num_sentences} raw sentences for '{word}' ({language})...")
        raw_sentences = _generate_sentences_pass1(
            word=word,
            meaning=meaning,
            language=language,
            num_sentences=num_sentences,
            min_length=min_length,
            max_length=max_length,
            difficulty=difficulty,
            groq_api_key=groq_api_key,
        )
        
        if not raw_sentences:
            logger.warning(f"PASS 1 returned no sentences for '{word}'")
            return []
        
        # PASS 2: Batch validate + enrich all sentences in ONE call
        logger.info(f"PASS 2: Batch validating + enriching {len(raw_sentences)} sentences...")
        enriched_results = _validate_and_enrich_batch_pass2(
            sentences=raw_sentences,
            word=word,
            language=language,
            groq_api_key=groq_api_key,
        )
        
        # Combine with word/meaning metadata
        final_sentences = []
        for result in enriched_results:
            final_sentences.append({
                "sentence": result.get("sentence", ""),
                "english_translation": result.get("english_translation", ""),
                "context": result.get("context", "general"),
                "ipa": result.get("ipa", ""),
                "image_keywords": result.get("image_keywords", ""),
                "role_of_word": result.get("role_of_word", ""),
                "word": word,
                "meaning": meaning,
            })
        
        logger.info(f"✓ Completed 2-pass generation for '{word}': {len(final_sentences)} sentences")
        return final_sentences
        
    except Exception as e:
        logger.error(f"2-pass sentence generation error: {e}")
        raise


def generate_sentences_batch(
    words: list,
    language: str,
    num_sentences: int = 10,
    min_length: int = 5,
    max_length: int = 20,
    difficulty: str = "intermediate",
    groq_api_key: str = None,
) -> dict:
    """
    Generate sentences and meanings for multiple words.
    
    Args:
        words: List of target language words
        language: Language name
        num_sentences: Sentences per word
        min_length: Minimum sentence length (words)
        max_length: Maximum sentence length (words)
        difficulty: Sentence complexity level
        groq_api_key: Groq API key
        
    Returns:
        Dict with structure: {word: [sentence_dicts]}
    """
    all_sentences = {}
    
    for word in words:
        try:
            # Step 1: Generate meaning for this word
            logger.info(f"Generating meaning for '{word}'...")
            meaning = generate_word_meaning(
                word=word,
                language=language,
                groq_api_key=groq_api_key,
            )
            
            # Step 2: Generate sentences using the meaning
            logger.info(f"Generating sentences for '{word}'...")
            sentences = generate_sentences(
                word=word,
                meaning=meaning,
                language=language,
                num_sentences=num_sentences,
                min_length=min_length,
                max_length=max_length,
                difficulty=difficulty,
                groq_api_key=groq_api_key,
            )
            all_sentences[word] = sentences
        except Exception as e:
            logger.error(f"Error generating for '{word}': {e}")
            all_sentences[word] = []
    
    return all_sentences


def generate_complete_deck(
    words: list,
    language: str,
    groq_api_key: str,
    pixabay_api_key: str,
    output_dir: str = "./output",
    num_sentences: int = 10,
    min_length: int = 5,
    max_length: int = 20,
    difficulty: str = "intermediate",
    audio_speed: float = 0.8,
    # pitch: float = 0.0,  # Removed pitch parameter
    voice: Optional[str] = None,
    all_words: Optional[list] = None,
    progress_callback: Optional[callable] = None,
) -> dict:
    """
    Complete workflow: Generate sentences, audio, images, and create Anki TSV.
    
    Args:
        words: List of words to process
        language: Language name
        groq_api_key: Groq API key
        pixabay_api_key: Pixabay API key
        output_dir: Output directory
        num_sentences: Sentences per word
        min_length: Minimum words per sentence
        max_length: Maximum words per sentence
        difficulty: Sentence complexity level
        audio_speed: Audio playback speed
        # pitch: Audio pitch adjustment (percent, -50 to +50) [REMOVED]
        progress_callback: Callback function for progress updates: callback(step, message, details)
        
    Returns:
        Dict with keys: success, tsv_path, audio_dir, image_dir, error
    """
    import tempfile
    from pathlib import Path
    
    try:
        # Create temp directories (single media folder)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        media_dir = output_path / "media"
        media_dir.mkdir(exist_ok=True)
        
        # Step 1: Generate sentences
        logger.info(f"Generating sentences for {len(words)} words...")
        if progress_callback:
            progress_callback(1, "Generating sentences with AI", f"Creating {num_sentences} example sentences for {len(words)} word(s)...")
        
        sentences_batch = generate_sentences_batch(
            words=words,
            language=language,
            num_sentences=num_sentences,
            min_length=min_length,
            max_length=max_length,
            difficulty=difficulty,
            groq_api_key=groq_api_key,
        )
        
        # Step 2: Per-sentence audio, images, TSV rows
        logger.info("Generating audio and images per sentence, then building TSV rows...")
        if progress_callback:
            progress_callback(2, "Generating audio with Edge TTS", f"Creating {len(words) * num_sentences} audio files (speed: {audio_speed}x)...")
        
        words_data = []
        voice = voice or _voice_for_language(language)

        def rank_for_word(word: str) -> int:
            if all_words:
                try:
                    return all_words.index(word) + 1
                except ValueError:
                    return len(all_words) + 1
            return words.index(word) + 1

        for word_idx, word in enumerate(words, 1):
            safe_word = _sanitize_word(word)
            sents = sentences_batch.get(word, [])
            sentence_texts = [s.get("sentence", "") for s in sents]

            rank = rank_for_word(word)
            
            # Progress update for this word
            if progress_callback:
                progress_callback(2, "🎵 Generating audio files...", f"Processing word {word_idx}/{len(words)}: {word} ({len(sentence_texts)} sentences)")

            # Build per-sentence base names
            base_names = [f"{rank}_{safe_word}_{j:03d}" for j in range(1, len(sentence_texts) + 1)]

            # Audio per sentence with exact filenames
            audio_files = generate_audio(
                sentences=sentence_texts,
                voice=voice,
                output_dir=str(media_dir),
                batch_name="unused",
                rate=audio_speed,
                exact_filenames=[f"{b}.mp3" for b in base_names],
                language=language,
            )

            # Images per sentence with exact filenames (using keywords for better results)
            if progress_callback and word_idx == 1:
                progress_callback(3, "Downloading images from Pixabay", f"Finding relevant images for {len(words)} word(s)...")
            
            image_queries = []
            for s in sents:
                # Use image_keywords if available, otherwise fall back to English translation
                keywords = s.get("image_keywords", "").strip()
                if keywords:
                    image_queries.append(keywords)
                else:
                    image_queries.append(s.get("english_translation", ""))
            
            image_files = generate_images_pixabay(
                queries=image_queries,
                output_dir=str(media_dir),
                batch_name="unused",
                num_images=1,
                pixabay_api_key=pixabay_api_key,
                exact_filenames=[f"{b}.jpg" for b in base_names],
            )

            # Build TSV rows (one per sentence)
            for idx_sent, sent in enumerate(sents):
                file_base = base_names[idx_sent] if idx_sent < len(base_names) else f"{rank}_{safe_word}_{idx_sent+1:03d}"
                audio_name = audio_files[idx_sent] if idx_sent < len(audio_files) else ""
                image_name = image_files[idx_sent] if idx_sent < len(image_files) else ""
                
                # DEBUG: Log what's in the sent dict
                logger.debug(f"Building TSV row {idx_sent+1} for word '{word}': sent dict keys = {sent.keys()}")
                logger.debug(f"  sent['meaning'] = {sent.get('meaning', 'KEY_NOT_FOUND')}")
                logger.debug(f"  sent['word'] = {sent.get('word', 'KEY_NOT_FOUND')}")
                
                # Generate IPA with hybrid approach
                ai_ipa = sent.get("ipa", "")
                final_ipa = generate_ipa_hybrid(
                    text=sent.get("sentence", ""),
                    language=language,
                    ai_ipa=ai_ipa
                )

                words_data.append({
                    "file_name": file_base,
                    "word": word,
                    "meaning": sent.get("meaning", word),
                    "sentence": sent.get("sentence", ""),
                    "ipa": final_ipa,
                    "english": sent.get("english_translation", ""),
                    "context": sent.get("context", ""),
                    "image_keywords": sent.get("image_keywords", ""),
                    "role_of_word": sent.get("role_of_word", ""),
                    "audio": f"[sound:{audio_name}]" if audio_name else "",
                    "image": f"<img src=\"{image_name}\">" if image_name else "",
                    "tags": "",
                })

        # Step 5: Create TSV
        tsv_path = output_path / "ANKI_IMPORT.tsv"
        if not create_anki_tsv(words_data, str(tsv_path)):
            raise Exception("Failed to create TSV file")
        
        return {
            "success": True,
            "tsv_path": str(tsv_path),
            "media_dir": str(media_dir),
            "output_dir": str(output_path),
            "error": None,
        }
        
    except Exception as e:
        logger.error(f"Complete deck generation error: {e}")
        return {
            "success": False,
            "tsv_path": None,
            "media_dir": None,
            "output_dir": None,
            "error": str(e),
        }


# ============================================================================
# AUDIO GENERATION (Edge TTS)
# ============================================================================

async def generate_audio_async(
    text: str,
    voice: str,
    output_path: str,
    rate: float = 0.8,  # Playback speed for learners
    # pitch: float = 0.0,  # Removed pitch parameter
) -> bool:
    """
    Generate audio asynchronously using Edge TTS.
    
    Args:
        text: Text to synthesize
        voice: Edge TTS voice code (e.g., "en-US-AvaNeural")
        output_path: Path to save MP3 file
        rate: Playback speed (0.5-2.0; 0.8 is learner-friendly)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Edge TTS rate format: "+0%" for normal, "-20%" for 0.8x
        rate_pct = int((rate - 1.0) * 100)
        rate_str = f"{rate_pct:+d}%"

        kwargs = {"text": text, "voice": voice, "rate": rate_str}

        communicate = edge_tts.Communicate(**kwargs)
        await communicate.save(output_path)
        return True
    except Exception as e:
        logger.error(f"Edge TTS error for {voice}: {e}")
        return False


def generate_audio(
    sentences: list[str],
    voice: str,
    output_dir: str,
    batch_name: str = "batch",
    rate: float = 0.8,
    # pitch: float = 0.0,  # Removed pitch parameter
    exact_filenames: Optional[List[str]] = None,
    language: str = "English",
) -> list[str]:
    """
    Batch generate audio files synchronously using Edge TTS.
    
    Args:
        sentences: List of sentences to synthesize
        voice: Edge TTS voice code
        output_dir: Directory to save MP3 files
        batch_name: Prefix for filenames
        rate: Playback speed
        # pitch: Pitch adjustment (percent) [REMOVED]
        exact_filenames: Custom filenames for each sentence
        language: Language name (kept for API compatibility)
        
    Returns:
        List of generated file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    generated = []
    
    async def batch_generate():
        tasks = []
        for i, sentence in enumerate(sentences):
            filename = exact_filenames[i] if exact_filenames and i < len(exact_filenames) else f"{batch_name}_{i+1:02d}.mp3"
            output_path = Path(output_dir) / filename
            
            # Use Edge TTS
            tasks.append(generate_audio_async(sentence, voice, str(output_path), rate))
        
        results = await asyncio.gather(*tasks)
        return results
    
    # Run event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    results = loop.run_until_complete(batch_generate())
    
    for i, success in enumerate(results):
        if success:
            filename = exact_filenames[i] if exact_filenames and i < len(exact_filenames) else f"{batch_name}_{i+1:02d}.mp3"
            generated.append(filename)
    
    return generated


def _sanitize_word(word: str) -> str:
    """Sanitize word for filesystem-safe names."""
    safe = re.sub(r"[^\w\-]+", "_", word.strip())
    return safe or "word"


def _voice_for_language(language: str) -> str:
    voice_map = {
        "Spanish": "es-ES-ElviraNeural",
        "French": "fr-FR-DeniseNeural",
        "German": "de-DE-KatjaNeural",
        "Italian": "it-IT-IsabellaNeural",
        "Portuguese": "pt-BR-FranciscaNeural",
        "Russian": "ru-RU-SvetlanaNeural",
        "Japanese": "ja-JP-NanamiNeural",
        "Korean": "ko-KR-SoonBokNeural",
        "Chinese (Simplified)": "zh-CN-XiaoxiaoNeural",
        "Chinese (Traditional)": "zh-TW-HsiaoChenNeural",
        "Arabic": "ar-SA-LeenNeural",
        "Hindi": "hi-IN-SwaraNeural",
        "Mandarin Chinese": "zh-CN-XiaoxiaoNeural",
        "English": "en-US-AvaNeural",
    }
    return voice_map.get(language, "en-US-AvaNeural")


# ============================================================================
# IMAGE GENERATION (Pixabay)
# ============================================================================

def generate_images_pixabay(
    queries: list[str],
    output_dir: str,
    batch_name: str = "batch",
    num_images: int = 1,
    pixabay_api_key: str = None,
    randomize: bool = True,
    exact_filenames: Optional[List[str]] = None,
) -> list[str]:
    """
    Download images from Pixabay.
    
    Args:
        queries: List of search queries (one per sentence)
        output_dir: Directory to save JPG files
        batch_name: Prefix for filenames
        num_images: Number of images per query (usually 1 for Anki)
        pixabay_api_key: Pixabay API key
        randomize: Randomize from top 3 results
        
    Returns:
        List of generated file paths
    """
    if not pixabay_api_key:
        raise ValueError("Pixabay API key required")
    
    os.makedirs(output_dir, exist_ok=True)
    generated = []
    
    for i, query in enumerate(queries):
        try:
            # Search Pixabay
            params = {
                "key": pixabay_api_key,
                "q": query,
                "per_page": 3,  # Only get top 3 results instead of 5
                "image_type": "photo",
                "category": "people,places,nature",
            }
            
            response = requests.get("https://pixabay.com/api/", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            hits = data.get("hits", [])
            
            if not hits:
                logger.warning(f"No images found for query: {query}")
                continue
            
            # Select image (randomize from top 3 or use first)
            import random
            img_idx = random.randint(0, min(2, len(hits)-1)) if randomize else 0
            image_url = hits[img_idx]["webformatURL"]
            
            # Download image
            img_response = requests.get(image_url, timeout=10)
            img_response.raise_for_status()
            
            filename = exact_filenames[i] if exact_filenames and i < len(exact_filenames) else f"{batch_name}_{i+1:02d}.jpg"
            output_path = Path(output_dir) / filename
            with open(output_path, "wb") as f:
                f.write(img_response.content)
            generated.append(filename)
            
        except Exception as e:
            logger.error(f"Pixabay error for query '{query}': {e}")
            continue
    
    return generated


def generate_images_batch(
    words: list,
    output_dir: str,
    pixabay_api_key: str,
) -> dict:
    """
    Generate images for batch of words.
    
    Args:
        words: List of words to get images for
        output_dir: Base output directory
        pixabay_api_key: Pixabay API key
        
    Returns:
        Dict with {word: [image_filenames]}
    """
    images_output = {}
    
    for word in words:
        word_image_dir = Path(output_dir) / word.replace(" ", "_")
        word_image_dir.mkdir(parents=True, exist_ok=True)
        
        # Download one image per word
        image_files = generate_images_pixabay(
            queries=[word],
            output_dir=str(word_image_dir),
            batch_name=word.replace(" ", "_"),
            num_images=1,
            pixabay_api_key=pixabay_api_key,
        )
        
        images_output[word] = image_files
    
    return images_output


# ============================================================================
# TSV & ZIP EXPORT
# ============================================================================

def create_anki_tsv(
    rows: list[dict],
    output_path: str,
) -> bool:
    """Create Anki TSV without headers in expected field order."""
    try:

        columns = [
            "File Name",
            "What is the Word?",
            "Meaning of the Word",
            "Sentence",
            "IPA Transliteration",
            "English Translation",
            "Sound",
            "Image",
            "Image Keywords",
            "Tags",
        ]

        formatted_rows = []
        for r in rows:
            formatted_rows.append({
                "File Name": r.get("file_name", ""),
                "What is the Word?": r.get("word", ""),
                "Meaning of the Word": r.get("meaning", ""),
                "Sentence": r.get("sentence", ""),
                "IPA Transliteration": r.get("ipa", ""),
                "English Translation": r.get("english", ""),
                "Sound": r.get("audio", ""),
                "Image": r.get("image", ""),
                "Image Keywords": r.get("image_keywords", ""),
                "Tags": r.get("tags", ""),
            })

        df = pd.DataFrame(formatted_rows, columns=columns)
        df.to_csv(output_path, sep="\t", index=False, header=False, encoding="utf-8")
        return True

    except Exception as e:
        logger.error(f"TSV creation error: {e}")
        return False


def create_zip_export(
    tsv_path: str,
    media_dir: str,
    output_zip: str,
) -> bool:
    """
    Create ZIP file with TSV + media folder.
    
    Args:
        tsv_path: Path to ANKI_IMPORT.tsv
        media_dir: Path to media folder (contains audio + images)
        output_zip: Path to save ZIP file
        
    Returns:
        True if successful
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create structure
            deck_dir = Path(tmpdir) / "AnkiDeck"
            deck_dir.mkdir()
            
            # Copy files
            shutil.copy(tsv_path, deck_dir / "ANKI_IMPORT.tsv")
            
            if os.path.exists(media_dir):
                shutil.copytree(media_dir, deck_dir / "media")
            
            # Create instructions file
            instructions = r"""HOW TO IMPORT TO ANKI
=====================================
1. Extract this ZIP to a folder
2. Open Anki > File > Import
3. Select ANKI_IMPORT.tsv
4. Choose the note type and deck
5. Copy all files from the media/ folder to Anki collection.media folder
6. Start learning!

Finding Anki Media Folder:
  Easy way: In Anki, go to Main Menu > Tools > Check Media > View Files
  
  Manual locations:
  Windows: C:\Users\<YourUsername>\AppData\Roaming\Anki2\User 1\collection.media
  Mac: ~/Library/Application Support/Anki2/User 1/collection.media
  Linux: ~/.local/share/Anki2/User 1/collection.media
"""
            with open(deck_dir / "IMPORT_INSTRUCTIONS.txt", "w", encoding="utf-8") as f:
                f.write(instructions)
            
            # Create ZIP
            shutil.make_archive(output_zip.replace(".zip", ""), "zip", tmpdir, "AnkiDeck")
            return True
            
    except Exception as e:
        logger.error(f"ZIP creation error: {e}")
        return False


def create_apkg_export(
    rows: list[dict],
    media_dir: str,
    output_apkg: str,
    language: str,
    deck_name: str = "Language Learning",
) -> bool:
    """
    Create .apkg file (Anki deck package) with 3-card template.
    
    Args:
        rows: List of card data dicts
        media_dir: Path to media folder (contains audio + images)
        output_apkg: Path to save .apkg file
        language: Target language name (e.g., "Spanish")
        deck_name: Name of the Anki deck
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Preparing to create .apkg at: {output_apkg}")
    output_path = Path(output_apkg)
    if not output_path.parent.exists():
        logger.warning(f"Output parent directory does not exist. Attempting to create: {output_path.parent}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
    if not output_path.parent.exists():
        logger.error(f"Failed to create output parent directory: {output_path.parent}")
        raise FileNotFoundError(f"Could not create output directory: {output_path.parent}")

    # Create note model with 10 fields and 3 card templates
    model_id = random.randrange(1 << 30, 1 << 31)
    model = genanki.Model(
        model_id,
        'Fluent Forever Language Learning',
        fields=[
            {'name': 'File Name'},
            {'name': 'What is the Word?'},
            {'name': 'Meaning of the Word'},
            {'name': 'Sentence'},
            {'name': 'IPA Transliteration'},
            {'name': 'English Translation'},
            {'name': 'Sound'},
            {'name': 'Image'},
            {'name': 'Image Keywords'}
        ],
        templates=[
            {
                'name': 'Card 1: Listening',
                'qfmt': '''<div class="hint">🎧 Listen and understand</div>\n<div class="sound">{{Sound}}</div>''',
                'afmt': '''{{FrontSide}}\n<hr id="answer">\n<div class="sentence">{{Sentence}}</div>\n<div class="image">{{Image}}</div>\n<div class="english">{{English Translation}}</div>\n<div class="word-info"><strong>Word:</strong> {{What is the Word?}} ({{Meaning of the Word}})</div>\n<div class="ipa">{{IPA Transliteration}}</div>\n<div class="keywords">Keywords: {{Image Keywords}}</div>'''
            },
            {
                'name': 'Card 2: Production',
                'qfmt': '''<div class="hint">💬 Say this in ''' + language + ''':</div>\n<div class="english-prompt">{{English Translation}}</div>''',
                'afmt': '''{{FrontSide}}\n<hr id="answer">\n<div class="sentence">{{Sentence}}</div>\n<div class="sound">{{Sound}}</div>\n<div class="image">{{Image}}</div>\n<div class="ipa">{{IPA Transliteration}}</div>\n<div class="word-info"><strong>Word:</strong> {{What is the Word?}} ({{Meaning of the Word}})</div>\n<div class="keywords">Keywords: {{Image Keywords}}</div>'''
            },
            {
                'name': 'Card 3: Reading',
                'qfmt': '''<div class="hint">📖 Read and understand:</div>\n<div class="sentence">{{Sentence}}</div>''',
                'afmt': '''{{FrontSide}}\n<hr id="answer">\n<div class="sound">{{Sound}}</div>\n<div class="image">{{Image}}</div>\n<div class="english">{{English Translation}}</div>\n<div class="ipa">{{IPA Transliteration}}</div>\n<div class="word-info"><strong>Word:</strong> {{What is the Word?}} ({{Meaning of the Word}})</div>\n<div class="keywords">Keywords: {{Image Keywords}}</div>'''
            }
        ],
        css='''.card {\n    font-family: arial;\n    font-size: 20px;\n    text-align: center;\n    color: var(--text-fg, black);\n    background-color: var(--bg, white);\n}\n\n.hint {\n    font-size: 16px;\n    color: var(--subtle-fg, #666);\n    margin: 10px;\n    font-style: italic;\n}\n\n.sentence {\n    font-size: 32px;\n    color: var(--accent, #0066cc);\n    margin: 20px;\n    font-weight: bold;\n}\n\n.english-prompt {\n    font-size: 28px;\n    color: var(--accent-2, #009900);\n    margin: 20px;\n    font-weight: bold;\n}\n\n.sound {\n    margin: 20px;\n}\n\n.english {\n    font-size: 22px;\n    color: var(--accent-2, #009900);\n    margin: 15px;\n}\n\n.ipa {\n    font-size: 16px;\n    color: var(--subtle-fg, #666);\n    font-family: "Charis SIL", "Doulos SIL", serif;\n    margin: 10px;\n}\n\n.word-info {\n    font-size: 14px;\n    color: var(--fg, #333);\n    margin: 15px;\n}\n\n.keywords {\n    font-size: 12px;\n    color: var(--subtle-fg, #999);\n    margin: 10px;\n    font-style: italic;\n}\n\n.image {\n    margin: 20px;\n}\n\n.image img {\n    max-width: 500px;\n    max-height: 400px;\n}'''
    )

    # Create deck
    deck_id = random.randrange(1 << 30, 1 << 31)
    deck = genanki.Deck(deck_id, deck_name)

    # Collect media files
    media_files = []
    for row in rows:
        # Extract audio and image filenames
        audio_match = re.search(r'\[sound:(.*?)\]', row.get('audio', ''))
        audio_file = audio_match.group(1) if audio_match else ''
        image_match = re.search(r'src="(.*?)"', row.get('image', ''))
        image_file = image_match.group(1) if image_match else ''
        # Add media files to list
        if audio_file:
            audio_path = os.path.join(media_dir, audio_file)
            if os.path.exists(audio_path):
                media_files.append(audio_path)
            else:
                logger.warning(f"Missing audio file, skipping: {audio_path}")
        if image_file:
            image_path = os.path.join(media_dir, image_file)
            if os.path.exists(image_path):
                media_files.append(image_path)
            else:
                logger.warning(f"Missing image file, skipping: {image_path}")
        # Create note
        def _s(val):
            return "" if val is None else str(val)
        note = genanki.Note(
            model=model,
            fields=[
                _s(row.get('file_name', '')),
                _s(row.get('word', '')),
                _s(row.get('meaning', '')),
                _s(row.get('sentence', '')),
                _s(row.get('ipa', '')),
                _s(row.get('english', '')),
                _s(row.get('audio', '')),
                _s(row.get('image', '')),
                _s(row.get('image_keywords', ''))
            ]
        )
        deck.add_note(note)

    # Create package
    try:
        package = genanki.Package(deck)
        package.media_files = media_files
        package.write_to_file(str(output_path))
        logger.info(f"Created .apkg file with {len(rows)} notes at {output_apkg}")
        return True
    except FileNotFoundError as fnf_err:
        logger.error(f"FileNotFoundError during .apkg creation: {fnf_err}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"Attempted output path: {output_path}")
        return False
    except Exception as e:
        logger.error(f"General error during .apkg creation: {e}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"Attempted output path: {output_path}")
        return False



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
        "pixabay_requests": total_sentences,  # One per sentence
        "groq_tokens_est": int(num_words * 400),  # 2-pass architecture: ~400 tokens/word
        "edge_tts_chars": int(total_sentences * avg_chars_per_sentence),
    }


def get_available_voices(language_code: str) -> list[str]:
    """
    Get available Edge TTS voices for a language (async).
    Falls back to language defaults if full list unavailable.
    
    Args:
        language_code: ISO language code (e.g., "en", "es")
        
    Returns:
        List of voice codes
    """
    # Map language codes to available voices (can be extended)
    voice_map = {
        "en": ["en-US-AvaNeural", "en-US-BrianNeural", "en-GB-RyanNeural"],
        "es": ["es-ES-ElviraNeural", "es-MX-DaliaNeural"],
        "fr": ["fr-FR-DeniseNeural", "fr-FR-HenriNeural"],
        "de": ["de-DE-KatjaNeural", "de-DE-SashaNeural"],
        "it": ["it-IT-IsabellaNeural"],
        "pt": ["pt-BR-FranciscaNeural"],
        "ru": ["ru-RU-DmitryNeural"],
        "ja": ["ja-JP-NanamiNeural"],
        "ko": ["ko-KR-SunHiNeural"],
        "zh": ["zh-CN-XiaoxiaoNeural"],
        "ar": ["ar-SA-ZariyahNeural"],
        "hi": ["hi-IN-SwatiNeural"],
    }
    
    return voice_map.get(language_code, ["en-US-AvaNeural"])


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

"""
Core functions for Anki card generation.
Handles: Groq sentences, Edge TTS audio (with Google fallback), Pixabay images, TSV export, ZIP creation.
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

logger = logging.getLogger(__name__)

# Try to import hybrid TTS
try:
    from tts_hybrid import generate_audio_hybrid_async
    HAS_HYBRID_TTS = True
except ImportError:
    HAS_HYBRID_TTS = False
    logger.warning("Hybrid TTS module not available, using Edge TTS only")
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
    Generate sentences using Groq API.
    
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
        List of dicts with keys: sentence, english_translation, contexts, parts_of_speech
    """
    if not groq_api_key:
        raise ValueError("Groq API key required")
        
    client = Groq(api_key=groq_api_key)
    
    difficulty_desc = {
        "beginner": "simple, present tense, common scenarios",
        "intermediate": "mixed tenses, formal and informal, various contexts",
        "advanced": "complex structures, rare vocabulary, literary/academic"
    }
    
    prompt = f"""Generate exactly {num_sentences} natural {language} sentences using the word "{word}" ({meaning}).

Requirements:
- Each sentence must be {min_length}-{max_length} words long
- Difficulty: {difficulty_desc.get(difficulty, difficulty_desc['intermediate'])}
- Cover different:
  * Grammatical roles (subject, object, predicate)
  * Sentence types (declarative, interrogative, imperative)
  * Contexts (daily life, work, academic, informal)
  * Tenses/moods (when applicable to {language})

Format: Return ONLY a valid JSON array with NO additional text. Each item must have:
{{"sentence": "{language} sentence", "english_translation": "English translation", "context": "context type"}}

IMPORTANT: Return ONLY valid JSON, nothing else. No markdown, no code blocks, no explanation."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200,
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response (handle markdown blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        sentences = json.loads(response_text)
        
        # Validate and format
        validated = []
        for s in sentences[:num_sentences]:
            if isinstance(s, dict) and "sentence" in s and "english_translation" in s:
                validated.append({
                    "sentence": s["sentence"],
                    "english_translation": s["english_translation"],
                    "context": s.get("context", "general"),
                    "word": word,
                    "meaning": meaning,
                })
        
        return validated if validated else []
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return []
    except Exception as e:
        logger.error(f"Groq API error: {e}")
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
    voice: Optional[str] = None,
    all_words: Optional[list] = None,
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
        sentences_batch = generate_sentences_batch(
            words=words,
            language=language,
            num_sentences=num_sentences,
            min_length=min_length,
            max_length=max_length,
            difficulty=difficulty,
            groq_api_key=groq_api_key,
        )
        
        # Step 2-4: Per-sentence audio, images, TSV rows
        logger.info("Generating audio and images per sentence, then building TSV rows...")
        words_data = []
        voice = voice or _voice_for_language(language)

        def rank_for_word(word: str) -> int:
            if all_words:
                try:
                    return all_words.index(word) + 1
                except ValueError:
                    return len(all_words) + 1
            return words.index(word) + 1

        for word in words:
            safe_word = _sanitize_word(word)
            sents = sentences_batch.get(word, [])
            sentence_texts = [s.get("sentence", "") for s in sents]

            rank = rank_for_word(word)

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

            # Images per sentence with exact filenames (using English translations for better results)
            english_translations = [s.get("english_translation", "") for s in sents]
            image_files = generate_images_pixabay(
                queries=english_translations,
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

                words_data.append({
                    "file_name": file_base,
                    "word": word,
                    "meaning": sent.get("meaning", word),
                    "sentence": sent.get("sentence", ""),
                    "ipa": sent.get("ipa", ""),
                    "english": sent.get("english_translation", ""),
                    "context": sent.get("context", ""),
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
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate_str)
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
    exact_filenames: Optional[List[str]] = None,
    language: str = "English",
) -> list[str]:
    """
    Batch generate audio files synchronously.
    Tries Edge TTS first, falls back to Google Cloud TTS if available.
    
    Args:
        sentences: List of sentences to synthesize
        voice: Edge TTS voice code
        output_dir: Directory to save MP3 files
        batch_name: Prefix for filenames
        rate: Playback speed
        exact_filenames: Custom filenames for each sentence
        language: Language name (for Google fallback)
        
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
            
            # Use hybrid TTS if available, otherwise use basic Edge TTS
            if HAS_HYBRID_TTS:
                tasks.append(generate_audio_hybrid_async(
                    sentence, voice, language, str(output_path), rate, use_google_fallback=True
                ))
            else:
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
            "Tags",
        ]

        formatted_rows = []
        for r in rows:
            formatted_rows.append({
                "File Name": f"{r.get('file_name','')}",
                "What is the Word?": r.get("word", ""),
                "Meaning of the Word": r.get("meaning", ""),
                "Sentence": r.get("sentence", ""),
                "IPA Transliteration": r.get("ipa", ""),
                "English Translation": r.get("english", ""),
                "Sound": r.get("audio", ""),
                "Image": r.get("image", ""),
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
            instructions = """HOW TO IMPORT TO ANKI
=====================================
1. Extract this ZIP to a folder
2. Open Anki → File → Import
3. Select ANKI_IMPORT.tsv
4. Choose the note type and deck
5. Copy all files from the media/ folder to Anki's collection.media folder
6. Start learning!

Finding Anki's Media Folder:
  Easy way: In Anki, go to Main Menu → Tools → Check Media → View Files
  
  Manual locations:
  Windows: C:\\Users\\<YourUsername>\\AppData\\Roaming\\Anki2\\User 1\\collection.media
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


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def estimate_api_costs(num_words: int, num_sentences: int = 10) -> dict:
    """
    Estimate API usage for cost calculator.
    
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
        "groq_tokens_est": int(total_sentences * 150),  # Rough estimate
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

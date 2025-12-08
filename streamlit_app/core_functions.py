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

logger = logging.getLogger(__name__)

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
        response = client.messages.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200,
        )
        
        response_text = response.content[0].text.strip()
        
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
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=f"{rate-1:+.0%}")
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
) -> list[str]:
    """
    Batch generate audio files synchronously.
    
    Args:
        sentences: List of sentences to synthesize
        voice: Edge TTS voice code
        output_dir: Directory to save MP3 files
        batch_name: Prefix for filenames
        rate: Playback speed
        
    Returns:
        List of generated file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    generated = []
    
    async def batch_generate():
        tasks = []
        for i, sentence in enumerate(sentences):
            output_path = Path(output_dir) / f"{batch_name}_{i+1:02d}.mp3"
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
            generated.append(f"{batch_name}_{i+1:02d}.mp3")
    
    return generated


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
) -> list[str]:
    """
    Download images from Pixabay.
    
    Args:
        queries: List of search queries (one per sentence)
        output_dir: Directory to save JPG files
        batch_name: Prefix for filenames
        num_images: Number of images per query (usually 1 for Anki)
        pixabay_api_key: Pixabay API key
        randomize: Randomize from top 5 results
        
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
                "per_page": 5,
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
            
            # Select image (randomize from top 5 or use first)
            import random
            img_idx = random.randint(0, min(4, len(hits)-1)) if randomize else 0
            image_url = hits[img_idx]["webformatURL"]
            
            # Download image
            img_response = requests.get(image_url, timeout=10)
            img_response.raise_for_status()
            
            output_path = Path(output_dir) / f"{batch_name}_{i+1:02d}.jpg"
            with open(output_path, "wb") as f:
                f.write(img_response.content)
            
            generated.append(f"{batch_name}_{i+1:02d}.jpg")
            
        except Exception as e:
            logger.error(f"Pixabay error for query '{query}': {e}")
            continue
    
    return generated


# ============================================================================
# TSV & ZIP EXPORT
# ============================================================================

def create_anki_tsv(
    words_data: list[dict],
    output_path: str,
) -> bool:
    """
    Create Anki-compatible TSV file.
    
    Args:
        words_data: List of dicts with keys:
                    word, meaning, sentences (list of dicts), audio_files, image_files
        output_path: Path to save TSV file
        
    Returns:
        True if successful
    """
    try:
        rows = []
        
        for word_info in words_data:
            word = word_info["word"]
            meaning = word_info["meaning"]
            sentences = word_info.get("sentences", [])
            audio_files = word_info.get("audio_files", [])
            image_files = word_info.get("image_files", [])
            
            for i, sent in enumerate(sentences):
                audio_tag = f"[sound:{audio_files[i]}]" if i < len(audio_files) else ""
                image_tag = f'<img src="{image_files[i]}">' if i < len(image_files) else ""
                
                row = {
                    "Word": word,
                    "Meaning": meaning,
                    "Sentence": sent.get("sentence", ""),
                    "English Translation": sent.get("english_translation", ""),
                    "Context": sent.get("context", ""),
                    "Audio": audio_tag,
                    "Image": image_tag,
                }
                rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, sep="\t", index=False, encoding="utf-8")
        return True
        
    except Exception as e:
        logger.error(f"TSV creation error: {e}")
        return False


def create_zip_export(
    tsv_path: str,
    audio_dir: str,
    image_dir: str,
    output_zip: str,
) -> bool:
    """
    Create ZIP file with TSV + media folders.
    
    Args:
        tsv_path: Path to ANKI_IMPORT.tsv
        audio_dir: Path to audio folder
        image_dir: Path to images folder
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
            
            if os.path.exists(audio_dir):
                shutil.copytree(audio_dir, deck_dir / "audio")
            
            if os.path.exists(image_dir):
                shutil.copytree(image_dir, deck_dir / "images")
            
            # Create instructions file
            instructions = """HOW TO IMPORT TO ANKI
=====================================
1. Extract this ZIP to a folder
2. Open Anki → File → Import
3. Select ANKI_IMPORT.tsv
4. Choose the note type and deck
5. Drag audio/ and images/ folders to Anki's media folder
6. Start learning!

Media Folder Location:
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

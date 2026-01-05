# Audio generation module
# Extracted from core_functions.py for better separation of concerns

import os
import asyncio
import logging
import re
from typing import Optional, List
import edge_tts

# Import error recovery
from error_recovery import graceful_degradation, resilient_audio_generation

logger = logging.getLogger(__name__)

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

        kwargs = {"text": text, "voice": voice, "rate": rate_str}

        communicate = edge_tts.Communicate(**kwargs)
        await communicate.save(output_path)

        # Check if file was actually created and has content
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return True
        else:
            logger.warning(f"Edge TTS save completed but file not created or empty: {output_path}")
            return False

    except Exception as exc:
        logger.error(f"Edge TTS error for {voice}: {exc}")
        return False

@graceful_degradation("Audio generation", continue_on_failure=True)
@resilient_audio_generation(max_retries=1)
def generate_audio(
    sentences: List[str],
    voice: str,
    output_dir: str,
    batch_name: str = "batch",
    rate: float = 0.8,
    exact_filenames: Optional[List[str]] = None,
    language: str = "English",
    unique_id: str = None,
) -> List[str]:
    """
    Batch generate audio files synchronously using Edge TTS.

    Args:
        sentences: List of sentences to synthesize
        voice: Edge TTS voice code
        output_dir: Directory to save MP3 files
        batch_name: Prefix for filenames
        rate: Playback speed
        exact_filenames: Custom filenames for each sentence
        language: Language name (kept for API compatibility)

    Returns:
        List of generated file paths
    """
    os.makedirs(output_dir, exist_ok=True)

    async def batch_generate():
        tasks = []
        for i, sentence in enumerate(sentences):
            from pathlib import Path
            if exact_filenames and i < len(exact_filenames):
                filename = exact_filenames[i]
            else:
                # Use unique ID to prevent filename conflicts
                unique_suffix = f"_{unique_id}" if unique_id else ""
                filename = f"{batch_name}_{i+1:02d}{unique_suffix}.mp3"
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

    # Maintain correct indices even for failed generations
    generated_files = []
    for i, success in enumerate(results):
        if success:
            if exact_filenames and i < len(exact_filenames):
                filename = exact_filenames[i]
            else:
                # Use unique ID to prevent filename conflicts
                unique_suffix = f"_{unique_id}" if unique_id else ""
                filename = f"{batch_name}_{i+1:02d}{unique_suffix}.mp3"
            generated_files.append(filename)
        else:
            generated_files.append("")  # Empty string for failed generations

    return generated_files

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
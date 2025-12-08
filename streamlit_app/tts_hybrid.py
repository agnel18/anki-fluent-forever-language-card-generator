"""
Hybrid TTS module: Edge TTS (primary) + Google Cloud TTS (fallback)
"""

import os
import asyncio
import json
from pathlib import Path
import edge_tts
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ============================================================================
# GOOGLE CLOUD TTS SETUP
# ============================================================================

def get_google_tts_client():
    """Initialize Google Cloud TTS client if credentials exist."""
    try:
        from google.cloud import texttospeech
        
        # Check for JSON credentials file
        creds_file = Path(__file__).parent.parent / "languagelearning-480303-93748916f7bd.json"
        if creds_file.exists():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_file)
            client = texttospeech.TextToSpeechClient()
            logger.info("✅ Google Cloud TTS initialized successfully")
            return client
        else:
            logger.warning(f"Google Cloud TTS credentials not found at: {creds_file}")
            logger.warning("(Optional) To set up Google TTS fallback, see app's API setup page")
    except ImportError:
        logger.warning("Google Cloud TTS library not installed")
        logger.warning("Install with: pip install google-cloud-texttospeech")
    except Exception as e:
        logger.warning(f"Google Cloud TTS not available: {e}")
    return None


GOOGLE_TTS_CLIENT = None


def init_google_tts():
    """Initialize Google TTS client once."""
    global GOOGLE_TTS_CLIENT
    if GOOGLE_TTS_CLIENT is None:
        GOOGLE_TTS_CLIENT = get_google_tts_client()
    return GOOGLE_TTS_CLIENT


# ============================================================================
# VOICE MAPPING
# ============================================================================

GOOGLE_VOICE_MAP = {
    "Spanish": "es-ES-Neural2-C",  # Female Spanish
    "French": "fr-FR-Neural2-C",  # Female French
    "German": "de-DE-Neural2-C",  # Female German
    "Italian": "it-IT-Neural2-C",  # Female Italian
    "Portuguese": "pt-BR-Neural2-C",  # Female Brazilian Portuguese
    "Russian": "ru-RU-Neural2-C",  # Female Russian
    "Japanese": "ja-JP-Neural2-C",  # Female Japanese
    "Korean": "ko-KR-Neural2-C",  # Female Korean
    "Chinese (Simplified)": "zh-CN-Neural2-C",  # Female Mandarin
    "Mandarin Chinese": "zh-CN-Neural2-C",  # Female Mandarin
    "Arabic": "ar-XA-Neural2-C",  # Female Arabic
    "Hindi": "hi-IN-Neural2-C",  # Female Hindi
    "English": "en-US-Neural2-C",  # Female English
}


# ============================================================================
# HYBRID TTS FUNCTIONS
# ============================================================================

async def generate_audio_edge_tts_async(
    text: str,
    voice: str,
    output_path: str,
    rate: float = 0.8,
) -> bool:
    """
    Generate audio using Edge TTS.
    
    Args:
        text: Text to synthesize
        voice: Edge TTS voice code (e.g., "en-US-AvaNeural")
        output_path: Path to save MP3 file
        rate: Playback speed (0.5-2.0)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        rate_pct = int((rate - 1.0) * 100)
        rate_str = f"{rate_pct:+d}%"
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate_str)
        await communicate.save(output_path)
        logger.info(f"✅ Edge TTS: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Edge TTS failed for {voice}: {e}")
        return False


def generate_audio_google_tts(
    text: str,
    language: str,
    output_path: str,
    rate: float = 0.8,
) -> bool:
    """
    Generate audio using Google Cloud TTS.
    
    Args:
        text: Text to synthesize
        language: Language name (e.g., "Spanish", "French")
        output_path: Path to save MP3 file
        rate: Playback speed (0.75-1.25 for Google)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from google.cloud import texttospeech
        
        client = init_google_tts()
        if not client:
            logger.warning("Google Cloud TTS client not initialized")
            return False
        
        voice_name = GOOGLE_VOICE_MAP.get(language, "en-US-Neural2-C")
        
        # Google uses SSML for rate control
        synthesis_input = texttospeech.SynthesisInput(
            text=text
        )
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_name.split("-")[0] + "-" + voice_name.split("-")[1],
            name=f"projects/languagelearning-480303/locations/global/voices/{voice_name}",
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=rate,  # Google: 0.25 to 4.0
            pitch=0.0,
        )
        
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )
        
        with open(output_path, "wb") as out_file:
            out_file.write(response.audio_content)
        
        logger.info(f"✅ Google TTS: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Google TTS failed: {e}")
        return False


async def generate_audio_hybrid_async(
    text: str,
    voice: str,
    language: str,
    output_path: str,
    rate: float = 0.8,
    use_google_fallback: bool = True,
) -> bool:
    """
    Generate audio: Try Edge TTS first, fall back to Google if it fails.
    
    Args:
        text: Text to synthesize
        voice: Edge TTS voice code
        language: Language name (for Google fallback)
        output_path: Path to save MP3 file
        rate: Playback speed
        use_google_fallback: Whether to try Google TTS if Edge fails
        
    Returns:
        True if successful
    """
    # Try Edge TTS first
    success = await generate_audio_edge_tts_async(text, voice, output_path, rate)
    if success:
        return True
    
    # Fall back to Google TTS if enabled
    if use_google_fallback:
        logger.info(f"Edge TTS failed, attempting Google Cloud TTS fallback...")
        success = generate_audio_google_tts(text, language, output_path, rate)
        if success:
            logger.info(f"✅ Google Cloud TTS succeeded")
        else:
            logger.error(f"⚠️ Both Edge TTS and Google TTS failed")
            logger.error(f"   (Optional) To set up Google TTS, see the API setup page")
        return success
    
    logger.error(f"Edge TTS failed and fallback is disabled")
    return False

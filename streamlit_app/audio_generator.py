# Audio generation module
# Extracted from core_functions.py for better separation of concerns

import os
import asyncio
import logging
import re
from typing import Optional, List
import azure.cognitiveservices.speech as speechsdk

# Import error recovery
from error_recovery import graceful_degradation, resilient_audio_generation

logger = logging.getLogger(__name__)

# ============================================================================
# AZURE COGNITIVE SERVICES TTS CONFIGURATION
# ============================================================================

# Azure TTS Configuration
def get_azure_tts_config():
    # Check session state first, then environment variables
    import streamlit as st
    subscription_key = ""
    try:
        subscription_key = st.session_state.get("azure_tts_key", os.getenv("AZURE_TTS_KEY", ""))
    except:
        subscription_key = os.getenv("AZURE_TTS_KEY", "")
    
    return {
        "subscription_key": subscription_key,
        "region": "centralindia",  # From deployment
        "resource_name": "anki-audio-gen-1"  # From deployment
    }

def get_azure_speech_config():
    """Get Azure Speech configuration."""
    config = get_azure_tts_config()
    if not config["subscription_key"]:
        raise ValueError("AZURE_TTS_KEY environment variable not set")

    speech_config = speechsdk.SpeechConfig(
        subscription=config["subscription_key"],
        region=config["region"]
    )
    speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"  # Default voice
    return speech_config

def is_azure_tts_configured():
    """Check if Azure TTS is properly configured."""
    try:
        get_azure_speech_config()
        return True
    except ValueError:
        return False

def get_tts_provider():
    """Get the current TTS provider being used."""
    if is_azure_tts_configured():
        return "Azure Cognitive Services TTS"
    else:
        return "Azure TTS (not configured)"

# ============================================================================
# AUDIO GENERATION (Azure TTS)
# ============================================================================
async def generate_audio_async(
    text: str,
    voice: str,
    output_path: str,
    rate: float = 0.8,  # Playback speed for learners
) -> bool:
    """
    Generate audio asynchronously using Azure Cognitive Services TTS.

    Args:
        text: Text to synthesize
        voice: Azure TTS voice name (e.g., "en-US-AriaNeural")
        output_path: Path to save MP3 file
        rate: Playback speed (0.5-2.0; 0.8 is learner-friendly)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Validate input text
        if not text or not text.strip():
            logger.warning("Empty or whitespace-only text provided for audio generation")
            return False

        # Get Azure speech configuration
        speech_config = get_azure_speech_config()

        # Configure audio output
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)

        # Create synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        # Set speech rate using SSML (Azure TTS uses percentage: 0% = normal, -50% = half speed)
        rate_pct = int((rate - 1.0) * 100)
        ssml = f"""<speak version='1.0' xml:lang='en-US'>
            <voice name='{voice}'>
                <prosody rate='{rate_pct}%'>
                    {text.strip()}
                </prosody>
            </voice>
        </speak>"""

        # Synthesize speech using SSML
        result = synthesizer.speak_ssml_async(ssml).get()

        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info(f"Azure TTS synthesis completed for voice: {voice}")
            return True
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logger.error(f"Azure TTS synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logger.error(f"Azure TTS error details: {cancellation_details.error_details}")
            return False

        return False

    except Exception as exc:
        logger.error(f"Azure TTS error for {voice}: {exc}")
        # Clean up any empty file that might have been created
        if os.path.exists(output_path) and os.path.getsize(output_path) == 0:
            try:
                os.unlink(output_path)
            except:
                pass  # Ignore cleanup errors
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
    Batch generate audio files synchronously using Azure TTS.

    Args:
        sentences: List of sentences to synthesize
        voice: Azure TTS voice name
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

            # Use Azure TTS
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
    """Get default Azure TTS voice for a language."""
    voice_map = {
        "Spanish": "es-ES-ElviraNeural",
        "French": "fr-FR-DeniseNeural",
        "German": "de-DE-KatjaNeural",
        "Italian": "it-IT-IsabellaNeural",
        "Portuguese": "pt-BR-FranciscaNeural",
        "Russian": "ru-RU-SvetlanaNeural",
        "Japanese": "ja-JP-NanamiNeural",
        "Korean": "ko-KR-SunHiNeural",
        "Chinese (Simplified)": "zh-CN-XiaoxiaoNeural",
        "Chinese (Traditional)": "zh-TW-HsiaoChenNeural",
        "Arabic": "ar-SA-ZariyahNeural",
        "Hindi": "hi-IN-SwaraNeural",
        "Mandarin Chinese": "zh-CN-XiaoxiaoNeural",
        "English": "en-US-AriaNeural",
    }
    return voice_map.get(language, "en-US-AriaNeural")

def get_available_voices(language_code: str) -> list[str]:
    """
    Get available Azure TTS voices for a language.

    Args:
        language_code: ISO language code (e.g., "en", "es")

    Returns:
        List of Azure TTS voice names
    """
    # Map language codes to available Azure TTS voices
    voice_map = {
        "en": ["en-US-AriaNeural", "en-US-ZiraNeural", "en-GB-SoniaNeural"],
        "es": ["es-ES-ElviraNeural", "es-MX-DaliaNeural"],
        "fr": ["fr-FR-DeniseNeural", "fr-FR-HenriNeural"],
        "de": ["de-DE-KatjaNeural", "de-DE-ConradNeural"],
        "it": ["it-IT-ElsaNeural", "it-IT-IsabellaNeural"],
        "pt": ["pt-BR-FranciscaNeural", "pt-BR-AntonioNeural"],
        "ru": ["ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural"],
        "ja": ["ja-JP-NanamiNeural", "ja-JP-KeitaNeural"],
        "ko": ["ko-KR-SunHiNeural", "ko-KR-InJoonNeural"],
        "zh": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"],
        "ar": ["ar-SA-ZariyahNeural", "ar-SA-HamedNeural"],
        "hi": ["hi-IN-SwaraNeural", "hi-IN-MadhurNeural"],
    }

    return voice_map.get(language_code, ["en-US-AriaNeural"])
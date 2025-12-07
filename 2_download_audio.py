from __future__ import annotations
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ========== CONFIGURATION ==========
# Audio speed for learners (0.8 = 80% speed, slower for comprehension)
# You can change this: 0.5 (very slow) to 2.0 (fast)
AUDIO_SPEED = float(os.getenv("AUDIO_SPEED", "0.8"))  # Default: 0.8x speed (recommended for learners)
GOOGLE_TTS_API_KEY = os.getenv("GOOGLE_TTS_API_KEY")  # From .env file

# ========== LANGUAGE CONFIGURATION ==========
def load_language_config() -> dict:
    """Load language configuration from language_config.txt"""
    config_file = Path(__file__).parent / "language_config.txt"
    
    if not config_file.exists():
        print("\n❌ ERROR: language_config.txt not found!")
        print("   Please run: python 0_select_language.py")
        sys.exit(1)
    
    config = {}
    with open(config_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    
    return config

# Load configuration
CONFIG = load_language_config()
LANGUAGE_NAME = CONFIG.get("language_name", "Unknown")
LANGUAGE_CODE = CONFIG.get("language_code", "XX")
GOOGLE_TTS_CODE = CONFIG.get("google_tts_code", LANGUAGE_CODE)  # Some languages need different code for TTS
FREQUENCY_FILE = Path(CONFIG.get("frequency_file"))
OUTPUT_BASE = CONFIG.get("output_dir", "FluentForever_Output")
BATCH_WORDS = int(os.getenv("BATCH_WORDS", "5"))

# ========== FILE PATHS ==========
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / OUTPUT_BASE
AUDIO_DIR = OUTPUT_DIR / "audio"
WORKING_DATA = OUTPUT_DIR / "working_data.xlsx"
TRACKING_FILE = FREQUENCY_FILE  # Frequency list with Status column

def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure Sentences, Audio, Images columns exist for tracking"""
    if "Sentences" not in df.columns:
        df["Sentences"] = 0
    if "Audio" not in df.columns:
        df["Audio"] = 0
    if "Images" not in df.columns:
        df["Images"] = 0
    df["Sentences"] = df["Sentences"].fillna(0).astype(int)
    df["Audio"] = df["Audio"].fillna(0).astype(int)
    df["Images"] = df["Images"].fillna(0).astype(int)
    return df


def update_audio_count(freq_num: int, count: int) -> None:
    """Update Audio column count in tracking file"""
    df_track = ensure_columns(pd.read_excel(TRACKING_FILE))
    idx = freq_num - 1
    if 0 <= idx < len(df_track):
        df_track.at[idx, "Audio"] = count
        df_track.to_excel(TRACKING_FILE, index=False)
        print(f"✅ Updated Audio={count}/10 for freq #{freq_num} in {TRACKING_FILE.name}")

print(f"\n{'='*60}")
print(f"DOWNLOADING AUDIO (Google Text-to-Speech): {LANGUAGE_NAME}")
print(f"{'='*60}")
print(f"Language Code: {GOOGLE_TTS_CODE}")
print(f"Audio Speed: {AUDIO_SPEED}x (0.8 = slower for learners)")
print(f"Output Directory: {OUTPUT_DIR}")
print(f"{'='*60}\n")

# Create directories
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def safe_word(word: str) -> str:
    """Clean word for filenames"""
    return word.replace("/", "-").replace("\\", "-").strip()


def check_api_key() -> None:
    """Check if Google TTS API key is configured"""
    if not GOOGLE_TTS_API_KEY:
        print(f"\n❌ ERROR: GOOGLE_TTS_API_KEY not found in .env file")
        print(f"\n📝 SETUP INSTRUCTIONS:")
        print(f"   1. Create a .env file in the project root")
        print(f"   2. Add your API key: GOOGLE_TTS_API_KEY=your_api_key_here")
        print(f"   3. See README.md section 4b for detailed setup")
        print(f"\n💡 NOTE: Google TTS API requires a credit/debit card (even though it's free tier)")
        print(f"   If you don't have a card, use the fallback script: python 2_download_audio_soundoftext.py")
        sys.exit(1)
    
    print(f"✅ API Key found: {GOOGLE_TTS_API_KEY[:10]}...")  # Only show first 10 chars for security


def download_audio_gtts(text: str, outfile: Path) -> bool:
    """Download audio using Google Text-to-Speech API (REST API with API key)"""
    try:
        # Google TTS REST API endpoint
        url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        
        # Request payload
        payload = {
            "input": {"text": text},
            "voice": {
                "languageCode": GOOGLE_TTS_CODE,
                "ssmlGender": "NEUTRAL"
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": AUDIO_SPEED  # 0.8 = slower for learners
            }
        }
        
        # Add API key to request
        headers = {"Content-Type": "application/json"}
        params = {"key": GOOGLE_TTS_API_KEY}
        
        # Make the request
        response = requests.post(url, json=payload, headers=headers, params=params, timeout=30)
        
        # Check for errors
        if response.status_code != 200:
            print(f"  ❌ API Error: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
        
        # Extract audio content (it's base64 encoded)
        import base64
        audio_content = base64.b64decode(response.json()["audioContent"])
        
        # Write the audio file
        outfile.write_bytes(audio_content)
        print(f"  ✓ Saved audio -> {outfile.name} ({len(audio_content)} bytes)")
        return True
        
    except Exception as exc:
        import traceback
        print(f"  ❌ Error downloading audio: {exc}")
        print(f"  Details: {traceback.format_exc()[:200]}")
        return False


def all_audio_present(files: list[Path]) -> bool:
    """Check if all audio files exist and have reasonable size"""
    for f in files:
        if not f.exists():
            return False
        if f.stat().st_size <= 1024:
            return False
    return True


def update_working_data_audio(word: str, freq_num: int) -> None:
    """Update Sound column in working_data.xlsx"""
    df = pd.read_excel(WORKING_DATA)
    pattern = f"{freq_num:04d}_{word}_"
    mask = df["File Name"].str.startswith(pattern, na=False)
    
    for idx in df[mask].index:
        file_name = df.at[idx, "File Name"]
        df.at[idx, "Sound"] = f"[sound:{file_name}.mp3]"
    
    df.to_excel(WORKING_DATA, index=False)
    print(f"✅ Updated Sound column in {WORKING_DATA.name}")


def main() -> None:
    """
    Main workflow:
    1. Load working_data.xlsx
    2. Find first word with sentences but no audio yet
    3. Download audio from Google Text-to-Speech API for each sentence
    4. Update Sound column with [sound:filename.mp3] tags
    5. Mark word as audio_done
    """
    # Verify input file exists
    if not WORKING_DATA.exists():
        print(f"❌ Error: {WORKING_DATA} not found.")
        print("   Run script 1 first to generate sentences.")
        sys.exit(1)

    # Check API key is configured
    check_api_key()

    # Load working data
    df = pd.read_excel(WORKING_DATA)
    df_track = ensure_columns(pd.read_excel(TRACKING_FILE))
    processed_count = 0

    # Iterate through tracking file to find words that need audio
    for track_idx in df_track.index:
        if processed_count >= BATCH_WORDS:
            print(f"⏸️ Reached batch limit ({BATCH_WORDS} words). Run again for more.")
            break

        sentences_count = int(df_track.at[track_idx, "Sentences"])
        audio_count = int(df_track.at[track_idx, "Audio"])
        
        # Only process if sentences are complete but audio is not
        if sentences_count > 0 and audio_count < 10:
            freq_num = track_idx + 1
            # Get word from first matching row in working_data
            pattern_prefix = f"{freq_num:04d}_"
            matching_rows = df[df["File Name"].str.startswith(pattern_prefix, na=False)]
            
            if matching_rows.empty:
                continue
                
            first_row = matching_rows.iloc[0]
            file_name = first_row["File Name"]
            parts = file_name.split("_")
            if len(parts) >= 2:
                word = "_".join(parts[1:-1])
            else:
                continue

            processed_count += 1

            pattern = f"{freq_num:04d}_{word}_"
            word_mask = df["File Name"].str.startswith(pattern, na=False)
            # Only download for rows that don't have Sound yet
            empty_sound_mask = (df["Sound"].isna()) | (df["Sound"] == "")
            word_rows = df[word_mask & empty_sound_mask]

            print(f"📝 Processing word: '{word}' (frequency #{freq_num})")
            print(f"   Sentences to download: {len(word_rows)}")

            target_files: list[Path] = []

            for _, row in word_rows.iterrows():
                file_name = row["File Name"]
                sentence = row["Sentence"]
                filename = f"{file_name}.mp3"
                outfile = AUDIO_DIR / filename
                target_files.append(outfile)

                if outfile.exists() and outfile.stat().st_size > 1024:
                    print(f"  ⏭️  Skipping existing: {outfile.name}")
                    continue

                print(f"  📥 Downloading: {sentence[:60]}... -> {filename}")
                ok = download_audio_gtts(sentence, outfile)
                if ok:
                    # Small delay to be respectful to API
                    time.sleep(0.2)

            if all_audio_present(target_files):
                update_working_data_audio(word, freq_num)
                update_audio_count(freq_num, len(target_files))
                print(f"✅ Audio complete for '{word}' ({len(target_files)}/10)! Ready for script 3\n")
            else:
                actual_count = sum(1 for f in target_files if f.exists() and f.stat().st_size > 1024)
                update_audio_count(freq_num, actual_count)
                print(f"⚠️ Audio incomplete for '{word}' ({actual_count}/{len(target_files)} files)")

    print(f"\n{'='*60}")
    print(f"✅ Audio step finished for this batch.")
    print(f"📊 API USAGE NOTE:")
    print(f"   Google Text-to-Speech free tier: 1 million characters/month")
    print(f"   This batch used approximately {processed_count * 10 * 50} characters")
    print(f"   (assuming ~50 chars per sentence)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

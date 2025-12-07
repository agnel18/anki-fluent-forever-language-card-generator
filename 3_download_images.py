from __future__ import annotations
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

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
OUTPUT_BASE = CONFIG.get("output_dir", "FluentForever_Output")
BATCH_WORDS = int(os.getenv("BATCH_WORDS", "5"))

# Load environment (.env at repository root)
load_dotenv(Path(__file__).parent.parent / ".env")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "").strip()

# ========== FILE PATHS ============
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / OUTPUT_BASE
IMAGE_DIR = OUTPUT_DIR / "images"
WORKING_DATA = OUTPUT_DIR / "working_data.xlsx"
TRACKING_FILE = Path(CONFIG.get("frequency_file"))

print(f"\n{'='*60}")
print(f"DOWNLOADING IMAGES FOR: {LANGUAGE_NAME}")
print(f"{'='*60}")
print(f"Language Code: {LANGUAGE_CODE}")
print(f"Output Directory: {OUTPUT_DIR}")
print(f"{'='*60}\n")

# Create directories
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def download_image(search_terms: list[str], outfile: Path, max_retries: int = 3) -> bool:
    """
    Download a thumbnail image from Pexels trying each search term until one succeeds.
    
    Safety Features:
    - Max 3 retry attempts per search term (prevents infinite loops)
    - Detects rate limit errors (429) and stops immediately
    - Respectful delays between requests
    
    Args:
        search_terms: List of search terms to try
        outfile: Output file path
        max_retries: Maximum retry attempts per term (default: 3)
    
    Returns: True if successful, False otherwise
    """
    if not PEXELS_API_KEY:
        print("❌ PEXELS_API_KEY missing. Set it in your .env file.")
        return False

    headers = {"Authorization": PEXELS_API_KEY}

    for term in search_terms:
        params = {"query": term, "per_page": 1}
        
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 4s, 8s, 16s
                    print(f"  ⏳ Retry {attempt}/{max_retries} after {wait_time}s...")
                    time.sleep(wait_time)
                
                resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=15)
            except requests.RequestException as exc:  # noqa: BLE001
                print(f"  Error calling Pexels for '{term}': {exc}")
                if attempt == max_retries:
                    break  # Try next search term
                continue

            if resp.status_code == 429:
                print(f"  ⚠️  RATE LIMIT HIT (429) - Stopping to protect your account")
                print(f"  💡 Pexels free tier: ~200 requests/hour")
                return False  # Stop completely on rate limit
            
            if resp.status_code != 200:
                print(f"  Pexels error for '{term}': HTTP {resp.status_code} - {resp.text[:200]}")
                if attempt == max_retries:
                    break  # Try next search term
                continue

            data = resp.json()
            photos = data.get("photos", [])
            if not photos:
                print(f"  No images found for query '{term}'")
                if attempt == max_retries:
                    break  # Try next search term
                continue

            src = photos[0].get("src", {})
            image_url = src.get("tiny") or src.get("small") or src.get("medium")
            if not image_url:
                print(f"  No usable image URLs for '{term}'")
                if attempt == max_retries:
                    break  # Try next search term
                continue

            try:
                img_resp = requests.get(image_url, timeout=15)
            except requests.RequestException as exc:  # noqa: BLE001
                print(f"  Error downloading image for '{term}': {exc}")
                if attempt == max_retries:
                    break  # Try next search term
                continue

            if img_resp.status_code != 200 or len(img_resp.content) < 2048:
                print(f"  Invalid image response for '{term}' (status {img_resp.status_code}, size {len(img_resp.content)})")
                if attempt == max_retries:
                    break  # Try next search term
                continue

            outfile.write_bytes(img_resp.content)
            print(f"  Saved image -> {outfile.name} ({len(img_resp.content)} bytes) [query: '{term}']")
            return True

    return False


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


def all_images_present(files: list[Path]) -> bool:
    """Check if all image files exist and have reasonable size"""
    for f in files:
        if not f.exists():
            return False
        if f.stat().st_size <= 1024:
            return False
    return True


def update_working_data_images(word: str, freq_num: int) -> None:
    """Update Image column in working_data.xlsx"""
    df = pd.read_excel(WORKING_DATA)
    if "Image" in df.columns:
        df["Image"] = df["Image"].astype("string")
    pattern = f"{freq_num:04d}_{word}_"
    mask = df["File Name"].str.startswith(pattern, na=False)
    
    for idx in df[mask].index:
        file_name = df.at[idx, "File Name"]
        df.at[idx, "Image"] = f"<img src=\"{file_name}.jpg\">"
    
    df.to_excel(WORKING_DATA, index=False)
    print(f"Updated Image column in {WORKING_DATA.name}")


def update_images_count(freq_num: int, count: int) -> None:
    """Update Images column count in tracking file"""
    df_track = ensure_columns(pd.read_excel(TRACKING_FILE))
    idx = freq_num - 1
    if 0 <= idx < len(df_track):
        df_track.at[idx, "Images"] = count
        df_track.to_excel(TRACKING_FILE, index=False)
        print(f"✅ Updated Images={count}/10 for freq #{freq_num} in {TRACKING_FILE.name}")


def main() -> None:
    """
    Main workflow:
    1. Load working_data.xlsx
    2. Find first word with audio but no images yet
    3. Search for images on Pexels using the English translation (thumbnail only)
    4. Download first relevant image for each sentence
    5. Update Image column with <img src="filename.jpg"> tags
    """
    # Verify input file exists
    if not WORKING_DATA.exists():
        print(f"Error: {WORKING_DATA} not found.")
        print("   Run script 2 first to download audio.")
        sys.exit(1)

    if not TRACKING_FILE.exists():
        print(f"Error: {TRACKING_FILE} not found.")
        print("   Run script 1/2 first to populate the frequency list.")
        sys.exit(1)

    if not PEXELS_API_KEY:
        print("❌ Missing PEXELS_API_KEY. Set it in your .env file before running.")
        sys.exit(1)

    df = pd.read_excel(WORKING_DATA)
    df_track = ensure_columns(pd.read_excel(TRACKING_FILE))

    processed_count = 0

    # Iterate over tracking file to decide which words need images
    for track_idx in df_track.index:
        if processed_count >= BATCH_WORDS:
            print(f"⏸️ Reached batch limit ({BATCH_WORDS} words). Run again for more.")
            break

        audio_count = int(df_track.at[track_idx, "Audio"])
        images_count = int(df_track.at[track_idx, "Images"])

        # Only process if audio exists and images are incomplete
        if audio_count > 0 and images_count < 10:
            freq_num = track_idx + 1
            pattern_prefix = f"{freq_num:04d}_"
            word_rows = df[df["File Name"].str.startswith(pattern_prefix, na=False)]
            if word_rows.empty:
                continue

            first_row = word_rows.iloc[0]
            file_name = first_row["File Name"]
            parts = file_name.split("_")
            if len(parts) < 3:
                continue
            word = "_".join(parts[1:-1])

            processed_count += 1

            print(f"Processing word: '{word}' (frequency #{freq_num})")
            print(f"   Sentences to download images for: {len(word_rows)}")

            target_files: list[Path] = []

            for _, row in word_rows.iterrows():
                file_name = row["File Name"]
                english_translation = str(row.get("English Translation", "")).strip()

                search_terms: list[str] = []
                if english_translation:
                    search_terms.append(english_translation)
                    tokens = [t.strip(".,!?;:") for t in english_translation.split() if t.strip(".,!?;:")]
                    if len(tokens) >= 2:
                        last_two = " ".join(tokens[-2:])
                        if last_two not in search_terms:
                            search_terms.append(last_two)
                    if tokens:
                        last_one = tokens[-1]
                        if last_one not in search_terms:
                            search_terms.append(last_one)
                if word not in search_terms:
                    search_terms.append(word)

                filename = f"{file_name}.jpg"
                outfile = IMAGE_DIR / filename
                target_files.append(outfile)

                if outfile.exists() and outfile.stat().st_size > 1500:
                    print(f"  Skipping existing: {outfile.name}")
                    continue

                print(f"  Downloading image for: {search_terms[0]} -> {filename}")
                ok = download_image(search_terms, outfile)
                if ok:
                    time.sleep(0.5)

            if all_images_present(target_files):
                update_working_data_images(word, freq_num)
                update_images_count(freq_num, len(target_files))
                print(f"Image download complete for '{word}' ({len(target_files)}/10)! Ready for script 4\n")
            else:
                actual_count = sum(1 for f in target_files if f.exists() and f.stat().st_size > 1024)
                update_images_count(freq_num, actual_count)
                print(f"⚠️ Image download incomplete for '{word}' ({actual_count}/{len(target_files)} files)")

    print("✅ Image step finished for this batch.")


if __name__ == "__main__":
    main()

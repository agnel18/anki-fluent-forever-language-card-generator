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

# Load environment (.env at repository root)
load_dotenv(Path(__file__).parent.parent / ".env")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "").strip()

# ========== FILE PATHS ==========
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / OUTPUT_BASE
IMAGE_DIR = OUTPUT_DIR / "images"
WORKING_DATA = OUTPUT_DIR / "working_data.xlsx"

print(f"\n{'='*60}")
print(f"DOWNLOADING IMAGES FOR: {LANGUAGE_NAME}")
print(f"{'='*60}")
print(f"Language Code: {LANGUAGE_CODE}")
print(f"Output Directory: {OUTPUT_DIR}")
print(f"{'='*60}\n")

# Create directories
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def download_image(search_terms: list[str], outfile: Path) -> bool:
    """Download a thumbnail image from Pexels trying each search term until one succeeds."""
    if not PEXELS_API_KEY:
        print("❌ PEXELS_API_KEY missing. Set it in your .env file.")
        return False

    headers = {"Authorization": PEXELS_API_KEY}

    for term in search_terms:
        params = {"query": term, "per_page": 1}
        try:
            resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=15)
        except requests.RequestException as exc:  # noqa: BLE001
            print(f"  Error calling Pexels for '{term}': {exc}")
            continue

        if resp.status_code != 200:
            print(f"  Pexels error for '{term}': HTTP {resp.status_code} - {resp.text[:200]}")
            continue

        data = resp.json()
        photos = data.get("photos", [])
        if not photos:
            print(f"  No images found for query '{term}'")
            continue

        src = photos[0].get("src", {})
        image_url = src.get("tiny") or src.get("small") or src.get("medium")
        if not image_url:
            print(f"  No usable image URLs for '{term}'")
            continue

        try:
            img_resp = requests.get(image_url, timeout=15)
        except requests.RequestException as exc:  # noqa: BLE001
            print(f"  Error downloading image for '{term}': {exc}")
            continue

        if img_resp.status_code != 200 or len(img_resp.content) < 2048:
            print(f"  Invalid image response for '{term}' (status {img_resp.status_code}, size {len(img_resp.content)})")
            continue

        outfile.write_bytes(img_resp.content)
        print(f"  Saved image -> {outfile.name} ({len(img_resp.content)} bytes) [query: '{term}']")
        return True

    return False


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

    if not PEXELS_API_KEY:
        print("❌ Missing PEXELS_API_KEY. Set it in your .env file before running.")
        sys.exit(1)

    # Load working data
    df = pd.read_excel(WORKING_DATA)
    
    # Find first word that needs images (Image column is empty)
    processed_words = set()
    
    for idx in df.index:
        if pd.isna(df.at[idx, "Image"]) or df.at[idx, "Image"] == "":
            file_name = df.at[idx, "File Name"]
            # Extract word from filename pattern: 0001_word_01
            parts = file_name.split("_")
            if len(parts) >= 2:
                freq_num = parts[0]
                word = "_".join(parts[1:-1])  # Handle multi-part words
                
                if word not in processed_words:
                    processed_words.add(word)
                    
                    # Get all sentence rows for this word
                    pattern = f"{freq_num}_{word}_"
                    word_mask = df["File Name"].str.startswith(pattern, na=False)
                    word_rows = df[word_mask]
                    
                    print(f"Processing word: '{word}' (frequency #{freq_num})")
                    print(f"   Sentences to download images for: {len(word_rows)}")
                    
                    # Download image for each sentence
                    target_files: list[Path] = []
                    
                    for _, row in word_rows.iterrows():
                        file_name = row["File Name"]
                        # Use English translation as the search query (better results), fallback to word
                        english_translation = str(row.get("English Translation", "")).strip()

                        # Build a small set of fallbacks: full translation, last two words, last word, then the base word
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
                            time.sleep(0.5)  # Gentle rate limit for Pexels

                    # Update working data if all images present
                    if all_images_present(target_files):
                        update_working_data_images(word, int(freq_num))
                        print(f"Image download complete for '{word}'!")
                        print(f"   Ready for script 4 (create Anki cards)\n")
                    else:
                        print(f"Image download incomplete for '{word}' (some files missing)")
                    
                    return  # Process one word at a time

    print("All words have images! Nothing more to do.")


if __name__ == "__main__":
    main()

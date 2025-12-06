from __future__ import annotations
import sys
import time
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import requests

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
FREQUENCY_FILE = Path(CONFIG.get("frequency_file"))
OUTPUT_BASE = CONFIG.get("output_dir", "FluentForever_Output")

# ========== FILE PATHS ==========
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / OUTPUT_BASE
AUDIO_DIR = OUTPUT_DIR / "audio"
WORKING_DATA = OUTPUT_DIR / "working_data.xlsx"

print(f"\n{'='*60}")
print(f"🌍 DOWNLOADING AUDIO FOR: {LANGUAGE_NAME}")
print(f"{'='*60}")
print(f"Language Code: {LANGUAGE_CODE}")
print(f"Output Directory: {OUTPUT_DIR}")
print(f"{'='*60}\n")

# Create directories
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def safe_word(word: str) -> str:
    """Clean word for filenames"""
    return word.replace("/", "-").replace("\\", "-").strip()


def build_driver() -> webdriver.Chrome:
    """Create Selenium WebDriver for Chrome automation"""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver
    except Exception as exc:
        print(f"Error creating Chrome driver: {exc}")
        raise


def download_audio(driver: webdriver.Chrome, text: str, outfile: Path) -> bool:
    """Download audio for a sentence from soundoftext.com"""
    try:
        print(f"    Opening soundoftext.com...")
        driver.get("https://soundoftext.com/")
        wait = WebDriverWait(driver, 20)

        print(f"    Finding text input...")
        textarea = wait.until(EC.presence_of_element_located((By.NAME, "text")))
        textarea.clear()
        textarea.send_keys(text)

        print(f"    Setting language to {LANGUAGE_NAME}...")
        voice_select = wait.until(EC.presence_of_element_located((By.NAME, "voice")))
        voice_select.send_keys(LANGUAGE_NAME)
        voice_select.send_keys(Keys.RETURN)

        print(f"    Clicking submit...")
        submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
        try:
            submit_btn.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", submit_btn)

        print(f"    Waiting for download link to appear...")
        time.sleep(3)
        download_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.card__action[download][href]")))
        mp3_url = download_link.get_attribute("href")
        
        if not mp3_url:
            print("  Error: Download link href missing")
            return False
        
        print(f"    Downloading MP3 from URL...")
        mp3 = requests.get(mp3_url, timeout=20)
        if mp3.status_code != 200:
            print(f"  Error: HTTP {mp3.status_code}")
            return False
            
        outfile.write_bytes(mp3.content)
        print(f"  ✓ Saved audio -> {outfile.name} ({len(mp3.content)} bytes)")
        return True
    except Exception as exc:
        import traceback
        print(f"  Error downloading audio: {exc}")
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
    3. Download audio from soundoftext.com for each sentence
    4. Update Sound column with [sound:filename.mp3] tags
    5. Mark word as audio_done
    """
    # Verify input file exists
    if not WORKING_DATA.exists():
        print(f"❌ Error: {WORKING_DATA} not found.")
        print("   Run script 1 first to generate sentences.")
        sys.exit(1)

    # Load working data
    df = pd.read_excel(WORKING_DATA)
    
    # Find first word that needs audio (Sound column is empty)
    # Group by File Name prefix to get unique words
    processed_words = set()
    
    for idx in df.index:
        if pd.isna(df.at[idx, "Sound"]) or df.at[idx, "Sound"] == "":
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
                    
                    print(f"📝 Processing word: '{word}' (frequency #{freq_num})")
                    print(f"   Sentences to download: {len(word_rows)}")
                    
                    # Download audio for each sentence
                    driver = build_driver()
                    target_files: list[Path] = []
                    
                    try:
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
                            ok = download_audio(driver, sentence, outfile)
                            if ok:
                                time.sleep(1.5)  # Rate limiting
                    finally:
                        driver.quit()

                    # Update working data if all audio present
                    if all_audio_present(target_files):
                        update_working_data_audio(word, int(freq_num))
                        print(f"✅ Audio complete for '{word}'!")
                        print(f"   Ready for script 3 (download images)\n")
                    else:
                        print(f"❌ Audio incomplete for '{word}' (some files missing)")
                    
                    return  # Process one word at a time

    print("✅ All words have audio! Nothing more to do.")


if __name__ == "__main__":
    main()

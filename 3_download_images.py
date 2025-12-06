from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

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

# ========== FILE PATHS ==========
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / OUTPUT_BASE  # All output
AUDIO_DIR = OUTPUT_DIR / "audio"  # For reference (not used in this script)
IMAGE_DIR = OUTPUT_DIR / "images"  # Where JPG images are saved
WORKING_DATA = OUTPUT_DIR / "working_data.xlsx"  # Source data with sentences

print(f"\n{'='*60}")
print(f"🌍 DOWNLOADING IMAGES FOR: {LANGUAGE_NAME}")
print(f"{'='*60}")
print(f"Language Code: {LANGUAGE_CODE}")
print(f"Output Directory: {OUTPUT_DIR}")
print(f"{'='*60}\n")

# Create directories if they don't exist
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure Status column exists in tracking spreadsheet."""
    if "Status" not in df.columns:
        df["Status"] = ""
    df["Status"] = df["Status"].fillna("")
    return df


def safe_word(word: str) -> str:
    """Clean word for use in filenames (replace special chars)."""
    return word.replace("/", "-").replace("\\", "-").strip()


def get_word_rows(word: str, freq_num: int) -> pd.DataFrame:
    """
    Load the 5 sentence rows for this word from working_data.xlsx.
    Filters rows by file name pattern {freq:04d}_{word}_*
    """
    if not WORKING_DATA.exists():
        print(f"Error: {WORKING_DATA} not found. Run script 1 first.")
        sys.exit(1)
    df = pd.read_excel(WORKING_DATA)
    # Find rows matching this word's file name pattern
    pattern = f"{freq_num:04d}_{word}_"
    mask = df["File Name"].str.startswith(pattern, na=False)
    return df[mask]


def build_driver() -> webdriver.Chrome:
    """
    Create a Selenium WebDriver instance for Chrome automation.
    Uses ChromeDriverManager to automatically download compatible ChromeDriver.
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def download_image_for_sentence(driver: webdriver.Chrome, sentence: str, outfile: Path) -> bool:
    """
    Download a clean image (without text) for a sentence from Google Images.
    
    Strategy:
    1. Search Google Images with "pure image" keyword + photo type filter
    2. Try multiple image results (first 5) to find one without text
    3. Extract the image URL and download it
    4. Save to outfile
    
    Returns True if successful, False if failed
    """
    try:
        # Use "pure image" keyword to tell Google to filter for text-free images
        # Also filter by type=photo to get actual photos, not diagrams/charts
        search_query = f"{sentence} pure image"
        search_url = f"https://www.google.com/search?q={search_query}&tbm=isch&tbs=itp:photo"
        driver.get(search_url)
        wait = WebDriverWait(driver, 15)  # Wait up to 15 seconds
        time.sleep(2)  # Wait for page to load
        
        # Try multiple CSS selectors for finding image thumbnails
        # (Google changes these frequently, so we try multiple)
        selectors = [
            "img.rg_i",  # Common class for image thumbnails
            "img.Q4LuWd",  # Alternative class
            "div.H8Rx8c img",  # Image inside container
            "div[data-ri] img",  # Data-indexed images
        ]
        
        thumbnails = None
        # Try each selector until we find thumbnails
        for selector in selectors:
            try:
                thumbnails = driver.find_elements(By.CSS_SELECTOR, selector)
                if thumbnails and len(thumbnails) > 0:
                    break  # Found thumbnails, use this selector
            except Exception:  # noqa: BLE001
                continue  # Try next selector
        
        if not thumbnails or len(thumbnails) == 0:
            print("  Error: No thumbnails found")
            return False
        
        # Try first 5 image results to find one that downloads successfully
        for idx in range(min(5, len(thumbnails))):
            try:
                thumb = thumbnails[idx]
                src = thumb.get_attribute("src")  # Get the image URL

                
                # If src is base64 or data URL, try clicking to load full image
                if not src or not src.startswith("http"):
                    try:
                        thumb.click()
                        time.sleep(1)
                        large_img = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img.sFlh5c, img.n3VNCb")))
                        src = large_img.get_attribute("src")
                    except Exception:  # noqa: BLE001
                        continue
                
                if not src or not src.startswith("http"):
                    continue
                
                img_data = requests.get(src, timeout=20)
                if img_data.status_code == 200 and len(img_data.content) > 500:
                    outfile.write_bytes(img_data.content)
                    print(f"  Saved image -> {outfile}")
                    return True
            except Exception:  # noqa: BLE001
                continue
        
        print("  Error: Could not download any valid images")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"  Error downloading image: {exc}")
        return False


def all_images_present(files: list[Path]) -> bool:
    return all(f.exists() and f.stat().st_size > 0 for f in files)


def main() -> None:
    if not EXCEL_FILE.exists():
        print(f"Error: Excel file not found at {EXCEL_FILE}")
        sys.exit(1)

    df = ensure_columns(pd.read_excel(EXCEL_FILE))
    todo = df[df["Status"] == "audio_done"]
    if todo.empty:
        print("No rows with Status=audio_done. Nothing to do.")
        return

    idx = todo.index[0]
    word_raw = df.loc[idx, "Arabic Word"]
    word = safe_word(str(word_raw))
    freq_num = idx + 1
    print(f"Starting image download for '{word}' (freq #{freq_num})")

    word_rows = get_word_rows(word, freq_num)
    if word_rows.empty:
        print(f"Critical: No rows found in working_data.xlsx for word '{word}'. Run script 1 first.")
        return

    driver = build_driver()
    target_files: list[Path] = []

    try:
        for _, row in word_rows.iterrows():
            file_name = row["File Name"]
            english = row["English Sentence"]
            filename = f"{file_name}.jpg"
            outfile = IMAGE_DIR / filename
            target_files.append(outfile)

            if outfile.exists() and outfile.stat().st_size > 0:
                print(f"  Skipping existing image (OK): {outfile.name}")
                continue

            print(f"  Downloading image: {english} -> {filename}")
            download_image_for_sentence(driver, english, outfile)
            time.sleep(1.5)
    finally:
        driver.quit()

    if all_images_present(target_files):
        # Update working_data.xlsx with image references
        work_df = pd.read_excel(WORKING_DATA)
        pattern = f"{freq_num:04d}_{word}_"
        mask = work_df["File Name"].str.startswith(pattern, na=False)
        for idx_work in work_df[mask].index:
            file_name = work_df.at[idx_work, "File Name"]
            work_df.at[idx_work, "Image"] = f'<img src="{file_name}.jpg">'
        work_df.to_excel(WORKING_DATA, index=False)
        print(f"Updated Image column in {WORKING_DATA.name}")
        
        df.at[idx, "Status"] = "images_done"
        df.to_excel(EXCEL_FILE, index=False)
        print(f"Images complete for '{word}'. Status set to images_done.")
    else:
        print("Images incomplete (some files missing). Status not updated.")


if __name__ == "__main__":
    main()

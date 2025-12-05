from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

# ========== CONFIG: File paths and settings ==========
BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = BASE_DIR / "Arabic Frequency Word List.xlsx"  # Tracking file
OUTPUT_DIR = BASE_DIR / "FluentForever_Arabic_Perfect"  # All output
AUDIO_DIR = OUTPUT_DIR / "audio"  # Where MP3 files are saved
IMAGE_DIR = OUTPUT_DIR / "images"  # For reference (not used in this script)
WORKING_DATA = OUTPUT_DIR / "working_data.xlsx"  # Source data with sentences

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
    options.add_argument("--start-maximized")  # Open maximized
    options.add_argument("--disable-extensions")  # Disable browser extensions
    # Not using headless mode so you can see what's happening
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver
    except Exception as exc:
        print(f"Error creating Chrome driver: {exc}")
        raise


def download_audio(driver: webdriver.Chrome, text: str, outfile: Path) -> bool:
    """
    Download Arabic audio for a sentence from soundoftext.com.
    
    Steps:
    1. Navigate to soundoftext.com
    2. Fill in the Arabic text
    3. Select Arabic as language
    4. Submit to generate audio
    5. Wait for download link to appear
    6. Extract URL and download MP3
    7. Save to outfile path
    
    Returns True if successful, False if failed
    """
    try:
        print(f"    Opening soundoftext.com...")
        driver.get("https://soundoftext.com/")
        wait = WebDriverWait(driver, 20)  # Wait up to 20 seconds for elements

        print(f"    Finding text input...")
        # Find the text input field by name="text"
        textarea = wait.until(EC.presence_of_element_located((By.NAME, "text")))
        textarea.clear()
        textarea.send_keys(text)  # Type the Arabic sentence

        print(f"    Setting language to Arabic...")
        # Select Arabic from the language dropdown
        voice_select = wait.until(EC.presence_of_element_located((By.NAME, "voice")))
        voice_select.send_keys("Arabic")  # Type "Arabic"
        voice_select.send_keys(Keys.RETURN)  # Select it

        print(f"    Clicking submit...")
        # Find and click the submit button
        submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)  # Scroll into view
        try:
            submit_btn.click()
        except ElementClickInterceptedException:
            # If normal click fails (e.g., ad overlay), use JavaScript click
            driver.execute_script("arguments[0].click();", submit_btn)

        print(f"    Waiting for download link to appear...")
        time.sleep(3)  # Wait for audio generation
        
        # Find the download link with href attribute (appears after generation)
        download_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.card__action[download][href]")))
        mp3_url = download_link.get_attribute("href")  # Extract URL
        
        if not mp3_url:
            print("  Error: Download link href missing")
            return False
        
        print(f"    Downloading MP3 from URL...")
        # Download the MP3 file using requests (no browser needed)
        mp3 = requests.get(mp3_url, timeout=20)
        if mp3.status_code != 200:
            print(f"  Error: HTTP {mp3.status_code}")
            return False
            
        # Save MP3 to disk
        outfile.write_bytes(mp3.content)
        print(f"  ✓ Saved audio -> {outfile.name} ({len(mp3.content)} bytes)")
        return True
    except Exception as exc:  # noqa: BLE001
        import traceback
        print(f"  Error downloading audio: {exc}")
        print(f"  Details: {traceback.format_exc()[:200]}")
        return False


def all_audio_present(files: list[Path]) -> bool:
    """Check that all expected audio files exist and have reasonable size."""
    for f in files:
        if not f.exists():
            return False
        if f.stat().st_size <= 1024:  # File should be > 1KB
            return False
    return True


def update_working_data_audio(word: str, freq_num: int) -> None:
    """
    Update the Sound column in working_data.xlsx for this word's rows.
    Sound format: [sound:filename.mp3] (Anki tag format)
    """
    df = pd.read_excel(WORKING_DATA)
    pattern = f"{freq_num:04d}_{word}_"
    mask = df["File Name"].str.startswith(pattern, na=False)
    
    # Add sound tag to each row for this word
    for idx in df[mask].index:
        file_name = df.at[idx, "File Name"]
        df.at[idx, "Sound"] = f"[sound:{file_name}.mp3]"
    
    df.to_excel(WORKING_DATA, index=False)
    print(f"Updated Sound column in {WORKING_DATA.name}")


def main() -> None:
    """
    Main workflow:
    1. Find first word with Status="sentences_done" (from script 1)
    2. Get its 5 sentence rows from working_data.xlsx
    3. For each sentence, download audio from soundoftext.com
    4. Update Sound column with [sound:filename.mp3] tags
    5. Update Status to "audio_done" so script 3 can process it
    """
    # Check that tracking file exists
    if not EXCEL_FILE.exists():
        print(f"Error: Excel file not found at {EXCEL_FILE}")
        sys.exit(1)

    # Load tracking spreadsheet
    df = ensure_columns(pd.read_excel(EXCEL_FILE))
    
    # Find words ready for audio (Status="sentences_done")
    todo = df[df["Status"] == "sentences_done"]
    if todo.empty:
        print("No rows with Status=sentences_done. Nothing to do.")
        return

    # Get the first word to process
    idx = todo.index[0]
    word_raw = df.loc[idx, "Arabic Word"]
    word = safe_word(str(word_raw))
    freq_num = idx + 1  # Position in frequency list
    print(f"Starting audio download for '{word}' (freq #{freq_num})")
    print(f"Audio files will be saved to: {AUDIO_DIR.absolute()}")

    # Get the 5 sentence rows for this word
    word_rows = get_word_rows(word, freq_num)
    if word_rows.empty:
        print(f"Critical: No rows found in working_data.xlsx for word '{word}'. Run script 1 first.")
        return

    # Create Chrome driver for automation
    driver = build_driver()
    success_flags: list[bool] = []
    target_files: list[Path] = []

    try:
        # Process each of the 5 sentences
        for _, row in word_rows.iterrows():
            file_name = row["File Name"]
            arabic = row["Arabic Sentence"]
            filename = f"{file_name}.mp3"
            outfile = AUDIO_DIR / filename
            target_files.append(outfile)

            # Skip if audio already downloaded
            if outfile.exists() and outfile.stat().st_size > 1024:
                print(f"  Skipping existing audio (OK): {outfile.name}")
                success_flags.append(True)
                continue

            print(f"  Downloading audio: {arabic} -> {filename}")
            ok = download_audio(driver, arabic, outfile)
            success_flags.append(ok)
            time.sleep(1.5)  # Rate limiting to be nice to the server
    finally:
        # Always close browser, even if error occurred
        driver.quit()

    # Check if all audio files were successfully downloaded
    if all_audio_present(target_files):
        # Update working_data.xlsx with Sound column
        update_working_data_audio(word, freq_num)
        # Mark this word as processed
        df.at[idx, "Status"] = "audio_done"
        df.to_excel(EXCEL_FILE, index=False)
        print(f"Audio complete for '{word}'. Status set to audio_done.")
    else:
        print("Audio incomplete (some files missing or too small). Status not updated.")


if __name__ == "__main__":
    main()


def download_audio(driver: webdriver.Chrome, text: str, outfile: Path) -> bool:
    try:
        print(f"    Opening soundoftext.com...")
        driver.get("https://soundoftext.com/")
        wait = WebDriverWait(driver, 20)

        print(f"    Finding text input...")
        textarea = wait.until(EC.presence_of_element_located((By.NAME, "text")))
        textarea.clear()
        textarea.send_keys(text)

        print(f"    Setting language to Arabic...")
        voice_select = wait.until(EC.presence_of_element_located((By.NAME, "voice")))
        voice_select.send_keys("Arabic")
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
        # Wait for the download link to appear with the href attribute
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
    except Exception as exc:  # noqa: BLE001
        import traceback
        print(f"  Error downloading audio: {exc}")
        print(f"  Details: {traceback.format_exc()[:200]}")
        return False


def all_audio_present(files: list[Path]) -> bool:
    for f in files:
        if not f.exists():
            return False
        if f.stat().st_size <= 1024:
            return False
    return True


def update_working_data_audio(word: str, freq_num: int) -> None:
    """Update Sound column in working_data.xlsx for this word's rows"""
    df = pd.read_excel(WORKING_DATA)
    pattern = f"{freq_num:04d}_{word}_"
    mask = df["File Name"].str.startswith(pattern, na=False)
    
    for idx in df[mask].index:
        file_name = df.at[idx, "File Name"]
        df.at[idx, "Sound"] = f"[sound:{file_name}.mp3]"
    
    df.to_excel(WORKING_DATA, index=False)
    print(f"Updated Sound column in {WORKING_DATA.name}")


def main() -> None:
    if not EXCEL_FILE.exists():
        print(f"Error: Excel file not found at {EXCEL_FILE}")
        sys.exit(1)

    df = ensure_columns(pd.read_excel(EXCEL_FILE))
    todo = df[df["Status"] == "sentences_done"]
    if todo.empty:
        print("No rows with Status=sentences_done. Nothing to do.")
        return

    idx = todo.index[0]
    word_raw = df.loc[idx, "Arabic Word"]
    word = safe_word(str(word_raw))
    freq_num = idx + 1
    print(f"Starting audio download for '{word}' (freq #{freq_num})")
    print(f"Audio files will be saved to: {AUDIO_DIR.absolute()}")

    word_rows = get_word_rows(word, freq_num)
    if word_rows.empty:
        print(f"Critical: No rows found in working_data.xlsx for word '{word}'. Run script 1 first.")
        return

    driver = build_driver()
    success_flags: list[bool] = []
    target_files: list[Path] = []

    try:
        for _, row in word_rows.iterrows():
            file_name = row["File Name"]
            arabic = row["Arabic Sentence"]
            filename = f"{file_name}.mp3"
            outfile = AUDIO_DIR / filename
            target_files.append(outfile)

            if outfile.exists() and outfile.stat().st_size > 1024:
                print(f"  Skipping existing audio (OK): {outfile.name}")
                success_flags.append(True)
                continue

            print(f"  Downloading audio: {arabic} -> {filename}")
            ok = download_audio(driver, arabic, outfile)
            success_flags.append(ok)
            time.sleep(1.5)
    finally:
        driver.quit()

    if all_audio_present(target_files):
        update_working_data_audio(word, freq_num)
        df.at[idx, "Status"] = "audio_done"
        df.to_excel(EXCEL_FILE, index=False)
        print(f"Audio complete for '{word}'. Status set to audio_done.")
    else:
        print("Audio incomplete (some files missing or too small). Status not updated.")


if __name__ == "__main__":
    main()

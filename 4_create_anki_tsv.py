from __future__ import annotations
import sys
from pathlib import Path

import pandas as pd

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
EXCEL_FILE = FREQUENCY_FILE  # Tracking file with Status
OUTPUT_DIR = BASE_DIR / OUTPUT_BASE  # All output directory
WORKING_DATA = OUTPUT_DIR / "working_data.xlsx"  # Source data (with sentences, audio, images)
ANKI_TSV = OUTPUT_DIR / "ANKI_IMPORT.tsv"  # Final output: Anki import file (tab-separated)

print(f"\n{'='*60}")
print(f"🌍 CREATING ANKI CARDS FOR: {LANGUAGE_NAME}")
print(f"{'='*60}")
print(f"Language Code: {LANGUAGE_CODE}")
print(f"Output Directory: {OUTPUT_DIR}")
print(f"{'='*60}\n")

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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


def main() -> None:
    """
    Main workflow:
    1. Find all words with Status="images_done" (fully processed by scripts 1-3)
    2. Load working_data.xlsx with all rows
    3. Filter to rows with both Sound and Image populated
    4. Export to TSV format for Anki import
    5. Mark all processed words as "complete"
    
    TSV Format:
    - Tab-separated values (not comma-separated)
    - Header row with column names
    - Data rows with sentence information
    - Sound: [sound:filename.mp3] format
    - Image: <img src="filename.jpg"> format
    """
    # Verify input files exist
    if not EXCEL_FILE.exists():
        print(f"Error: Excel file not found at {EXCEL_FILE}")
        sys.exit(1)

    if not WORKING_DATA.exists():
        print(f"Error: {WORKING_DATA} not found. Run scripts 1-3 first.")
        sys.exit(1)

    # Load tracking spreadsheet to find completed words (Images >= 10)
    df_tracking = ensure_columns(pd.read_excel(EXCEL_FILE))
    
    # Load all data rows from working_data.xlsx
    df_work = pd.read_excel(WORKING_DATA)
    
    # Filter to rows that have BOTH Sound AND Image populated (fully complete)
    # Only export rows where both columns are filled and non-empty
    completed = df_work[(df_work["Sound"].notna()) & (df_work["Sound"] != "") & 
                        (df_work["Image"].notna()) & (df_work["Image"] != "")]
    
    if completed.empty:
        print("No completed rows in working_data.xlsx to export.")
        return

    # Export to TSV (tab-separated values) format that Anki can import
    # Anki expects tab-separated values with headers
    completed.to_csv(ANKI_TSV, sep="\t", index=False, encoding="utf-8")
    print(f"✅ Exported {len(completed)} rows to {ANKI_TSV}")
    print(f"\n📊 Summary:")
    
    # Show completion counts for each word
    for idx in df_tracking.index:
        sentences = df_tracking.at[idx, "Sentences"]
        audio = df_tracking.at[idx, "Audio"]
        images = df_tracking.at[idx, "Images"]
        if sentences > 0 or audio > 0 or images > 0:
            print(f"   Word #{idx+1}: Sentences={sentences}/10 | Audio={audio}/10 | Images={images}/10}")
    print(f"Marked {len(todo)} words as complete in {EXCEL_FILE.name}")


if __name__ == "__main__":
    main()

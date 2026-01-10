"""
Word Data Fetcher Module

Fetches enriched word data (meanings, usages, variations) from various APIs.
Supports Hindi (Shabdkosh), Arabic (Almaany), Chinese (MDBG), Spanish (WordReference), with Wiktionary fallback.

Output format: {"meaning": str, "usages": [str], "variations": [str], "source": str}
"""

import asyncio
import aiohttp
import requests
import time
import json
from typing import Optional, Dict

# Configuration
API_TIMEOUT = 10
MAX_RETRIES = 2

# In-memory cache: {(word, lang): data}
CACHE = {}

def fetch_from_main_source(word: str, lang: str) -> Optional[Dict]:
    """
    Fetch from main source for the language.
    Returns dict or None if failed.
    """
    if lang == "hi":
        return fetch_shabdkosh(word)
    elif lang == "ar":
        return fetch_almaany(word)
    elif lang == "zh":
        return fetch_mdbg(word)
    elif lang == "es":
        return fetch_wordreference(word)
    else:
        return None

def fetch_from_fallbacks(word: str, lang: str) -> Optional[Dict]:
    """
    Fetch from Wiktionary HTML scraping (more reliable than API).
    """
    return fetch_wiktionary(word, lang)

def aggregate_data(main: Optional[Dict], fallback: Optional[Dict]) -> Dict:
    """
    Aggregate: Use main if available and has real data, else fallback, else N/A.
    """
    def has_real_data(data: Dict) -> bool:
        """Check if the data has actual content, not just N/A"""
        return (data and
                data.get('meaning') and
                data.get('meaning') != 'N/A' and
                len(data.get('meaning', '')) > 2)

    if main and has_real_data(main):
        return main
    elif fallback and has_real_data(fallback):
        return fallback
    else:
        return {
            "meaning": "N/A",
            "usages": ["N/A"],
            "variations": ["N/A"],
            "source": "N/A"
        }

def fetch_word_data(word: str, lang: str) -> Dict:
    """
    Main function: Fetch with caching, retries, aggregation.
    """
    cache_key = (word, lang)
    if cache_key in CACHE:
        return CACHE[cache_key]

    main_data = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            main_data = fetch_from_main_source(word, lang)
            if main_data:
                break
        except Exception as e:
            print(f"Main source attempt {attempt + 1} failed: {e}")
            time.sleep(1)

    fallback_data = None
    # Check if main_data has real content, not just N/A
    def has_real_data(data):
        return (data and
                data.get('meaning') and
                data.get('meaning') != 'N/A' and
                len(data.get('meaning', '')) > 2)

    if not main_data or not has_real_data(main_data):
        for attempt in range(MAX_RETRIES + 1):
            try:
                fallback_data = fetch_from_fallbacks(word, lang)
                if fallback_data and has_real_data(fallback_data):
                    break
            except Exception as e:
                print(f"Fallback attempt {attempt + 1} failed: {e}")
                time.sleep(1)

    data = aggregate_data(main_data, fallback_data)
    CACHE[cache_key] = data
    return data

# API Implementations (placeholders - need to implement actual fetching)

def fetch_shabdkosh(word: str) -> Optional[Dict]:
    """
    Scrape from Shabdkosh website for Hindi.
    """
    from bs4 import BeautifulSoup
    url = f"https://www.shabdkosh.com/hi/translate/{word}/english-{word}-meaning"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(url, timeout=API_TIMEOUT, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract meaning
            meaning_elem = soup.find('div', class_='meaning')
            meaning = meaning_elem.text.strip() if meaning_elem else "N/A"
            
            # Extract usages/examples
            usage_elems = soup.find_all('div', class_='example')
            usages = [elem.text.strip() for elem in usage_elems[:3]] if usage_elems else ["N/A"]
            
            # Variations (hard to extract, maybe synonyms)
            variations = ["N/A"]
            
            return {
                "meaning": meaning,
                "usages": usages,
                "variations": variations,
                "source": "Shabdkosh"
            }
    except Exception as e:
        print(f"Shabdkosh scrape failed: {e}")
    return None

def fetch_almaany(word: str) -> Optional[Dict]:
    """
    Fetch from Almaany.
    TODO: Implement.
    """
    # Placeholder
    return None

def fetch_mdbg(word: str) -> Optional[Dict]:
    """
    Fetch from MDBG.
    TODO: Implement.
    """
    # Placeholder
    return None

def fetch_wordreference(word: str) -> Optional[Dict]:
    """
    Fetch from WordReference for Spanish.
    TODO: Implement.
    """
    # Placeholder - return None for now since we're focusing on Hindi
    return None

def fetch_wiktionary(word: str, lang: str) -> Optional[Dict]:
    """
    Fetch from Wiktionary using multiple approaches:
    1. Language-specific Wiktionary API (e.g., hi.wiktionary.org for Hindi)
    2. English Wiktionary API as fallback
    3. HTML scraping as last resort
    """
    from bs4 import BeautifulSoup

    # Proper User-Agent header (required by Wikimedia)
    headers = {
        'User-Agent': 'LanguageAnkiDeckGenerator/1.0 (educational app; contact@example.com) Python-requests/2.31.0'
    }

    # Try language-specific Wiktionary first
    lang_subdomains = {
        'hi': 'hi',  # Hindi
        'ar': 'ar',  # Arabic
        'zh': 'zh',  # Chinese
        'es': 'es',  # Spanish
        'fr': 'fr',  # French
        'de': 'de',  # German
    }

    subdomain = lang_subdomains.get(lang, 'en')

    # Try REST API first
    try:
        url = f"https://{subdomain}.wiktionary.org/api/rest_v1/page/definition/{word}"
        response = requests.get(url, timeout=API_TIMEOUT, headers=headers)

        if response.status_code == 200:
            data = response.json()
            # Look for language-specific definitions
            if lang in data and data[lang]:
                lang_defs = []
                for definition in data[lang][0].get("definitions", []):
                    # Clean HTML tags from definition
                    soup = BeautifulSoup(definition.get("definition", ""), 'html.parser')
                    clean_def = soup.get_text().strip()
                    if clean_def:
                        lang_defs.append(clean_def)

                if lang_defs:
                    meaning = lang_defs[0]
                    usages = lang_defs[1:3] if len(lang_defs) > 1 else ["N/A"]
                    variations = ["N/A"]  # Variations hard to extract
                    return {
                        "meaning": meaning,
                        "usages": usages,
                        "variations": variations,
                        "source": f"Wiktionary ({subdomain})"
                    }
    except Exception as e:
        print(f"Wiktionary REST API failed for {subdomain}: {e}")

    # Try English Wiktionary as fallback
    if lang != 'en':
        try:
            url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{word}"
            response = requests.get(url, timeout=API_TIMEOUT, headers=headers)

            if response.status_code == 200:
                data = response.json()
                # Look for any definitions (could be English or translations)
                for lang_code, lang_data in data.items():
                    if lang_data:
                        definitions = lang_data[0].get("definitions", [])
                        if definitions:
                            soup = BeautifulSoup(definitions[0].get("definition", ""), 'html.parser')
                            clean_def = soup.get_text().strip()
                            if clean_def:
                                return {
                                    "meaning": clean_def,
                                    "usages": ["N/A"],
                                    "variations": ["N/A"],
                                    "source": "Wiktionary (en)"
                                }
        except Exception as e:
            print(f"Wiktionary English fallback failed: {e}")

    # Last resort: Google Translate (most reliable fallback)
    try:
        from translate import Translator
        translator = Translator(to_lang='en')

        # Try to translate the word
        translation = translator.translate(word)

        if translation and len(translation) > 0:
            return {
                "meaning": translation,
                "usages": ["N/A"],
                "variations": ["N/A"],
                "source": "Google Translate"
            }
    except ImportError:
        print("Google Translate library not available")
    except Exception as e:
        print(f"Google Translate failed: {e}")

    return None

# Test function
if __name__ == "__main__":
    # Test with Hindi word
    result = fetch_word_data("में", "hi")
    print(json.dumps(result, indent=2, ensure_ascii=False))
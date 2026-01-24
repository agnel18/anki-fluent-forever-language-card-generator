# Image generation module
# Extracted from core_functions.py for better separation of concerns

import os
import logging
import requests
from pathlib import Path
from typing import Optional, List, Tuple, Dict

# Import error recovery
from streamlit_app.error_recovery import graceful_degradation

logger = logging.getLogger(__name__)

# ============================================================================
# IMAGE GENERATION (Google Custom Search)
# ============================================================================
@graceful_degradation("Image generation", continue_on_failure=True)
def generate_images_google(
    queries: List[str],
    output_dir: str,
    batch_name: str = "batch",
    num_images: int = 1,
    google_api_key: Optional[str] = None,
    custom_search_engine_id: Optional[str] = None,
    randomize: bool = True,
    exact_filenames: Optional[List[str]] = None,
    used_image_urls: Optional[set[str]] = None,
    unique_id: str = None,
) -> Tuple[List[str], set[str]]:
    """
    Download images from Google Custom Search.

    Args:
        queries: List of search queries (one per sentence)
        output_dir: Directory to save JPG files
        batch_name: Prefix for filenames
        num_images: Number of images per query (usually 1 for Anki)
        google_api_key: Google API key (same as Gemini)
        custom_search_engine_id: Google Custom Search Engine ID
        randomize: Randomize from top 3 results
        exact_filenames: Optional list of exact filenames to use
        used_image_urls: Set of already used image URLs to avoid duplicates

    Returns:
        Tuple of (list of generated file paths, updated used_image_urls set)
    """
    if not google_api_key:
        raise ValueError("Google API key required")
    if not custom_search_engine_id:
        raise ValueError("Google Custom Search Engine ID required")

    os.makedirs(output_dir, exist_ok=True)
    generated = []

    # Initialize or use provided used URLs set
    if used_image_urls is None:
        used_image_urls = set()

    google_logger = logging.getLogger("google_image_download")
    for i, query in enumerate(queries):
        try:
            google_logger.info(f"Google Custom Search for query: {query}")
            # --- API USAGE TRACKING ---
            try:
                import streamlit as st
                if "google_api_calls" not in st.session_state:
                    st.session_state.google_api_calls = 0
                st.session_state.google_api_calls += 1
            except Exception:
                pass
            # -------------------------
            # Search Google Custom Search
            # Convert comma-separated keywords to space-separated for Google
            search_query = " ".join(query.split(",")).strip()
            print(f"GOOGLE SEARCH QUERY FOR SENTENCE {i+1}: '{search_query}'")  # EXACT query sent to Google

            params = {
                "key": google_api_key,
                "cx": custom_search_engine_id,
                "q": search_query,
                "searchType": "image",
                "num": 10,  # Get top 10 results for fallback
                "safe": "active",  # Safe search
                "imgSize": "large",  # Prefer larger images
            }

            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            items = data.get("items", [])

            google_logger.info(f"Google hits for '{query}': {len(items)}")
            if not items:
                google_logger.warning(f"No images found for query: {query}")
                continue

            image_url = None
            # 1. Try to pick from top 3, but NEVER reuse images within the same batch
            for item in items[:3]:
                url = item.get("link")
                if url and url not in used_image_urls:
                    image_url = url
                    used_image_urls.add(url)
                    google_logger.info(f"Selected unique image from top 3: {image_url}")
                    break

            # 2. If no unique image found, try top 10 with strict uniqueness
            if not image_url:
                for item in items[:10]:
                    url = item.get("link")
                    if url and url not in used_image_urls:
                        image_url = url
                        used_image_urls.add(url)
                        google_logger.info(f"Selected unique image from top 10: {image_url}")
                        break

            # 3. If still no unique image, use query-based deterministic selection
            if not image_url:
                available_urls = [item.get("link") for item in items[:10] if item.get("link") and item.get("link") not in used_image_urls]
                if available_urls:
                    # Use query-based selection to ensure variety - different queries get different images
                    import hashlib
                    query_hash = hashlib.md5(query.encode()).hexdigest()
                    selected_index = int(query_hash[:8], 16) % len(available_urls)
                    image_url = available_urls[selected_index]
                    used_image_urls.add(image_url)
                    google_logger.info(f"Selected unique image with query-based selection: {image_url}")
                else:
                    # Ultimate fallback - use query hash to select from all available, allowing reuse but ensuring different queries get different images
                    available_urls = [item.get("link") for item in items[:10] if item.get("link")]
                    if available_urls:
                        # Use query hash to deterministically select different images for different queries
                        import hashlib
                        query_hash = hashlib.md5(query.encode()).hexdigest()
                        selected_index = int(query_hash[:8], 16) % len(available_urls)
                        image_url = available_urls[selected_index]
                        used_image_urls.add(image_url)
                        google_logger.warning(f"Using deterministic selection due to limited unique results (query: {query}): {image_url}")
                    else:
                        google_logger.error(f"No images available for query: {query}")
                        continue

            google_logger.info(f"Downloading image: {image_url}")
            # Download image
            img_response = requests.get(image_url, timeout=10)
            img_response.raise_for_status()

            filename = exact_filenames[i] if exact_filenames and i < len(exact_filenames) else f"{batch_name}_{i+1:02d}.jpg"
            # Add unique ID to prevent filename conflicts
            if unique_id and not exact_filenames:
                name_part, ext_part = filename.rsplit('.', 1) if '.' in filename else (filename, 'jpg')
                filename = f"{name_part}_{unique_id}.{ext_part}"
            output_path = Path(output_dir) / filename
            with open(output_path, "wb") as f:
                f.write(img_response.content)
            google_logger.info(f"Saved image to {output_path}")
            generated.append(filename)

        except Exception as e:
            google_logger.error(f"Google Custom Search error for query '{query}': {e}")
            generated.append("")  # Add empty string to maintain index alignment
            continue

    return generated, used_image_urls
def generate_images_batch(
    words: List[str],
    output_dir: str,
    google_api_key: str,
    custom_search_engine_id: str,
    used_image_urls: Optional[set[str]] = None,
) -> Tuple[Dict[str, List[str]], set[str]]:
    """
    Generate images for batch of words using Google Custom Search.

    Args:
        words: List of words to get images for
        output_dir: Base output directory
        google_api_key: Google API key (same as Gemini)
        custom_search_engine_id: Google Custom Search Engine ID
        used_image_urls: Set of already used image URLs to avoid duplicates

    Returns:
        Tuple of (dict with {word: [image_filenames]}, updated used_image_urls set)
    """
    images_output = {}

    # Initialize or use provided used URLs set
    if used_image_urls is None:
        used_image_urls = set()

    for word in words:
        word_image_dir = Path(output_dir) / word.replace(" ", "_")
        word_image_dir.mkdir(parents=True, exist_ok=True)

        # Download one image per word
        image_files, used_image_urls = generate_images_google(
            queries=[word],
            output_dir=str(word_image_dir),
            batch_name=word.replace(" ", "_"),
            num_images=1,
            google_api_key=google_api_key,
            custom_search_engine_id=custom_search_engine_id,
            used_image_urls=used_image_urls,
        )

        images_output[word] = image_files

    return images_output, used_image_urls
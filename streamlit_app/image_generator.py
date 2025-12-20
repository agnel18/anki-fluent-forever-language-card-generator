# Image generation module
# Extracted from core_functions.py for better separation of concerns

import os
import logging
import requests
from pathlib import Path
from typing import Optional, List, Tuple, Dict

# Import error recovery
from error_recovery import graceful_degradation

logger = logging.getLogger(__name__)

# ============================================================================
# IMAGE GENERATION (Pixabay)
# ============================================================================
@graceful_degradation("Image generation", continue_on_failure=True)
def generate_images_pixabay(
    queries: List[str],
    output_dir: str,
    batch_name: str = "batch",
    num_images: int = 1,
    pixabay_api_key: Optional[str] = None,
    randomize: bool = True,
    exact_filenames: Optional[List[str]] = None,
    used_image_urls: Optional[set[str]] = None,
) -> Tuple[List[str], set[str]]:
    """
    Download images from Pixabay.

    Args:
        queries: List of search queries (one per sentence)
        output_dir: Directory to save JPG files
        batch_name: Prefix for filenames
        num_images: Number of images per query (usually 1 for Anki)
        pixabay_api_key: Pixabay API key
        randomize: Randomize from top 3 results
        exact_filenames: Optional list of exact filenames to use
        used_image_urls: Set of already used image URLs to avoid duplicates

    Returns:
        Tuple of (list of generated file paths, updated used_image_urls set)
    """
    if not pixabay_api_key:
        raise ValueError("Pixabay API key required")

    os.makedirs(output_dir, exist_ok=True)
    generated = []

    # Initialize or use provided used URLs set
    if used_image_urls is None:
        used_image_urls = set()

    pixabay_logger = logging.getLogger("pixabay_download")
    for i, query in enumerate(queries):
        try:
            pixabay_logger.info(f"Pixabay search for query: {query}")
            # --- API USAGE TRACKING ---
            try:
                import streamlit as st
                if "pixabay_api_calls" not in st.session_state:
                    st.session_state.pixabay_api_calls = 0
                st.session_state.pixabay_api_calls += 1
            except Exception:
                pass
            # -------------------------
            # Search Pixabay
            # Convert comma-separated keywords to space-separated for Pixabay
            search_query = " ".join(query.split(",")).strip()

            params = {
                "key": pixabay_api_key,
                "q": search_query,
                "per_page": 10,  # Get top 10 results for fallback
                "image_type": "photo",
            }

            response = requests.get("https://pixabay.com/api/", params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            hits = data.get("hits", [])

            pixabay_logger.info(f"Pixabay hits for '{query}': {len(hits)}")
            if not hits:
                pixabay_logger.warning(f"No images found for query: {query}")
                continue

            image_url = None
            # 1. Try to pick a unique image from the top 3
            for hit in hits[:3]:
                url = hit.get("webformatURL")
                if url and url not in used_image_urls:
                    image_url = url
                    used_image_urls.add(url)
                    pixabay_logger.info(f"Selected image from top 3: {image_url}")
                    break

            # 2. If all top 3 are used, expand to top 10
            if not image_url:
                for hit in hits[:10]:
                    url = hit.get("webformatURL")
                    if url and url not in used_image_urls:
                        image_url = url
                        used_image_urls.add(url)
                        pixabay_logger.info(f"Selected image from top 10: {image_url}")
                        break

            # 3. If all top 10 are used, fallback to first (allow duplicate)
            if not image_url:
                image_url = hits[0].get("webformatURL")
                used_image_urls.add(image_url)
                pixabay_logger.info(f"Fallback to first image: {image_url}")

            pixabay_logger.info(f"Downloading image: {image_url}")
            # Download image
            img_response = requests.get(image_url, timeout=10)
            img_response.raise_for_status()

            filename = exact_filenames[i] if exact_filenames and i < len(exact_filenames) else f"{batch_name}_{i+1:02d}.jpg"
            output_path = Path(output_dir) / filename
            with open(output_path, "wb") as f:
                f.write(img_response.content)
            pixabay_logger.info(f"Saved image to {output_path}")
            generated.append(filename)

        except Exception as e:
            pixabay_logger.error(f"Pixabay error for query '{query}': {e}")
            continue

    return generated, used_image_urls

def generate_images_batch(
    words: List[str],
    output_dir: str,
    pixabay_api_key: str,
    used_image_urls: Optional[set[str]] = None,
) -> Tuple[Dict[str, List[str]], set[str]]:
    """
    Generate images for batch of words.

    Args:
        words: List of words to get images for
        output_dir: Base output directory
        pixabay_api_key: Pixabay API key
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
        image_files, used_image_urls = generate_images_pixabay(
            queries=[word],
            output_dir=str(word_image_dir),
            batch_name=word.replace(" ", "_"),
            num_images=1,
            pixabay_api_key=pixabay_api_key,
            used_image_urls=used_image_urls,
        )

        images_output[word] = image_files

    return images_output, used_image_urls
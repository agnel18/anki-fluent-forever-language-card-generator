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
# IMAGE GENERATION (Pixabay Only)
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
    unique_id: str = None,
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
            print(f"PIXABAY SEARCH QUERY FOR SENTENCE {i+1}: '{search_query}'")  # EXACT query sent to Pixabay

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
            # 1. Try to pick from top 3, but NEVER reuse images within the same batch
            for hit in hits[:3]:
                url = hit.get("webformatURL")
                if url and url not in used_image_urls:
                    image_url = url
                    used_image_urls.add(url)
                    pixabay_logger.info(f"Selected unique image from top 3: {image_url}")
                    break

            # 2. If no unique image found, try top 10 with strict uniqueness
            if not image_url:
                for hit in hits[:10]:
                    url = hit.get("webformatURL")
                    if url and url not in used_image_urls:
                        image_url = url
                        used_image_urls.add(url)
                        pixabay_logger.info(f"Selected unique image from top 10: {image_url}")
                        break

            # 3. If still no unique image, use query-based deterministic selection
            if not image_url:
                available_urls = [hit.get("webformatURL") for hit in hits[:10] if hit.get("webformatURL") and hit.get("webformatURL") not in used_image_urls]
                if available_urls:
                    # Use query-based selection to ensure variety - different queries get different images
                    import hashlib
                    query_hash = hashlib.md5(query.encode()).hexdigest()
                    selected_index = int(query_hash[:8], 16) % len(available_urls)
                    image_url = available_urls[selected_index]
                    used_image_urls.add(image_url)
                    pixabay_logger.info(f"Selected unique image with query-based selection: {image_url}")
                else:
                    # Ultimate fallback - use query hash to select from all available, allowing reuse but ensuring different queries get different images
                    available_urls = [hit.get("webformatURL") for hit in hits[:10] if hit.get("webformatURL")]
                    if available_urls:
                        # Use query hash to deterministically select different images for different queries
                        import hashlib
                        query_hash = hashlib.md5(query.encode()).hexdigest()
                        selected_index = int(query_hash[:8], 16) % len(available_urls)
                        image_url = available_urls[selected_index]
                        used_image_urls.add(image_url)
                        pixabay_logger.warning(f"Using deterministic selection due to limited unique results (query: {query}): {image_url}")
                    else:
                        pixabay_logger.error(f"No images available for query: {query}")
                        continue

            pixabay_logger.info(f"Downloading image: {image_url}")
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
            pixabay_logger.info(f"Saved image to {output_path}")
            generated.append(filename)

        except Exception as e:
            pixabay_logger.error(f"Pixabay error for query '{query}': {e}")
            generated.append("")  # Add empty string to maintain index alignment
            continue

    return generated, used_image_urls
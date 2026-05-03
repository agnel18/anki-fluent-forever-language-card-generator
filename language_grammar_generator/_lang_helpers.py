"""
Shared language-folder/code mappings for the validation toolchain.

Single source of truth: parses
`streamlit_app/language_analyzers/analyzer_registry.py` to extract the
`folder_to_code` dict, so adding a new language requires editing only that
one file. Previously each of `validate_implementation.py`,
`compare_with_gold_standard.py`, and `run_all_tests.py` had its own
hardcoded mapping that drifted out of sync (Portuguese hit this gap).
"""

from __future__ import annotations

import ast
from functools import lru_cache
from pathlib import Path
from typing import Dict


REGISTRY_PATH = (
    Path(__file__).resolve().parent.parent
    / "streamlit_app"
    / "language_analyzers"
    / "analyzer_registry.py"
)


@lru_cache(maxsize=1)
def folder_to_code() -> Dict[str, str]:
    """Parse `folder_to_code` out of analyzer_registry.py.

    The dict is currently a method-local variable inside `_discover_analyzers`;
    `ast.walk` visits all nested nodes, so this still finds it. If the source
    file ever changes the assignment shape (computed, multi-line update, etc.)
    this raises and surfaces the breakage early.
    """
    src = REGISTRY_PATH.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "folder_to_code":
                    return ast.literal_eval(node.value)
    raise RuntimeError(
        f"Could not find a `folder_to_code = {{...}}` assignment in {REGISTRY_PATH}. "
        "Update _lang_helpers.py if the registry's structure changed."
    )


@lru_cache(maxsize=1)
def code_to_folder() -> Dict[str, str]:
    """Inverse of folder_to_code — maps ISO language code to folder name."""
    return {code: folder for folder, code in folder_to_code().items()}


def get_directory_name(language_code: str) -> str:
    """Map an ISO language code to its folder name under `languages/`.

    Examples:
        pt -> portuguese
        lv -> latvian
        zh -> chinese_simplified
        zh-tw -> chinese_traditional
        en -> english (always present in the registry)

    Falls back to the normalized code itself if no mapping exists.
    """
    normalized = language_code.replace("-", "_").lower()
    mapping = code_to_folder()
    # Try the original code first (handles "zh-tw" if registered with hyphen),
    # then the underscore-normalized form.
    return mapping.get(language_code, mapping.get(normalized, normalized))


def get_file_name(language_code: str) -> str:
    """Map an ISO language code to its analyzer file prefix.

    Convention across all 14 shipped analyzers: hyphens become underscores;
    the prefix is otherwise the lowercase code.

    Examples: pt -> pt; zh-tw -> zh_tw; ml -> ml.
    """
    return language_code.replace("-", "_").lower()


def get_class_prefix(language_code: str) -> str:
    """Map an ISO language code to its analyzer class prefix.

    Convention: split on hyphens or underscores, title-case each segment,
    concatenate.

    Examples: pt -> Pt; zh-tw -> ZhTw; zh_tw -> ZhTw; lv -> Lv.
    """
    parts = language_code.replace("-", "_").split("_")
    return "".join(part.title() for part in parts if part)


def get_class_name(language_code: str) -> str:
    """Convenience: full analyzer class name (`{Prefix}Analyzer`)."""
    return f"{get_class_prefix(language_code)}Analyzer"

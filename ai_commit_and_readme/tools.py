"""
Utility functions for documentation enrichment and other helpers.
"""

import glob
import os
from pathlib import Path
from typing import Any, Callable, Protocol

from .constants import API_KEY, MODEL, README_PATH, WIKI_PATH, WIKI_URL, WIKI_URL_BASE

PROMPT_PATH = Path(__file__).parent / "prompt.md"

# For better type annotations
CtxDict = dict[str, Any]


# Define a protocol for functions that can be piped
class PipeFunction(Protocol):
    """Protocol for functions that can be used in a pipeline."""

    def __call__(self, ctx: CtxDict) -> CtxDict: ...


def initialize_context(ctx: CtxDict) -> CtxDict:
    """Initialize context with default values if not already initialized."""
    if "context_initialized" not in ctx:
        defaults = [
            ("readme_path", README_PATH),
            ("wiki_path", WIKI_PATH),
            ("api_key", API_KEY),
            ("wiki_url", WIKI_URL),
            ("wiki_url_base", WIKI_URL_BASE),
            ("model", MODEL),
        ]
        for key, value in defaults:
            ctx[key] = value
        wiki_files, wiki_file_paths = get_wiki_files()
        ctx["file_paths"] = {"README.md": README_PATH, "wiki": wiki_file_paths}
        ctx["ai_suggestions"] = {"README.md": None, "wiki": None}
        ctx["wiki_files"] = wiki_files
        ctx["wiki_file_paths"] = wiki_file_paths
        ctx["context_initialized"] = True
    return ctx


def ensure_initialized(func: Callable) -> PipeFunction:
    """Decorator that ensures context is initialized before executing a function."""

    def wrapper(ctx: CtxDict) -> CtxDict:
        ctx = initialize_context(ctx)
        return func(ctx)

    return wrapper


def get_wiki_files() -> tuple[list[str], dict[str, str]]:
    """Return a list of wiki markdown files (including Home.md) and their paths"""
    files = glob.glob(f"{WIKI_PATH}/*.md")
    filenames = [os.path.basename(f) for f in files]
    file_paths = {os.path.basename(f): f for f in files}
    return filenames, file_paths


def get_prompt_template(section: str) -> str:
    """Load a named prompt section from prompt.md by \"## section\" header (simple line scan)."""
    try:
        with open(PROMPT_PATH, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError as err:
        raise RuntimeError(f"Prompt template file not found: {PROMPT_PATH}") from err
    section_header = f"## {section}"
    in_section = False
    section_lines: list[str] = []
    for line in lines:
        if line.strip().startswith("## "):
            if in_section:
                break
            in_section = line.strip() == section_header
            continue
        if in_section:
            section_lines.append(line)
    if section_lines:
        return "".join(section_lines).strip()
    raise ValueError(f'Prompt section "{section}" not found in prompt.md')

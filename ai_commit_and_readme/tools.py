"""
Utility functions for documentation enrichment and other helpers.
"""

import glob
import os
from pathlib import Path

from .constants import API_KEY, MODEL, README_PATH, WIKI_PATH, WIKI_URL, WIKI_URL_BASE

PROMPT_PATH = Path(__file__).parent / "prompt.md"


def chain_handler(func):
    """Decorator to ensure handler returns ctx for chaining and populates ctx with constants if not set."""

    def wrapper(ctx, *args, **kwargs):
        if "chain_handler_initialized" not in ctx:
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
            ctx["chain_handler_initialized"] = True
        func(ctx, *args, **kwargs)
        return ctx

    return wrapper


def get_wiki_files():
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
    section_lines = []
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

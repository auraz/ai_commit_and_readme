"""
Utility functions for documentation enrichment and other helpers.
"""
import glob, os
from pathlib import Path
from .constants import README_PATH, WIKI_PATH, API_KEY, WIKI_URL, WIKI_URL_BASE, MODEL

PROMPT_PATH = Path(__file__).parent / "prompt.md"
try:
    PROMPT_TEMPLATE = PROMPT_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    raise RuntimeError(f"Prompt template file not found: {PROMPT_PATH}")


def chain_handler(func):
    """Decorator to ensure handler returns ctx for chaining and populates ctx with constants if not set."""
    def wrapper(ctx, *args, **kwargs):
        if 'chain_handler_initialized' not in ctx:
            defaults = [
                ('readme_path', README_PATH),
                ('wiki_path', WIKI_PATH),
                ('api_key', API_KEY),
                ('wiki_url', WIKI_URL),
                ('wiki_url_base', WIKI_URL_BASE),
                ('model', MODEL),
            ]
            for key, value in defaults:
                ctx[key] = value
            ctx["file_paths"] = {"readme": README_PATH, "wiki": WIKI_PATH}
            ctx["ai_suggestions"] = {"readme": None, "wiki": None}
            wiki_files, wiki_file_paths = get_wiki_files()
            ctx["wiki_files"] = wiki_files
            ctx["wiki_file_paths"] = wiki_file_paths
            ctx['chain_handler_initialized'] = True
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
    """ Load a named prompt section from prompt.md by section header, section: 'enrich' or 'select_wiki_articles'."""
    with open(PROMPT_PATH, encoding="utf-8") as f:
        content = f.read()
    sections = content.split('# ---')
    for s in sections:
        if section == 'enrich' and 'enriching a single file' in s:
            return s.strip()
        elif section == 'select_wiki_articles' and 'selecting which wiki articles' in s:
            return s.strip()
    raise ValueError(f"Prompt section '{section}' not found in prompt.md")

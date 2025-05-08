"""
Utility functions for documentation enrichment and other helpers.
"""
from pathlib import Path
from .constants import README_PATH, WIKI_PATH, API_KEY, WIKI_URL, WIKI_URL_BASE, MODEL

PROMPT_PATH = Path(__file__).parent / "prompt.md"
try:
    PROMPT_TEMPLATE = PROMPT_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    raise RuntimeError(f"Prompt template file not found: {PROMPT_PATH}")


def get_enrich_prompt(file_type: str, file_var: str) -> str:
    """
    Example: get_enrich_prompt('README.md', 'readme')
    """
    return PROMPT_TEMPLATE.format(file_type=file_type, file_var=file_var)


def chain_handler(func):
    """Decorator to ensure handler returns ctx for chaining and populates ctx with constants if not set."""
    def wrapper(ctx, *args, **kwargs):
        defaults = [
            ('readme_path', README_PATH),
            ('wiki_path', WIKI_PATH),
            ('api_key', API_KEY),
            ('wiki_url', WIKI_URL),
            ('wiki_url_base', WIKI_URL_BASE),
            ('model', MODEL),
        ]
        [ctx.setdefault(key, value) for key, value in defaults]
        func(ctx, *args, **kwargs)
        return ctx
    return wrapper

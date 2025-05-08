"""
tools.py: Utility functions for documentation enrichment and other helpers.
"""

from pathlib import Path

PROMPT_PATH = Path(__file__).parent / "prompt.md"
try:
    PROMPT_TEMPLATE = PROMPT_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    raise RuntimeError(f"Prompt template file not found: {PROMPT_PATH}")

def get_enrich_prompt(file_type: str, file_var: str) -> str:
    """
    Returns a generic enrichment prompt for the given file type and variable.
    Example: get_enrich_prompt('README.md', 'readme')
    """
    return PROMPT_TEMPLATE.format(file_type=file_type, file_var=file_var)


def chain_handler(func):
    """Decorator to ensure handler returns ctx for chaining."""
    def wrapper(ctx, *args, **kwargs):
        func(ctx, *args, **kwargs)
        return ctx
    return wrapper

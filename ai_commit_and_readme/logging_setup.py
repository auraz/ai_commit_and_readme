#!/usr/bin/env python3
"""Logging configuration and message templates."""

import logging

from rich.logging import RichHandler

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)]
    )

setup_logging()  # Initialize on import

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

class LogMessages:
    
    DIFF_SIZE = "📏 Your staged changes are {:,} characters long!"
    DIFF_TOKENS = "🔢 That's about {:,} tokens for the AI to read."
    FILE_SIZE = "📄 Update to {} is currently {:,} characters."
    FILE_TOKENS = "🔢 That's {:,} tokens in update to {}!"
    NO_CHANGES = "✅ No staged changes detected. Nothing to enrich."
    LARGE_DIFF = "⚠️  Diff is too large (>100000 characters). Falling back to \"git diff --cached --name-only\"."
    API_ERROR = "❌ Error from OpenAI API: {}"
    NO_API_KEY = "🔑 OPENAI_API_KEY not set. Skipping README update."
    SUCCESS = "🎉✨ SUCCESS: {} enriched and staged with AI suggestions for {}! ✨🎉"
    NO_ENRICHMENT = "👍 No enrichment needed for {}."
    NO_WIKI_ARTICLES = "[i] No valid wiki articles selected. Using Usage.md as fallback."
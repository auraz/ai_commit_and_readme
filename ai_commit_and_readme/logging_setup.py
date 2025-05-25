"""Logging configuration and message templates."""

import logging

from rich.logging import RichHandler

# Configure logging on import
logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(markup=True)])


def get_logger(name: str) -> logging.Logger:
    """Get logger instance for module."""
    return logging.getLogger(name)


class LogMessages:
    """Centralized log message templates."""

    DIFF_SIZE = "📏 Your staged changes are {:,} characters long!"
    DIFF_TOKENS = "🔢 That's about {:,} tokens for the AI to read."
    FILE_SIZE = "📄 Update to {} is currently {:,} characters."
    FILE_TOKENS = "🔢 That's {:,} tokens in update to {}!"
    NO_CHANGES = "✅ No staged changes detected. Nothing to enrich."
    LARGE_DIFF = '⚠️  Diff is too large (>100000 characters). Falling back to "git diff --cached --name-only".'
    API_ERROR = "❌ Error from OpenAI API: {}"
    NO_API_KEY = "🔑 OPENAI_API_KEY not set. Skipping README update."
    SUCCESS = "🎉✨ SUCCESS: {} enriched and staged with AI suggestions for {}! ✨🎉"
    NO_ENRICHMENT = "👍 No enrichment needed for {}."
    NO_WIKI_ARTICLES = "[i] No valid wiki articles selected."
    GETTING_DIFF = "📊 Getting staged changes..."
    DIFF_ERROR = "❌ Error getting diff: {}"
"""Project settings and configuration."""

import os
from typing import Optional


class Settings:
    """Centralized project settings."""

    # Model configuration
    DEFAULT_MODEL: str = os.getenv("AUTODOC_MODEL", "gpt-4o")

    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # Paths
    WIKI_PATH: str = os.getenv("WIKI_PATH", "wiki")
    WIKI_URL_BASE: Optional[str] = os.getenv("WIKI_URL_BASE")

    # Document improvement settings
    TARGET_SCORE: int = int(os.getenv("AUTODOC_TARGET_SCORE", "85"))
    MAX_ITERATIONS: int = int(os.getenv("AUTODOC_MAX_ITERATIONS", "3"))

    @classmethod
    def get_model(cls) -> str:
        """Get the configured model name."""
        return cls.DEFAULT_MODEL

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Get the appropriate API key based on model."""
        if cls.DEFAULT_MODEL.startswith("claude"):
            return cls.ANTHROPIC_API_KEY
        return cls.OPENAI_API_KEY

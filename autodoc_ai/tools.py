"""AI enrichment utilities and context management."""

import logging
from typing import Optional

from rich.logging import RichHandler

# Configure logging on import
logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(markup=True)])
logger = logging.getLogger("autodoc_ai")


def load_file(file_path: str) -> Optional[str]:
    """Load file content."""
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None

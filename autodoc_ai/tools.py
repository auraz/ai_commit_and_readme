"""AI enrichment utilities and context management."""

import logging

from rich.logging import RichHandler

# Configure logging on import
logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(markup=True)])
logger = logging.getLogger("autodoc_ai")

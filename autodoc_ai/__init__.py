"""AI-powered documentation generation and maintenance tool."""

import logging

from rich.logging import RichHandler

# Configure logging for the package
logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(markup=True)])
logger = logging.getLogger("autodoc_ai")

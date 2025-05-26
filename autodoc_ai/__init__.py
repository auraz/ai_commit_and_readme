"""AI-powered documentation generation and maintenance tool."""

import logging
import os

from rich.logging import RichHandler

# Get logging level from environment or default to INFO
log_level = os.getenv("AUTODOC_LOG_LEVEL", "INFO").upper()
if log_level == "DEBUG":
    # Set debug logging for all components
    logging.basicConfig(level=logging.DEBUG, format="%(message)s", handlers=[RichHandler(markup=True)])
    
    # Enable debug logging for CrewAI and LiteLLM
    logging.getLogger("crewai").setLevel(logging.DEBUG)
    logging.getLogger("litellm").setLevel(logging.DEBUG)
else:
    # Configure normal logging for the package
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO), format="%(message)s", handlers=[RichHandler(markup=True)])

logger = logging.getLogger("autodoc_ai")

"""AI-powered documentation generation and maintenance tool."""

import logging
import os

from rich.logging import RichHandler

# Get logging level from environment or default to INFO
log_level = os.getenv("AUTODOC_LOG_LEVEL", "INFO").upper()

# Configure logging with cleaner format
if log_level == "DEBUG":
    # Set debug logging for all components
    logging.basicConfig(level=logging.DEBUG, format="%(message)s", handlers=[RichHandler(markup=True, show_time=False, show_path=False)])

    # Enable debug logging for CrewAI and LiteLLM
    logging.getLogger("crewai").setLevel(logging.DEBUG)
    logging.getLogger("litellm").setLevel(logging.DEBUG)
else:
    # Configure normal logging for the package
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO), format="%(message)s", handlers=[RichHandler(markup=True, show_time=False, show_path=False)])

    # Suppress verbose CrewAI status messages and LiteLLM logs
    logging.getLogger("crewai.crew").setLevel(logging.WARNING)
    logging.getLogger("crewai.agent").setLevel(logging.WARNING)
    logging.getLogger("litellm").setLevel(logging.ERROR)
    logging.getLogger("litellm.utils").setLevel(logging.ERROR)
    logging.getLogger("LiteLLM").setLevel(logging.ERROR)
    logging.getLogger("LiteLLM.utils").setLevel(logging.ERROR)

    # Also disable litellm's own verbose output
    os.environ["LITELLM_LOG"] = "ERROR"

logger = logging.getLogger("autodoc_ai")

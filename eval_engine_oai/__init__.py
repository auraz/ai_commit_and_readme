"""OpenAI Evals Integration for Document Evaluation and Improvement.

This module integrates with the OpenAI Evals framework to provide
document evaluation and improvement capabilities, implementing
a closed-loop system for continuous documentation quality enhancement.
"""

__version__ = "0.1.0"

import logging
import os
from typing import Dict, Optional, List, Any, Tuple

# Configure default logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

# Import and re-export main components
from .evaluator import DocEvaluator, evaluate_document
from .improver import DocImprover, improve_document
from .runner import ClosedLoopRunner, run_improvement_cycle

__all__ = [
    "DocEvaluator",
    "DocImprover",
    "ClosedLoopRunner",
    "evaluate_document",
    "improve_document",
    "run_improvement_cycle",
]
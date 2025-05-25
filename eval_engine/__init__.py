"""Evaluation Engine for Documentation Quality and Improvement.

This package provides a closed-loop system for evaluating and improving
documentation quality using AI assistance.
"""

__version__ = "0.1.0"

from .engine import EvaluationEngine, ClosedLoopRunner
from .evaluators.base import BaseEvaluator
from .improvers.base import BaseImprover
from .storage.history import EvaluationHistory

__all__ = [
    "EvaluationEngine",
    "ClosedLoopRunner",
    "BaseEvaluator",
    "BaseImprover",
    "EvaluationHistory",
]
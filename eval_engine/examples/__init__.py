"""Example usage of the Documentation Evaluation Engine.

This package contains example scripts demonstrating how to use
the evaluation engine for evaluating and improving documentation.

Available examples:
- evaluate_and_improve.py: Shows how to evaluate README files,
  improve them based on evaluation results, and run closed-loop
  improvement cycles.
"""

from .evaluate_and_improve import (
    example_evaluate_readme,
    example_improve_readme,
    example_run_cycle
)

__all__ = [
    "example_evaluate_readme",
    "example_improve_readme",
    "example_run_cycle"
]
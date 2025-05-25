"""README Evaluator using autodoceval-crewai for AI-powered evaluation."""

import logging
from pathlib import Path
from typing import Tuple

from evcrew import DocumentCrew

from ..tools import load_file

logger = logging.getLogger(__name__)


def evaluate(readme_path: str) -> Tuple[int, str]:
    """Evaluate README using autodoceval-crewai returning score and report."""
    try:
        content = load_file(readme_path)
        if not content:
            return 0, "Error: Unable to read README file"
        
        crew = DocumentCrew(target_score=85, max_iterations=1)  # Single evaluation
        score, feedback = crew.evaluate_one(content)
        
        report = f"""README Evaluation (AI-Powered by CrewAI)
{'=' * 60}

File: {Path(readme_path).name}
Score: {score:.0f}/100

Evaluation Feedback:
{feedback}

{'=' * 60}"""
        
        return int(score), report
    except Exception as e:
        logger.error(f"Error evaluating README: {e}")
        return 0, f"Error evaluating README: {str(e)}"
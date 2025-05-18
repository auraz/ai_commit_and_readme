"""README Evaluator

AI-powered evaluator for README.md files using OpenAI to assess quality,
completeness, and adherence to best practices.
"""

import logging
from typing import Tuple

from ..tools import evaluate_with_ai, format_evaluation_results, load_file

logger = logging.getLogger(__name__)

# Evaluation categories and their weights
CATEGORIES = {
    "title_and_description": 10,
    "structure_and_organization": 15,
    "installation_guide": 15,
    "usage_examples": 15,
    "feature_explanation": 10,
    "documentation_links": 10,
    "badges_and_shields": 5, 
    "license_information": 5,
    "contributing_guidelines": 5,
    "conciseness_and_clarity": 10
}

# Name of the README evaluation prompt file
README_EVAL_PROMPT_FILE = 'readme_eval.md'


def evaluate(readme_path: str) -> Tuple[int, str]:
    """Main evaluation function.
    
    Returns:
        tuple of (total score, formatted report)
    """
    # Evaluate the README file using the shared tools
    return evaluate_with_ai(
        file_path=readme_path,
        prompt_filename=README_EVAL_PROMPT_FILE,
        format_vars={"readme_content": load_file(readme_path) or ""},
        categories=CATEGORIES,
        report_title="README Evaluation (AI-Powered)"
    )





if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python -m ai_commit_and_readme.evals.readme_eval <path/to/README.md>\n")
        sys.exit(1)

    score, report = evaluate(sys.argv[1])
    sys.stdout.write(report + "\n")
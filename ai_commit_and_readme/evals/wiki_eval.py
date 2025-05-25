"""Wiki Evaluator using autodoceval-crewai for AI-powered evaluation."""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from evcrew import DocumentCrew

from ..tools import load_file

logger = logging.getLogger(__name__)


class WikiEvaluator:
    """Evaluates wiki pages using autodoceval-crewai."""
    
    def evaluate(self, wiki_path: str, page_type: Optional[str] = None) -> Tuple[int, str]:
        """Evaluate a wiki page using autodoceval-crewai.
        
        Args:
            wiki_path: Path to the wiki page to evaluate
            page_type: Optional specific page type (not used in CrewAI evaluation)
            
        Returns:
            Tuple of (score, formatted report)
        """
        try:
            content = load_file(wiki_path)
            if not content:
                return 0, f"Wiki page not found or empty: {wiki_path}"
            
            filename = os.path.basename(wiki_path)
            crew = DocumentCrew(target_score=85, max_iterations=1)  # Single evaluation
            score, feedback = crew.evaluate_one(content)
            
            report = f"""Wiki Page Evaluation (AI-Powered by CrewAI)
{'=' * 60}

File: {filename}
Score: {score:.0f}/100

Evaluation Feedback:
{feedback}

{'=' * 60}"""
            
            return int(score), report
        except Exception as e:
            logger.error(f"Error evaluating wiki page: {e}")
            return 0, f"Error evaluating wiki page: {str(e)}"


def evaluate(wiki_path: str) -> Tuple[int, str]:
    """Evaluate a single wiki page."""
    evaluator = WikiEvaluator()
    return evaluator.evaluate(wiki_path)


def evaluate_directory(directory_path: str) -> Dict[str, Tuple[int, str]]:
    """Evaluate all markdown files in a directory.
    
    Args:
        directory_path: Path to directory containing wiki pages
        
    Returns:
        Dictionary mapping filenames to (score, report) tuples
    """
    results = {}
    evaluator = WikiEvaluator()
    
    wiki_dir = Path(directory_path)
    if not wiki_dir.exists() or not wiki_dir.is_dir():
        logger.error(f"Directory not found: {directory_path}")
        return results
    
    markdown_files = list(wiki_dir.glob("*.md"))
    if not markdown_files:
        logger.warning(f"No markdown files found in {directory_path}")
        return results
    
    for wiki_file in markdown_files:
        try:
            score, report = evaluator.evaluate(str(wiki_file))
            results[wiki_file.name] = (score, report)
            logger.info(f"Evaluated {wiki_file.name}: Score {score}")
        except Exception as e:
            logger.error(f"Error evaluating {wiki_file.name}: {e}")
            results[wiki_file.name] = (0, f"Error: {str(e)}")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python -m ai_commit_and_readme.evals.wiki_eval <path/to/wiki.md> [--dir]\n")
        sys.exit(1)
    
    path = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == "--dir":
        results = evaluate_directory(path)
        for filename, (score, _) in sorted(results.items(), key=lambda x: x[1][0], reverse=True):
            sys.stdout.write(f"{filename}: {score}\n")
    else:
        score, report = evaluate(path)
        sys.stdout.write(report + "\n")
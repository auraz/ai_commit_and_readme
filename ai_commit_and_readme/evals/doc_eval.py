"""Document evaluator using autodoceval-crewai with type-specific prompts."""

import logging
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

from evcrew import DocumentCrew

from ..tools import load_file

logger = logging.getLogger(__name__)

# Wiki page type detection patterns
WIKI_TYPE_PATTERNS = {
    "api": ["endpoint", "request", "response", "authentication", "api"],
    "architecture": ["architecture", "design", "components", "system", "diagram"],
    "installation": ["install", "setup", "requirements", "prerequisites"],
    "usage": ["usage", "how to", "example", "getting started"],
    "security": ["security", "authentication", "authorization", "vulnerability"],
    "contributing": ["contribute", "pull request", "development", "guidelines"],
}


class DocEvaluator:
    """Evaluates documentation using autodoceval-crewai with type-specific prompts."""

    def __init__(self):
        """Initialize evaluator with prompt templates."""
        self.prompts_dir = Path(__file__).parent.parent / "prompts" / "evals"
        self.type_prompts = self._load_type_prompts()

    def _load_type_prompts(self) -> Dict[str, str]:
        """Load all type-specific evaluation prompts."""
        prompts = {}
        for prompt_file in self.prompts_dir.glob("*_eval.md"):
            page_type = prompt_file.stem.replace("_eval", "")
            with open(prompt_file, encoding="utf-8") as f:
                prompts[page_type] = f.read()
        return prompts

    def _detect_doc_type(self, content: str, filename: str) -> str:
        """Detect document type from content and filename."""
        content_lower = content.lower()
        filename_lower = filename.lower()

        # README files are always README type
        if "readme" in filename_lower:
            return "readme"

        # Check filename patterns for wiki pages
        for page_type, patterns in WIKI_TYPE_PATTERNS.items():
            if any(pattern in filename_lower for pattern in patterns):
                return page_type

        # Check content patterns
        for page_type, patterns in WIKI_TYPE_PATTERNS.items():
            matches = sum(1 for pattern in patterns if pattern in content_lower)
            if matches >= 2:  # At least 2 pattern matches
                return page_type

        return "wiki"  # Default type

    def evaluate(self, doc_path: str, doc_type: Optional[str] = None) -> Tuple[int, str]:
        """Evaluate a document using type-specific prompts with CrewAI agents."""
        try:
            content = load_file(doc_path)
            if not content:
                return 0, f"Document not found or empty: {doc_path}"

            filename = os.path.basename(doc_path)

            # Detect type if not provided
            if not doc_type:
                doc_type = self._detect_doc_type(content, filename)

            # Get type-specific prompt if available
            type_prompt = self.type_prompts.get(doc_type, "")

            # Create enhanced content with type-specific criteria
            if type_prompt:
                enhanced_content = f"""Please evaluate this {doc_type} documentation:

{content}

Use these specific evaluation criteria:
{type_prompt}"""
            else:
                enhanced_content = content

            # Use CrewAI for evaluation
            crew = DocumentCrew(target_score=85, max_iterations=1)
            score, feedback = crew.evaluate_one(enhanced_content)

            report = f"""{doc_type.upper()} Evaluation (AI-Powered by CrewAI)
{"=" * 60}

File: {filename}
Type: {doc_type.title()} Documentation
Score: {score:.0f}/100

Evaluation Feedback:
{feedback}

{"=" * 60}"""

            return int(score), report

        except Exception as e:
            logger.error(f"Error evaluating document: {e}")
            return 0, f"Error evaluating document: {e!s}"


def evaluate_readme(readme_path: str) -> Tuple[int, str]:
    """Evaluate README file."""
    evaluator = DocEvaluator()
    return evaluator.evaluate(readme_path, "readme")


def evaluate_wiki(wiki_path: str, page_type: Optional[str] = None) -> Tuple[int, str]:
    """Evaluate wiki page."""
    evaluator = DocEvaluator()
    return evaluator.evaluate(wiki_path, page_type)


def evaluate_all(directory_path: str) -> Dict[str, Tuple[int, str]]:
    """Evaluate all markdown files in a directory using CrewAI batch processing."""
    results = {}
    evaluator = DocEvaluator()

    doc_dir = Path(directory_path)
    if not doc_dir.exists() or not doc_dir.is_dir():
        logger.error(f"Directory not found: {directory_path}")
        return results

    markdown_files = list(doc_dir.glob("*.md"))
    if not markdown_files:
        logger.warning(f"No markdown files found in {directory_path}")
        return results

    # Process all documents
    for doc_file in markdown_files:
        try:
            score, report = evaluator.evaluate(str(doc_file))
            results[doc_file.name] = (score, report)
            logger.info(f"Evaluated {doc_file.name}: Score {score}")
        except Exception as e:
            logger.error(f"Error evaluating {doc_file.name}: {e}")
            results[doc_file.name] = (0, f"Error: {e!s}")

    return results

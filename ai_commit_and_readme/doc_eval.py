"""Document evaluator extending autodoceval-crewai with type-specific prompts."""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple

from evcrew import DocumentCrew

from .tools import get_logger, load_file

logger = get_logger(__name__)

# Wiki page type detection patterns
WIKI_TYPE_PATTERNS = {
    "api": ["endpoint", "request", "response", "authentication", "api"],
    "architecture": ["architecture", "design", "components", "system", "diagram"],
    "installation": ["install", "setup", "requirements", "prerequisites"],
    "usage": ["usage", "how to", "example", "getting started"],
    "security": ["security", "authentication", "authorization", "vulnerability"],
    "contributing": ["contribute", "pull request", "development", "guidelines"],
}


class DocEvaluator(DocumentCrew):
    """Enhanced document evaluator with type-specific prompt support."""

    def __init__(self, target_score: int = 85, max_iterations: int = 1):
        """Initialize evaluator with prompt templates and CrewAI settings."""
        super().__init__(target_score=target_score, max_iterations=max_iterations)
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

    def evaluate_with_type(self, doc_path: str, doc_type: Optional[str] = None, extra_prompt: Optional[str] = None) -> Tuple[int, str]:
        """Evaluate a document using type-specific prompts."""
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
            enhanced_content = f"Please evaluate this {doc_type} documentation:\n\n{content}\n\n"

            if type_prompt:
                enhanced_content += f"Use these specific evaluation criteria:\n{type_prompt}\n\n"

            if extra_prompt:
                enhanced_content += f"Additional evaluation criteria:\n{extra_prompt}"

            # Use parent class evaluation
            score, feedback = self.evaluate_one(enhanced_content)

            report = (
                f"{doc_type.upper()} Evaluation (AI-Powered by CrewAI)\n"
                + "=" * 60
                + f"\n\nFile: {filename}\nType: {doc_type.title()} Documentation\nScore: {score:.0f}/100\n\nEvaluation Feedback:\n{feedback}\n\n"
                + "=" * 60
            )

            return int(score), report

        except Exception as e:
            logger.error(f"Error evaluating document: {e}")
            return 0, f"Error evaluating document: {e!s}"


def evaluate_doc(doc_path: str, doc_type: Optional[str] = None, extra_prompt: Optional[str] = None) -> Tuple[int, str]:
    """Evaluate documentation file with optional type specification and extra evaluation criteria."""
    evaluator = DocEvaluator()
    return evaluator.evaluate_with_type(doc_path, doc_type, extra_prompt)


def evaluate_all(directory_path: str) -> Dict[str, Tuple[int, str]]:
    """Evaluate all markdown files in a directory."""
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
            score, report = evaluator.evaluate_with_type(str(doc_file))
            results[doc_file.name] = (score, report)
            logger.info(f"Evaluated {doc_file.name}: Score {score}")
        except Exception as e:
            logger.error(f"Error evaluating {doc_file.name}: {e}")
            results[doc_file.name] = (0, f"Error: {e!s}")

    return results

"""Crew for evaluating documentation."""

import os
from pathlib import Path
from typing import Optional, Tuple

from evcrew import DocumentCrew

from ..tools import get_logger, load_file

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


class EvaluationCrew(DocumentCrew):
    """Crew for evaluating documentation quality using evcrew."""

    def __init__(self, target_score: int = 85, max_iterations: int = 1):
        """Initialize evaluation crew."""
        super().__init__(target_score=target_score, max_iterations=max_iterations)
        self.prompts_dir = Path(__file__).parent.parent / "prompts" / "evals"
        self.type_prompts = self._load_type_prompts()

    def _load_type_prompts(self) -> dict:
        """Load all type-specific evaluation prompts."""
        prompts = {}
        for prompt_file in self.prompts_dir.glob("*_eval.md"):
            page_type = prompt_file.stem.replace("_eval", "")
            with open(prompt_file, encoding="utf-8") as f:
                prompts[page_type] = f.read()
        return prompts

    def run(self, doc_path: str, doc_type: Optional[str] = None, extra_criteria: Optional[str] = None) -> Tuple[int, str]:
        """Evaluate a document's quality with type-specific prompts."""
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

        if extra_criteria:
            enhanced_content += f"Additional evaluation criteria:\n{extra_criteria}"

        # Use parent class evaluation
        try:
            score, feedback = self.evaluate_one(enhanced_content)
        except Exception as e:
            logger.error(f"Error evaluating document: {e}")
            return 0, f"Error evaluating document: {e!s}"

        report = (
            f"{doc_type.upper()} Evaluation (AI-Powered by CrewAI)\n"
            + "=" * 60
            + f"\n\nFile: {filename}\nType: {doc_type.title()} Documentation\nScore: {score:.0f}/100\n\nEvaluation Feedback:\n{feedback}\n\n"
            + "=" * 60
        )

        return int(score), report

    def _detect_doc_type(self, content: str, filename: str) -> str:
        """Detect document type from content and filename."""
        content_lower = content.lower()
        filename_lower = filename.lower()

        if "readme" in filename_lower:
            return "readme"

        for page_type, patterns in WIKI_TYPE_PATTERNS.items():
            if any(pattern in filename_lower for pattern in patterns):
                return page_type

        for page_type, patterns in WIKI_TYPE_PATTERNS.items():
            matches = sum(1 for pattern in patterns if pattern in content_lower)
            if matches >= 2:
                return page_type

        return "wiki"

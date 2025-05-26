"""Crew for enriching documentation."""

from typing import Dict, Optional, Tuple

from ..agents import CodeAnalystAgent, DocumentationWriterAgent
from .base import BaseCrew


class EnrichmentCrew(BaseCrew):
    """Crew for enriching documentation based on code changes."""

    def __init__(self):
        """Initialize enrichment crew with specialized agents."""
        super().__init__()
        self.code_analyst = CodeAnalystAgent()
        self.doc_writer = DocumentationWriterAgent()
        self.agents = [self.code_analyst, self.doc_writer]

    def _execute(self, diff: str, doc_content: str, doc_type: str, file_path: str, other_docs: Optional[Dict[str, str]] = None) -> Tuple[bool, str]:
        """Execute documentation enrichment."""
        analysis_task = self.code_analyst.create_task(diff, diff=diff)
        update_task = self.doc_writer.create_task(doc_content, doc_type=doc_type, file_path=file_path, other_docs=other_docs, context_tasks=[analysis_task])

        crew = self._create_crew([analysis_task, update_task])
        result = crew.kickoff()

        update_result = result.pydantic
        return update_result.needs_update, update_result.updated_sections

    def _handle_error(self, error: Exception) -> Tuple[bool, str]:
        """Handle enrichment errors."""
        return False, "NO CHANGES"

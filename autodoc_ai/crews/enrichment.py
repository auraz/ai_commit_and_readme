"""Crew for enriching documentation."""

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

    def _execute(self, diff: str, doc_content: str, doc_type: str, file_path: str, other_docs: dict[str, str] | None = None) -> tuple[bool, str]:
        """Execute documentation enrichment."""
        from .. import logger

        logger.info(f"🔍 Starting enrichment for {doc_type} file: {file_path}")

        analysis_task = self.code_analyst.create_task(diff, diff=diff)
        update_task = self.doc_writer.create_task(doc_content, doc_type=doc_type, file_path=file_path, other_docs=other_docs, context_tasks=[analysis_task])

        crew = self._create_crew([analysis_task, update_task])

        logger.info(f"🎯 Kicking off enrichment crew for {file_path}...")
        result = crew.kickoff()
        logger.info(f"✨ Enrichment crew completed for {file_path}")
        logger.debug(f"Enrichment crew result type: {type(result)}")
        logger.debug(f"Enrichment crew result: {result}")

        # Handle None result (error case)
        if result is None:
            logger.warning(f"Enrichment crew returned None for {file_path} - likely due to an error")
            return False, "NO CHANGES"

        # Extract raw output from CrewOutput object
        result_str = str(result.raw) if hasattr(result, "raw") else str(result)

        logger.debug(f"Extracted result string: {result_str[:200]}...")

        # Handle string output from CrewAI
        if result_str:
            # Check if the output indicates updates are needed
            needs_update = "NO CHANGES" not in result_str.upper()

            # Extract the updated content
            if needs_update:
                # Remove any markdown code blocks if present
                import re

                # Look for content between markdown code blocks
                code_block_match = re.search(r"```(?:markdown)?\n(.*?)\n```", result_str, re.DOTALL)
                if code_block_match:
                    return True, code_block_match.group(1)
                # Otherwise return the entire result
                return True, result_str
            else:
                return False, "NO CHANGES"

        # If result has pydantic attribute (future compatibility)
        if hasattr(result, "pydantic"):
            update_result = result.pydantic
            return update_result.needs_update, update_result.updated_sections

        return False, "NO CHANGES"

    def _handle_error(self, error: Exception) -> tuple[bool, str]:
        """Handle enrichment errors."""
        return False, "NO CHANGES"

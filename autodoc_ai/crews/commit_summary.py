"""Crew for generating commit summaries."""

from ..agents import CommitSummaryAgent
from .base import BaseCrew


class CommitSummaryCrew(BaseCrew):
    """Crew for generating commit summaries."""

    def __init__(self):
        """Initialize commit summary crew."""
        super().__init__()
        self.summary_agent = CommitSummaryAgent()
        self.agents = [self.summary_agent]

    def _execute(self, diff: str) -> str:
        """Execute commit summary generation."""
        task = self.summary_agent.create_task(diff)
        crew = self._create_crew([task], verbose=False)
        result = crew.kickoff()

        # Handle string output from CrewAI
        if isinstance(result, str):
            # Extract summary from the string output
            # Remove any extra formatting or quotes
            summary = result.strip()
            if summary.startswith('"') and summary.endswith('"'):
                summary = summary[1:-1]
            return summary if summary else "Update codebase"
        
        # If result has pydantic attribute (future compatibility)
        if hasattr(result, 'pydantic'):
            return result.pydantic.summary
        
        return "Update codebase"

    def _handle_error(self, error: Exception) -> str:
        """Handle summary generation errors."""
        return "Update codebase"

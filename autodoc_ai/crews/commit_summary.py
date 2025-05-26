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

        return result.pydantic.summary

    def _handle_error(self, error: Exception) -> str:
        """Handle summary generation errors."""
        return "Update codebase"

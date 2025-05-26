"""Crew for selecting wiki articles."""

from typing import List

from ..agents import WikiSelectorAgent
from .base import BaseCrew


class WikiSelectorCrew(BaseCrew):
    """Crew for selecting wiki articles to update."""

    def __init__(self):
        """Initialize wiki selector crew."""
        super().__init__()
        self.selector = WikiSelectorAgent()
        self.agents = [self.selector]

    def _execute(self, diff: str, wiki_files: List[str]) -> List[str]:
        """Execute wiki article selection."""
        task = self.selector.create_task(diff, wiki_files=wiki_files)
        crew = self._create_crew([task], verbose=False)
        result = crew.kickoff()

        return result.pydantic.selected_articles

    def _handle_error(self, error: Exception) -> List[str]:
        """Handle selection errors."""
        return []

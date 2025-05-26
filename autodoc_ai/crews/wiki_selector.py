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

        # Handle string output from CrewAI
        if isinstance(result, str):
            # Parse the output to extract selected articles
            import re
            # Look for list patterns in the output
            matches = re.findall(r'["\']([A-Za-z-]+\.md)["\']', result)
            if matches:
                return [m for m in matches if m in wiki_files]
            # Fallback: look for wiki file names mentioned in the text
            selected = []
            for wiki_file in wiki_files:
                if wiki_file in result:
                    selected.append(wiki_file)
            return selected
        
        # If result has pydantic attribute (future compatibility)
        if hasattr(result, 'pydantic'):
            return result.pydantic.selected_articles
        
        return []

    def _handle_error(self, error: Exception) -> List[str]:
        """Handle selection errors."""
        return []

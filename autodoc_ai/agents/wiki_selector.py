"""Agent for selecting wiki articles."""

from crewai import Task
from pydantic import BaseModel

from .base import BaseAgent


class WikiSelectionResult(BaseModel):
    """Result of wiki article selection."""

    selected_articles: list[str]


class WikiSelectorAgent(BaseAgent):
    """Agent for selecting relevant wiki articles based on code changes."""

    def __init__(self):
        """Initialize wiki selector with model configuration."""
        super().__init__(
            role="Documentation Selector",
            goal="Select relevant wiki articles that need updates based on code changes",
            backstory="You are an expert at understanding which documentation needs updates.",
        )
        self.agent.verbose = False

    def create_task(self, content: str, **kwargs) -> Task:
        """Create task for selecting wiki articles."""
        wiki_files = kwargs.get("wiki_files", [])

        prompt_template = self.load_prompt("wiki_selector")
        description = prompt_template.format(content=content, wiki_files=", ".join(wiki_files))

        return Task(
            description=description,
            agent=self.agent,
            expected_output="Structured wiki selection",
            output_pydantic=WikiSelectionResult,
        )

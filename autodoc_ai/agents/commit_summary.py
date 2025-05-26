"""Agent for generating commit summaries."""

from crewai import Task
from pydantic import BaseModel

from .base import BaseAgent


class CommitSummaryResult(BaseModel):
    """Result of commit summary generation."""

    summary: str


class CommitSummaryAgent(BaseAgent):
    """Agent for generating concise commit summaries."""

    def __init__(self):
        """Initialize commit summary agent with model configuration."""
        super().__init__(
            role="Commit Message Expert",
            goal="Generate concise, meaningful commit summaries",
            backstory="You are an expert at writing clear commit messages that follow best practices.",
        )
        self.agent.verbose = False

    def create_task(self, content: str, **kwargs) -> Task:
        """Create task for generating commit summary."""
        prompt_template = self.load_prompt("commit_summary")
        description = prompt_template.format(content=content)

        return Task(
            description=description,
            agent=self.agent,
            expected_output="Structured commit summary",
            output_pydantic=CommitSummaryResult,
        )

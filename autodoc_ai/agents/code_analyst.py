"""Agent for analyzing code changes."""

from typing import List

from crewai import Task
from crewai.tools import tool as crewai_tool
from pydantic import BaseModel

from .base import BaseAgent


class CodeAnalysisResult(BaseModel):
    """Result of code diff analysis."""

    changes_summary: str
    documentation_impacts: List[str]


class CodeAnalystAgent(BaseAgent):
    """Agent for analyzing code changes and identifying documentation impacts."""

    def __init__(self):
        """Initialize code analyst with model configuration."""
        super().__init__(
            role="Senior Code Analyst",
            goal="Analyze code changes and identify documentation impacts",
            backstory="You are an expert at understanding code changes and their implications.",
        )

        @crewai_tool("analyze_diff")
        def analyze_diff(diff: str) -> str:
            """Analyze git diff to understand code changes."""
            return f"Analyzed diff with {len(diff.splitlines())} lines of changes"

        self.agent.tools = [analyze_diff]

    def create_task(self, content: str, **kwargs) -> Task:
        """Create task for analyzing code changes."""
        diff = kwargs.get("diff", content)
        prompt_template = self.load_prompt("code_analyst")
        description = prompt_template.format(diff=diff)

        return Task(
            description=description,
            agent=self.agent,
            expected_output="Structured code analysis",
            output_pydantic=CodeAnalysisResult,
        )

"""Base agent class for all documentation agents."""

import os
from pathlib import Path

from crewai import LLM, Agent


class BaseAgent:
    """Base agent with common functionality for all documentation agents."""

    def __init__(self, role: str, goal: str, backstory: str):
        """Initialize base agent with common configuration."""
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.model = os.getenv("AUTODOC_MODEL", "gpt-4o-mini")

        # Create LLM instance
        llm = LLM(model=self.model, temperature=0.7)

        # Create the CrewAI agent with maximum verbosity in debug mode
        verbose = os.getenv("AUTODOC_LOG_LEVEL", "INFO").upper() == "DEBUG"
        self.agent = Agent(
            role=self.role, 
            goal=self.goal, 
            backstory=self.backstory, 
            verbose=verbose, 
            llm=llm, 
            allow_delegation=False,
            max_iter=10 if verbose else 5  # More iterations in debug mode
        )

    def save(self, *args, **kwargs) -> None:
        """Documentation agents don't save results directly."""
        pass

    def load_prompt(self, prompt_name: str) -> str:
        """Load prompt from prompts/tasks directory."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "tasks" / f"{prompt_name}.md"
        if prompt_path.exists():
            return prompt_path.read_text()
        else:
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

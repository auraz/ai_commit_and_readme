"""Base agent class for all documentation agents."""

import sys
from pathlib import Path

# Add parent directory to path to import from sibling repo
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from autodoceval_crewai.evcrew.agents.base import BaseAgent as ExternalBaseAgent

from ..settings import Settings


class BaseAgent(ExternalBaseAgent):
    """Base agent with common functionality for all documentation agents."""

    def __init__(self, role: str, goal: str, backstory: str):
        """Initialize base agent with common configuration."""
        super().__init__(role=role, goal=goal, backstory=backstory)
        self.model = Settings.get_model()
        self.agent.llm_model = self.model
        self.agent.verbose = True
        self.agent.tools = []

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

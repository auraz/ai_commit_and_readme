"""Base crew class for all documentation crews."""

from typing import Any, List

from crewai import Crew, Task

from ..settings import Settings
from ..tools import get_logger

logger = get_logger(__name__)


class BaseCrew:
    """Base crew with common functionality for all documentation crews."""

    def __init__(self):
        """Initialize base crew."""
        self.model = Settings.get_model()
        self.agents = []

    def _create_crew(self, tasks: List[Task], verbose: bool = True) -> Crew:
        """Create crew with agents and tasks."""
        return Crew(agents=[agent.agent for agent in self.agents], tasks=tasks, verbose=verbose)

    def run(self, *args, **kwargs) -> Any:
        """Run the crew with error handling."""
        try:
            return self._execute(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            return self._handle_error(e)

    def _execute(self, *args, **kwargs) -> Any:
        """Execute the crew logic. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement _execute method")

    def _handle_error(self, error: Exception) -> Any:
        """Handle errors. Override in subclasses for custom error handling."""
        return None

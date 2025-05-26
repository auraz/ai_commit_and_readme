"""Base crew class for all documentation crews."""

import os
from typing import Any, List, Optional

from crewai import Crew, Task

from .. import logger


class BaseCrew:
    """Base crew with common functionality for all documentation crews."""

    def __init__(self):
        """Initialize base crew."""
        self.model = os.getenv("AUTODOC_MODEL", "gpt-4o-mini")
        self.agents = []
        logger.debug(f"Initialized {self.__class__.__name__} with model: {self.model}")

    def _create_crew(self, tasks: List[Task], verbose: Optional[bool] = None) -> Crew:
        """Create crew with agents and tasks."""

        # Set verbose based on log level if not specified
        if verbose is None:
            verbose = os.getenv("AUTODOC_LOG_LEVEL", "INFO").upper() == "DEBUG"
        
        # Force verbose=True in debug mode
        if os.getenv("AUTODOC_LOG_LEVEL", "INFO").upper() == "DEBUG":
            verbose = True
            logger.debug(f"Debug mode: Forcing verbose=True for crew execution")

        def step_callback(step_output):
            """Callback for each step in task execution."""
            logger.info(f"🔄 Step: {step_output}")
            if os.getenv("AUTODOC_LOG_LEVEL", "INFO").upper() == "DEBUG":
                logger.debug(f"Step output details: {step_output}")

        def task_callback(output):
            """Callback for task completion."""
            # Extract task description from output if available
            task_desc = "Task"
            if hasattr(output, "task") and hasattr(output.task, "description"):
                task_desc = output.task.description[:50]
            logger.info(f"✅ Task completed: '{task_desc}...'")
            if hasattr(output, "raw"):
                logger.info(f"   Output preview: {str(output.raw)[:100]}...")
                if os.getenv("AUTODOC_LOG_LEVEL", "INFO").upper() == "DEBUG":
                    logger.debug(f"Full task output: {output.raw}")
                    logger.debug(f"Output object: {output}")

        def before_kickoff(data):
            """Callback before crew execution starts."""
            logger.info(f"🚀 Starting crew execution with {len(tasks)} tasks...")
            for i, task in enumerate(tasks, 1):
                logger.info(f"   Task {i}: {task.description[:60]}...")

        def after_kickoff(output):
            """Callback after crew execution completes."""
            logger.info("🏁 Crew execution completed!")

        return Crew(
            agents=[agent.agent for agent in self.agents],
            tasks=tasks,
            verbose=verbose,
            step_callback=step_callback,
            task_callback=task_callback,
            before_kickoff_callbacks=[before_kickoff],
            after_kickoff_callbacks=[after_kickoff],
        )

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

    def load_file(self, file_path: str) -> Optional[str]:
        """Load file content."""
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

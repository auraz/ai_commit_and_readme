"""Agent for updating documentation."""

from crewai import Task
from crewai.tools import tool as crewai_tool
from pydantic import BaseModel

from .base import BaseAgent


class DocumentUpdateResult(BaseModel):
    """Result of documentation update."""

    updated_sections: str
    needs_update: bool


class DocumentationWriterAgent(BaseAgent):
    """Agent for updating documentation based on code changes."""

    def __init__(self):
        """Initialize documentation writer with model configuration."""
        super().__init__(
            role="Technical Documentation Expert",
            goal="Update documentation to reflect code changes accurately",
            backstory="You are a world-class technical writer who creates clear documentation.",
        )

        @crewai_tool("read_documentation")
        def read_documentation(file_path: str, content: str) -> str:
            """Read and understand current documentation."""
            return f"Read {file_path} with {len(content.splitlines())} lines"

        self.agent.tools = [read_documentation]

    def create_task(self, content: str, **kwargs) -> Task:
        """Create task for updating documentation."""
        doc_type = kwargs.get("doc_type", "documentation")
        file_path = kwargs.get("file_path", "document")
        context_tasks = kwargs.get("context_tasks", [])

        prompt_template = self.load_prompt("documentation_writer")
        description = prompt_template.format(doc_type=doc_type, file_path=file_path, content=content)

        return Task(
            description=description,
            agent=self.agent,
            expected_output="Structured documentation update",
            output_pydantic=DocumentUpdateResult,
            context=context_tasks,
        )

"""Agent for updating documentation."""

from crewai import Task
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

    def create_task(self, content: str, **kwargs) -> Task:
        """Create task for updating documentation."""
        doc_type = kwargs.get("doc_type", "documentation")
        file_path = kwargs.get("file_path", "document")
        context_tasks = kwargs.get("context_tasks", [])
        other_docs = kwargs.get("other_docs", {})

        prompt_template = self.load_prompt("documentation_writer")

        # Format other docs info if provided
        other_docs_info = ""
        if other_docs and doc_type == "wiki":
            other_docs_info = "\n\nOther wiki documents in this project:\n"
            for doc_name, summary in other_docs.items():
                other_docs_info += f"- {doc_name}: {summary}\n"
            other_docs_info += "\nEnsure this document has unique content that doesn't duplicate what's covered in other wiki files."

        description = prompt_template.format(doc_type=doc_type, file_path=file_path, content=content) + other_docs_info

        return Task(
            description=description,
            agent=self.agent,
            expected_output="Structured documentation update",
            output_pydantic=DocumentUpdateResult,
            context=context_tasks,
        )

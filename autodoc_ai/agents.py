"""CrewAI agents for documentation enrichment, article selection, and commit summary generation."""

import sys
from pathlib import Path
from typing import List, Tuple

from crewai import Crew, Task
from crewai.tools import tool
from pydantic import BaseModel

# Add parent directory to path to import from sibling repo
sys.path.append(str(Path(__file__).parent.parent.parent))
from autodoceval_crewai.evcrew.agents.base import BaseAgent

from .tools import get_logger

logger = get_logger(__name__)


@tool("analyze_diff")
def analyze_diff(diff: str) -> str:
    """Analyze git diff to understand code changes."""
    return f"Analyzed diff with {len(diff.splitlines())} lines of changes"


@tool("read_documentation")
def read_documentation(file_path: str, content: str) -> str:
    """Read and understand current documentation."""
    return f"Read {file_path} with {len(content.splitlines())} lines"


class CodeAnalysisResult(BaseModel):
    """Result of code diff analysis."""

    changes_summary: str
    documentation_impacts: List[str]


class DocumentUpdateResult(BaseModel):
    """Result of documentation update."""

    updated_sections: str
    needs_update: bool


class WikiSelectionResult(BaseModel):
    """Result of wiki article selection."""

    selected_articles: List[str]


class CommitSummaryResult(BaseModel):
    """Result of commit summary generation."""

    summary: str


class CodeAnalystAgent(BaseAgent):
    """Agent for analyzing code changes and identifying documentation impacts."""

    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize code analyst with model configuration."""
        super().__init__(
            role="Senior Code Analyst",
            goal="Analyze code changes and identify documentation impacts",
            backstory="""You are an expert at understanding code changes and their implications.
            You excel at identifying what documentation needs to be updated based on git diffs.""",
        )
        self.model = model
        # Override the llm_model from parent
        self.agent.llm_model = model
        self.agent.tools = [analyze_diff]
        self.agent.verbose = True

    def create_task(self, content: str, **kwargs) -> Task:
        """Create task for analyzing code changes."""
        diff = kwargs.get("diff", content)
        return Task(
            description=f"""Analyze the following git diff and identify what documentation updates are needed:
            
            {diff}
            
            Focus on:
            1. New features or functionality added
            2. Changed APIs or interfaces
            3. Updated configuration options
            4. Modified commands or workflows
            5. Deprecated or removed features
            
            Return a structured analysis with:
            - Summary of changes
            - List of documentation impacts
            """,
            agent=self.agent,
            expected_output="Structured code analysis",
            output_pydantic=CodeAnalysisResult,
        )

    def save(self, *args, **kwargs) -> None:
        """Code analyst doesn't save results."""
        pass


class DocumentationWriterAgent(BaseAgent):
    """Agent for updating documentation based on code changes."""

    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize documentation writer with model configuration."""
        super().__init__(
            role="Technical Documentation Expert",
            goal="Update documentation to reflect code changes accurately",
            backstory="""You are a world-class technical writer who creates clear, comprehensive documentation.
            You ensure docs are always in sync with code and avoid duplication between different doc files.""",
        )
        self.model = model
        self.agent.llm_model = model
        self.agent.tools = [read_documentation]
        self.agent.verbose = True

    def create_task(self, content: str, **kwargs) -> Task:
        """Create task for updating documentation."""
        doc_type = kwargs.get("doc_type", "documentation")
        file_path = kwargs.get("file_path", "document")
        context_tasks = kwargs.get("context_tasks", [])

        return Task(
            description=f"""Update the {doc_type} documentation based on the code changes analysis.
            
            Current {file_path}:
            {content}
            
            Important guidelines:
            - Only output new or updated sections, not the full document
            - Start updated sections with their header (## Section Name)
            - Avoid duplicating content that exists in other documentation files
            - README should be concise and point to Wiki for details
            - Each document should have unique purpose and content
            - If no changes needed, set needs_update to false and updated_sections to 'NO CHANGES'
            
            Return structured result with:
            - updated_sections: The new/updated content or 'NO CHANGES'
            - needs_update: Boolean indicating if updates are needed
            """,
            agent=self.agent,
            expected_output="Structured documentation update",
            output_pydantic=DocumentUpdateResult,
            context=context_tasks,
        )

    def save(self, *args, **kwargs) -> None:
        """Documentation writer doesn't save results directly."""
        pass


class WikiSelectorAgent(BaseAgent):
    """Agent for selecting relevant wiki articles based on code changes."""

    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize wiki selector with model configuration."""
        super().__init__(
            role="Documentation Selector",
            goal="Select relevant wiki articles that need updates based on code changes",
            backstory="You are an expert at understanding which documentation needs updates based on code changes.",
        )
        self.model = model
        self.agent.llm_model = model
        self.agent.verbose = False

    def create_task(self, content: str, **kwargs) -> Task:
        """Create task for selecting wiki articles."""
        wiki_files = kwargs.get("wiki_files", [])

        return Task(
            description=f"""Based on the following code changes, select which wiki articles should be updated.
            
            Code changes:
            {content}
            
            Available wiki articles:
            {", ".join(wiki_files)}
            
            Consider updating:
            - Usage.md if commands or workflows changed
            - Architecture.md if system design changed
            - Configuration.md if config options changed
            - API.md if APIs changed
            - Security.md if security features changed
            
            Return structured result with:
            - selected_articles: List of wiki filenames that need updates
            """,
            agent=self.agent,
            expected_output="Structured wiki selection",
            output_pydantic=WikiSelectionResult,
        )

    def save(self, *args, **kwargs) -> None:
        """Wiki selector doesn't save results."""
        pass


class CommitSummaryAgent(BaseAgent):
    """Agent for generating concise commit summaries."""

    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize commit summary agent with model configuration."""
        super().__init__(
            role="Commit Message Expert",
            goal="Generate concise, meaningful commit summaries",
            backstory="You are an expert at writing clear, informative commit messages that follow best practices.",
        )
        self.model = model
        self.agent.llm_model = model
        self.agent.verbose = False

    def create_task(self, content: str, **kwargs) -> Task:
        """Create task for generating commit summary."""
        return Task(
            description=f"""Generate a concise commit summary based on these changes:
            
            {content}
            
            Guidelines:
            - Be specific about what changed
            - Use present tense (e.g., 'Add', 'Fix', 'Update')
            - Keep it under 50 characters if possible
            - Focus on the why, not just the what
            
            Return structured result with:
            - summary: The commit message
            """,
            agent=self.agent,
            expected_output="Structured commit summary",
            output_pydantic=CommitSummaryResult,
        )

    def save(self, *args, **kwargs) -> None:
        """Commit summary agent doesn't save results."""
        pass


class EnrichmentCrew:
    """Crew for enriching documentation based on code changes."""

    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize enrichment crew with specialized agents."""
        self.model = model
        self.code_analyst = CodeAnalystAgent(model)
        self.doc_writer = DocumentationWriterAgent(model)

    def enrich_documentation(self, diff: str, doc_content: str, doc_type: str, file_path: str) -> Tuple[bool, str]:
        """Enrich documentation based on code changes."""
        try:
            # Create tasks
            analysis_task = self.code_analyst.create_task(diff, diff=diff)
            update_task = self.doc_writer.create_task(doc_content, doc_type=doc_type, file_path=file_path, context_tasks=[analysis_task])

            # Create and run the crew
            crew = Crew(agents=[self.code_analyst.agent, self.doc_writer.agent], tasks=[analysis_task, update_task], verbose=True)

            result = crew.kickoff()

            # Extract the final output from the update task
            if hasattr(result, "pydantic") and isinstance(result.pydantic, DocumentUpdateResult):
                update_result = result.pydantic
                return update_result.needs_update, update_result.updated_sections
            else:
                # Fallback for non-pydantic results
                suggestion = str(result).strip()
                needs_update = suggestion != "NO CHANGES"
                return needs_update, suggestion

        except Exception as e:
            logger.error(f"Error in enrichment crew: {e}")
            return False, "NO CHANGES"


def select_wiki_articles_with_agent(diff: str, wiki_files: list[str], model: str = "gpt-4o-mini") -> list[str]:
    """Use an agent to select relevant wiki articles based on code changes."""
    try:
        selector = WikiSelectorAgent(model)
        task = selector.create_task(diff, wiki_files=wiki_files)

        crew = Crew(agents=[selector.agent], tasks=[task], verbose=False)
        result = crew.kickoff()

        # Extract from pydantic result
        if hasattr(result, "pydantic") and isinstance(result.pydantic, WikiSelectionResult):
            return result.pydantic.selected_articles
        else:
            # Fallback parsing
            selected = [f.strip() for f in str(result).split(",") if f.strip()]
            return [f for f in selected if f in wiki_files]

    except Exception as e:
        logger.error(f"Error selecting wiki articles: {e}")
        return []


def generate_commit_summary(diff: str, model: str = "gpt-4o-mini") -> str:
    """Generate a commit summary using an agent."""
    try:
        summary_agent = CommitSummaryAgent(model)
        task = summary_agent.create_task(diff)

        crew = Crew(agents=[summary_agent.agent], tasks=[task], verbose=False)
        result = crew.kickoff()

        # Extract from pydantic result
        if hasattr(result, "pydantic") and isinstance(result.pydantic, CommitSummaryResult):
            return result.pydantic.summary
        else:
            return str(result).strip()

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return "Update codebase"

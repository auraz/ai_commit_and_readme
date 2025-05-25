"""CrewAI agents for documentation enrichment, article selection, and commit summary generation."""

from typing import List, Tuple

from crewai import Agent, Crew, Task
from crewai.tools import tool

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


class CodeAnalystAgent:
    """Agent for analyzing code changes and identifying documentation impacts."""

    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize code analyst with model configuration."""
        self.model = model
        self.agent = Agent(
            role="Senior Code Analyst",
            goal="Analyze code changes and identify documentation impacts",
            backstory="""You are an expert at understanding code changes and their implications.
            You excel at identifying what documentation needs to be updated based on git diffs.""",
            verbose=True,
            allow_delegation=False,
            tools=[analyze_diff],
            llm_config={"model": self.model},
        )

    def create_analysis_task(self, diff: str) -> Task:
        """Create task for analyzing code changes."""
        return Task(
            description=f"""Analyze the following git diff and identify what documentation updates are needed:
            
            {diff}
            
            Focus on:
            1. New features or functionality added
            2. Changed APIs or interfaces
            3. Updated configuration options
            4. Modified commands or workflows
            5. Deprecated or removed features
            """,
            agent=self.agent,
            expected_output="List of documentation changes needed based on the code diff",
        )


class DocumentationWriterAgent:
    """Agent for updating documentation based on code changes."""

    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize documentation writer with model configuration."""
        self.model = model
        self.agent = Agent(
            role="Technical Documentation Expert",
            goal="Update documentation to reflect code changes accurately",
            backstory="""You are a world-class technical writer who creates clear, comprehensive documentation.
            You ensure docs are always in sync with code and avoid duplication between different doc files.""",
            verbose=True,
            allow_delegation=False,
            tools=[read_documentation],
            llm_config={"model": self.model},
        )

    def create_update_task(self, doc_type: str, file_path: str, doc_content: str, context_tasks: List[Task]) -> Task:
        """Create task for updating documentation."""
        return Task(
            description=f"""Update the {doc_type} documentation based on the code changes analysis.
            
            Current {file_path}:
            {doc_content}
            
            Important guidelines:
            - Only output new or updated sections, not the full document
            - Start updated sections with their header (## Section Name)
            - Avoid duplicating content that exists in other documentation files
            - README should be concise and point to Wiki for details
            - Each document should have unique purpose and content
            - If no changes needed, return 'NO CHANGES'
            """,
            agent=self.agent,
            expected_output="Updated documentation sections or 'NO CHANGES'",
            context=context_tasks,
        )


class WikiSelectorAgent:
    """Agent for selecting relevant wiki articles based on code changes."""

    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize wiki selector with model configuration."""
        self.model = model
        self.agent = Agent(
            role="Documentation Selector",
            goal="Select relevant wiki articles that need updates based on code changes",
            backstory="You are an expert at understanding which documentation needs updates based on code changes.",
            verbose=False,
            allow_delegation=False,
            llm_config={"model": self.model},
        )

    def create_selection_task(self, diff: str, wiki_files: List[str]) -> Task:
        """Create task for selecting wiki articles."""
        return Task(
            description=f"""Based on the following code changes, select which wiki articles should be updated.
            Return ONLY a comma-separated list of filenames that need updates.
            
            Code changes:
            {diff}
            
            Available wiki articles:
            {", ".join(wiki_files)}
            
            Consider updating:
            - Usage.md if commands or workflows changed
            - Architecture.md if system design changed
            - Configuration.md if config options changed
            - API.md if APIs changed
            - Security.md if security features changed
            """,
            agent=self.agent,
            expected_output="Comma-separated list of wiki filenames to update",
        )


class CommitSummaryAgent:
    """Agent for generating concise commit summaries."""

    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize commit summary agent with model configuration."""
        self.model = model
        self.agent = Agent(
            role="Commit Message Expert",
            goal="Generate concise, meaningful commit summaries",
            backstory="You are an expert at writing clear, informative commit messages that follow best practices.",
            verbose=False,
            allow_delegation=False,
            llm_config={"model": self.model},
        )

    def create_summary_task(self, diff: str) -> Task:
        """Create task for generating commit summary."""
        return Task(
            description=f"""Generate a concise commit summary based on these changes:
            
            {diff}
            
            Guidelines:
            - Be specific about what changed
            - Use present tense (e.g., 'Add', 'Fix', 'Update')
            - Keep it under 50 characters if possible
            - Focus on the why, not just the what
            """,
            agent=self.agent,
            expected_output="A concise commit summary",
        )


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
            analysis_task = self.code_analyst.create_analysis_task(diff)
            update_task = self.doc_writer.create_update_task(doc_type, file_path, doc_content, [analysis_task])

            # Create and run the crew
            crew = Crew(agents=[self.code_analyst.agent, self.doc_writer.agent], tasks=[analysis_task, update_task], verbose=True)

            result = crew.kickoff()

            # Extract the final output
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
        task = selector.create_selection_task(diff, wiki_files)

        crew = Crew(agents=[selector.agent], tasks=[task], verbose=False)
        result = crew.kickoff()

        # Parse the result
        selected = [f.strip() for f in str(result).split(",") if f.strip()]
        return [f for f in selected if f in wiki_files]

    except Exception as e:
        logger.error(f"Error selecting wiki articles: {e}")
        return []


def generate_commit_summary(diff: str, model: str = "gpt-4o-mini") -> str:
    """Generate a commit summary using an agent."""
    try:
        summary_agent = CommitSummaryAgent(model)
        task = summary_agent.create_summary_task(diff)

        crew = Crew(agents=[summary_agent.agent], tasks=[task], verbose=False)
        result = crew.kickoff()

        return str(result).strip()

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return "Update codebase"

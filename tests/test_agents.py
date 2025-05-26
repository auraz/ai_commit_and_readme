"""Tests for agent classes."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from crewai import Task

from autodoc_ai.agents import (
    BaseAgent,
    CodeAnalystAgent,
    CommitSummaryAgent,
    DocumentationWriterAgent,
    WikiSelectorAgent,
)


class TestBaseAgent:
    """Tests for BaseAgent."""

    def test_init(self):
        """Test base agent initialization."""
        agent = BaseAgent(role="Test Agent", goal="Test Goal", backstory="Test Story")
        assert agent.model == "gpt-4o-mini"  # Default model
        assert agent.agent is not None
        assert agent.role == "Test Agent"
        assert agent.goal == "Test Goal"
        assert agent.backstory == "Test Story"

    def test_init_with_custom_model(self, monkeypatch):
        """Test base agent with custom model."""
        monkeypatch.setenv("AUTODOC_MODEL", "gpt-4")
        agent = BaseAgent(role="Test", goal="Test", backstory="Test")
        assert agent.model == "gpt-4"

    @patch("autodoc_ai.agents.base.Agent")
    @patch("autodoc_ai.agents.base.LLM")
    def test_create_agent(self, mock_llm_class, mock_agent_class):
        """Test agent creation."""
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm

        BaseAgent(role="Developer", goal="Write code", backstory="Expert coder")

        # Check LLM was created
        mock_llm_class.assert_called_once_with(model="gpt-4o-mini", temperature=0.7)

        # Check Agent was created
        mock_agent_class.assert_called_once()
        call_kwargs = mock_agent_class.call_args[1]
        assert call_kwargs["role"] == "Developer"
        assert call_kwargs["goal"] == "Write code"
        assert call_kwargs["backstory"] == "Expert coder"
        assert call_kwargs["verbose"] is False  # Default is INFO level
        assert call_kwargs["allow_delegation"] is False
        assert call_kwargs["max_iter"] == 5  # Default for non-debug

    def test_create_agent_debug_mode(self, monkeypatch):
        """Test agent creation in debug mode."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "DEBUG")

        with patch("autodoc_ai.agents.base.Agent") as mock_agent_class, patch("autodoc_ai.agents.base.LLM"):
            BaseAgent(role="Test", goal="Test", backstory="Test")

            call_kwargs = mock_agent_class.call_args[1]
            assert call_kwargs["verbose"] is True
            assert call_kwargs["max_iter"] == 10

    def test_save_method(self):
        """Test save method does nothing."""
        agent = BaseAgent(role="Test", goal="Test", backstory="Test")
        # Should not raise any errors
        agent.save()
        agent.save("arg1", key="value")

    def test_load_prompt_success(self, tmp_path, monkeypatch):
        """Test successful prompt loading."""
        # Create a temporary prompt file
        prompts_dir = tmp_path / "prompts" / "tasks"
        prompts_dir.mkdir(parents=True)
        prompt_file = prompts_dir / "test_prompt.md"
        prompt_file.write_text("Test prompt content")

        # Monkey patch the path
        monkeypatch.setattr(Path, "parent", tmp_path)

        agent = BaseAgent(role="Test", goal="Test", backstory="Test")
        with patch.object(Path, "__new__", return_value=prompt_file):
            content = agent.load_prompt("test_prompt")
            assert content == "Test prompt content"

    def test_load_prompt_not_found(self):
        """Test prompt loading when file doesn't exist."""
        agent = BaseAgent(role="Test", goal="Test", backstory="Test")
        with pytest.raises(FileNotFoundError, match="Prompt file not found"):
            agent.load_prompt("nonexistent_prompt")


class TestCodeAnalystAgent:
    """Tests for CodeAnalystAgent."""

    def test_init(self):
        """Test code analyst initialization."""
        agent = CodeAnalystAgent()
        assert agent.role == "Senior Code Analyst"
        assert "code changes" in agent.goal.lower()
        assert agent.agent is not None

    def test_create_task_with_diff(self):
        """Test task creation with diff parameter."""
        agent = CodeAnalystAgent()

        # Mock the prompt loading
        with patch.object(agent, "load_prompt", return_value="Analyze: {diff}"):
            task = agent.create_task("Analyze this diff", diff="+ added line\n- removed line")

            assert isinstance(task, Task)
            assert "added line" in task.description
            assert "removed line" in task.description
            assert task.agent == agent.agent
            assert task.expected_output == "Structured code analysis"

    def test_create_task_default_diff(self):
        """Test task creation with content as diff."""
        agent = CodeAnalystAgent()

        with patch.object(agent, "load_prompt", return_value="Analyze: {diff}"):
            task = agent.create_task("diff content here")

            assert "diff content here" in task.description


class TestDocumentationWriterAgent:
    """Tests for DocumentationWriterAgent."""

    def test_init(self):
        """Test documentation writer initialization."""
        agent = DocumentationWriterAgent()
        assert agent.role == "Technical Documentation Expert"
        assert "documentation" in agent.goal.lower()
        assert agent.agent is not None

    def test_create_task_readme(self):
        """Test task creation for README."""
        agent = DocumentationWriterAgent()

        with patch.object(agent, "load_prompt", return_value="Update {doc_type} at {file_path}: {content}"):
            task = agent.create_task("README content", doc_type="README", file_path="README.md")

            assert isinstance(task, Task)
            assert "README" in task.description
            assert "README.md" in task.description
            assert task.agent == agent.agent

    def test_create_task_wiki_with_other_docs(self):
        """Test task creation for wiki with other docs context."""
        agent = DocumentationWriterAgent()

        with patch.object(agent, "load_prompt", return_value="Update {doc_type} at {file_path}: {content}"):
            other_docs = {"API.md": "API documentation summary", "Usage.md": "Usage guide summary"}

            task = agent.create_task("Wiki content", doc_type="wiki", file_path="Architecture.md", other_docs=other_docs)

            assert "wiki" in task.description
            assert "Architecture.md" in task.description
            assert "API.md" in task.description
            assert "Usage.md" in task.description
            assert "unique content" in task.description

    def test_create_task_with_context_tasks(self):
        """Test task creation with context tasks."""
        agent = DocumentationWriterAgent()
        # Create a proper Task mock that passes pydantic validation
        context_task = MagicMock(spec=Task)
        context_task.model_dump = MagicMock(return_value={"description": "test", "agent": None})

        with patch.object(agent, "load_prompt", return_value="Update: {content}"), patch("autodoc_ai.agents.documentation_writer.Task") as mock_task:
            mock_task_instance = MagicMock()
            mock_task.return_value = mock_task_instance

            task = agent.create_task("Write docs", doc_type="README", file_path="README.md", context_tasks=[context_task])

            # Verify Task was called with context
            mock_task.assert_called_once()
            call_kwargs = mock_task.call_args[1]
            assert call_kwargs["context"] == [context_task]
            assert task == mock_task_instance

    def test_create_task_defaults(self):
        """Test task creation with default parameters."""
        agent = DocumentationWriterAgent()

        with patch.object(agent, "load_prompt", return_value="{doc_type} {file_path}: {content}"):
            task = agent.create_task("Content here")

            assert "documentation" in task.description  # default doc_type
            assert "document" in task.description  # default file_path


class TestWikiSelectorAgent:
    """Tests for WikiSelectorAgent."""

    def test_init(self):
        """Test wiki selector initialization."""
        agent = WikiSelectorAgent()
        assert agent.role == "Documentation Selector"
        assert "wiki articles" in agent.goal.lower()
        assert agent.agent is not None

    def test_create_task(self):
        """Test task creation with wiki files."""
        agent = WikiSelectorAgent()
        wiki_files = ["Usage.md", "API.md", "FAQ.md"]

        with patch.object(agent, "load_prompt", return_value="Select from {wiki_files}: {content}"):
            task = agent.create_task("diff content", wiki_files=wiki_files)

            assert isinstance(task, Task)
            assert "Usage.md, API.md, FAQ.md" in task.description
            assert "diff content" in task.description
            assert task.agent == agent.agent

    def test_create_task_empty_wiki_files(self):
        """Test task creation with empty wiki files."""
        agent = WikiSelectorAgent()

        with patch.object(agent, "load_prompt", return_value="Select from {wiki_files}: {content}"):
            task = agent.create_task("diff", wiki_files=[])

            assert task.description  # Should still create a task


class TestCommitSummaryAgent:
    """Tests for CommitSummaryAgent."""

    def test_init(self):
        """Test commit summary agent initialization."""
        agent = CommitSummaryAgent()
        assert agent.role == "Commit Message Expert"
        assert "commit" in agent.goal.lower()
        assert agent.agent is not None
        assert agent.agent.verbose is False  # Explicitly set to False

    def test_create_task(self):
        """Test task creation."""
        agent = CommitSummaryAgent()

        with patch.object(agent, "load_prompt", return_value="Summarize: {content}"):
            task = agent.create_task("diff content")

            assert isinstance(task, Task)
            assert "diff content" in task.description
            assert task.agent == agent.agent
            assert task.expected_output == "Structured commit summary"


@pytest.mark.parametrize(
    "agent_class,expected_role",
    [
        (CodeAnalystAgent, "Senior Code Analyst"),
        (DocumentationWriterAgent, "Technical Documentation Expert"),
        (WikiSelectorAgent, "Documentation Selector"),
        (CommitSummaryAgent, "Commit Message Expert"),
    ],
)
def test_agent_roles(agent_class, expected_role):
    """Test that each agent has the correct role."""
    agent = agent_class()
    assert agent.role == expected_role


def test_all_agents_verbose_mode():
    """Test that all agents respect debug mode."""
    with patch.dict(os.environ, {"AUTODOC_LOG_LEVEL": "DEBUG"}):
        agents = [
            CodeAnalystAgent(),
            DocumentationWriterAgent(),
            WikiSelectorAgent(),
            CommitSummaryAgent(),
        ]

        for agent in agents:
            # WikiSelectorAgent and CommitSummaryAgent explicitly set verbose=False
            if isinstance(agent, WikiSelectorAgent | CommitSummaryAgent):
                assert agent.agent.verbose is False
            else:
                # Other agents should be verbose in debug mode
                assert agent.agent.verbose is True
            assert agent.agent.allow_delegation is False


def test_all_agents_inherit_base():
    """Test that all agents inherit from BaseAgent."""
    agents = [
        CodeAnalystAgent(),
        DocumentationWriterAgent(),
        WikiSelectorAgent(),
        CommitSummaryAgent(),
    ]

    for agent in agents:
        assert isinstance(agent, BaseAgent)
        assert hasattr(agent, "model")
        assert hasattr(agent, "agent")
        assert hasattr(agent, "save")
        assert hasattr(agent, "load_prompt")


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])

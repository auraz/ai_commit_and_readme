"""Tests for commit summary crew."""

from unittest.mock import MagicMock, patch

import pytest

from autodoc_ai.crews.commit_summary import CommitSummaryCrew


class TestCommitSummaryCrew:
    """Tests for CommitSummaryCrew."""

    def test_init(self):
        """Test commit summary crew initialization."""
        crew = CommitSummaryCrew()
        assert hasattr(crew, "summary_agent")
        assert len(crew.agents) == 1

    @patch("autodoc_ai.crews.commit_summary.CommitSummaryAgent")
    def test_execute_success(self, mock_agent_class):
        """Test successful commit summary generation."""
        # Mock the agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # Mock the task
        mock_task = MagicMock()
        mock_agent.create_task.return_value = mock_task

        crew = CommitSummaryCrew()

        # Mock crew output
        mock_output = MagicMock()
        mock_output.raw = "feat: Add new authentication system with OAuth2 support"

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            result = crew._execute("test diff content")

            assert result == "feat: Add new authentication system with OAuth2 support"
            mock_agent.create_task.assert_called_once_with("test diff content")

    def test_execute_none_result(self):
        """Test handling None result from crew."""
        crew = CommitSummaryCrew()

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = None
            mock_create_crew.return_value = mock_crew_instance

            result = crew._execute("test diff")

            assert result == "Update codebase"

    def test_execute_empty_raw_output(self):
        """Test handling empty raw output."""
        crew = CommitSummaryCrew()

        # Create a mock output object that has empty raw but no pydantic
        class MockOutput:
            def __init__(self):
                self.raw = ""
        
        mock_output = MockOutput()

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            result = crew._execute("test diff")

            assert result == "Update codebase"

    def test_execute_with_object_output(self):
        """Test handling output without raw attribute."""
        crew = CommitSummaryCrew()

        mock_output = "Direct string output"

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            result = crew._execute("test diff")

            assert result == "Direct string output"

    def test_execute_multiline_output(self):
        """Test handling multiline commit message."""
        crew = CommitSummaryCrew()

        mock_output = MagicMock()
        mock_output.raw = """feat: Add comprehensive logging system

- Implement structured logging with levels
- Add log rotation and archiving
- Include performance metrics logging"""

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            result = crew._execute("test diff")

            assert "feat: Add comprehensive logging system" in result
            assert "Implement structured logging" in result

    def test_handle_error(self):
        """Test error handling."""
        crew = CommitSummaryCrew()
        error = Exception("API error")
        result = crew._handle_error(error)
        assert result == "Update codebase"

    def test_run_integration(self):
        """Test the public run method."""
        crew = CommitSummaryCrew()

        expected_summary = "fix: Resolve memory leak in data processor"
        with patch.object(crew, "_execute", return_value=expected_summary) as mock_execute:
            result = crew.run("diff content")

            assert result == expected_summary
            mock_execute.assert_called_once_with("diff content")

    def test_logging_messages(self, caplog):
        """Test that appropriate log messages are generated."""
        crew = CommitSummaryCrew()

        mock_output = MagicMock()
        mock_output.raw = "chore: Update dependencies"

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            with caplog.at_level("INFO"):
                crew._execute("test diff")

            assert "Starting commit summary generation" in caplog.text
            assert "Kicking off commit summary crew" in caplog.text
            assert "Commit summary crew completed" in caplog.text

    def test_crew_creation_with_task(self):
        """Test that crew is created with proper task."""
        crew = CommitSummaryCrew()

        mock_output = MagicMock()
        mock_output.raw = "test: Add unit tests"

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            crew._execute("test diff")

            # Verify _create_crew was called with a list containing one task
            mock_create_crew.assert_called_once()
            tasks_arg = mock_create_crew.call_args[0][0]
            assert isinstance(tasks_arg, list)
            assert len(tasks_arg) == 1


def test_execute_result_with_pydantic_summary():
    """Test handling result with pydantic attribute."""
    crew = CommitSummaryCrew()

    # Create a mock result with pydantic attribute but no raw
    mock_result = MagicMock()
    mock_result.pydantic.summary = "Pydantic summary"
    # Make str(result) return empty string
    mock_result.__str__.return_value = ""
    # Remove raw attribute
    del mock_result.raw

    with patch.object(crew, "_create_crew") as mock_create_crew:
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_create_crew.return_value = mock_crew_instance

        result = crew._execute("test diff")

        # Should return the pydantic summary
        assert result == "Pydantic summary"


def test_execute_fallback_to_default():
    """Test fallback to default when no valid output."""
    crew = CommitSummaryCrew()

    # Create a simple object that returns empty string
    class EmptyResult:
        def __str__(self):
            return ""

    mock_result = EmptyResult()

    with patch.object(crew, "_create_crew") as mock_create_crew:
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_create_crew.return_value = mock_crew_instance

        result = crew._execute("test diff")

        # Should return the fallback
        assert result == "Update codebase"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])

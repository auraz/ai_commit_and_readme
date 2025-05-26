"""Tests for wiki selector crew."""

from unittest.mock import MagicMock, patch

import pytest

from autodoc_ai.crews.wiki_selector import WikiSelectorCrew


class TestWikiSelectorCrew:
    """Tests for WikiSelectorCrew."""

    def test_init(self):
        """Test wiki selector initialization."""
        crew = WikiSelectorCrew()
        assert crew.selector is not None
        assert len(crew.agents) == 1

    @patch("autodoc_ai.crews.wiki_selector.WikiSelectorAgent")
    def test_execute_success(self, mock_agent_class):
        """Test successful wiki selection."""
        # Mock the agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # Mock the task creation
        mock_task = MagicMock()
        mock_agent.create_task.return_value = mock_task

        # Create crew and mock its kickoff
        crew = WikiSelectorCrew()

        # Mock crew output
        mock_output = MagicMock()
        mock_output.raw = '["Usage.md", "API.md", "Installation.md"]'

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            result = crew._execute("test diff", ["Usage.md", "API.md", "Installation.md", "FAQ.md"])

            assert result == ["Usage.md", "API.md", "Installation.md"]
            mock_agent.create_task.assert_called_once_with("test diff", wiki_files=["Usage.md", "API.md", "Installation.md", "FAQ.md"])

    def test_execute_none_result(self):
        """Test handling of None result from crew."""
        crew = WikiSelectorCrew()

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = None
            mock_create_crew.return_value = mock_crew_instance

            result = crew._execute("test diff", ["File1.md", "File2.md"])

            assert result == []

    def test_execute_with_json_list(self):
        """Test parsing JSON list from crew output."""
        crew = WikiSelectorCrew()

        mock_output = MagicMock()
        mock_output.raw = '["README.md", "Usage.md"]'

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            result = crew._execute("test diff", ["README.md", "Usage.md", "API.md"])

            assert result == ["README.md", "Usage.md"]

    def test_execute_with_text_mentions(self):
        """Test extracting wiki files from text output."""
        crew = WikiSelectorCrew()

        mock_output = MagicMock()
        mock_output.raw = """
        Based on the diff, I recommend updating the following wiki files:
        - Usage.md: Contains usage examples that need updating
        - API.md: API documentation affected by the changes
        - Configuration.md: New config options added
        """

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            wiki_files = ["Usage.md", "API.md", "Configuration.md", "FAQ.md", "Installation.md"]
            result = crew._execute("test diff", wiki_files)

            assert "Usage.md" in result
            assert "API.md" in result
            assert "Configuration.md" in result
            assert "FAQ.md" not in result

    def test_execute_with_pydantic_output(self):
        """Test handling pydantic output format."""
        crew = WikiSelectorCrew()

        mock_output = MagicMock()
        # When raw is None or empty, it should check pydantic
        mock_output.raw = ""
        # Add hasattr check for pydantic
        mock_output.pydantic = MagicMock()
        mock_output.pydantic.selected_articles = ["Architecture.md", "Deployment.md"]

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            result = crew._execute("test diff", ["Architecture.md", "Deployment.md", "Security.md"])

            assert result == ["Architecture.md", "Deployment.md"]

    def test_execute_empty_output(self):
        """Test handling empty output."""
        crew = WikiSelectorCrew()

        mock_output = MagicMock()
        mock_output.raw = ""
        # Make sure hasattr returns False for pydantic
        mock_output.configure_mock(**{"pydantic": None})
        del mock_output.pydantic  # Remove the attribute

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            result = crew._execute("test diff", ["File1.md", "File2.md"])

            assert result == []

    def test_execute_with_regex_matches(self):
        """Test regex pattern matching for wiki files."""
        crew = WikiSelectorCrew()

        mock_output = MagicMock()
        mock_output.raw = 'The selected files are: ["Home.md", "Getting-Started.md", "Troubleshooting.md"]'

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            wiki_files = ["Home.md", "Getting-Started.md", "Troubleshooting.md", "Advanced.md"]
            result = crew._execute("test diff", wiki_files)

            assert "Home.md" in result
            assert "Getting-Started.md" in result
            assert "Troubleshooting.md" in result
            assert len(result) == 3

    def test_handle_error(self):
        """Test error handling."""
        crew = WikiSelectorCrew()
        error = Exception("Test error")
        result = crew._handle_error(error)
        assert result == []

    def test_run_integration(self):
        """Test the public run method."""
        crew = WikiSelectorCrew()

        with patch.object(crew, "_execute", return_value=["Selected.md"]) as mock_execute:
            result = crew.run("diff content", ["Selected.md", "NotSelected.md"])

            assert result == ["Selected.md"]
            mock_execute.assert_called_once_with("diff content", ["Selected.md", "NotSelected.md"])


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])

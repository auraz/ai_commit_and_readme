"""Tests for enrichment crew."""

from unittest.mock import MagicMock, patch

import pytest

from autodoc_ai.crews.enrichment import EnrichmentCrew


class TestEnrichmentCrew:
    """Tests for EnrichmentCrew."""

    def test_init(self):
        """Test enrichment crew initialization."""
        crew = EnrichmentCrew()
        assert crew.code_analyst is not None
        assert crew.doc_writer is not None
        assert len(crew.agents) == 2

    def test_execute_success_with_changes(self):
        """Test successful enrichment with changes needed."""
        crew = EnrichmentCrew()

        # Mock crew output with markdown content
        mock_output = MagicMock()
        mock_output.raw = """The documentation needs updating. Here's the updated content:

```markdown
# Updated README

This is the new content with improvements.
```"""

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            needs_update, content = crew._execute(diff="test diff", doc_content="old content", doc_type="README", file_path="README.md")

            assert needs_update is True
            assert content == "# Updated README\n\nThis is the new content with improvements."

    def test_execute_no_changes_needed(self):
        """Test enrichment when no changes are needed."""
        crew = EnrichmentCrew()

        mock_output = MagicMock()
        mock_output.raw = "The documentation is already up to date. NO CHANGES needed."

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            needs_update, content = crew._execute(diff="test diff", doc_content="current content", doc_type="wiki", file_path="Usage.md")

            assert needs_update is False
            assert content == "NO CHANGES"

    def test_execute_with_none_result(self):
        """Test handling None result from crew."""
        crew = EnrichmentCrew()

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = None
            mock_create_crew.return_value = mock_crew_instance

            needs_update, content = crew._execute(diff="test diff", doc_content="content", doc_type="README", file_path="README.md")

            assert needs_update is False
            assert content == "NO CHANGES"

    def test_execute_with_pydantic_output(self):
        """Test handling pydantic output format."""
        crew = EnrichmentCrew()

        mock_output = MagicMock()
        mock_output.raw = ""  # Empty raw to trigger pydantic check
        mock_output.pydantic = MagicMock()
        mock_output.pydantic.needs_update = True
        mock_output.pydantic.updated_sections = "# New Content\n\nUpdated documentation."

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            needs_update, content = crew._execute(diff="test diff", doc_content="old content", doc_type="wiki", file_path="API.md")

            assert needs_update is True
            assert content == "# New Content\n\nUpdated documentation."

    def test_execute_with_other_docs(self):
        """Test enrichment with other docs context."""
        crew = EnrichmentCrew()

        mock_output = MagicMock()
        mock_output.raw = "Updated content without duplication"

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            other_docs = {"Usage.md": "Usage guide content", "API.md": "API reference content"}

            needs_update, content = crew._execute(diff="test diff", doc_content="current content", doc_type="wiki", file_path="Architecture.md", other_docs=other_docs)

            assert needs_update is True
            assert content == "Updated content without duplication"

    def test_execute_with_plain_text_output(self):
        """Test handling plain text output without markdown blocks."""
        crew = EnrichmentCrew()

        mock_output = MagicMock()
        mock_output.raw = "This is the updated documentation content directly."

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            needs_update, content = crew._execute(diff="test diff", doc_content="old", doc_type="README", file_path="README.md")

            assert needs_update is True
            assert content == "This is the updated documentation content directly."

    def test_handle_error(self):
        """Test error handling."""
        crew = EnrichmentCrew()
        error = Exception("API error")
        needs_update, content = crew._handle_error(error)
        assert needs_update is False
        assert content == "NO CHANGES"

    def test_run_integration(self):
        """Test the public run method."""
        crew = EnrichmentCrew()

        with patch.object(crew, "_execute", return_value=(True, "Updated content")) as mock_execute:
            result = crew.run(diff="diff", doc_content="content", doc_type="README", file_path="README.md")

            assert result == (True, "Updated content")
            mock_execute.assert_called_once()

    def test_logging_messages(self, caplog):
        """Test that appropriate log messages are generated."""
        crew = EnrichmentCrew()

        mock_output = MagicMock()
        mock_output.raw = "Updated content"

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            with caplog.at_level("INFO"):
                crew._execute(diff="test diff", doc_content="content", doc_type="README", file_path="README.md")

            assert "Starting enrichment for README file: README.md" in caplog.text
            assert "Kicking off enrichment crew for README.md" in caplog.text
            assert "Enrichment crew completed for README.md" in caplog.text


def test_execute_with_code_block_extraction():
    """Test extraction of content from markdown code blocks."""
    crew = EnrichmentCrew()

    mock_output = MagicMock()
    mock_output.raw = """Here's the updated content:

```markdown
# Extracted Content

This should be extracted.
```

Some other text outside."""

    with patch.object(crew, "_create_crew") as mock_create_crew:
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_output
        mock_create_crew.return_value = mock_crew_instance

        needs_update, content = crew._execute(diff="test diff", doc_content="old content", doc_type="README", file_path="README.md")

        assert needs_update is True
        assert content == "# Extracted Content\n\nThis should be extracted."


def test_execute_non_string_no_raw_no_pydantic():
    """Test handling non-string result without raw or pydantic attributes."""
    crew = EnrichmentCrew()

    # Create a simple object that returns empty string
    class EmptyResult:
        def __str__(self):
            return ""

    mock_result = EmptyResult()

    with patch.object(crew, "_create_crew") as mock_create_crew:
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_create_crew.return_value = mock_crew_instance

        needs_update, content = crew._execute(diff="test diff", doc_content="old content", doc_type="README", file_path="README.md")

        # Should return the fallback
        assert needs_update is False
        assert content == "NO CHANGES"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])

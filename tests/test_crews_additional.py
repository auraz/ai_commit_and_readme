"""Additional tests for crew classes to increase coverage."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from autodoc_ai.crews.base import BaseCrew
from autodoc_ai.crews.commit_summary import CommitSummaryCrew
from autodoc_ai.crews.enrichment import EnrichmentCrew
from autodoc_ai.crews.pipeline import PipelineCrew
from autodoc_ai.crews.wiki_selector import WikiSelectorCrew


class TestBaseCrew:
    """Additional tests for BaseCrew."""

    def test_callbacks_with_output_attributes(self):
        """Test callbacks handle different output formats."""
        crew = BaseCrew()
        mock_agent = MagicMock()
        mock_agent.agent = MagicMock()
        crew.agents = [mock_agent]

        mock_task = MagicMock()
        mock_task.description = "Test task with a very long description that should be shown"
        tasks = [mock_task]

        with patch("autodoc_ai.crews.base.Crew") as mock_crew_class:
            crew._create_crew(tasks)
            call_args = mock_crew_class.call_args[1]

            # Test task callback with output that has task attribute
            task_callback = call_args.get("task_callback")
            if task_callback:
                # Test with output that has task and raw
                mock_output = MagicMock()
                mock_output.task = mock_task
                mock_output.raw = "Task completed successfully with detailed output"
                task_callback(mock_output)

                # Test with output without task attribute
                mock_output2 = MagicMock()
                del mock_output2.task
                mock_output2.raw = "Direct output"
                task_callback(mock_output2)

    def test_callbacks_debug_mode_detailed(self, monkeypatch):
        """Test callbacks provide detailed output in debug mode."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "DEBUG")

        crew = BaseCrew()
        mock_agent = MagicMock()
        mock_agent.agent = MagicMock()
        crew.agents = [mock_agent]

        mock_task = MagicMock()
        tasks = [mock_task]

        with patch("autodoc_ai.crews.base.Crew") as mock_crew_class:
            crew._create_crew(tasks)
            call_args = mock_crew_class.call_args[1]

            # Test step callback in debug mode
            step_callback = call_args.get("step_callback")
            if step_callback:
                step_callback("Detailed step output with context")


class TestCommitSummaryCrew:
    """Additional tests for CommitSummaryCrew."""

    def test_execute_with_quoted_output(self):
        """Test handling output with quotes."""
        crew = CommitSummaryCrew()

        mock_output = MagicMock()
        mock_output.raw = '"feat: Add new feature with quotes"'

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            result = crew._execute("test diff")

            # Should strip quotes
            assert result == "feat: Add new feature with quotes"

    def test_execute_empty_string_fallback(self):
        """Test fallback when output is empty string."""
        crew = CommitSummaryCrew()

        mock_output = MagicMock()
        mock_output.raw = '""'  # Empty quoted string

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            result = crew._execute("test diff")

            assert result == "Update codebase"

    def test_execute_with_pydantic_future(self):
        """Test future compatibility with pydantic output."""
        crew = CommitSummaryCrew()

        mock_output = MagicMock()
        mock_output.raw = ""
        mock_output.pydantic = MagicMock()
        mock_output.pydantic.summary = "feat: Future pydantic support"

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            result = crew._execute("test diff")

            assert result == "feat: Future pydantic support"


class TestEnrichmentCrew:
    """Additional tests for EnrichmentCrew."""

    def test_execute_no_code_blocks(self):
        """Test when output has no markdown code blocks."""
        crew = EnrichmentCrew()

        mock_output = MagicMock()
        mock_output.raw = "Direct content without markdown blocks"

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            needs_update, content = crew._execute(diff="test diff", doc_content="old", doc_type="README", file_path="README.md")

            assert needs_update is True
            assert content == "Direct content without markdown blocks"

    def test_execute_with_markdown_code_block(self):
        """Test extracting content from markdown code blocks."""
        crew = EnrichmentCrew()

        mock_output = MagicMock()
        mock_output.raw = """Here's the updated documentation:

```markdown
# Updated Documentation

This is the extracted content from the code block.
```

End of output."""

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            needs_update, content = crew._execute(diff="test diff", doc_content="old", doc_type="README", file_path="README.md")

            assert needs_update is True
            assert content == "# Updated Documentation\n\nThis is the extracted content from the code block."

    def test_execute_uppercase_no_changes(self):
        """Test detection of NO CHANGES in uppercase."""
        crew = EnrichmentCrew()

        mock_output = MagicMock()
        mock_output.raw = "The document looks good. NO CHANGES required."

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            needs_update, content = crew._execute(diff="test diff", doc_content="current", doc_type="wiki", file_path="FAQ.md")

            assert needs_update is False
            assert content == "NO CHANGES"


class TestWikiSelectorCrew:
    """Additional tests for WikiSelectorCrew."""

    def test_execute_with_json_parsing(self):
        """Test JSON array parsing from output."""
        crew = WikiSelectorCrew()

        mock_output = MagicMock()
        mock_output.raw = 'Selected files: ["API.md", "Usage.md", "Installation.md"]'

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            wiki_files = ["API.md", "Usage.md", "Installation.md", "FAQ.md"]
            result = crew._execute("test diff", wiki_files)

            # Should extract all three files
            assert len(result) == 3
            assert "API.md" in result
            assert "Usage.md" in result
            assert "Installation.md" in result

    def test_execute_with_single_quotes(self):
        """Test parsing with single quotes."""
        crew = WikiSelectorCrew()

        mock_output = MagicMock()
        mock_output.raw = "['Configuration.md', 'Security.md']"

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            wiki_files = ["Configuration.md", "Security.md", "Other.md"]
            result = crew._execute("test diff", wiki_files)

            assert "Configuration.md" in result
            assert "Security.md" in result

    def test_execute_fallback_text_search(self):
        """Test fallback text search when no JSON found."""
        crew = WikiSelectorCrew()

        mock_output = MagicMock()
        mock_output.raw = """
        After analyzing the diff, the following wiki files need updates:
        - Architecture.md: System design changes
        - Deployment.md: New deployment steps
        
        FAQ.md and Contributing.md don't need updates.
        """

        with patch.object(crew, "_create_crew") as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance

            wiki_files = ["Architecture.md", "Deployment.md", "FAQ.md", "Contributing.md"]
            result = crew._execute("test diff", wiki_files)

            assert "Architecture.md" in result
            assert "Deployment.md" in result
            assert "FAQ.md" in result  # Also mentioned in text
            assert "Contributing.md" in result  # Also mentioned


class TestPipelineCrew:
    """Additional tests for PipelineCrew."""

    def test_count_tokens_with_unsupported_model(self):
        """Test token counting with unsupported model."""
        crew = PipelineCrew()
        crew.model = "unsupported-model-xyz"

        # Should fall back to cl100k_base encoding
        count = crew._count_tokens("Test text for token counting")
        assert isinstance(count, int)
        assert count > 0

    def test_get_git_diff_with_subprocess_error(self):
        """Test git diff with subprocess error details."""
        crew = PipelineCrew()

        with patch("subprocess.check_output") as mock_check:
            error = subprocess.CalledProcessError(128, "git diff", stderr=b"fatal: not a git repository")
            mock_check.side_effect = error

            with pytest.raises(ValueError, match="Git diff error"):
                crew._get_git_diff()

    def test_get_commits_diff_single_commit(self):
        """Test commits diff with single commit (edge case)."""
        crew = PipelineCrew()

        with patch("subprocess.check_output") as mock_check:
            mock_check.side_effect = [
                "\n",  # Empty line (filtered out)
                # Should raise ValueError for no commits
            ]

            with pytest.raises(ValueError, match="No commits in the last"):
                crew._get_commits_diff(1)

    def test_write_outputs_debug_logging(self, caplog, tmp_path, monkeypatch):
        """Test debug logging in write outputs."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "DEBUG")

        crew = PipelineCrew()
        readme_path = tmp_path / "README.md"

        mock_run = MagicMock()
        monkeypatch.setattr("subprocess.run", mock_run)

        ctx = {"readme_path": str(readme_path), "wiki_file_paths": {}}

        suggestions = {"README.md": "New content", "wiki": {}}

        with caplog.at_level("DEBUG"):
            crew._write_outputs(suggestions, ctx)

        assert "Writing outputs" in caplog.text

    def test_process_documents_no_wiki_files(self, monkeypatch):
        """Test document processing with no wiki files."""
        crew = PipelineCrew()

        ctx = {"readme_path": "/tmp/README.md", "wiki_files": [], "wiki_file_paths": {}}

        # Mock the load_file method
        with patch.object(crew, "load_file", return_value="README content"), patch.object(crew.enrichment_crew, "run", return_value=(False, "NO CHANGES")):
            result = crew._process_documents("test diff", ctx)

            assert result["selected_articles"] == []
            assert result["suggestions"]["README.md"] is None

    def test_generate_summary_with_diff_parameter(self):
        """Test generate summary with provided diff."""
        crew = PipelineCrew()

        with patch.object(crew.commit_summary_crew, "run", return_value="feat: Custom diff summary"):
            summary = crew.generate_summary("custom diff content")

            assert summary == "feat: Custom diff summary"
            crew.commit_summary_crew.run.assert_called_once_with("custom diff content")

    def test_generate_summary_try_staged_first(self):
        """Test generate summary tries staged changes first."""
        crew = PipelineCrew()

        with patch("subprocess.check_output") as mock_check:
            mock_check.side_effect = [
                "staged diff content",  # git diff --cached succeeds
            ]

            with patch.object(crew.commit_summary_crew, "run", return_value="feat: Staged changes"):
                summary = crew.generate_summary()

                assert summary == "feat: Staged changes"
                # Should only call once for staged diff
                assert mock_check.call_count == 1

    def test_generate_summary_fallback_to_last_commit(self):
        """Test generate summary falls back to last commit."""
        crew = PipelineCrew()

        with patch("subprocess.check_output") as mock_check:
            mock_check.side_effect = [
                "",  # No staged changes
                "last commit diff",  # Last commit diff
            ]

            with patch.object(crew.commit_summary_crew, "run", return_value="fix: Last commit"):
                summary = crew.generate_summary()

                assert summary == "fix: Last commit"

    def test_write_suggestion_and_stage_with_none(self):
        """Test write suggestion handles None input."""
        crew = PipelineCrew()
        crew._write_suggestion_and_stage("/tmp/test.md", None, "test")
        # Should return early without writing

    def test_execute_debug_diff_preview(self, monkeypatch, caplog):
        """Test debug mode shows diff preview."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "DEBUG")

        crew = PipelineCrew()
        long_diff = "x" * 2000  # Long diff for preview

        with (
            patch("subprocess.check_output", return_value=long_diff),
            patch.object(crew, "_process_documents", return_value={"suggestions": {}, "selected_articles": []}),
            patch.object(crew, "_write_outputs"),
            caplog.at_level("DEBUG"),
        ):
            crew._execute()

            assert "Git diff preview" in caplog.text
            assert "=" * 80 in caplog.text


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])

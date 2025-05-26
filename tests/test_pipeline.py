"""Tests for pipeline crew."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from autodoc_ai.crews.pipeline import PipelineCrew


class TestPipelineCrew:
    """Tests for the main pipeline crew."""

    @pytest.fixture
    def pipeline_crew(self):
        """Create a pipeline crew instance."""
        return PipelineCrew()

    @pytest.fixture
    def mock_context(self, tmp_path):
        """Create a mock context for testing."""
        readme_path = tmp_path / "README.md"
        readme_path.write_text("# Test README\n\nTest content")

        wiki_path = tmp_path / "wiki"
        wiki_path.mkdir()
        (wiki_path / "Usage.md").write_text("# Usage\n\nHow to use")
        (wiki_path / "API.md").write_text("# API\n\nAPI reference")

        return {
            "readme_path": str(readme_path),
            "wiki_path": str(wiki_path),
            "api_key": "test-key",
            "model": "gpt-4o-mini",
            "wiki_files": ["Usage.md", "API.md"],
            "wiki_file_paths": {"Usage.md": str(wiki_path / "Usage.md"), "API.md": str(wiki_path / "API.md")},
        }

    def test_create_context(self, pipeline_crew, monkeypatch):
        """Test context creation."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("WIKI_PATH", "wiki")

        ctx = pipeline_crew._create_context()

        assert ctx["api_key"] == "test-key"
        assert ctx["model"] == "gpt-4o-mini"
        assert ctx["wiki_path"] == "wiki"
        assert "readme_path" in ctx

    def test_get_wiki_files(self, pipeline_crew, tmp_path):
        """Test getting wiki files."""
        wiki_path = tmp_path / "wiki"
        wiki_path.mkdir()
        (wiki_path / "File1.md").touch()
        (wiki_path / "File2.md").touch()
        (wiki_path / "not-md.txt").touch()

        files, paths = pipeline_crew._get_wiki_files(str(wiki_path))

        assert len(files) == 2
        assert "File1.md" in files
        assert "File2.md" in files
        assert "not-md.txt" not in files

    @patch("subprocess.check_output")
    def test_get_git_diff(self, mock_subprocess, pipeline_crew):
        """Test getting git diff."""
        mock_subprocess.return_value = "diff content"

        diff = pipeline_crew._get_git_diff()

        assert diff == "diff content"
        mock_subprocess.assert_called_with(["git", "diff", "--cached", "-U1"], text=True)

    @patch("subprocess.check_output")
    def test_get_git_diff_no_changes(self, mock_subprocess, pipeline_crew):
        """Test getting git diff with no changes."""
        mock_subprocess.return_value = ""

        with pytest.raises(ValueError, match="No staged changes"):
            pipeline_crew._get_git_diff()

    @patch("subprocess.check_output")
    def test_get_commits_diff(self, mock_subprocess, pipeline_crew):
        """Test getting commits diff."""
        mock_subprocess.side_effect = [
            "hash1\nhash2\nhash3",  # git log output
            "parent-hash",  # git rev-parse output
            "diff content",  # git diff output
            "commit log output",  # git log --oneline output
        ]

        diff = pipeline_crew._get_commits_diff(7)

        assert diff == "diff content"
        assert mock_subprocess.call_count == 4

    def test_count_tokens(self, pipeline_crew):
        """Test token counting."""
        text = "This is a test text"
        count = pipeline_crew._count_tokens(text)

        # Should return a positive integer
        assert isinstance(count, int)
        assert count > 0

    @patch("autodoc_ai.crews.pipeline.EnrichmentCrew")
    @patch("autodoc_ai.crews.pipeline.WikiSelectorCrew")
    def test_process_documents(self, mock_wiki_selector, mock_enrichment, pipeline_crew, mock_context):
        """Test document processing."""
        # Replace the actual crew instances with mocks
        mock_wiki_instance = MagicMock()
        mock_wiki_instance.run.return_value = ["Usage.md"]
        pipeline_crew.wiki_selector_crew = mock_wiki_instance

        mock_enrich_instance = MagicMock()
        mock_enrich_instance.run.return_value = (True, "# Updated README\n\nNew content")
        pipeline_crew.enrichment_crew = mock_enrich_instance

        diff = "test diff"
        result = pipeline_crew._process_documents(diff, mock_context)

        assert "suggestions" in result
        assert "selected_articles" in result
        assert result["selected_articles"] == ["Usage.md"]

    def test_write_suggestion_and_stage(self, pipeline_crew, tmp_path, monkeypatch):
        """Test writing suggestions and staging."""
        file_path = tmp_path / "test.md"
        file_path.write_text("old content")

        # Mock subprocess.run
        mock_run = MagicMock()
        monkeypatch.setattr("subprocess.run", mock_run)

        pipeline_crew._write_suggestion_and_stage(str(file_path), "new content", "test")

        assert file_path.read_text() == "new content\n"
        mock_run.assert_called_once_with(["git", "add", str(file_path)])

    def test_write_suggestion_no_changes(self, pipeline_crew, tmp_path):
        """Test writing suggestions with NO CHANGES."""
        file_path = tmp_path / "test.md"

        # Should not write or stage
        pipeline_crew._write_suggestion_and_stage(str(file_path), "NO CHANGES", "test")

        assert not file_path.exists()

    @patch("autodoc_ai.crews.pipeline.PipelineCrew._get_git_diff")
    @patch("autodoc_ai.crews.pipeline.PipelineCrew._process_documents")
    @patch("autodoc_ai.crews.pipeline.PipelineCrew._write_outputs")
    def test_execute_success(self, mock_write, mock_process, mock_diff, pipeline_crew, monkeypatch):
        """Test successful pipeline execution."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        mock_diff.return_value = "test diff"
        mock_process.return_value = {"suggestions": {"README.md": "updated"}, "selected_articles": ["Usage.md"]}

        result = pipeline_crew._execute()

        assert result["success"] is True
        assert "suggestions" in result
        assert "selected_wiki_articles" in result

    def test_execute_no_api_key(self, pipeline_crew, monkeypatch):
        """Test execution without API key."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        result = pipeline_crew._execute()

        assert result["success"] is False
        assert "No API key" in result["error"]

    def test_handle_error(self, pipeline_crew):
        """Test error handling."""
        error = Exception("Test error")
        result = pipeline_crew._handle_error(error)

        assert result["success"] is False
        assert result["error"] == "Test error"

    @patch("subprocess.check_output")
    def test_generate_summary(self, mock_subprocess, pipeline_crew):
        """Test commit summary generation."""
        mock_subprocess.return_value = "test diff"

        # Mock the commit summary crew
        with patch.object(pipeline_crew.commit_summary_crew, "run", return_value="Summary of changes"):
            summary = pipeline_crew.generate_summary()

            assert summary == "Summary of changes"

    @patch("subprocess.check_output")
    def test_generate_summary_no_changes(self, mock_subprocess, pipeline_crew):
        """Test commit summary with no changes."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "git")

        summary = pipeline_crew.generate_summary()

        assert summary == "No changes to summarize"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])

"""Tests to fill coverage gaps and reach 95%."""

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from autodoc_ai.crews.base import BaseCrew
from autodoc_ai.crews.pipeline import PipelineCrew
from autodoc_ai.crews.wiki_selector import WikiSelectorCrew
from autodoc_ai.crews.commit_summary import CommitSummaryCrew


class TestBaseCrew:
    """Tests to cover missing lines in BaseCrew."""
    
    def test_create_crew_explicit_verbose_true(self):
        """Test crew creation with explicit verbose=True."""
        crew = BaseCrew()
        mock_agent = MagicMock()
        mock_agent.agent = MagicMock()
        crew.agents = [mock_agent]
        
        with patch("autodoc_ai.crews.base.Crew") as mock_crew_class:
            crew._create_crew([], verbose=True)
            
            call_args = mock_crew_class.call_args[1]
            assert call_args["verbose"] is True
    
    def test_create_crew_explicit_verbose_false(self):
        """Test crew creation with explicit verbose=False."""
        crew = BaseCrew()
        mock_agent = MagicMock()
        mock_agent.agent = MagicMock()
        crew.agents = [mock_agent]
        
        with patch("autodoc_ai.crews.base.Crew") as mock_crew_class:
            crew._create_crew([], verbose=False)
            
            call_args = mock_crew_class.call_args[1]
            assert call_args["verbose"] is False
    
    def test_task_callback_without_raw_attribute(self):
        """Test task callback when output has no raw attribute."""
        crew = BaseCrew()
        mock_agent = MagicMock()
        mock_agent.agent = MagicMock()
        crew.agents = [mock_agent]
        
        mock_task = MagicMock()
        mock_task.description = "Task description"
        
        with patch("autodoc_ai.crews.base.Crew") as mock_crew_class:
            crew._create_crew([mock_task])
            call_args = mock_crew_class.call_args[1]
            
            task_callback = call_args.get("task_callback")
            if task_callback:
                # Output without raw attribute
                mock_output = MagicMock()
                mock_output.task = mock_task
                del mock_output.raw  # Remove raw attribute
                
                # Should not raise error
                task_callback(mock_output)
    
    def test_after_kickoff_callback(self):
        """Test after_kickoff callback execution."""
        crew = BaseCrew()
        mock_agent = MagicMock()
        mock_agent.agent = MagicMock()
        crew.agents = [mock_agent]
        
        with patch("autodoc_ai.crews.base.Crew") as mock_crew_class:
            crew._create_crew([])
            call_args = mock_crew_class.call_args[1]
            
            after_callbacks = call_args.get("after_kickoff_callbacks", [])
            assert len(after_callbacks) == 1
            
            # Call the callback
            after_callbacks[0]("Final output")


class TestPipelineCrew:
    """Tests to cover missing lines in PipelineCrew."""
    
    def test_get_commits_diff_git_error_handling(self):
        """Test error message extraction from git error."""
        crew = PipelineCrew()
        
        with patch("subprocess.check_output") as mock_check:
            error = subprocess.CalledProcessError(
                128, 
                ["git", "log"],
                stderr=b"fatal: your current branch 'main' does not have any commits yet"
            )
            mock_check.side_effect = error
            
            with pytest.raises(ValueError) as exc_info:
                crew._get_commits_diff(7)
            
            assert "Git commits error" in str(exc_info.value)
    
    def test_process_documents_token_logging(self, caplog):
        """Test token count logging for documents."""
        crew = PipelineCrew()
        
        ctx = {
            "readme_path": "/tmp/README.md",
            "wiki_files": ["Usage.md"],
            "wiki_file_paths": {"Usage.md": "/tmp/wiki/Usage.md"}
        }
        
        with patch.object(crew, 'load_file', side_effect=["README content", "Wiki content"]):
            with patch.object(crew.enrichment_crew, 'run', return_value=(False, "NO CHANGES")):
                with patch.object(crew.wiki_selector_crew, 'run', return_value=["Usage.md"]):
                    with caplog.at_level("INFO"):
                        result = crew._process_documents("test diff", ctx)
                    
                    # Check token logging occurred
                    assert "tokens" in caplog.text


class TestWikiSelectorCrew:
    """Tests to cover missing lines in WikiSelectorCrew."""
    
    def test_execute_with_hasattr_pydantic_check(self):
        """Test pydantic attribute check with hasattr."""
        crew = WikiSelectorCrew()
        
        mock_output = MagicMock()
        mock_output.raw = None  # Trigger pydantic check
        
        # Create a mock that properly handles hasattr
        class MockPydantic:
            selected_articles = ["Test.md"]
        
        mock_output.pydantic = MockPydantic()
        
        with patch.object(crew, '_create_crew') as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance
            
            result = crew._execute("test diff", ["Test.md", "Other.md"])
            
            assert result == ["Test.md"]


class TestCommitSummaryCrew:
    """Tests to cover missing lines in CommitSummaryCrew."""
    
    def test_execute_none_string_result(self):
        """Test when crew returns None but converted to string 'None'."""
        crew = CommitSummaryCrew()
        
        mock_output = None
        
        with patch.object(crew, '_create_crew') as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance
            
            result = crew._execute("test diff")
            
            # str(None) = "None", which is truthy but should return default
            assert result == "Update codebase"
    
    def test_execute_whitespace_only_result(self):
        """Test when result is only whitespace."""
        crew = CommitSummaryCrew()
        
        mock_output = MagicMock()
        mock_output.raw = "   \n\t   "  # Only whitespace
        
        with patch.object(crew, '_create_crew') as mock_create_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = mock_output
            mock_create_crew.return_value = mock_crew_instance
            
            result = crew._execute("test diff")
            
            assert result == "Update codebase"


# Additional specific line coverage tests
class TestMiscCoverage:
    """Tests for miscellaneous coverage gaps."""
    
    def test_pipeline_generate_summary_no_diff_anywhere(self):
        """Test when no diff is found anywhere."""
        crew = PipelineCrew()
        
        with patch("subprocess.check_output") as mock_check:
            # All attempts to get diff fail
            mock_check.side_effect = [
                "",  # No staged changes
                subprocess.CalledProcessError(1, "git")  # No last commit
            ]
            
            summary = crew.generate_summary()
            assert summary == "No changes to summarize"
    
    def test_pipeline_write_outputs_none_wiki_suggestion(self):
        """Test write outputs with None wiki suggestions."""
        crew = PipelineCrew()
        
        ctx = {
            "readme_path": "/tmp/README.md",
            "wiki_file_paths": {"Test.md": "/tmp/wiki/Test.md"}
        }
        
        suggestions = {
            "README.md": None,
            "wiki": {"Test.md": None}
        }
        
        # Should not write any files
        with patch("subprocess.run") as mock_run:
            crew._write_outputs(suggestions, ctx)
            mock_run.assert_not_called()


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
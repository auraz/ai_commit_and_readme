"""Tests for base crew functionality."""

import os
from unittest.mock import MagicMock, patch

import pytest

from autodoc_ai.crews.base import BaseCrew


class TestBaseCrew:
    """Tests for BaseCrew class."""

    def test_init(self):
        """Test base crew initialization."""
        crew = BaseCrew()
        assert crew.model == os.getenv("AUTODOC_MODEL", "gpt-4o-mini")
        assert crew.agents == []

    def test_create_crew_default_verbose(self):
        """Test crew creation with default verbose setting."""
        crew = BaseCrew()

        # Mock agents
        mock_agent1 = MagicMock()
        mock_agent1.agent = MagicMock()
        mock_agent2 = MagicMock()
        mock_agent2.agent = MagicMock()
        crew.agents = [mock_agent1, mock_agent2]

        # Mock tasks
        mock_task1 = MagicMock()
        mock_task1.description = "Task 1 description"
        mock_task2 = MagicMock()
        mock_task2.description = "Task 2 description"
        tasks = [mock_task1, mock_task2]

        with patch("autodoc_ai.crews.base.Crew") as mock_crew_class:
            crew._create_crew(tasks)

            # Check crew was created with correct parameters
            mock_crew_class.assert_called_once()
            call_args = mock_crew_class.call_args[1]
            assert len(call_args["agents"]) == 2
            assert len(call_args["tasks"]) == 2

    def test_create_crew_debug_mode(self, monkeypatch):
        """Test crew creation in debug mode."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "DEBUG")

        crew = BaseCrew()
        mock_agent = MagicMock()
        mock_agent.agent = MagicMock()
        crew.agents = [mock_agent]

        mock_task = MagicMock()
        mock_task.description = "Test task"
        tasks = [mock_task]

        with patch("autodoc_ai.crews.base.Crew") as mock_crew_class:
            crew._create_crew(tasks)

            # In debug mode, verbose should be True
            call_args = mock_crew_class.call_args[1]
            assert call_args["verbose"] is True

    def test_create_crew_with_callbacks_disabled(self, monkeypatch):
        """Test crew creation with callbacks disabled."""
        monkeypatch.setenv("AUTODOC_DISABLE_CALLBACKS", "true")

        crew = BaseCrew()
        mock_agent = MagicMock()
        mock_agent.agent = MagicMock()
        crew.agents = [mock_agent]

        mock_task = MagicMock()
        tasks = [mock_task]

        with patch("autodoc_ai.crews.base.Crew") as mock_crew_class:
            crew._create_crew(tasks)

            # Callbacks should not be included
            call_args = mock_crew_class.call_args[1]
            assert "step_callback" not in call_args
            assert "task_callback" not in call_args

    def test_run_success(self):
        """Test successful run."""

        class TestCrew(BaseCrew):
            def _execute(self, *args, **kwargs):
                return {"result": "success"}

        crew = TestCrew()
        result = crew.run("test_arg", key="value")
        assert result == {"result": "success"}

    def test_run_error_handling(self):
        """Test error handling in run."""

        class TestCrew(BaseCrew):
            def _execute(self, *args, **kwargs):
                raise ValueError("Test error")

            def _handle_error(self, error):
                return {"error": str(error)}

        crew = TestCrew()
        result = crew.run()
        assert result == {"error": "Test error"}

    def test_run_error_debug_mode(self, monkeypatch, caplog):
        """Test error handling with debug logging."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "DEBUG")

        class TestCrew(BaseCrew):
            def _execute(self, *args, **kwargs):
                raise ValueError("Test error")

        crew = TestCrew()
        with caplog.at_level("DEBUG"):
            result = crew.run()

        assert result is None  # Default _handle_error returns None
        assert "Full traceback:" in caplog.text
        assert "ValueError: Test error" in caplog.text

    def test_execute_not_implemented(self):
        """Test that _execute must be implemented by subclasses."""
        crew = BaseCrew()
        with pytest.raises(NotImplementedError):
            crew._execute()

    def test_handle_error_default(self):
        """Test default error handling."""
        crew = BaseCrew()
        result = crew._handle_error(Exception("test"))
        assert result is None

    def test_load_file_success(self, tmp_path):
        """Test successful file loading."""
        test_file = tmp_path / "test.md"
        test_file.write_text("Test content", encoding="utf-8")

        crew = BaseCrew()
        content = crew.load_file(str(test_file))
        assert content == "Test content"

    def test_load_file_not_found(self):
        """Test file loading with non-existent file."""
        crew = BaseCrew()
        content = crew.load_file("/non/existent/file.md")
        assert content is None

    def test_load_file_error(self, tmp_path, monkeypatch):
        """Test file loading with read error."""
        test_file = tmp_path / "test.md"
        test_file.write_text("Test content")

        # Mock open to raise an error
        def mock_open(*args, **kwargs):
            raise PermissionError("Access denied")

        monkeypatch.setattr("builtins.open", mock_open)

        crew = BaseCrew()
        content = crew.load_file(str(test_file))
        assert content is None

    def test_callbacks_functionality(self):
        """Test callback functions work correctly."""
        crew = BaseCrew()
        mock_agent = MagicMock()
        mock_agent.agent = MagicMock()
        crew.agents = [mock_agent]

        mock_task = MagicMock()
        mock_task.description = "A very long task description that should be truncated"
        tasks = [mock_task]

        # Create crew and extract callbacks
        with patch("autodoc_ai.crews.base.Crew") as mock_crew_class:
            crew._create_crew(tasks)
            call_args = mock_crew_class.call_args[1]

            # Test step callback
            step_callback = call_args.get("step_callback")
            if step_callback:
                step_callback("Step output")  # Should not raise

            # Test task callback
            task_callback = call_args.get("task_callback")
            if task_callback:
                mock_output = MagicMock()
                mock_output.task = mock_task
                mock_output.raw = "Task output"
                task_callback(mock_output)  # Should not raise

            # Test before/after kickoff callbacks
            before_callbacks = call_args.get("before_kickoff_callbacks", [])
            after_callbacks = call_args.get("after_kickoff_callbacks", [])

            if before_callbacks:
                before_callbacks[0]({"data": "test"})  # Should not raise

            if after_callbacks:
                after_callbacks[0]("Final output")  # Should not raise


def test_create_crew_debug_logging(monkeypatch, caplog):
    """Test that debug logging works correctly in callbacks."""
    monkeypatch.setenv("AUTODOC_LOG_LEVEL", "DEBUG")

    class TestCrew(BaseCrew):
        def __init__(self):
            super().__init__()
            self.agents = [MagicMock()]

    crew = TestCrew()
    tasks = [MagicMock()]

    # Mock the Crew class
    with patch("autodoc_ai.crews.base.Crew") as mock_crew_class:
        mock_crew_instance = MagicMock()
        mock_crew_class.return_value = mock_crew_instance

        # Create crew with task callback enabled
        monkeypatch.delenv("AUTODOC_DISABLE_CALLBACKS", raising=False)

        crew._create_crew(tasks, verbose=True)

        # Get the task callback
        task_callback = mock_crew_class.call_args[1]["task_callback"]

        # Create mock output with raw attribute
        mock_output = MagicMock()
        mock_output.raw = "This is the full raw output for testing"

        # Call task callback with mock output
        with caplog.at_level("DEBUG"):
            task_callback(mock_output)

            # Check debug logs were created
            assert "Full task output: This is the full raw output for testing" in caplog.text
            assert "Output object:" in caplog.text


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])

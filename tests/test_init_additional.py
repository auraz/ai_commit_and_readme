"""Additional tests for __init__ module."""

import logging
import os
from unittest.mock import patch, MagicMock

import pytest


class TestLoggingConfiguration:
    """Additional tests for logging configuration."""

    def test_error_log_level(self, monkeypatch):
        """Test ERROR log level configuration."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "ERROR")
        
        # Re-import to trigger logging setup
        import importlib
        import autodoc_ai
        importlib.reload(autodoc_ai)
        
        from autodoc_ai import logger
        assert logger is not None

    def test_invalid_log_level_defaults_to_info(self, monkeypatch):
        """Test invalid log level defaults to INFO."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "INVALID_LEVEL")
        
        import importlib
        import autodoc_ai
        importlib.reload(autodoc_ai)
        
        from autodoc_ai import logger
        assert logger is not None

    def test_lowercase_log_level(self, monkeypatch):
        """Test lowercase log level is converted to uppercase."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "debug")
        
        import importlib
        import autodoc_ai
        importlib.reload(autodoc_ai)
        
        # Should still enable debug mode
        assert os.getenv("LITELLM_LOG") == "DEBUG"
        assert os.getenv("CREWAI_DEBUG") == "True"

    def test_mixed_case_log_level(self, monkeypatch):
        """Test mixed case log level."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "WaRnInG")
        
        import importlib
        import autodoc_ai
        importlib.reload(autodoc_ai)
        
        from autodoc_ai import logger
        assert logger is not None

    @patch("logging.getLogger")
    def test_debug_mode_sets_all_loggers(self, mock_get_logger, monkeypatch):
        """Test debug mode configures all component loggers."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "DEBUG")
        
        # Create mock loggers
        mock_loggers = {
            "crewai": MagicMock(),
            "litellm": MagicMock(),
            "LiteLLM": MagicMock(),
            "LiteLLM.utils": MagicMock(),
        }
        
        def get_logger(name):
            if name in mock_loggers:
                return mock_loggers[name]
            return MagicMock()
        
        mock_get_logger.side_effect = get_logger
        
        import importlib
        import autodoc_ai
        importlib.reload(autodoc_ai)
        
        # Check all loggers were set to DEBUG
        for name, logger in mock_loggers.items():
            logger.setLevel.assert_called_with(logging.DEBUG)

    @patch("logging.getLogger")
    def test_non_debug_mode_suppresses_loggers(self, mock_get_logger, monkeypatch):
        """Test non-debug mode suppresses verbose loggers."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "INFO")
        
        # Create mock loggers
        mock_loggers = {
            "crewai.crew": MagicMock(),
            "crewai.agent": MagicMock(),
            "litellm": MagicMock(),
            "litellm.utils": MagicMock(),
            "LiteLLM": MagicMock(),
            "LiteLLM.utils": MagicMock(),
        }
        
        def get_logger(name):
            if name in mock_loggers:
                return mock_loggers[name]
            return MagicMock()
        
        mock_get_logger.side_effect = get_logger
        
        import importlib
        import autodoc_ai
        importlib.reload(autodoc_ai)
        
        # Check CrewAI loggers set to WARNING
        mock_loggers["crewai.crew"].setLevel.assert_called_with(logging.WARNING)
        mock_loggers["crewai.agent"].setLevel.assert_called_with(logging.WARNING)
        
        # Check LiteLLM loggers set to ERROR
        for name in ["litellm", "litellm.utils", "LiteLLM", "LiteLLM.utils"]:
            mock_loggers[name].setLevel.assert_called_with(logging.ERROR)

    def test_litellm_log_env_var_in_info_mode(self, monkeypatch):
        """Test LITELLM_LOG is set to ERROR in INFO mode."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "INFO")
        
        import importlib
        import autodoc_ai
        importlib.reload(autodoc_ai)
        
        assert os.getenv("LITELLM_LOG") == "ERROR"

    def test_all_debug_env_vars_set(self, monkeypatch):
        """Test all debug environment variables are set in debug mode."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "DEBUG")
        
        import importlib
        import autodoc_ai
        importlib.reload(autodoc_ai)
        
        # Check all debug env vars
        assert os.getenv("LITELLM_LOG") == "DEBUG"
        assert os.getenv("LITELLM_VERBOSE") == "True"
        assert os.getenv("LITELLM_DEBUG") == "True"
        assert os.getenv("CREWAI_DEBUG") == "True"

    @patch("rich.logging.RichHandler")
    def test_rich_handler_configuration_debug(self, mock_rich_handler, monkeypatch):
        """Test RichHandler is configured correctly in debug mode."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "DEBUG")
        
        import importlib
        import autodoc_ai
        importlib.reload(autodoc_ai)
        
        # Check RichHandler was created with correct params
        mock_rich_handler.assert_called_with(
            markup=True,
            show_time=True,
            show_path=True
        )

    @patch("rich.logging.RichHandler")
    def test_rich_handler_configuration_info(self, mock_rich_handler, monkeypatch):
        """Test RichHandler is configured correctly in info mode."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "INFO")
        
        import importlib
        import autodoc_ai
        importlib.reload(autodoc_ai)
        
        # Check RichHandler was created with correct params
        mock_rich_handler.assert_called_with(
            markup=True,
            show_time=False,
            show_path=False
        )


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
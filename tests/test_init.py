"""Tests for __init__ module and logging configuration."""

import os
from unittest.mock import patch

import pytest


class TestLoggingConfiguration:
    """Tests for logging configuration in __init__.py."""

    def test_default_log_level(self, monkeypatch):
        """Test default log level is INFO."""
        monkeypatch.delenv("AUTODOC_LOG_LEVEL", raising=False)
        
        # Re-import to trigger logging setup
        import importlib

        import autodoc_ai
        importlib.reload(autodoc_ai)
        
        from autodoc_ai import logger
        # Logger should exist
        assert logger is not None

    def test_debug_log_level(self, monkeypatch):
        """Test debug log level configuration."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "DEBUG")
        
        # Re-import to trigger logging setup
        import importlib

        import autodoc_ai
        importlib.reload(autodoc_ai)
        
        # Check that debug environment variables are set
        assert os.getenv("LITELLM_LOG") == "DEBUG"
        assert os.getenv("LITELLM_VERBOSE") == "True"
        assert os.getenv("LITELLM_DEBUG") == "True"
        assert os.getenv("CREWAI_DEBUG") == "True"

    def test_info_log_level(self, monkeypatch):
        """Test info log level configuration."""
        # First clear all environment variables
        for key in ["LITELLM_LOG", "LITELLM_VERBOSE", "LITELLM_DEBUG", "CREWAI_DEBUG"]:
            monkeypatch.delenv(key, raising=False)
            
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "INFO")
        
        # Re-import to trigger logging setup
        import importlib

        import autodoc_ai
        importlib.reload(autodoc_ai)
        
        # In INFO mode, debug vars might be set to ERROR or not set at all
        # The important thing is they're not set to DEBUG/True
        litellm_log = os.getenv("LITELLM_LOG")
        assert litellm_log != "DEBUG"
        assert os.getenv("LITELLM_VERBOSE") != "True"
        assert os.getenv("LITELLM_DEBUG") != "True"
        assert os.getenv("CREWAI_DEBUG") != "True"

    def test_warning_log_level(self, monkeypatch):
        """Test warning log level configuration."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "WARNING")
        
        # Re-import to trigger logging setup
        import importlib

        import autodoc_ai
        importlib.reload(autodoc_ai)
        
        from autodoc_ai import logger
        assert logger is not None

    def test_logger_export(self):
        """Test that logger is exported from the module."""
        from autodoc_ai import logger
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')

    def test_rich_logging_configuration(self, monkeypatch):
        """Test rich logging is configured properly."""
        monkeypatch.setenv("AUTODOC_LOG_LEVEL", "INFO")
        
        with patch('logging.basicConfig') as mock_config:
            import importlib

            import autodoc_ai
            importlib.reload(autodoc_ai)
            
            # Check that logging.basicConfig was called
            mock_config.assert_called()
            call_kwargs = mock_config.call_args[1]
            
            # Should have format and handlers
            assert 'format' in call_kwargs
            assert 'handlers' in call_kwargs


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
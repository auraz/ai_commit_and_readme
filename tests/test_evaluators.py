"""Tests for document evaluators."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from autodoc_ai.crews.evaluation import EvaluationCrew


def test_evaluate_readme():
    """Test README evaluation."""
    crew = EvaluationCrew()

    # Mock the evaluate_one method on the instance
    with patch.object(crew, "evaluate_one", return_value=(85.0, "Good documentation.")), tempfile.NamedTemporaryFile(mode="w+", suffix=".md") as tmp:
        tmp.write("# Test README\n\nTest content.")
        tmp.flush()

        score, report = crew.run(tmp.name, "readme")

        assert score == 85
        assert "README Evaluation" in report
        assert "Score: 85/100" in report


def test_evaluate_missing_file():
    """Test evaluation of non-existent file."""
    crew = EvaluationCrew()
    score, report = crew.run("/nonexistent/file.md", "readme")
    assert score == 0
    assert "Document not found or empty" in report


def test_evaluate_with_extra_prompt():
    """Test evaluation with extra prompt criteria."""
    crew = EvaluationCrew()

    # Mock the evaluate_one method on the instance
    with (
        patch.object(crew, "evaluate_one", return_value=(90.0, "Excellent documentation with security focus.")),
        tempfile.NamedTemporaryFile(mode="w+", suffix=".md") as tmp,
    ):
        tmp.write("# Security Guide\n\nThis document covers security best practices.")
        tmp.flush()

        score, report = crew.run(tmp.name, "security", "Focus on authentication and authorization practices")

        assert score == 90
        assert "SECURITY Evaluation" in report
        assert "Score: 90/100" in report


def test_detect_doc_type():
    """Test document type detection."""
    crew = EvaluationCrew()

    # Test README detection
    assert crew._detect_doc_type("", "README.md") == "readme"

    # Test filename-based detection
    assert crew._detect_doc_type("", "installation.md") == "installation"
    assert crew._detect_doc_type("", "api_reference.md") == "api"

    # Test content-based detection
    content = "This document describes the system architecture and design patterns used."
    assert crew._detect_doc_type(content, "overview.md") == "architecture"


def test_evaluate_all_in_directory():
    """Test evaluating multiple documents."""
    crew = EvaluationCrew()

    # Set up mock to return different scores based on content
    def mock_evaluate(content):
        if "README" in content:
            return (85.0, "Good.")
        elif "Usage" in content:
            return (90.0, "Excellent.")
        elif "FAQ" in content:
            return (75.0, "Needs work.")
        return (0.0, "Unknown")

    with patch.object(crew, "evaluate_one", side_effect=mock_evaluate), tempfile.TemporaryDirectory() as tmpdir:
        files = ["README.md", "Usage.md", "FAQ.md"]
        results = {}

        for filename in files:
            filepath = Path(tmpdir) / filename
            filepath.write_text(f"# {filename}\n\nContent.")

            score, report = crew.run(str(filepath))
            results[filename] = (score, report)

        assert results["README.md"][0] == 85
        assert results["Usage.md"][0] == 90
        assert results["FAQ.md"][0] == 75


@patch("autodoc_ai.crews.evaluation.DocumentCrew.evaluate_one")
def test_evaluation_error_handling(mock_evaluate_one):
    """Test error handling during evaluation."""
    mock_evaluate_one.side_effect = Exception("API error")

    crew = EvaluationCrew()

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".md") as tmp:
        tmp.write("# Test\n\nContent")
        tmp.flush()

        score, report = crew.run(tmp.name)

        assert score == 0
        assert "Error evaluating document" in report
        assert "API error" in report


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])

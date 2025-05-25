"""Tests for document evaluators."""

import tempfile
from unittest.mock import MagicMock, patch

import pytest

from ai_commit_and_readme.doc_eval import evaluate_all, evaluate_doc


@patch("ai_commit_and_readme.doc_eval.DocumentCrew")
def test_evaluate_readme(mock_crew_class):
    """Test README evaluation."""
    mock_crew = MagicMock()
    mock_crew_class.return_value = mock_crew
    mock_crew.evaluate_one.return_value = (85.0, "Good documentation.")

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".md") as tmp:
        tmp.write("# Test README\n\nTest content.")
        tmp.flush()

        score, report = evaluate_doc(tmp.name, "readme")

        assert score == 85
        assert "README Evaluation" in report
        assert "Score: 85/100" in report


@patch("ai_commit_and_readme.doc_eval.DocumentCrew")
def test_evaluate_missing_file(mock_crew_class):
    """Test evaluation of non-existent file."""
    score, report = evaluate_doc("/nonexistent/file.md", "readme")
    assert score == 0
    assert "Document not found or empty" in report


@patch("ai_commit_and_readme.doc_eval.DocumentCrew")
def test_evaluate_all(mock_crew_class):
    """Test evaluating directory of documents."""
    mock_crew = MagicMock()
    mock_crew_class.return_value = mock_crew
    
    # Set up mock to return different scores based on filename
    def mock_evaluate(doc_path, doc_type=None):
        if "README" in doc_path:
            return (85.0, "Good.")
        elif "Usage" in doc_path:
            return (90.0, "Excellent.")
        elif "FAQ" in doc_path:
            return (75.0, "Needs work.")
        return (0.0, "Unknown")
    
    mock_crew.evaluate_one.side_effect = mock_evaluate

    with tempfile.TemporaryDirectory() as tmpdir:
        files = ["README.md", "Usage.md", "FAQ.md"]
        for filename in files:
            filepath = f"{tmpdir}/{filename}"
            with open(filepath, "w") as f:
                f.write(f"# {filename}\n\nContent.")

        results = evaluate_all(tmpdir)

        assert len(results) == 3
        assert results["README.md"][0] == 85
        assert results["Usage.md"][0] == 90
        assert results["FAQ.md"][0] == 75


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])

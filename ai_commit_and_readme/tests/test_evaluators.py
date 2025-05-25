#!/usr/bin/env python3
"""Tests for evaluators using autodoceval-crewai."""

import tempfile
from unittest import TestCase
from unittest.mock import patch, MagicMock

import pytest

from ai_commit_and_readme.evals.readme_eval import evaluate as evaluate_readme
from ai_commit_and_readme.evals.wiki_eval import WikiEvaluator, evaluate_directory


class TestReadmeEvaluator(TestCase):
    """Test suite for README evaluator using autodoceval-crewai."""

    def setUp(self):
        """Set up test fixtures."""
        self.good_readme = """# Project Name

A brief description of the project.

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

```bash
git clone https://github.com/user/project.git
cd project
pip install -r requirements.txt
```

## Usage

```python
import project

result = project.do_something()
print(result)
```

## Documentation

For more information, see our [wiki](https://github.com/user/project/wiki).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"""

    @patch('ai_commit_and_readme.evals.readme_eval.DocumentCrew')
    def test_evaluate_readme(self, mock_crew_class):
        """Test README evaluation with mock DocumentCrew."""
        # Configure mock
        mock_crew = MagicMock()
        mock_crew_class.return_value = mock_crew
        mock_crew.evaluate_one.return_value = (85.0, "Good documentation with clear structure.")
        
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".md") as tmp:
            tmp.write(self.good_readme)
            tmp.flush()
            
            score, report = evaluate_readme(tmp.name)
            
            # Check score
            self.assertEqual(score, 85)
            
            # Verify report contains expected sections
            self.assertIn("README Evaluation (AI-Powered by CrewAI)", report)
            self.assertIn("Score: 85/100", report)
            self.assertIn("Good documentation with clear structure.", report)
            
            # Verify DocumentCrew was called correctly
            mock_crew_class.assert_called_once_with(target_score=85, max_iterations=1)
            mock_crew.evaluate_one.assert_called_once()

    def test_evaluate_missing_file(self):
        """Test evaluation of non-existent file."""
        score, report = evaluate_readme("/nonexistent/file.md")
        self.assertEqual(score, 0)
        self.assertIn("Error: Unable to read README file", report)


class TestWikiEvaluator(TestCase):
    """Test suite for Wiki evaluator using autodoceval-crewai."""

    def setUp(self):
        """Set up test fixtures."""
        self.wiki_content = """# Installation Guide

This guide covers installation of our software.

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Installation Steps

1. Clone the repository
2. Install dependencies
3. Configure environment

## Troubleshooting

If you encounter issues, check the FAQ.
"""

    @patch('ai_commit_and_readme.evals.wiki_eval.DocumentCrew')
    def test_evaluate_wiki(self, mock_crew_class):
        """Test wiki page evaluation with mock DocumentCrew."""
        # Configure mock
        mock_crew = MagicMock()
        mock_crew_class.return_value = mock_crew
        mock_crew.evaluate_one.return_value = (90.0, "Excellent installation guide.")
        
        evaluator = WikiEvaluator()
        
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".md") as tmp:
            tmp.write(self.wiki_content)
            tmp.flush()
            
            score, report = evaluator.evaluate(tmp.name)
            
            # Check score
            self.assertEqual(score, 90)
            
            # Verify report contains expected sections
            self.assertIn("Wiki Page Evaluation (AI-Powered by CrewAI)", report)
            self.assertIn("Score: 90/100", report)
            self.assertIn("Excellent installation guide.", report)

    @patch('ai_commit_and_readme.evals.wiki_eval.DocumentCrew')
    def test_evaluate_directory(self, mock_crew_class):
        """Test evaluating directory of wiki pages."""
        # Configure mock
        mock_crew = MagicMock()
        mock_crew_class.return_value = mock_crew
        mock_crew.evaluate_one.side_effect = [
            (85.0, "Good guide."),
            (90.0, "Excellent docs."),
            (75.0, "Needs improvement.")
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            files = ["Installation.md", "Usage.md", "FAQ.md"]
            for filename in files:
                filepath = f"{tmpdir}/{filename}"
                with open(filepath, "w") as f:
                    f.write(f"# {filename}\n\nTest content.")
            
            results = evaluate_directory(tmpdir)
            
            # Check results
            self.assertEqual(len(results), 3)
            self.assertEqual(results["Installation.md"][0], 85)
            self.assertEqual(results["Usage.md"][0], 90)
            self.assertEqual(results["FAQ.md"][0], 75)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
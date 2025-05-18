#!/usr/bin/env python3
"""
Tests for AI-powered README evaluator.
"""

import json
import tempfile
from unittest import TestCase
from unittest.mock import patch, MagicMock

import pytest

from ai_commit_and_readme.evals.readme_eval import (
    evaluate as evaluate_readme,
    CATEGORIES
)
from ai_commit_and_readme.tools import (
    format_evaluation_results,
    load_file,
    evaluate_with_ai,
    get_ai_evaluation
)


class TestReadmeEvaluator(TestCase):
    """Test suite for AI-powered README evaluator."""

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
        
        self.mock_evaluation = {
            "scores": {
                "title_and_description": [10, "Clear title and description"],
                "structure_and_organization": [14, "Well organized"],
                "installation_guide": [12, "Installation steps clear"],
                "usage_examples": [12, "Good examples"],
                "feature_explanation": [9, "Features well explained"],
                "documentation_links": [8, "Some links present"],
                "badges_and_shields": [3, "Few badges"],
                "license_information": [5, "License included"],
                "contributing_guidelines": [5, "Contributing guidelines clear"],
                "conciseness_and_clarity": [9, "Overall clear and concise"]
            },
            "total_score": 87,
            "max_score": 100,
            "grade": "B",
            "summary": "Good README with clear structure",
            "top_recommendations": [
                "Add more badges",
                "Improve documentation links",
                "Add more usage examples"
            ]
        }

    def test_format_results(self):
        """Test formatting of evaluation results."""
        report = format_evaluation_results(
            self.mock_evaluation, 
            "README Evaluation (AI-Powered)", 
            CATEGORIES
        )
        
        # Check the report contains expected sections
        self.assertIn("README Evaluation (AI-Powered)", report)
        self.assertIn("Overall Score: 87/100", report)
        self.assertIn("Grade: B", report)
        self.assertIn("Summary: Good README", report)
        self.assertIn("Category Breakdown:", report)
        self.assertIn("Top Improvement Recommendations:", report)
        self.assertIn("Add more badges", report)

    @patch('ai_commit_and_readme.tools.OpenAI')
    def test_evaluate_file(self, mock_openai_class):
        """Test readme file evaluation with mock API."""
        # Configure mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = json.dumps(self.mock_evaluation)
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".md") as tmp:
            tmp.write(self.good_readme)
            tmp.flush()
            
            score, report = evaluate_readme(tmp.name)
            
            # Check score matches mock
            self.assertEqual(score, 87)
            
            # Verify report contains expected sections
            self.assertIn("README Evaluation (AI-Powered)", report)
            self.assertIn("Overall Score: 87/100", report)
            self.assertIn("Grade: B", report)



if __name__ == "__main__":
    pytest.main(["-xvs", __file__])

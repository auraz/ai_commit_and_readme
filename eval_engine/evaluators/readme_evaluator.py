"""README Evaluator for Documentation Quality.

This module provides a specialized evaluator for README.md files,
assessing them against best practices and common standards.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List

from .base import BaseEvaluator

logger = logging.getLogger(__name__)

# Default categories and weights for README evaluation
README_CATEGORIES = {
    "title_and_description": 10,
    "structure_and_organization": 15,
    "installation_guide": 15,
    "usage_examples": 15,
    "feature_explanation": 10,
    "documentation_links": 10,
    "badges_and_shields": 5,
    "license_information": 5,
    "contributing_guidelines": 5,
    "conciseness_and_clarity": 10
}


class ReadmeEvaluator(BaseEvaluator):
    """README file evaluator.
    
    Evaluates README files against common best practices and standards,
    providing quantitative scoring and qualitative feedback.
    """
    
    def __init__(
        self,
        prompts_dir: Optional[Path] = None,
        model: str = "gpt-4",
        temperature: float = 0.2,
        api_key: Optional[str] = None,
        track_history: bool = True,
        evaluation_id: Optional[str] = None,
        categories: Optional[Dict[str, int]] = None
    ):
        """Initialize the README evaluator.
        
        Args:
            prompts_dir: Directory containing evaluation prompt templates
            model: OpenAI model to use for evaluation
            temperature: Temperature setting for the model
            api_key: OpenAI API key (if None, will use environment variable)
            track_history: Whether to track evaluation history
            evaluation_id: Optional unique ID for this evaluation
            categories: Custom category weights (if None, uses defaults)
        """
        super().__init__(
            prompts_dir=prompts_dir,
            model=model,
            temperature=temperature,
            api_key=api_key,
            track_history=track_history,
            evaluation_id=evaluation_id
        )
        self.categories = categories or README_CATEGORIES
        
    def evaluate(self, content: str, **kwargs) -> Tuple[int, Dict[str, Any]]:
        """Evaluate README content.
        
        Args:
            content: The README content to evaluate
            **kwargs: Additional arguments:
                - filename: Optional filename for context
                - repository_info: Optional dict with repo information
                
        Returns:
            Tuple of (score, evaluation_results)
        """
        # Get optional parameters
        filename = kwargs.get("filename", "README.md")
        repository_info = kwargs.get("repository_info", {})
        
        # Load README evaluation prompt
        prompt_template = self.load_prompt("readme_eval.md")
        if not prompt_template:
            logger.error("Failed to load README evaluation prompt")
            return 0, {"error": "Failed to load evaluation prompt"}
        
        # Replace content placeholder in prompt
        prompt = prompt_template.replace("{readme_content}", content)
        
        # Add repository context if available
        if repository_info and "{repository_info}" in prompt:
            repo_context = f"""
            Repository Name: {repository_info.get('name', 'Unknown')}
            Main Language: {repository_info.get('language', 'Unknown')}
            Description: {repository_info.get('description', 'None provided')}
            """
            prompt = prompt.replace("{repository_info}", repo_context)
        
        # Call the model for evaluation
        evaluation = self.call_model(prompt)
        if not evaluation:
            logger.error("Evaluation failed - no response from model")
            return 0, {"error": "Evaluation failed"}
        
        # Extract the overall score
        total_score = self._calculate_total_score(evaluation)
        evaluation["total_score"] = total_score
        
        # Ensure we have a max score
        if "max_score" not in evaluation:
            evaluation["max_score"] = sum(self.categories.values())
        
        # Add grade if not present
        if "grade" not in evaluation:
            evaluation["grade"] = self._calculate_grade(total_score, evaluation["max_score"])
        
        # Generate improvement recommendations if not present
        if "top_recommendations" not in evaluation or not evaluation["top_recommendations"]:
            evaluation["top_recommendations"] = self._generate_recommendations(evaluation)
        
        # Track this evaluation in history
        metadata = {
            "filename": filename,
            "type": "readme",
            "repository_info": repository_info
        }
        self.track_evaluation(content, total_score, evaluation, metadata)
        
        return total_score, evaluation
    
    def _calculate_total_score(self, evaluation: Dict[str, Any]) -> int:
        """Calculate the total score from category scores.
        
        Args:
            evaluation: The evaluation results
            
        Returns:
            Total score as int
        """
        if "total_score" in evaluation and isinstance(evaluation["total_score"], (int, float)):
            return int(evaluation["total_score"])
        
        total = 0
        if "scores" in evaluation:
            scores = evaluation["scores"]
            for category, weight in self.categories.items():
                if category in scores:
                    category_data = scores[category]
                    if isinstance(category_data, list) and len(category_data) > 0:
                        # Format: [score, reason]
                        category_score = category_data[0]
                    elif isinstance(category_data, dict) and "score" in category_data:
                        # Format: {"score": value, "reason": "text"}
                        category_score = category_data["score"]
                    else:
                        # Unknown format, skip
                        continue
                    
                    if isinstance(category_score, (int, float)):
                        total += category_score
        
        return min(int(total), 100)  # Ensure maximum score is 100
    
    def _calculate_grade(self, score: int, max_score: int) -> str:
        """Calculate a letter grade based on the score.
        
        Args:
            score: The total score
            max_score: The maximum possible score
            
        Returns:
            Letter grade as string
        """
        percentage = (score / max_score) * 100
        
        if percentage >= 90:
            return "Excellent"
        elif percentage >= 80:
            return "Good"
        elif percentage >= 70:
            return "Satisfactory"
        elif percentage >= 60:
            return "Needs Improvement"
        else:
            return "Poor"
    
    def _generate_recommendations(self, evaluation: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on scores.
        
        Args:
            evaluation: The evaluation results
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if "scores" in evaluation:
            scores = evaluation["scores"]
            # Find the lowest scoring categories
            sorted_categories = []
            
            for category, data in scores.items():
                if isinstance(data, list) and len(data) > 0:
                    score = data[0]
                    reason = data[1] if len(data) > 1 else ""
                elif isinstance(data, dict) and "score" in data:
                    score = data["score"]
                    reason = data.get("reason", "")
                else:
                    # Skip unknown formats
                    continue
                
                max_score = self.categories.get(category, 10)
                percentage = (score / max_score) * 100
                sorted_categories.append((category, score, max_score, percentage, reason))
            
            # Sort by percentage score
            sorted_categories.sort(key=lambda x: x[3])
            
            # Generate recommendations for the lowest 3 categories
            for category, score, max_score, percentage, reason in sorted_categories[:3]:
                if percentage < 70:  # Only recommend if score is below 70%
                    category_name = category.replace("_", " ").title()
                    
                    # Extract action items from the reason
                    if reason:
                        recommendations.append(f"Improve {category_name}: {reason}")
                    else:
                        recommendations.append(f"Improve {category_name} - currently at {score}/{max_score}")
        
        # Add generic recommendations if we couldn't generate any specific ones
        if not recommendations:
            recommendations = [
                "Add a clear title and concise description of the project",
                "Include installation instructions with prerequisites",
                "Add usage examples with code snippets"
            ]
        
        return recommendations
    
    def create_report(self, content: str, filename: str = "README.md", **kwargs) -> str:
        """Create a formatted evaluation report for a README file.
        
        Args:
            content: The README content to evaluate
            filename: The README filename
            **kwargs: Additional arguments passed to evaluate()
            
        Returns:
            Formatted report as string
        """
        score, evaluation = self.evaluate(content, filename=filename, **kwargs)
        
        # Create title
        title = f"README Evaluation: {filename}"
        
        # Generate the report
        return self.format_evaluation_report(evaluation, title)
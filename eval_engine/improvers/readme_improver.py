"""README Improver for Documentation Enhancement.

This module provides a specialized improver for README.md files,
enhancing them based on evaluation results to align with best practices.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List

from .base import BaseImprover

logger = logging.getLogger(__name__)


class ReadmeImprover(BaseImprover):
    """README file improver.
    
    Improves README files based on evaluation results, focusing on
    areas that scored lowest in the evaluation.
    """
    
    def __init__(
        self,
        prompts_dir: Optional[Path] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        track_history: bool = True,
        improvement_id: Optional[str] = None
    ):
        """Initialize the README improver.
        
        Args:
            prompts_dir: Directory containing improvement prompt templates
            model: OpenAI model to use for improvements
            temperature: Temperature setting for the model
            api_key: OpenAI API key (if None, will use environment variable)
            track_history: Whether to track improvement history
            improvement_id: Optional unique ID for this improvement session
        """
        super().__init__(
            prompts_dir=prompts_dir,
            model=model,
            temperature=temperature,
            api_key=api_key,
            track_history=track_history,
            improvement_id=improvement_id
        )
        
        # Create readme improver prompt if it doesn't exist
        self._ensure_readme_improver_prompt()
        
    def _ensure_readme_improver_prompt(self) -> None:
        """Ensure the README improver prompt exists."""
        prompt_file = "readme_improver.md"
        
        # Check if prompt exists, create it if not
        if not self.load_prompt(prompt_file):
            default_prompt = """You are an expert technical writer specializing in README files for software projects.
Your task is to improve the provided README based on the evaluation feedback.

CURRENT README:
```
{readme_content}
```

EVALUATION RESULTS:
```
{evaluation_results}
```

AREAS TO FOCUS ON:
{focus_areas}

INSTRUCTIONS:
1. Keep the project's intended audience and purpose in mind.
2. Maintain the existing structure unless reorganization would significantly improve clarity.
3. Preserve any existing links, code snippets, and technical information.
4. Address all the issues mentioned in the evaluation, especially in the focus areas.
5. Keep a similar tone but improve clarity and conciseness.
6. Do not invent features or details not present in the original.
7. Ensure proper markdown formatting.

PROVIDE AN IMPROVED VERSION OF THE ENTIRE README FILE:
"""
            
            self.save_prompt(prompt_file, default_prompt)
    
    def improve(self, content: str, evaluation_results: Dict[str, Any], **kwargs) -> Tuple[str, Dict[str, Any]]:
        """Improve README content based on evaluation results.
        
        Args:
            content: The README content to improve
            evaluation_results: Results from an evaluator
            **kwargs: Additional arguments:
                - filename: Optional filename for context
                - repository_info: Optional dict with repo information
                - focus_categories: Optional list of categories to focus on
                
        Returns:
            Tuple of (improved_content, improvement_details)
        """
        # Get optional parameters
        filename = kwargs.get("filename", "README.md")
        repository_info = kwargs.get("repository_info", {})
        focus_categories = kwargs.get("focus_categories", None)
        
        # Load README improver prompt
        prompt_template = self.load_prompt("readme_improver.md")
        if not prompt_template:
            logger.error("Failed to load README improver prompt")
            return content, {"error": "Failed to load improver prompt"}
        
        # Determine focus areas
        focus_areas = self._determine_focus_areas(evaluation_results, focus_categories)
        
        # Format evaluation results as text
        eval_text = self._format_evaluation_for_prompt(evaluation_results)
        
        # Replace placeholders in prompt
        prompt = prompt_template.replace("{readme_content}", content)
        prompt = prompt.replace("{evaluation_results}", eval_text)
        prompt = prompt.replace("{focus_areas}", focus_areas)
        
        # Add repository context if available
        if repository_info and "{repository_info}" in prompt:
            repo_context = f"""
            Repository Name: {repository_info.get('name', 'Unknown')}
            Main Language: {repository_info.get('language', 'Unknown')}
            Description: {repository_info.get('description', 'None provided')}
            """
            prompt = prompt.replace("{repository_info}", repo_context)
        
        # Call the model for improvement
        improved_content = self.call_model(prompt, response_format="text")
        if not improved_content:
            logger.error("Improvement failed - no response from model")
            return content, {"error": "Improvement failed"}
        
        # Clean up the improved content
        improved_content = self._clean_improved_content(improved_content)
        
        # Track this improvement in history
        metadata = {
            "filename": filename,
            "type": "readme",
            "repository_info": repository_info,
            "focus_areas": focus_areas
        }
        self.track_improvement(content, improved_content, evaluation_results, None, metadata)
        
        # Create improvement details
        details = {
            "original_content": content,
            "improved_content": improved_content,
            "focus_areas": focus_areas.split("\n"),
            "diff": self.calculate_diff(content, improved_content)
        }
        
        return improved_content, details
    
    def _determine_focus_areas(self, evaluation_results: Dict[str, Any], focus_categories: Optional[List[str]] = None) -> str:
        """Determine focus areas for improvement based on evaluation results.
        
        Args:
            evaluation_results: Results from an evaluator
            focus_categories: Optional list of categories to focus on
            
        Returns:
            Formatted string of focus areas
        """
        focus_areas = []
        
        # Use provided focus categories if available
        if focus_categories:
            for category in focus_categories:
                focus_areas.append(f"- Improve {category.replace('_', ' ').title()}")
            return "\n".join(focus_areas)
        
        # Use recommendations from evaluation
        recommendations = evaluation_results.get("top_recommendations", [])
        if recommendations:
            for rec in recommendations:
                focus_areas.append(f"- {rec}")
            return "\n".join(focus_areas)
        
        # Find lowest scoring categories if no recommendations
        if "scores" in evaluation_results:
            scores = evaluation_results["scores"]
            category_scores = []
            
            for category, data in scores.items():
                if isinstance(data, list) and len(data) > 0:
                    score = data[0]
                    max_score = 10  # Default max
                    
                    # Format category name for display
                    category_display = category.replace("_", " ").title()
                    category_scores.append((category_display, score, max_score))
            
            # Sort by score and take lowest 3
            category_scores.sort(key=lambda x: x[1])
            for category, score, max_score in category_scores[:3]:
                percent = (score / max_score) * 100
                if percent < 80:  # Only focus on categories scoring below 80%
                    focus_areas.append(f"- Improve {category}: Currently scores {score}/{max_score}")
        
        # Default focus areas if nothing else is available
        if not focus_areas:
            focus_areas = [
                "- Improve the clarity and structure of the content",
                "- Enhance the installation and usage sections",
                "- Add more examples and context where appropriate"
            ]
        
        return "\n".join(focus_areas)
    
    def _format_evaluation_for_prompt(self, evaluation_results: Dict[str, Any]) -> str:
        """Format evaluation results for inclusion in the improvement prompt.
        
        Args:
            evaluation_results: Results from an evaluator
            
        Returns:
            Formatted evaluation results as string
        """
        eval_parts = []
        
        # Total score
        total_score = evaluation_results.get("total_score", 0)
        max_score = evaluation_results.get("max_score", 100)
        grade = evaluation_results.get("grade", "N/A")
        
        eval_parts.append(f"Overall Score: {total_score}/{max_score} - Grade: {grade}")
        eval_parts.append("")
        
        # Summary
        summary = evaluation_results.get("summary", "")
        if summary:
            eval_parts.append(f"Summary: {summary}")
            eval_parts.append("")
        
        # Category scores
        if "scores" in evaluation_results:
            eval_parts.append("Category Scores:")
            
            scores = evaluation_results["scores"]
            for category, data in scores.items():
                if isinstance(data, list) and len(data) >= 2:
                    score, reason = data[0], data[1]
                elif isinstance(data, dict) and "score" in data:
                    score, reason = data.get("score", 0), data.get("reason", "No reason provided")
                else:
                    # Skip unknown formats
                    continue
                
                # Format category name for display
                category_display = category.replace("_", " ").title()
                eval_parts.append(f"- {category_display}: {score} - {reason}")
            
            eval_parts.append("")
        
        # Recommendations
        recommendations = evaluation_results.get("top_recommendations", [])
        if recommendations:
            eval_parts.append("Top Recommendations:")
            for rec in recommendations:
                eval_parts.append(f"- {rec}")
        
        return "\n".join(eval_parts)
    
    def _clean_improved_content(self, content: str) -> str:
        """Clean up the improved content from the model.
        
        Args:
            content: Raw improved content from the model
            
        Returns:
            Cleaned content
        """
        # Remove any markdown code block markers that might be in the model's response
        content = content.replace("```markdown", "").replace("```md", "").replace("```", "")
        
        # Remove any header comments the model might have added
        lines = content.splitlines()
        if lines and (lines[0].startswith("# Improved README") or lines[0].startswith("# Updated README")):
            lines = lines[1:]
            
        # Ensure the content starts with a heading
        found_heading = False
        for i, line in enumerate(lines):
            if line.strip().startswith("#"):
                found_heading = True
                break
            if line.strip() and not line.strip().startswith("<!--"):
                # Insert a heading if the first non-comment line isn't a heading
                lines.insert(i, "# Project Name")
                break
        
        # Join back into a string
        return "\n".join(lines)
    
    def perform_improvement_cycle(self, content: str, evaluator: Any, iterations: int = 1, **kwargs) -> Tuple[str, List[Dict[str, Any]]]:
        """Perform a full improvement cycle with evaluation, improvement, and re-evaluation.
        
        Args:
            content: The README content to improve
            evaluator: An evaluator instance
            iterations: Number of improvement iterations to perform
            **kwargs: Additional arguments passed to evaluate() and improve()
            
        Returns:
            Tuple of (final_improved_content, cycle_results)
        """
        cycle_results = []
        current_content = content
        
        for i in range(iterations):
            logger.info(f"Starting improvement iteration {i+1}/{iterations}")
            
            # Evaluate current content
            score_before, eval_results = evaluator.evaluate(current_content, **kwargs)
            logger.info(f"Evaluation score: {score_before}")
            
            # Improve content
            improved_content, improve_details = self.improve(current_content, eval_results, **kwargs)
            
            # Re-evaluate improved content
            score_after, eval_after = evaluator.evaluate(improved_content, **kwargs)
            logger.info(f"After improvement: {score_after} ({score_after - score_before:+.1f})")
            
            # Create result for this cycle
            cycle_result = {
                "iteration": i + 1,
                "score_before": score_before,
                "score_after": score_after,
                "improvement": score_after - score_before,
                "evaluation_before": eval_results,
                "evaluation_after": eval_after,
                "content_before": current_content,
                "content_after": improved_content,
                "improvement_details": improve_details
            }
            cycle_results.append(cycle_result)
            
            # Update for next iteration
            current_content = improved_content
            
            # Early stopping if no improvement or perfect score
            if score_after <= score_before or score_after >= 95:
                logger.info(f"Stopping after iteration {i+1}: " + 
                          f"{'No improvement' if score_after <= score_before else 'Near perfect score'}")
                break
        
        return current_content, cycle_results
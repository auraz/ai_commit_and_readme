"""README Evaluator based on OpenAI Evals framework.

This module implements a README evaluator that follows the OpenAI Evals pattern,
evaluating README files against standard quality criteria.
"""

import json
import logging
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Union, TypedDict

import numpy as np

from .base import BaseEvaluator, EvalSpec, CompletionFn, SampleResult

logger = logging.getLogger(__name__)

# Define types for this evaluator
class ReadmeSample(TypedDict):
    """Type for README sample input."""
    id: str
    content: str
    filename: str
    metadata: Dict[str, Any]

class CategoryScore(TypedDict):
    """Type for category score."""
    score: int
    max_score: int
    reason: str

class ReadmeEvalResult(TypedDict):
    """Type for README evaluation result."""
    total_score: int
    max_score: int
    grade: str
    summary: str
    category_scores: Dict[str, CategoryScore]
    top_recommendations: List[str]

# Default README evaluation categories and their weights
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

# Default README evaluation prompt template
DEFAULT_PROMPT_TEMPLATE = """You are an expert README evaluator with extensive experience in software documentation.
Analyze the provided README file and evaluate it based on the following categories:

1. Title and Description (0-10 points):
   - Clear project title
   - Concise project description
   - Purpose and value proposition clear

2. Structure and Organization (0-15 points):
   - Logical hierarchy of sections
   - Good use of headers, lists, and emphasis
   - Information flows naturally

3. Installation Guide (0-15 points):
   - Clear prerequisites
   - Step-by-step installation instructions
   - Troubleshooting information if relevant

4. Usage Examples (0-15 points):
   - Basic usage examples
   - Code snippets where relevant
   - Common use cases demonstrated

5. Feature Explanation (0-10 points):
   - Clear list of features
   - Benefits explained
   - Distinctive features highlighted

6. Documentation Links (0-10 points):
   - Links to more detailed documentation
   - References to API docs if applicable
   - Wiki or additional resources linked

7. Badges and Shields (0-5 points):
   - Build status
   - Version information
   - Other relevant metadata

8. License Information (0-5 points):
   - Clear license specified
   - Any usage restrictions noted

9. Contributing Guidelines (0-5 points):
   - How others can contribute
   - Code of conduct or contribution standards

10. Conciseness and Clarity (0-10 points):
    - Appropriate length (not too verbose or sparse)
    - Clear language and explanations
    - Free of jargon or unexplained technical terms

README CONTENT TO EVALUATE:
```
{content}
```

FORMAT YOUR RESPONSE AS JSON:
{
  "category_scores": {
    "title_and_description": {"score": 0, "max_score": 10, "reason": "reason"},
    "structure_and_organization": {"score": 0, "max_score": 15, "reason": "reason"},
    "installation_guide": {"score": 0, "max_score": 15, "reason": "reason"},
    "usage_examples": {"score": 0, "max_score": 15, "reason": "reason"},
    "feature_explanation": {"score": 0, "max_score": 10, "reason": "reason"},
    "documentation_links": {"score": 0, "max_score": 10, "reason": "reason"},
    "badges_and_shields": {"score": 0, "max_score": 5, "reason": "reason"},
    "license_information": {"score": 0, "max_score": 5, "reason": "reason"},
    "contributing_guidelines": {"score": 0, "max_score": 5, "reason": "reason"},
    "conciseness_and_clarity": {"score": 0, "max_score": 10, "reason": "reason"}
  },
  "total_score": 0,
  "max_score": 100,
  "grade": "Poor/Needs Improvement/Satisfactory/Good/Excellent",
  "summary": "Brief summary evaluation",
  "top_recommendations": [
    "First recommendation",
    "Second recommendation",
    "Third recommendation"
  ]
}

Ensure your response is ONLY valid JSON that can be parsed.
"""


class ReadmeEvaluator(BaseEvaluator[ReadmeSample, None, ReadmeEvalResult]):
    """README file evaluator following OpenAI Evals pattern.
    
    Evaluates README files against standard quality criteria.
    """
    
    def __init__(
        self,
        spec: Optional[EvalSpec] = None,
        completion_fn: Optional[CompletionFn] = None,
        registry_path = None,
        cache_results: bool = True,
        categories: Optional[Dict[str, int]] = None
    ):
        """Initialize the README evaluator.
        
        Args:
            spec: Evaluation specification
            completion_fn: Function to get completions from a model
            registry_path: Path to the registry directory
            cache_results: Whether to cache evaluation results
            categories: Custom category weights (if None, uses defaults)
        """
        if spec is None:
            spec = EvalSpec(
                id="readme_eval",
                name="README Evaluation",
                description="Evaluates README files against standard quality criteria",
                prompt_template=DEFAULT_PROMPT_TEMPLATE,
                metrics=["total_score"] + list(README_CATEGORIES.keys()),
            )
        
        super().__init__(spec, completion_fn, registry_path, cache_results)
        self.categories = categories or README_CATEGORIES
    
    def eval_sample(self, sample: ReadmeSample, model_output: Optional[None] = None) -> SampleResult[ReadmeEvalResult]:
        """Evaluate a README sample.
        
        Args:
            sample: The README sample to evaluate
            model_output: Not used for this evaluator
            
        Returns:
            Evaluation result
        """
        # Check cache first if enabled
        if self.cache_results:
            cache_key = self._get_cache_key(sample)
            if cache_key in self.results_cache:
                logger.debug(f"Using cached result for {sample.get('id', 'unknown')}")
                return self.results_cache[cache_key]
        
        # Prepare the prompt with the README content
        prompt = self.prepare_prompt(
            sample["content"],
            filename=sample.get("filename", "README.md"),
            **sample.get("metadata", {})
        )
        
        # Call the model for evaluation
        if not self.completion_fn:
            raise ValueError("No completion function provided")
        
        try:
            # Call with JSON response format
            response = self.completion_fn.client.chat.completions.create(
                model=self.completion_fn.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.completion_fn.temperature,
                response_format={"type": "json_object"}
            )
            
            # Get raw response
            raw_response = response.choices[0].message.content
            
            # Parse JSON response
            result_data = json.loads(raw_response)
            
            # Extract and normalize the evaluation result
            result = self._normalize_result(result_data)
            
            # Calculate metrics from the result
            metrics = self._calculate_metrics(result)
            
            # Create sample result
            sample_result = SampleResult(
                spec=self.spec,
                sample_id=sample.get("id", "unknown"),
                result=result,
                metrics=metrics,
            )
            
            # Cache the result if enabled
            if self.cache_results:
                cache_key = self._get_cache_key(sample)
                self.results_cache[cache_key] = sample_result
            
            return sample_result
            
        except Exception as e:
            logger.error(f"Error evaluating README: {e}")
            
            # Create an error result
            error_result: ReadmeEvalResult = {
                "total_score": 0,
                "max_score": 100,
                "grade": "Error",
                "summary": f"Error evaluating README: {str(e)}",
                "category_scores": {},
                "top_recommendations": ["Fix evaluation errors"]
            }
            
            return SampleResult(
                spec=self.spec,
                sample_id=sample.get("id", "unknown"),
                result=error_result,
                metrics={"total_score": 0},
            )
    
    def _normalize_result(self, result_data: Dict[str, Any]) -> ReadmeEvalResult:
        """Normalize the raw evaluation result.
        
        Args:
            result_data: Raw evaluation result data
            
        Returns:
            Normalized evaluation result
        """
        # Initialize default result
        result: ReadmeEvalResult = {
            "total_score": 0,
            "max_score": 100,
            "grade": "Poor",
            "summary": result_data.get("summary", "No summary provided"),
            "category_scores": {},
            "top_recommendations": result_data.get("top_recommendations", [])
        }
        
        # Process all category scores
        if "category_scores" in result_data:
            category_scores = result_data["category_scores"]
            
            for category, (max_score) in self.categories.items():
                if category in category_scores:
                    score_data = category_scores[category]
                    
                    # Handle different formats
                    if isinstance(score_data, dict):
                        # Format: {"score": value, "max_score": value, "reason": "text"}
                        score = score_data.get("score", 0)
                        reason = score_data.get("reason", "No reason provided")
                    elif isinstance(score_data, list) and len(score_data) >= 2:
                        # Format: [score, "reason"]
                        score = score_data[0]
                        reason = score_data[1]
                    else:
                        # Unknown format
                        score = 0
                        reason = str(score_data)
                    
                    result["category_scores"][category] = {
                        "score": score,
                        "max_score": max_score,
                        "reason": reason
                    }
        
        # Process scores in older format if needed
        elif "scores" in result_data:
            scores = result_data["scores"]
            for category, max_score in self.categories.items():
                if category in scores:
                    score_data = scores[category]
                    
                    # Handle different formats
                    if isinstance(score_data, list) and len(score_data) >= 2:
                        # Format: [score, "reason"]
                        score = score_data[0]
                        reason = score_data[1]
                    elif isinstance(score_data, dict) and "score" in score_data:
                        # Format: {"score": value, "reason": "text"}
                        score = score_data.get("score", 0)
                        reason = score_data.get("reason", "No reason provided")
                    else:
                        # Unknown format
                        score = 0
                        reason = str(score_data)
                    
                    result["category_scores"][category] = {
                        "score": score,
                        "max_score": max_score,
                        "reason": reason
                    }
        
        # Calculate total score if not provided
        if "total_score" in result_data and isinstance(result_data["total_score"], (int, float)):
            result["total_score"] = int(result_data["total_score"])
        else:
            # Calculate from category scores
            total = 0
            for category, data in result["category_scores"].items():
                total += data["score"]
            result["total_score"] = min(total, 100)
        
        # Set grade based on score if not provided
        if "grade" in result_data:
            result["grade"] = result_data["grade"]
        else:
            # Calculate grade based on percentage
            percentage = (result["total_score"] / result["max_score"]) * 100
            if percentage >= 90:
                result["grade"] = "Excellent"
            elif percentage >= 80:
                result["grade"] = "Good"
            elif percentage >= 70:
                result["grade"] = "Satisfactory"
            elif percentage >= 50:
                result["grade"] = "Needs Improvement"
            else:
                result["grade"] = "Poor"
        
        return result
    
    def _calculate_metrics(self, result: ReadmeEvalResult) -> Dict[str, float]:
        """Calculate metrics from the evaluation result.
        
        Args:
            result: Evaluation result
            
        Returns:
            Dictionary of metric names to values
        """
        metrics = {
            "total_score": float(result["total_score"]),
            "score_percentage": float(result["total_score"]) / float(result["max_score"]) * 100,
        }
        
        # Add category scores as metrics
        for category, data in result["category_scores"].items():
            metrics[category] = float(data["score"])
            metrics[f"{category}_percentage"] = float(data["score"]) / float(data["max_score"]) * 100
        
        return metrics
    
    def _get_cache_key(self, sample: ReadmeSample) -> str:
        """Get a cache key for a sample.
        
        Args:
            sample: README sample
            
        Returns:
            Cache key string
        """
        # Use content hash as cache key
        content = sample["content"]
        return hashlib.md5(content.encode()).hexdigest()
    
    def format_result(self, result: ReadmeEvalResult, filename: str = "README.md") -> str:
        """Format the evaluation result as a readable report.
        
        Args:
            result: Evaluation result
            filename: Filename for display
            
        Returns:
            Formatted report as string
        """
        lines = [
            f"README Evaluation: {filename}",
            "=" * (18 + len(filename)),
            "",
            f"Overall Score: {result['total_score']}/{result['max_score']} - Grade: {result['grade']}",
            "",
            f"Summary: {result['summary']}",
            "",
            "Category Breakdown:",
        ]
        
        # Add category scores
        for category, data in result["category_scores"].items():
            category_display = category.replace("_", " ").title()
            lines.append(f"- {category_display}: {data['score']}/{data['max_score']} - {data['reason']}")
        
        lines.append("")
        
        # Add recommendations
        lines.append("Top Improvement Recommendations:")
        for rec in result["top_recommendations"]:
            lines.append(f"- {rec}")
        
        return "\n".join(lines)
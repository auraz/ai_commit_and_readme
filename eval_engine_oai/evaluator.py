"""Document Evaluator using OpenAI Evals architecture.

This module provides document evaluation capabilities following the OpenAI Evals
evaluation patterns, allowing standardized assessment of documentation quality.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union, TypedDict
import hashlib
from datetime import datetime

import openai

logger = logging.getLogger(__name__)

# Type definitions for our evaluator
class DocumentSample(TypedDict):
    """Type for document sample input."""
    id: str
    content: str
    filename: str
    metadata: Dict[str, Any]

class CategoryScore(TypedDict):
    """Type for category score."""
    score: int
    max_score: int
    reason: str

class EvaluationResult(TypedDict):
    """Type for document evaluation result."""
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

# Generic document evaluation categories and their weights
GENERIC_CATEGORIES = {
    "content_quality": 20,
    "structure_and_organization": 20,
    "clarity_and_readability": 20,
    "completeness": 15,
    "technical_accuracy": 15,
    "formatting_and_presentation": 10
}

# Default README evaluation prompt template
README_EVAL_PROMPT = """You are an expert README evaluator with extensive experience in software documentation.
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

# Generic document evaluation prompt template
GENERIC_EVAL_PROMPT = """You are an expert documentation evaluator with extensive experience in technical writing.
Analyze the provided document and evaluate it based on the following categories:

1. Content Quality (0-20 points):
   - Accuracy of information
   - Relevance to the topic
   - Appropriate level of detail

2. Structure and Organization (0-20 points):
   - Logical flow and hierarchy
   - Good use of headers, sections, and subsections
   - Information properly grouped by topic

3. Clarity and Readability (0-20 points):
   - Clear explanations
   - Appropriate language for the audience
   - Free of jargon or unexplained technical terms

4. Completeness (0-15 points):
   - Covers all necessary topics
   - Addresses common questions
   - No significant gaps in information

5. Technical Accuracy (0-15 points):
   - Correctness of technical information
   - Up-to-date content
   - No misleading statements or errors

6. Formatting and Presentation (0-10 points):
   - Consistent formatting
   - Effective use of markdown features
   - Visually organized and easy to navigate

DOCUMENT CONTENT TO EVALUATE:
```
{content}
```

FORMAT YOUR RESPONSE AS JSON:
{
  "category_scores": {
    "content_quality": {"score": 0, "max_score": 20, "reason": "reason"},
    "structure_and_organization": {"score": 0, "max_score": 20, "reason": "reason"},
    "clarity_and_readability": {"score": 0, "max_score": 20, "reason": "reason"},
    "completeness": {"score": 0, "max_score": 15, "reason": "reason"},
    "technical_accuracy": {"score": 0, "max_score": 15, "reason": "reason"},
    "formatting_and_presentation": {"score": 0, "max_score": 10, "reason": "reason"}
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

class DocEvaluator:
    """Document evalu
ator using OpenAI Evals patterns.
    
    Evaluates documentation against standardized criteria using
    the OpenAI API and following the design of OpenAI Evals.
    """
    
    def __init__(
        self,
        client: Optional[openai.OpenAI] = None,
        model: str = "gpt-4",
        temperature: float = 0.2,
        cache_results: bool = True,
        cache_dir: Optional[str] = None
    ):
        """Initialize the document evaluator.
        
        Args:
            client: OpenAI client instance (if None, will create one)
            model: Model to use for evaluation
            temperature: Temperature for model inference
            cache_results: Whether to cache evaluation results
            cache_dir: Directory for caching results (if None, uses temporary directory)
        """
        self.client = client or self._create_client()
        self.model = model
        self.temperature = temperature
        self.cache_results = cache_results
        self.cache_dir = cache_dir
        
        # Set up cache
        self.results_cache = {}
        if cache_results and cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
    
    def _create_client(self) -> openai.OpenAI:
        """Create an OpenAI client.
        
        Returns:
            OpenAI client instance
            
        Raises:
            ValueError: If OPENAI_API_KEY environment variable is not set
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Please set it with your OpenAI API key."
            )
        
        return openai.OpenAI(api_key=api_key)
    
    def evaluate(
        self,
        content: str,
        doc_type: str = "readme",
        filename: Optional[str] = None,
        **kwargs
    ) -> Tuple[EvaluationResult, Dict[str, float]]:
        """Evaluate a document.
        
        Args:
            content: Document content to evaluate
            doc_type: Type of document (readme, generic, etc.)
            filename: Filename for the document (for display)
            **kwargs: Additional metadata for evaluation
            
        Returns:
            Tuple of (evaluation_result, metrics)
        """
        # Create a sample for evaluation
        sample_id = kwargs.get("id", f"{doc_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        filename = filename or f"{doc_type}.md"
        
        sample = {
            "id": sample_id,
            "content": content,
            "filename": filename,
            "metadata": kwargs
        }
        
        # Evaluate the sample
        result = self.eval_sample(sample, doc_type)
        
        # Calculate metrics
        metrics = self._calculate_metrics(result)
        
        return result, metrics
    
    def eval_sample(
        self,
        sample: DocumentSample,
        doc_type: str = "readme"
    ) -> EvaluationResult:
        """Evaluate a single document sample.
        
        Args:
            sample: Document sample to evaluate
            doc_type: Type of document
            
        Returns:
            Evaluation result
        """
        # Check cache first if enabled
        if self.cache_results:
            cache_key = self._get_cache_key(sample["content"])
            if cache_key in self.results_cache:
                logger.debug(f"Using cached result for {sample.get('id', 'unknown')}")
                return self.results_cache[cache_key]
        
        # Prepare the prompt with the document content
        prompt = self._get_prompt_for_doc_type(doc_type)
        prompt = prompt.replace("{content}", sample["content"])
        
        # Add any additional context from metadata
        metadata = sample.get("metadata", {})
        for key, value in metadata.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))
        
        try:
            # Call the model for evaluation
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Get raw response
            raw_response = response.choices[0].message.content
            
            # Parse JSON response
            result_data = json.loads(raw_response)
            
            # Normalize the result
            result = self._normalize_result(result_data, doc_type)
            
            # Cache the result if enabled
            if self.cache_results:
                cache_key = self._get_cache_key(sample["content"])
                self.results_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating document: {e}")
            
            # Create an error result
            error_result: EvaluationResult = {
                "total_score": 0,
                "max_score": 100,
                "grade": "Error",
                "summary": f"Error evaluating document: {str(e)}",
                "category_scores": {},
                "top_recommendations": ["Fix evaluation errors"]
            }
            
            return error_result
    
    def _get_prompt_for_doc_type(self, doc_type: str) -> str:
        """Get the evaluation prompt for a document type.
        
        Args:
            doc_type: Type of document
            
        Returns:
            Prompt template for the document type
        """
        if doc_type == "readme":
            return README_EVAL_PROMPT
        else:
            return GENERIC_EVAL_PROMPT
    
    def _normalize_result(
        self,
        result_data: Dict[str, Any],
        doc_type: str
    ) -> EvaluationResult:
        """Normalize the raw evaluation result.
        
        Args:
            result_data: Raw evaluation result data
            doc_type: Type of document
            
        Returns:
            Normalized evaluation result
        """
        # Get categories for this document type
        categories = README_CATEGORIES if doc_type == "readme" else GENERIC_CATEGORIES
        
        # Initialize default result
        result: EvaluationResult = {
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
            
            for category, max_score in categories.items():
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
            for category, max_score in categories.items():
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
    
    def _calculate_metrics(self, result: EvaluationResult) -> Dict[str, float]:
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
    
    def _get_cache_key(self, content: str) -> str:
        """Get a cache key for content.
        
        Args:
            content: Document content
            
        Returns:
            Cache key string
        """
        # Use content hash as cache key
        return hashlib.md5(content.encode()).hexdigest()
    
    def format_result(self, result: EvaluationResult, filename: str = "document.md") -> str:
        """Format the evaluation result as a readable report.
        
        Args:
            result: Evaluation result
            filename: Filename for display
            
        Returns:
            Formatted report as string
        """
        lines = [
            f"Documentation Evaluation: {filename}",
            "=" * (24 + len(filename)),
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


def evaluate_document(
    content: str,
    doc_type: str = "readme",
    filename: Optional[str] = None,
    model: str = "gpt-4",
    client: Optional[openai.OpenAI] = None,
    **kwargs
) -> Tuple[EvaluationResult, Dict[str, float]]:
    """Evaluate a document using OpenAI Evals patterns.
    
    Args:
        content: Document content to evaluate
        doc_type: Type of document (readme, generic, etc.)
        filename: Filename for the document (for display)
        model: Model to use for evaluation
        client: OpenAI client instance (if None, will create one)
        **kwargs: Additional metadata for evaluation
        
    Returns:
        Tuple of (evaluation_result, metrics)
    """
    evaluator = DocEvaluator(client=client, model=model)
    return evaluator.evaluate(content, doc_type, filename, **kwargs)
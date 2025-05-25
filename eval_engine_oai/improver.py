"""Document Improver using OpenAI Evals architecture.

This module provides document improvement capabilities, taking evaluation results
and generating improved content using large language models.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union
import difflib
from datetime import datetime

import openai

logger = logging.getLogger(__name__)

# Default README improver prompt template
README_IMPROVE_PROMPT = """You are an expert technical writer specializing in README files for software projects.
Your task is to improve the provided README based on the evaluation feedback.

## CURRENT README
```
{content}
```

## EVALUATION RESULTS
```
{evaluation_result}
```

## AREAS TO FOCUS ON
{focus_areas}

## IMPROVEMENT INSTRUCTIONS

1. Keep the project's intended audience and purpose in mind
2. Maintain the existing structure unless reorganization would significantly improve clarity
3. Preserve any existing links, code snippets, and technical information
4. Address all the issues mentioned in the evaluation results, especially in the focus areas
5. Keep a similar tone but improve clarity and conciseness
6. Do not invent features or capabilities not mentioned in the original README
7. Ensure proper markdown formatting throughout
8. Include appropriate section headers to organize content
9. Make code examples clear with proper syntax highlighting
10. Balance completeness with brevity

## ADDITIONAL CONSIDERATIONS

- If installation instructions are missing or unclear, add clear step-by-step instructions
- If usage examples are sparse, expand them with practical code snippets
- Ensure the project's value proposition is clearly stated near the beginning
- Add badges if appropriate (build status, version, license)
- If the license section is missing, add one with appropriate disclaimer
- Check for and fix any broken formatting or unclear sections

Write a complete, improved version of the README that addresses all the evaluation feedback while maintaining the original intent and technical accuracy.
"""

# Generic document improver prompt template
GENERIC_IMPROVE_PROMPT = """You are an expert technical writer specializing in documentation.
Your task is to improve the provided document based on the evaluation feedback.

## CURRENT DOCUMENT
```
{content}
```

## EVALUATION RESULTS
```
{evaluation_result}
```

## AREAS TO FOCUS ON
{focus_areas}

## IMPROVEMENT INSTRUCTIONS

1. Keep the document's intended audience and purpose in mind
2. Maintain the existing structure unless reorganization would significantly improve clarity
3. Preserve any existing links, code snippets, and technical information
4. Address all the issues mentioned in the evaluation results, especially in the focus areas
5. Keep a similar tone but improve clarity and conciseness
6. Do not invent features or capabilities not mentioned in the original document
7. Ensure proper markdown formatting throughout
8. Include appropriate section headers to organize content
9. Make code examples clear with proper syntax highlighting
10. Balance completeness with brevity

Write a complete, improved version of the document that addresses all the evaluation feedback while maintaining the original intent and technical accuracy.
"""


class DocImprover:
    """Document improver using OpenAI Evals patterns.
    
    Improves documentation based on evaluation results using
    large language models to generate enhanced content.
    """
    
    def __init__(
        self,
        client: Optional[openai.OpenAI] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """Initialize the document improver.
        
        Args:
            client: OpenAI client instance (if None, will create one)
            model: Model to use for improvements
            temperature: Temperature for model inference
            max_tokens: Maximum tokens for generation (if None, uses model default)
        """
        self.client = client or self._create_client()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
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
    
    def improve(
        self,
        content: str,
        evaluation_result: Dict[str, Any],
        doc_type: str = "readme",
        **kwargs
    ) -> Tuple[str, Dict[str, Any]]:
        """Improve a document based on evaluation results.
        
        Args:
            content: Document content to improve
            evaluation_result: Evaluation results
            doc_type: Type of document (readme, generic, etc.)
            **kwargs: Additional metadata for improvement
            
        Returns:
            Tuple of (improved_content, improvement_details)
        """
        # Prepare the improvement prompt
        prompt = self._prepare_prompt(content, evaluation_result, doc_type, **kwargs)
        
        try:
            # Call the model for improvement
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Get improved content
            improved_content = response.choices[0].message.content
            
            # Clean up the improved content
            improved_content = self._clean_improved_content(improved_content)
            
            # Generate improvement details
            details = self._generate_improvement_details(content, improved_content, evaluation_result)
            
            return improved_content, details
            
        except Exception as e:
            logger.error(f"Error improving document: {e}")
            return content, {"error": str(e)}
    
    def _prepare_prompt(
        self,
        content: str,
        evaluation_result: Dict[str, Any],
        doc_type: str,
        **kwargs
    ) -> str:
        """Prepare the improvement prompt.
        
        Args:
            content: Document content to improve
            evaluation_result: Evaluation results
            doc_type: Type of document
            **kwargs: Additional variables to substitute in the prompt
            
        Returns:
            Prepared prompt
        """
        # Get the appropriate prompt template
        template = README_IMPROVE_PROMPT if doc_type == "readme" else GENERIC_IMPROVE_PROMPT
        
        # Format evaluation results as text
        eval_text = json.dumps(evaluation_result, indent=2)
        
        # Determine focus areas based on evaluation results
        focus_areas = self._determine_focus_areas(evaluation_result)
        
        # Replace placeholders in prompt template
        prompt = template.replace("{content}", content)
        prompt = prompt.replace("{evaluation_result}", eval_text)
        prompt = prompt.replace("{focus_areas}", focus_areas)
        
        # Replace any other placeholders
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))
        
        return prompt
    
    def _determine_focus_areas(self, evaluation_result: Dict[str, Any]) -> str:
        """Determine focus areas for improvement based on evaluation results.
        
        Args:
            evaluation_result: Evaluation results
            
        Returns:
            Focus areas as a formatted string
        """
        focus_areas = []
        
        # Use recommendations if available
        if "top_recommendations" in evaluation_result:
            recommendations = evaluation_result["top_recommendations"]
            if recommendations:
                for rec in recommendations:
                    focus_areas.append(f"- {rec}")
                return "\n".join(focus_areas)
        
        # Otherwise find lowest scoring categories
        if "category_scores" in evaluation_result:
            categories = []
            for category, data in evaluation_result["category_scores"].items():
                if isinstance(data, dict) and "score" in data and "max_score" in data:
                    score = data["score"]
                    max_score = data["max_score"]
                    percentage = (score / max_score) * 100
                    categories.append((category, score, max_score, percentage))
            
            # Sort by percentage (lowest first)
            categories.sort(key=lambda x: x[3])
            
            # Take the lowest 3 categories
            for category, score, max_score, percentage in categories[:3]:
                if percentage < 80:  # Only focus on categories below 80%
                    category_display = category.replace("_", " ").title()
                    focus_areas.append(f"- Improve {category_display}: currently scores {score}/{max_score}")
        
        # Default focus areas if none found
        if not focus_areas:
            focus_areas = [
                "- Improve overall document structure and clarity",
                "- Add more detail where needed",
                "- Ensure all information is accurate and complete"
            ]
        
        return "\n".join(focus_areas)
    
    def _clean_improved_content(self, raw_content: str) -> str:
        """Clean up the improved content from the model.
        
        Args:
            raw_content: Raw content from the model
            
        Returns:
            Cleaned content
        """
        # Remove any markdown code block markers
        content = raw_content
        
        # Handle ```content``` blocks
        if content.startswith("```") and "```" in content[3:]:
            start_idx = content.find("```") + 3
            end_idx = content.find("```", start_idx)
            
            # Check if there's a language specifier
            language_end = content.find("\n", 3)
            if 3 < language_end < start_idx:
                start_idx = language_end + 1
            
            if end_idx > start_idx:
                content = content[start_idx:end_idx].strip()
        
        # Remove any header comments
        lines = content.splitlines()
        if lines and lines[0].startswith("/* ") and lines[0].endswith(" */"):
            lines = lines[1:]
        
        return "\n".join(lines)
    
    def _generate_improvement_details(
        self,
        original_content: str,
        improved_content: str,
        evaluation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate details about the improvements made.
        
        Args:
            original_content: Original content
            improved_content: Improved content
            evaluation_result: Evaluation results
            
        Returns:
            Dictionary of improvement details
        """
        # Calculate diff
        diff = difflib.unified_diff(
            original_content.splitlines(),
            improved_content.splitlines(),
            lineterm='',
            n=3
        )
        
        # Extract top improvements from evaluation result
        top_improvements = []
        if "top_recommendations" in evaluation_result:
            top_improvements = [
                f"Addressed: {rec}" for rec in evaluation_result["top_recommendations"]
            ]
        
        # Calculate basic metrics
        original_words = len(original_content.split())
        improved_words = len(improved_content.split())
        word_change = improved_words - original_words
        
        return {
            "diff": "\n".join(diff),
            "original_length": len(original_content),
            "improved_length": len(improved_content),
            "word_count_original": original_words,
            "word_count_improved": improved_words,
            "word_count_change": word_change,
            "top_improvements": top_improvements,
            "timestamp": datetime.now().isoformat()
        }
    
    def format_improvement_report(
        self,
        original_content: str,
        improved_content: str,
        evaluation_before: Dict[str, Any],
        evaluation_after: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format an improvement report.
        
        Args:
            original_content: Original content
            improved_content: Improved content
            evaluation_before: Evaluation results before improvement
            evaluation_after: Evaluation results after improvement (if available)
            
        Returns:
            Formatted report as string
        """
        lines = [
            "Improvement Report",
            "=================",
            "",
        ]
        
        # Add score improvement if available
        if evaluation_after:
            score_before = evaluation_before.get("total_score", 0)
            score_after = evaluation_after.get("total_score", 0)
            score_improvement = score_after - score_before
            
            lines.append(f"Score Before: {score_before}")
            lines.append(f"Score After: {score_after}")
            lines.append(f"Improvement: {score_improvement:+.1f} points")
            lines.append("")
        
        # Add content change metrics
        original_words = len(original_content.split())
        improved_words = len(improved_content.split())
        word_change = improved_words - original_words
        
        lines.append("Content Changes:")
        lines.append(f"- Original word count: {original_words}")
        lines.append(f"- Improved word count: {improved_words}")
        if word_change > 0:
            lines.append(f"- Added {word_change} words")
        elif word_change < 0:
            lines.append(f"- Removed {abs(word_change)} words")
        lines.append("")
        
        # Add improvements addressed
        if "top_recommendations" in evaluation_before:
            lines.append("Improvements Addressed:")
            for rec in evaluation_before["top_recommendations"]:
                lines.append(f"- {rec}")
            lines.append("")
        
        # Add category improvements if available
        if (evaluation_after and
            "category_scores" in evaluation_before and
            "category_scores" in evaluation_after):
            
            categories_before = evaluation_before["category_scores"]
            categories_after = evaluation_after["category_scores"]
            
            lines.append("Category Improvements:")
            for category in sorted(categories_before.keys()):
                if category in categories_after:
                    score_before = categories_before[category]["score"]
                    score_after = categories_after[category]["score"]
                    change = score_after - score_before
                    
                    if change != 0:
                        category_display = category.replace("_", " ").title()
                        lines.append(f"- {category_display}: {score_before} → {score_after} ({change:+d})")
            
            lines.append("")
        
        return "\n".join(lines)


def improve_document(
    content: str,
    evaluation_result: Dict[str, Any],
    doc_type: str = "readme",
    model: str = "gpt-4",
    client: Optional[openai.OpenAI] = None,
    **kwargs
) -> Tuple[str, Dict[str, Any]]:
    """Improve a document based on evaluation results.
    
    Args:
        content: Document content to improve
        evaluation_result: Evaluation results
        doc_type: Type of document (readme, generic, etc.)
        model: Model to use for improvements
        client: OpenAI client instance (if None, will create one)
        **kwargs: Additional metadata for improvement
        
    Returns:
        Tuple of (improved_content, improvement_details)
    """
    improver = DocImprover(client=client, model=model)
    return improver.improve(content, evaluation_result, doc_type, **kwargs)
"""Base Evaluator Class for Documentation Evaluation.

This module defines the base class that all document evaluators must implement.
It provides common functionality and a standardized interface for evaluation.
"""

import logging
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

from openai import OpenAI

logger = logging.getLogger(__name__)


class BaseEvaluator(ABC):
    """Base class for all document evaluators.
    
    This abstract base class defines the interface and common functionality
    for document evaluators. Specific evaluator types should inherit from this
    class and implement the required abstract methods.
    """
    
    def __init__(
        self, 
        prompts_dir: Optional[Path] = None, 
        model: str = "gpt-4",
        temperature: float = 0.2,
        api_key: Optional[str] = None,
        track_history: bool = True,
        evaluation_id: Optional[str] = None
    ):
        """Initialize the evaluator.
        
        Args:
            prompts_dir: Directory containing evaluation prompt templates
            model: OpenAI model to use for evaluation
            temperature: Temperature setting for the model
            api_key: OpenAI API key (if None, will use environment variable)
            track_history: Whether to track evaluation history
            evaluation_id: Optional unique ID for this evaluation
        """
        self.model = model
        self.temperature = temperature
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.track_history = track_history
        self.evaluation_id = evaluation_id or datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Set default prompts directory if not provided
        if prompts_dir is None:
            # Try to find the default prompts directory
            module_dir = Path(__file__).parent.parent.parent
            self.prompts_dir = module_dir / "ai_commit_and_readme" / "prompts" / "evals"
            if not self.prompts_dir.exists():
                # Fall back to a relative path
                self.prompts_dir = Path("prompts") / "evals"
        else:
            self.prompts_dir = prompts_dir
        
        # Initialize history
        self.history = [] if track_history else None
        
        # Ensure we have an API key
        if not self.api_key:
            logger.warning("No OpenAI API key provided or found in environment")

    @abstractmethod
    def evaluate(self, content: str, **kwargs) -> Tuple[int, Dict[str, Any]]:
        """Evaluate the provided content.
        
        Args:
            content: The document content to evaluate
            **kwargs: Additional arguments specific to the evaluator
            
        Returns:
            Tuple of (score, evaluation_results)
        """
        pass
    
    def load_prompt(self, prompt_file: str) -> Optional[str]:
        """Load a prompt template from file.
        
        Args:
            prompt_file: Filename of the prompt template
            
        Returns:
            The prompt template content or None if not found
        """
        prompt_path = self.prompts_dir / prompt_file
        if not prompt_path.exists():
            logger.error(f"Prompt file not found: {prompt_path}")
            return None
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading prompt file {prompt_path}: {e}")
            return None
    
    def call_model(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call the OpenAI API with the given prompt.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Parsed JSON response or None if failed
        """
        if not self.api_key:
            logger.error("No OpenAI API key available")
            return None
        
        try:
            client = OpenAI(api_key=self.api_key)
            
            logger.info(f"Sending request to model: {self.model}")
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Get raw response
            raw_response = response.choices[0].message.content
            
            # Parse JSON
            try:
                return json.loads(raw_response)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing model response: {e}")
                logger.debug(f"Raw response: {raw_response[:500]}...")
                return None
                
        except Exception as e:
            logger.error(f"Error calling model: {e}")
            return None
    
    def format_evaluation_report(self, 
                                evaluation: Dict[str, Any], 
                                title: str) -> str:
        """Format evaluation results as a readable report.
        
        Args:
            evaluation: The evaluation results
            title: The report title
            
        Returns:
            Formatted report as string
        """
        report = [title, "=" * len(title), ""]
        
        # Add score and grade
        total_score = evaluation.get("total_score", 0)
        max_score = evaluation.get("max_score", 100)
        grade = evaluation.get("grade", "N/A")
        
        report.append(f"Overall Score: {total_score}/{max_score} - Grade: {grade}")
        report.append("")
        
        # Add summary
        summary = evaluation.get("summary", "No summary provided")
        report.append(f"Summary: {summary}")
        report.append("")
        
        # Add category breakdown
        report.append("Category Breakdown:")
        
        if "scores" in evaluation:
            scores = evaluation["scores"]
            for category, data in scores.items():
                # Handle different score formats
                if isinstance(data, list) and len(data) >= 2:
                    # Format: [score, "reason"]
                    score, reason = data[0], data[1]
                elif isinstance(data, dict) and "score" in data:
                    # Format: {"score": value, "reason": "text"}
                    score, reason = data.get("score", 0), data.get("reason", "No reason provided")
                else:
                    # Unknown format
                    score, reason = "?", str(data)
                
                # Format category name for display
                category_display = category.replace("_", " ").title()
                report.append(f"- {category_display}: {score} - {reason}")
        else:
            report.append("No category scores found in evaluation")
        
        report.append("")
        
        # Add recommendations
        report.append("Top Improvement Recommendations:")
        recommendations = evaluation.get("top_recommendations", [])
        if recommendations:
            for rec in recommendations:
                report.append(f"- {rec}")
        else:
            report.append("No recommendations provided")
        
        # Join all lines
        return "\n".join(report)
    
    def track_evaluation(self, 
                         content: str, 
                         score: int, 
                         results: Dict[str, Any],
                         metadata: Optional[Dict[str, Any]] = None) -> None:
        """Track an evaluation in history.
        
        Args:
            content: The evaluated content
            score: The evaluation score
            results: The evaluation results
            metadata: Additional metadata to track
        """
        if not self.track_history:
            return
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "evaluation_id": self.evaluation_id,
            "score": score,
            "results": results,
            "content_hash": hash(content),  # Simple content fingerprint
            "metadata": metadata or {}
        }
        
        self.history.append(entry)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get evaluation history.
        
        Returns:
            List of evaluation history entries
        """
        return self.history if self.track_history else []
    
    def save_history(self, file_path: Path) -> bool:
        """Save evaluation history to file.
        
        Args:
            file_path: Path to save history to
            
        Returns:
            True if successful, False otherwise
        """
        if not self.track_history or not self.history:
            logger.warning("No history to save")
            return False
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving history: {e}")
            return False
    
    def load_history(self, file_path: Path) -> bool:
        """Load evaluation history from file.
        
        Args:
            file_path: Path to load history from
            
        Returns:
            True if successful, False otherwise
        """
        if not self.track_history:
            logger.warning("History tracking is disabled")
            return False
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.history = json.load(f)
            return True
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            return False
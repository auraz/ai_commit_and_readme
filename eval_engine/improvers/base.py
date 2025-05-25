"""Base Improver Class for Documentation Enhancement.

This module defines the base class that all document improvers must implement.
It provides common functionality and a standardized interface for enhancing
documentation based on evaluation results.
"""

import logging
import json
import os
import difflib
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

from openai import OpenAI

logger = logging.getLogger(__name__)


class BaseImprover(ABC):
    """Base class for all document improvers.
    
    This abstract base class defines the interface and common functionality
    for document improvers. Specific improver types should inherit from this
    class and implement the required abstract methods.
    """
    
    def __init__(
        self, 
        prompts_dir: Optional[Path] = None, 
        model: str = "gpt-4",
        temperature: float = 0.7,  # Higher temperature for more creative improvements
        api_key: Optional[str] = None,
        track_history: bool = True,
        improvement_id: Optional[str] = None
    ):
        """Initialize the improver.
        
        Args:
            prompts_dir: Directory containing improvement prompt templates
            model: OpenAI model to use for improvements
            temperature: Temperature setting for the model
            api_key: OpenAI API key (if None, will use environment variable)
            track_history: Whether to track improvement history
            improvement_id: Optional unique ID for this improvement session
        """
        self.model = model
        self.temperature = temperature
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.track_history = track_history
        self.improvement_id = improvement_id or datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Set default prompts directory if not provided
        if prompts_dir is None:
            # Try to find the default prompts directory
            module_dir = Path(__file__).parent.parent.parent
            self.prompts_dir = module_dir / "ai_commit_and_readme" / "prompts" / "improvers"
            if not self.prompts_dir.exists():
                # Create the improvers directory if it doesn't exist
                self.prompts_dir = module_dir / "ai_commit_and_readme" / "prompts" / "improvers"
                os.makedirs(self.prompts_dir, exist_ok=True)
        else:
            self.prompts_dir = prompts_dir
            
        # Initialize history
        self.history = [] if track_history else None
        
        # Ensure we have an API key
        if not self.api_key:
            logger.warning("No OpenAI API key provided or found in environment")

    @abstractmethod
    def improve(self, content: str, evaluation_results: Dict[str, Any], **kwargs) -> Tuple[str, Dict[str, Any]]:
        """Improve the provided content based on evaluation results.
        
        Args:
            content: The document content to improve
            evaluation_results: Results from an evaluator
            **kwargs: Additional arguments specific to the improver
            
        Returns:
            Tuple of (improved_content, improvement_details)
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
            # Try to find in the evals directory as fallback
            evals_dir = self.prompts_dir.parent / "evals"
            prompt_path = evals_dir / prompt_file
            if not prompt_path.exists():
                logger.error(f"Prompt file not found: {prompt_file}")
                return None
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading prompt file {prompt_path}: {e}")
            return None
    
    def save_prompt(self, prompt_file: str, content: str) -> bool:
        """Save a prompt template to file.
        
        Args:
            prompt_file: Filename of the prompt template
            content: Content to save
            
        Returns:
            True if successful, False otherwise
        """
        os.makedirs(self.prompts_dir, exist_ok=True)
        prompt_path = self.prompts_dir / prompt_file
        
        try:
            with open(prompt_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error saving prompt file {prompt_path}: {e}")
            return False
    
    def call_model(self, prompt: str, response_format: str = "text") -> Any:
        """Call the OpenAI API with the given prompt.
        
        Args:
            prompt: The prompt to send to the model
            response_format: Format of the response ("text" or "json_object")
            
        Returns:
            Model response as text, parsed JSON, or None if failed
        """
        if not self.api_key:
            logger.error("No OpenAI API key available")
            return None
        
        try:
            client = OpenAI(api_key=self.api_key)
            
            logger.info(f"Sending improvement request to model: {self.model}")
            
            format_param = {"type": response_format} if response_format == "json_object" else None
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                response_format=format_param
            )
            
            # Get raw response
            raw_response = response.choices[0].message.content
            
            # Parse JSON if requested
            if response_format == "json_object":
                try:
                    return json.loads(raw_response)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing model response: {e}")
                    logger.debug(f"Raw response: {raw_response[:500]}...")
                    return None
            
            return raw_response
                
        except Exception as e:
            logger.error(f"Error calling model: {e}")
            return None
    
    def calculate_diff(self, original: str, improved: str) -> str:
        """Calculate a diff between original and improved content.
        
        Args:
            original: Original content
            improved: Improved content
            
        Returns:
            Unified diff as string
        """
        original_lines = original.splitlines(keepends=True)
        improved_lines = improved.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines, 
            improved_lines,
            fromfile='original',
            tofile='improved',
            n=3
        )
        
        return ''.join(diff)
    
    def track_improvement(self, 
                         original: str,
                         improved: str,
                         evaluation_before: Dict[str, Any],
                         evaluation_after: Optional[Dict[str, Any]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> None:
        """Track an improvement in history.
        
        Args:
            original: The original content
            improved: The improved content
            evaluation_before: Evaluation results before improvement
            evaluation_after: Evaluation results after improvement (if available)
            metadata: Additional metadata to track
        """
        if not self.track_history:
            return
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "improvement_id": self.improvement_id,
            "score_before": evaluation_before.get("total_score", 0),
            "score_after": evaluation_after.get("total_score", 0) if evaluation_after else None,
            "content_hash_before": hash(original),
            "content_hash_after": hash(improved),
            "diff": self.calculate_diff(original, improved),
            "metadata": metadata or {}
        }
        
        self.history.append(entry)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get improvement history.
        
        Returns:
            List of improvement history entries
        """
        return self.history if self.track_history else []
    
    def save_history(self, file_path: Path) -> bool:
        """Save improvement history to file.
        
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
        """Load improvement history from file.
        
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
    
    def create_improvement_summary(self, 
                                 original: str, 
                                 improved: str, 
                                 evaluation_before: Dict[str, Any],
                                 evaluation_after: Optional[Dict[str, Any]] = None) -> str:
        """Create a summary of improvements made.
        
        Args:
            original: Original content
            improved: Improved content
            evaluation_before: Evaluation results before improvement
            evaluation_after: Evaluation results after improvement (if available)
            
        Returns:
            Formatted summary as string
        """
        summary = ["Improvement Summary", "=================", ""]
        
        # Score comparison
        score_before = evaluation_before.get("total_score", 0)
        score_after = evaluation_after.get("total_score", 0) if evaluation_after else "N/A"
        
        summary.append(f"Score Before: {score_before}")
        summary.append(f"Score After: {score_after}")
        
        if evaluation_after and score_after > score_before:
            improvement = score_after - score_before
            summary.append(f"Improvement: +{improvement} points")
        summary.append("")
        
        # Key improvements
        summary.append("Key Improvements:")
        
        # Extract recommendations that were addressed
        recommendations = evaluation_before.get("top_recommendations", [])
        if recommendations:
            for rec in recommendations:
                summary.append(f"- Addressed: {rec}")
        else:
            summary.append("- General improvements to document structure and content")
        
        summary.append("")
        
        # Changes summary
        original_words = len(original.split())
        improved_words = len(improved.split())
        word_diff = improved_words - original_words
        
        summary.append("Changes Statistics:")
        summary.append(f"- Original word count: {original_words}")
        summary.append(f"- Improved word count: {improved_words}")
        if word_diff > 0:
            summary.append(f"- Added {word_diff} words")
        elif word_diff < 0:
            summary.append(f"- Removed {abs(word_diff)} words")
        summary.append("")
        
        # Diff preview
        diff = self.calculate_diff(original, improved)
        if len(diff) < 500:  # Only include diff if it's reasonably small
            summary.append("Changes Preview:")
            summary.append("```")
            summary.append(diff)
            summary.append("```")
        
        return "\n".join(summary)
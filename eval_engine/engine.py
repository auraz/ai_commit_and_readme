"""Main Evaluation Engine for Documentation Quality.

This module provides the core engine components for document evaluation and improvement,
implementing a closed-loop system for continuous quality enhancement.
"""

import logging
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union, Type

logger = logging.getLogger(__name__)


class EvaluationEngine:
    """Core evaluation engine for documentation quality assessment.
    
    This class manages document evaluators and provides a unified interface
    for evaluating different types of documentation.
    """
    
    def __init__(self, 
                evaluators: Optional[Dict[str, Any]] = None,
                storage_dir: Optional[Path] = None):
        """Initialize the evaluation engine.
        
        Args:
            evaluators: Dictionary mapping document types to evaluator instances
            storage_dir: Directory for storing evaluation results and history
        """
        self.evaluators = evaluators or {}
        self.storage_dir = storage_dir or Path("evaluation_results")
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize evaluation history
        self.history = []
    
    def register_evaluator(self, doc_type: str, evaluator: Any) -> None:
        """Register an evaluator for a document type.
        
        Args:
            doc_type: Document type (e.g., "readme", "wiki")
            evaluator: Evaluator instance
        """
        self.evaluators[doc_type] = evaluator
        logger.info(f"Registered evaluator for {doc_type} documents")
    
    def get_evaluator(self, doc_type: str) -> Optional[Any]:
        """Get the evaluator for a document type.
        
        Args:
            doc_type: Document type
            
        Returns:
            Evaluator instance or None if not found
        """
        return self.evaluators.get(doc_type)
    
    def evaluate_document(self, content: str, doc_type: str, **kwargs) -> Tuple[int, Dict[str, Any]]:
        """Evaluate a document using the appropriate evaluator.
        
        Args:
            content: Document content
            doc_type: Document type
            **kwargs: Additional arguments passed to the evaluator
            
        Returns:
            Tuple of (score, evaluation_results)
            
        Raises:
            ValueError: If no evaluator is registered for the document type
        """
        evaluator = self.get_evaluator(doc_type)
        if not evaluator:
            raise ValueError(f"No evaluator registered for document type: {doc_type}")
        
        # Perform evaluation
        score, results = evaluator.evaluate(content, **kwargs)
        
        # Track in history
        self._track_evaluation(doc_type, content, score, results, kwargs)
        
        return score, results
    
    def evaluate_file(self, file_path: str, doc_type: Optional[str] = None, **kwargs) -> Tuple[int, Dict[str, Any]]:
        """Evaluate a document file using the appropriate evaluator.
        
        Args:
            file_path: Path to the document file
            doc_type: Document type (if None, will be inferred from file extension)
            **kwargs: Additional arguments passed to the evaluator
            
        Returns:
            Tuple of (score, evaluation_results)
            
        Raises:
            ValueError: If the file doesn't exist or doc_type cannot be inferred
        """
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Infer document type if not provided
        if doc_type is None:
            doc_type = self._infer_doc_type(file_path)
        
        # Add filename to kwargs
        kwargs["filename"] = os.path.basename(file_path)
        
        return self.evaluate_document(content, doc_type, **kwargs)
    
    def _infer_doc_type(self, file_path: str) -> str:
        """Infer document type from file path.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Inferred document type
            
        Raises:
            ValueError: If document type cannot be inferred
        """
        filename = os.path.basename(file_path).lower()
        
        if filename == "readme.md":
            return "readme"
        elif os.path.dirname(file_path).endswith("wiki") or "wiki" in filename:
            return "wiki"
        elif filename.endswith(".md"):
            return "markdown"
        else:
            raise ValueError(f"Cannot infer document type for: {file_path}")
    
    def _track_evaluation(self, 
                        doc_type: str, 
                        content: str, 
                        score: int, 
                        results: Dict[str, Any],
                        metadata: Dict[str, Any]) -> None:
        """Track an evaluation in history.
        
        Args:
            doc_type: Document type
            content: Document content
            score: Evaluation score
            results: Evaluation results
            metadata: Additional metadata
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "doc_type": doc_type,
            "score": score,
            "results": results,
            "content_hash": hash(content),
            "metadata": metadata
        }
        
        self.history.append(entry)
    
    def save_history(self, file_path: Optional[Path] = None) -> bool:
        """Save evaluation history to file.
        
        Args:
            file_path: Path to save history to (if None, uses default location)
            
        Returns:
            True if successful, False otherwise
        """
        if not file_path:
            file_path = self.storage_dir / "evaluation_history.json"
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving history: {e}")
            return False
    
    def load_history(self, file_path: Optional[Path] = None) -> bool:
        """Load evaluation history from file.
        
        Args:
            file_path: Path to load history from (if None, uses default location)
            
        Returns:
            True if successful, False otherwise
        """
        if not file_path:
            file_path = self.storage_dir / "evaluation_history.json"
        
        if not os.path.exists(file_path):
            logger.warning(f"History file not found: {file_path}")
            return False
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.history = json.load(f)
            return True
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            return False


class ClosedLoopRunner:
    """Runner for closed-loop document improvement.
    
    This class implements a closed-loop system that evaluates documents,
    improves them based on evaluation results, and repeats the cycle
    to achieve continuous quality enhancement.
    """
    
    def __init__(self, 
                evaluation_engine: EvaluationEngine,
                improvers: Optional[Dict[str, Any]] = None,
                storage_dir: Optional[Path] = None,
                max_iterations: int = 3):
        """Initialize the closed-loop runner.
        
        Args:
            evaluation_engine: Evaluation engine instance
            improvers: Dictionary mapping document types to improver instances
            storage_dir: Directory for storing improvement results and history
            max_iterations: Maximum number of improvement iterations per cycle
        """
        self.evaluation_engine = evaluation_engine
        self.improvers = improvers or {}
        self.storage_dir = storage_dir or Path("improvement_results")
        self.max_iterations = max_iterations
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize improvement history
        self.history = []
    
    def register_improver(self, doc_type: str, improver: Any) -> None:
        """Register an improver for a document type.
        
        Args:
            doc_type: Document type (e.g., "readme", "wiki")
            improver: Improver instance
        """
        self.improvers[doc_type] = improver
        logger.info(f"Registered improver for {doc_type} documents")
    
    def get_improver(self, doc_type: str) -> Optional[Any]:
        """Get the improver for a document type.
        
        Args:
            doc_type: Document type
            
        Returns:
            Improver instance or None if not found
        """
        return self.improvers.get(doc_type)
    
    def run_improvement_cycle(self, 
                            content: str, 
                            doc_type: str, 
                            iterations: Optional[int] = None,
                            **kwargs) -> Tuple[str, List[Dict[str, Any]]]:
        """Run a complete improvement cycle for a document.
        
        Args:
            content: Document content
            doc_type: Document type
            iterations: Number of improvement iterations (if None, uses max_iterations)
            **kwargs: Additional arguments passed to evaluator and improver
            
        Returns:
            Tuple of (improved_content, cycle_results)
            
        Raises:
            ValueError: If no evaluator or improver is registered for the document type
        """
        iterations = iterations or self.max_iterations
        cycle_id = datetime.now().strftime("%Y%m%d%H%M%S")
        cycle_results = []
        
        # Get evaluator and improver
        evaluator = self.evaluation_engine.get_evaluator(doc_type)
        improver = self.get_improver(doc_type)
        
        if not evaluator:
            raise ValueError(f"No evaluator registered for document type: {doc_type}")
        if not improver:
            raise ValueError(f"No improver registered for document type: {doc_type}")
        
        logger.info(f"Starting improvement cycle for {doc_type} document (max {iterations} iterations)")
        
        current_content = content
        best_content = content
        best_score = 0
        
        for i in range(iterations):
            logger.info(f"Starting iteration {i+1}/{iterations}")
            
            # Evaluate current content
            score_before, eval_results = evaluator.evaluate(current_content, **kwargs)
            logger.info(f"Initial evaluation score: {score_before}")
            
            # If this is better than any previous version, save it
            if score_before > best_score:
                best_score = score_before
                best_content = current_content
            
            # Improve content
            improved_content, improve_details = improver.improve(current_content, eval_results, **kwargs)
            
            # Re-evaluate improved content
            score_after, eval_after = evaluator.evaluate(improved_content, **kwargs)
            logger.info(f"After improvement: {score_after} ({score_after - score_before:+.1f})")
            
            # Create result for this iteration
            iteration_result = {
                "cycle_id": cycle_id,
                "iteration": i + 1,
                "doc_type": doc_type,
                "score_before": score_before,
                "score_after": score_after,
                "improvement": score_after - score_before,
                "evaluation_before": eval_results,
                "evaluation_after": eval_after,
                "content_hash_before": hash(current_content),
                "content_hash_after": hash(improved_content),
                "metadata": kwargs.copy(),
                "timestamp": datetime.now().isoformat()
            }
            cycle_results.append(iteration_result)
            
            # Track in history
            self.history.append(iteration_result)
            
            # Update for next iteration
            current_content = improved_content
            
            # If this is better than any previous version, save it
            if score_after > best_score:
                best_score = score_after
                best_content = improved_content
            
            # Early stopping conditions
            if score_after <= score_before:
                logger.info(f"Stopping after iteration {i+1}: No improvement")
                break
            
            if score_after >= 95:
                logger.info(f"Stopping after iteration {i+1}: Score {score_after} >= 95")
                break
        
        # Return the best content found during the cycle
        return best_content, cycle_results
    
    def run_file_improvement_cycle(self, 
                                file_path: str, 
                                doc_type: Optional[str] = None,
                                iterations: Optional[int] = None,
                                output_file: Optional[str] = None,
                                **kwargs) -> Tuple[str, List[Dict[str, Any]]]:
        """Run a complete improvement cycle for a document file.
        
        Args:
            file_path: Path to the document file
            doc_type: Document type (if None, will be inferred)
            iterations: Number of improvement iterations
            output_file: Path to save improved content (if None, doesn't save)
            **kwargs: Additional arguments passed to evaluator and improver
            
        Returns:
            Tuple of (improved_content, cycle_results)
            
        Raises:
            ValueError: If the file doesn't exist or doc_type cannot be inferred
        """
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Infer document type if not provided
        if doc_type is None:
            doc_type = self.evaluation_engine._infer_doc_type(file_path)
        
        # Add filename to kwargs
        kwargs["filename"] = os.path.basename(file_path)
        
        # Run improvement cycle
        improved_content, cycle_results = self.run_improvement_cycle(
            content, doc_type, iterations, **kwargs
        )
        
        # Save improved content if requested
        if output_file:
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(improved_content)
                logger.info(f"Saved improved content to: {output_file}")
            except Exception as e:
                logger.error(f"Error saving improved content: {e}")
        
        return improved_content, cycle_results
    
    def save_history(self, file_path: Optional[Path] = None) -> bool:
        """Save improvement history to file.
        
        Args:
            file_path: Path to save history to (if None, uses default location)
            
        Returns:
            True if successful, False otherwise
        """
        if not file_path:
            file_path = self.storage_dir / "improvement_history.json"
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving history: {e}")
            return False
    
    def load_history(self, file_path: Optional[Path] = None) -> bool:
        """Load improvement history from file.
        
        Args:
            file_path: Path to load history from (if None, uses default location)
            
        Returns:
            True if successful, False otherwise
        """
        if not file_path:
            file_path = self.storage_dir / "improvement_history.json"
        
        if not os.path.exists(file_path):
            logger.warning(f"History file not found: {file_path}")
            return False
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.history = json.load(f)
            return True
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            return False
    
    def get_improvement_metrics(self) -> Dict[str, Any]:
        """Get metrics on improvements across all documents.
        
        Returns:
            Dictionary of improvement metrics
        """
        if not self.history:
            return {"error": "No improvement history available"}
        
        metrics = {
            "total_documents": 0,
            "total_iterations": 0,
            "average_score_improvement": 0,
            "max_score_improvement": 0,
            "successful_improvements": 0,  # Where score increased
            "neutral_improvements": 0,      # Where score stayed the same
            "negative_improvements": 0,     # Where score decreased
            "by_doc_type": {}
        }
        
        # Dictionary to track unique documents
        unique_docs = set()
        
        # Process all history entries
        total_improvement = 0
        
        for entry in self.history:
            doc_type = entry.get("doc_type", "unknown")
            content_hash = entry.get("content_hash_before", 0)
            improvement = entry.get("improvement", 0)
            
            # Track unique documents
            doc_key = f"{doc_type}:{content_hash}"
            if doc_key not in unique_docs:
                unique_docs.add(doc_key)
                metrics["total_documents"] += 1
            
            # Count iterations
            metrics["total_iterations"] += 1
            
            # Track improvement metrics
            total_improvement += improvement
            
            # Update max improvement
            if improvement > metrics["max_score_improvement"]:
                metrics["max_score_improvement"] = improvement
            
            # Categorize improvements
            if improvement > 0:
                metrics["successful_improvements"] += 1
            elif improvement == 0:
                metrics["neutral_improvements"] += 1
            else:
                metrics["negative_improvements"] += 1
            
            # Track by document type
            if doc_type not in metrics["by_doc_type"]:
                metrics["by_doc_type"][doc_type] = {
                    "total_iterations": 0,
                    "total_improvement": 0,
                    "average_improvement": 0,
                    "successful_improvements": 0
                }
            
            metrics["by_doc_type"][doc_type]["total_iterations"] += 1
            metrics["by_doc_type"][doc_type]["total_improvement"] += improvement
            
            if improvement > 0:
                metrics["by_doc_type"][doc_type]["successful_improvements"] += 1
        
        # Calculate averages
        if metrics["total_iterations"] > 0:
            metrics["average_score_improvement"] = total_improvement / metrics["total_iterations"]
        
        # Calculate averages by doc type
        for doc_type in metrics["by_doc_type"]:
            if metrics["by_doc_type"][doc_type]["total_iterations"] > 0:
                metrics["by_doc_type"][doc_type]["average_improvement"] = (
                    metrics["by_doc_type"][doc_type]["total_improvement"] / 
                    metrics["by_doc_type"][doc_type]["total_iterations"]
                )
        
        return metrics
"""Closed-Loop Runner for Document Evaluation and Improvement.

This module implements a closed-loop system for document evaluation and improvement,
integrating the evaluation and improvement components into a unified workflow.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path

import openai

from .evaluator import DocEvaluator, evaluate_document
from .improver import DocImprover, improve_document

logger = logging.getLogger(__name__)


class ImprovementCycleResult:
    """Result of a complete improvement cycle."""
    
    def __init__(
        self,
        cycle_id: str,
        iterations: List[Dict[str, Any]],
        initial_content: str,
        final_content: str,
        initial_score: int,
        final_score: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize the cycle result.
        
        Args:
            cycle_id: Unique identifier for this cycle
            iterations: Results from each iteration
            initial_content: Content at the start of the cycle
            final_content: Content at the end of the cycle
            initial_score: Score at the start of the cycle
            final_score: Score at the end of the cycle
            metadata: Additional metadata
        """
        self.cycle_id = cycle_id
        self.iterations = iterations
        self.initial_content = initial_content
        self.final_content = final_content
        self.initial_score = initial_score
        self.final_score = final_score
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        
        # Calculate metrics
        self.metrics = {
            "iterations": len(iterations),
            "initial_score": initial_score,
            "final_score": final_score,
            "total_improvement": final_score - initial_score,
            "improvement_per_iteration": (final_score - initial_score) / len(iterations) if iterations else 0,
            "initial_word_count": len(initial_content.split()),
            "final_word_count": len(final_content.split()),
            "word_count_change": len(final_content.split()) - len(initial_content.split())
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation of the cycle result
        """
        return {
            "cycle_id": self.cycle_id,
            "timestamp": self.timestamp,
            "iterations": self.iterations,
            "metrics": self.metrics,
            "metadata": self.metadata
        }
    
    def format_report(self) -> str:
        """Format the cycle result as a readable report.
        
        Returns:
            Formatted report as string
        """
        lines = [
            f"Improvement Cycle: {self.cycle_id}",
            "=" * (19 + len(self.cycle_id)),
            "",
            f"Iterations: {len(self.iterations)}",
            f"Timestamp: {self.timestamp}",
            "",
        ]
        
        # Add score improvement
        initial_score = self.initial_score
        final_score = self.final_score
        total_improvement = final_score - initial_score
        
        lines.append(f"Initial Score: {initial_score}")
        lines.append(f"Final Score: {final_score}")
        lines.append(f"Total Improvement: {total_improvement:+.1f} points")
        lines.append("")
        
        # Add iteration summary
        lines.append("Iteration Summary:")
        for i, iteration in enumerate(self.iterations):
            score_before = iteration.get("score_before", 0)
            score_after = iteration.get("score_after", 0)
            improvement = score_after - score_before
            
            lines.append(f"- Iteration {i+1}: {score_before} → {score_after} ({improvement:+.1f})")
        
        lines.append("")
        
        return "\n".join(lines)


class ClosedLoopRunner:
    """Runner for closed-loop document evaluation and improvement.
    
    This class orchestrates the process of evaluating content, improving it,
    re-evaluating the improved content, and tracking progress over multiple iterations.
    """
    
    def __init__(
        self,
        client: Optional[openai.OpenAI] = None,
        evaluator: Optional[DocEvaluator] = None,
        improver: Optional[DocImprover] = None,
        results_dir: Optional[str] = None,
        evaluation_model: str = "gpt-4",
        improvement_model: str = "gpt-4"
    ):
        """Initialize the closed-loop runner.
        
        Args:
            client: OpenAI client (if None, will create one)
            evaluator: Document evaluator (if None, will create one)
            improver: Document improver (if None, will create one)
            results_dir: Directory for storing results (if None, uses "results")
            evaluation_model: Model to use for evaluation
            improvement_model: Model to use for improvement
        """
        # Create client if not provided
        self.client = client or self._create_client()
        
        # Create evaluator and improver if not provided
        self.evaluator = evaluator or DocEvaluator(
            client=self.client,
            model=evaluation_model
        )
        self.improver = improver or DocImprover(
            client=self.client,
            model=improvement_model
        )
        
        # Set up results directory
        self.results_dir = results_dir or "results"
        os.makedirs(self.results_dir, exist_ok=True)
    
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
    
    def run_cycle(
        self,
        content: str,
        doc_type: str = "readme",
        max_iterations: int = 3,
        min_improvement: float = 1.0,
        target_score: Optional[float] = None,
        save_results: bool = True,
        **kwargs
    ) -> ImprovementCycleResult:
        """Run a complete improvement cycle.
        
        Args:
            content: Initial content
            doc_type: Type of document (readme, generic, etc.)
            max_iterations: Maximum number of improvement iterations
            min_improvement: Minimum score improvement required to continue
            target_score: Target score to achieve (stops when reached)
            save_results: Whether to save results to disk
            **kwargs: Additional arguments for evaluation and improvement
            
        Returns:
            Improvement cycle result
        """
        # Generate a unique cycle ID
        cycle_id = kwargs.get("cycle_id", f"{doc_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        logger.info(f"Starting improvement cycle {cycle_id}")
        
        # Store iteration results
        iterations = []
        
        # Track best content and score
        current_content = content
        best_content = content
        best_score = 0
        
        # Initial evaluation
        eval_result, eval_metrics = self.evaluator.evaluate(
            content, 
            doc_type=doc_type,
            **kwargs
        )
        
        # Get initial score
        initial_score = eval_result.get("total_score", 0)
        best_score = initial_score
        
        # Log initial score
        logger.info(f"Initial evaluation score: {initial_score}")
        
        # Run iterations
        for i in range(max_iterations):
            logger.info(f"Running iteration {i+1}/{max_iterations}")
            
            # The first iteration already has an evaluation
            if i == 0:
                score_before = initial_score
                current_eval = eval_result
            else:
                # Evaluate current content
                current_eval, _ = self.evaluator.evaluate(
                    current_content,
                    doc_type=doc_type,
                    **kwargs
                )
                score_before = current_eval.get("total_score", 0)
                logger.info(f"Current score: {score_before}")
            
            # Check if we've reached the target score
            if target_score is not None and score_before >= target_score:
                logger.info(f"Reached target score {target_score}, stopping")
                break
            
            # Improve current content
            improved_content, improve_details = self.improver.improve(
                current_content,
                current_eval,
                doc_type=doc_type,
                **kwargs
            )
            
            # Evaluate improved content
            improved_eval, _ = self.evaluator.evaluate(
                improved_content,
                doc_type=doc_type,
                **kwargs
            )
            
            # Get score after improvement
            score_after = improved_eval.get("total_score", 0)
            logger.info(f"Score after improvement: {score_after} (change: {score_after - score_before:+.1f})")
            
            # Store iteration result
            iteration_result = {
                "iteration": i + 1,
                "score_before": score_before,
                "score_after": score_after,
                "improvement": score_after - score_before,
                "content_before": current_content,
                "content_after": improved_content,
                "eval_before": current_eval,
                "eval_after": improved_eval,
                "improvement_details": improve_details
            }
            iterations.append(iteration_result)
            
            # Check if we've improved
            if score_after > best_score:
                best_score = score_after
                best_content = improved_content
            
            # Check if we've reached the target score
            if target_score is not None and score_after >= target_score:
                logger.info(f"Reached target score {target_score}, stopping")
                break
            
            # Check if we've made enough improvement to continue
            if score_after - score_before < min_improvement:
                logger.info(f"Improvement ({score_after - score_before:+.1f}) below minimum threshold ({min_improvement}), stopping")
                break
            
            # Update current content for next iteration
            current_content = improved_content
        
        # Create cycle result
        cycle_result = ImprovementCycleResult(
            cycle_id=cycle_id,
            iterations=iterations,
            initial_content=content,
            final_content=best_content,
            initial_score=initial_score,
            final_score=best_score,
            metadata=kwargs
        )
        
        # Save results if requested
        if save_results:
            self._save_cycle_results(cycle_result, doc_type)
        
        return cycle_result
    
    def _save_cycle_results(self, cycle_result: ImprovementCycleResult, doc_type: str) -> None:
        """Save cycle results to disk.
        
        Args:
            cycle_result: Cycle result to save
            doc_type: Type of document
        """
        # Create directory for this cycle
        cycle_dir = os.path.join(self.results_dir, doc_type, cycle_result.cycle_id)
        os.makedirs(cycle_dir, exist_ok=True)
        
        # Save cycle report
        report_path = os.path.join(cycle_dir, "report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(cycle_result.format_report())
        
        # Save cycle data as JSON
        data_path = os.path.join(cycle_dir, "data.json")
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(cycle_result.to_dict(), f, indent=2, default=str)
        
        # Save original and final content
        original_path = os.path.join(cycle_dir, "original.md")
        with open(original_path, "w", encoding="utf-8") as f:
            f.write(cycle_result.initial_content)
        
        final_path = os.path.join(cycle_dir, "final.md")
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(cycle_result.final_content)
        
        # Save each iteration
        for i, iteration in enumerate(cycle_result.iterations):
            iter_dir = os.path.join(cycle_dir, f"iteration_{i+1}")
            os.makedirs(iter_dir, exist_ok=True)
            
            # Save before and after content
            with open(os.path.join(iter_dir, "before.md"), "w", encoding="utf-8") as f:
                f.write(iteration["content_before"])
            
            with open(os.path.join(iter_dir, "after.md"), "w", encoding="utf-8") as f:
                f.write(iteration["content_after"])
            
            # Save evaluation results
            with open(os.path.join(iter_dir, "eval_before.json"), "w", encoding="utf-8") as f:
                json.dump(iteration["eval_before"], f, indent=2)
            
            with open(os.path.join(iter_dir, "eval_after.json"), "w", encoding="utf-8") as f:
                json.dump(iteration["eval_after"], f, indent=2)
            
            # Save improvement details
            with open(os.path.join(iter_dir, "improvement_details.json"), "w", encoding="utf-8") as f:
                json.dump(iteration["improvement_details"], f, indent=2, default=str)


def run_improvement_cycle(
    content: str,
    doc_type: str = "readme",
    max_iterations: int = 3,
    min_improvement: float = 1.0,
    target_score: Optional[float] = None,
    client: Optional[openai.OpenAI] = None,
    evaluation_model: str = "gpt-4",
    improvement_model: str = "gpt-4",
    **kwargs
) -> Tuple[str, Dict[str, Any]]:
    """Run a complete improvement cycle.
    
    Args:
        content: Initial content to improve
        doc_type: Type of document (readme, generic, etc.)
        max_iterations: Maximum number of improvement iterations
        min_improvement: Minimum score improvement required to continue
        target_score: Target score to achieve (stops when reached)
        client: OpenAI client (if None, will create one)
        evaluation_model: Model to use for evaluation
        improvement_model: Model to use for improvement
        **kwargs: Additional arguments for evaluation and improvement
        
    Returns:
        Tuple of (improved_content, cycle_result.to_dict())
    """
    runner = ClosedLoopRunner(
        client=client,
        evaluation_model=evaluation_model,
        improvement_model=improvement_model
    )
    
    cycle_result = runner.run_cycle(
        content,
        doc_type=doc_type,
        max_iterations=max_iterations,
        min_improvement=min_improvement,
        target_score=target_score,
        **kwargs
    )
    
    return cycle_result.final_content, cycle_result.to_dict()
"""Closed-loop evaluation and improvement runner.

This module implements a runner for closed-loop document evaluation and improvement,
orchestrating the process of evaluating content, improving it, and tracking progress.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, TypeVar, Generic, Callable

import numpy as np
import openai

from .evals.base import BaseEvaluator, EvalSpec, CompletionFn, SampleResult
from .registry import get_registry, Registry
from .storage.history import EvaluationHistory

logger = logging.getLogger(__name__)


class ImprovementResult:
    """Result of an improvement operation."""

    def __init__(
        self,
        original_content: str,
        improved_content: str,
        improvement_details: Dict[str, Any],
        eval_before: Optional[Dict[str, Any]] = None,
        eval_after: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the improvement result.

        Args:
            original_content: Original content before improvement
            improved_content: Content after improvement
            improvement_details: Details of improvements made
            eval_before: Evaluation results before improvement
            eval_after: Evaluation results after improvement
        """
        self.original_content = original_content
        self.improved_content = improved_content
        self.improvement_details = improvement_details
        self.eval_before = eval_before
        self.eval_after = eval_after

        # Calculate improvement metrics
        self.metrics = self._calculate_metrics()

    def _calculate_metrics(self) -> Dict[str, float]:
        """Calculate improvement metrics.

        Returns:
            Dictionary of metric names to values
        """
        metrics = {}

        # Calculate score improvement if evaluations are available
        if self.eval_before and self.eval_after:
            score_before = self.eval_before.get("total_score", 0)
            score_after = self.eval_after.get("total_score", 0)

            metrics["score_before"] = float(score_before)
            metrics["score_after"] = float(score_after)
            metrics["score_improvement"] = float(score_after - score_before)
            metrics["score_improvement_percent"] = (
                float(score_after - score_before) / float(score_before) * 100
                if score_before > 0 else 0.0
            )

        # Calculate content change metrics
        original_words = len(self.original_content.split())
        improved_words = len(self.improved_content.split())

        metrics["original_word_count"] = original_words
        metrics["improved_word_count"] = improved_words
        metrics["word_count_change"] = improved_words - original_words
        metrics["word_count_change_percent"] = (
            (improved_words - original_words) / original_words * 100
            if original_words > 0 else 0.0
        )

        return metrics

    def format_report(self) -> str:
        """Format the improvement result as a readable report.

        Returns:
            Formatted report as string
        """
        lines = [
            "Improvement Report",
            "=================",
            "",
        ]

        # Add score improvement
        if "score_before" in self.metrics and "score_after" in self.metrics:
            score_before = self.metrics["score_before"]
            score_after = self.metrics["score_after"]
            score_improvement = self.metrics["score_improvement"]

            lines.append(f"Score Before: {score_before}")
            lines.append(f"Score After: {score_after}")
            lines.append(f"Improvement: {score_improvement:+.1f} points")
            lines.append("")

        # Add content change metrics
        original_words = self.metrics["original_word_count"]
        improved_words = self.metrics["improved_word_count"]
        word_change = self.metrics["word_count_change"]

        lines.append("Content Changes:")
        lines.append(f"- Original word count: {original_words}")
        lines.append(f"- Improved word count: {improved_words}")
        if word_change > 0:
            lines.append(f"- Added {word_change} words")
        elif word_change < 0:
            lines.append(f"- Removed {abs(word_change)} words")
        lines.append("")

        # Add improvement details
        if "top_improvements" in self.improvement_details:
            lines.append("Top Improvements:")
            for improvement in self.improvement_details["top_improvements"]:
                lines.append(f"- {improvement}")
            lines.append("")

        # Add category improvements if available
        if (self.eval_before and self.eval_after and
            "category_scores" in self.eval_before and
            "category_scores" in self.eval_after):

            categories_before = self.eval_before["category_scores"]
            categories_after = self.eval_after["category_scores"]

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


class CycleResult:
    """Result of a complete improvement cycle."""

    def __init__(
        self,
        cycle_id: str,
        iteration_results: List[ImprovementResult],
        initial_content: str,
        final_content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the cycle result.

        Args:
            cycle_id: Unique identifier for this cycle
            iteration_results: Results from each iteration
            initial_content: Content at the start of the cycle
            final_content: Content at the end of the cycle
            metadata: Additional metadata
        """
        self.cycle_id = cycle_id
        self.iteration_results = iteration_results
        self.initial_content = initial_content
        self.final_content = final_content
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

        # Calculate cycle metrics
        self.metrics = self._calculate_metrics()

    def _calculate_metrics(self) -> Dict[str, float]:
        """Calculate cycle metrics.

        Returns:
            Dictionary of metric names to values
        """
        metrics = {
            "iterations": len(self.iteration_results)
        }

        # Calculate total score improvement
        if (self.iteration_results and
            self.iteration_results[0].eval_before and
            self.iteration_results[-1].eval_after):

            score_before = self.iteration_results[0].eval_before.get("total_score", 0)
            score_after = self.iteration_results[-1].eval_after.get("total_score", 0)

            metrics["initial_score"] = float(score_before)
            metrics["final_score"] = float(score_after)
            metrics["total_improvement"] = float(score_after - score_before)
            metrics["improvement_per_iteration"] = (
                float(score_after - score_before) / len(self.iteration_results)
                if len(self.iteration_results) > 0 else 0.0
            )

        # Calculate content change metrics
        initial_words = len(self.initial_content.split())
        final_words = len(self.final_content.split())

        metrics["initial_word_count"] = initial_words
        metrics["final_word_count"] = final_words
        metrics["word_count_change"] = final_words - initial_words

        return metrics

    def format_report(self) -> str:
        """Format the cycle result as a readable report.

        Returns:
            Formatted report as string
        """
        lines = [
            f"Improvement Cycle: {self.cycle_id}",
            "=" * (19 + len(self.cycle_id)),
            "",
            f"Iterations: {len(self.iteration_results)}",
            f"Timestamp: {self.timestamp}",
            "",
        ]

        # Add score improvement
        if "initial_score" in self.metrics and "final_score" in self.metrics:
            initial_score = self.metrics["initial_score"]
            final_score = self.metrics["final_score"]
            total_improvement = self.metrics["total_improvement"]

            lines.append(f"Initial Score: {initial_score}")
            lines.append(f"Final Score: {final_score}")
            lines.append(f"Total Improvement: {total_improvement:+.1f} points")
            lines.append("")

        # Add iteration summary
        lines.append("Iteration Summary:")
        for i, result in enumerate(self.iteration_results):
            metrics = result.metrics
            if "score_before" in metrics and "score_after" in metrics:
                score_before = metrics["score_before"]
                score_after = metrics["score_after"]
                score_improvement = metrics["score_improvement"]

                lines.append(f"- Iteration {i+1}: {score_before} → {score_after} ({score_improvement:+.1f})")

        lines.append("")

        return "\n".join(lines)


class Improver:
    """Document improver using an LLM.

    This class implements a document improver that uses an LLM to generate
    improved content based on evaluation results.
    """

    def __init__(
        self,
        completion_fn: CompletionFn,
        prompt_template: str,
        improver_id: str = "default",
    ):
        """Initialize the improver.

        Args:
            completion_fn: Function to get completions from a model
            prompt_template: Template for the improvement prompt
            improver_id: Identifier for this improver
        """
        self.completion_fn = completion_fn
        self.prompt_template = prompt_template
        self.improver_id = improver_id

    def improve(
        self,
        content: str,
        evaluation_result: Dict[str, Any],
        **kwargs
    ) -> Tuple[str, Dict[str, Any]]:
        """Improve content based on evaluation results.

        Args:
            content: Content to improve
            evaluation_result: Results from evaluation
            **kwargs: Additional variables to substitute in the prompt

        Returns:
            Tuple of (improved_content, improvement_details)
        """
        # Prepare the improvement prompt
        prompt = self._prepare_prompt(content, evaluation_result, **kwargs)

        # Call the model for improvement
        try:
            raw_response = self.completion_fn(prompt)

            # Clean up the improved content
            improved_content = self._clean_improved_content(raw_response)

            # Generate improvement details
            details = self._generate_improvement_details(content, improved_content, evaluation_result)

            return improved_content, details

        except Exception as e:
            logger.error(f"Error improving content: {e}")
            return content, {"error": str(e)}

    def _prepare_prompt(
        self,
        content: str,
        evaluation_result: Dict[str, Any],
        **kwargs
    ) -> str:
        """Prepare the improvement prompt.

        Args:
            content: Content to improve
            evaluation_result: Results from evaluation
            **kwargs: Additional variables to substitute in the prompt

        Returns:
            Prepared prompt
        """
        # Format evaluation results as text
        eval_text = json.dumps(evaluation_result, indent=2)

        # Determine focus areas based on lowest scoring categories
        focus_areas = self._determine_focus_areas(evaluation_result)

        # Replace placeholders in prompt template
        prompt = self.prompt_template.replace("{content}", content)
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
            evaluation_result: Results from evaluation

        Returns:
            String of focus areas
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
        content = raw_content.replace("```markdown", "").replace("```md", "")

        # Handle ```content``` blocks
        if content.startswith("```") and content.endswith("```"):
            content = content[3:-3].strip()

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
            evaluation_result: Results from evaluation

        Returns:
            Dictionary of improvement details
        """
        import difflib

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

        return {
            "diff": "\n".join(diff),
            "original_length": len(original_content),
            "improved_length": len(improved_content),
            "top_improvements": top_improvements,
            "improver_id": self.improver_id,
            "timestamp": datetime.now().isoformat()
        }


class ClosedLoopRunner:
    """Runner for closed-loop document evaluation and improvement.

    This class orchestrates the process of evaluating content, improving it,
    re-evaluating the improved content, and tracking progress over multiple iterations.
    """

    def __init__(
        self,
        registry: Optional[Registry] = None,
        history: Optional[EvaluationHistory] = None,
        results_dir: Optional[Path] = None,
    ):
        """Initialize the closed-loop runner.

        Args:
            registry: Registry for evaluations and improvers
            history: History tracker for evaluations and improvements
            results_dir: Directory for storing results
        """
        self.registry = registry or get_registry()
        self.history = history or EvaluationHistory()
        self.results_dir = results_dir or Path("results")
        os.makedirs(self.results_dir, exist_ok=True)

        # Map of evaluators and improvers
        self.evaluators: Dict[str, BaseEvaluator] = {}
        self.improvers: Dict[str, Improver] = {}

        # Default improvement prompts by document type
        self.default_prompts = {
            "readme": self._get_default_readme_prompt(),
            "generic": self._get_default_generic_prompt()
        }

    def register_evaluator(
        self,
        doc_type: str,
        evaluator: BaseEvaluator
    ) -> None:
        """Register an evaluator for a document type.

        Args:
            doc_type: Document type
            evaluator: Evaluator instance
        """
        self.evaluators[doc_type] = evaluator
        logger.info(f"Registered evaluator for {doc_type} documents")

    def register_improver(
        self,
        doc_type: str,
        improver: Improver
    ) -> None:
        """Register an improver for a document type.

        Args:
            doc_type: Document type
            improver: Improver instance
        """
        self.improvers[doc_type] = improver
        logger.info(f"Registered improver for {doc_type} documents")

    def create_default_improver(
        self,
        doc_type: str,
        completion_fn: CompletionFn
    ) -> Improver:
        """Create a default improver for a document type.

        Args:
            doc_type: Document type
            completion_fn: Function to get completions from a model

        Returns:
            Improver instance
        """
        # Get the default prompt template for this document type
        prompt_template = self.default_prompts.get(doc_type, self.default_prompts["generic"])

        # Create and register the improver
        improver = Improver(completion_fn, prompt_template, f"{doc_type}_improver")
        self.register_improver(doc_type, improver)

        return improver

    def evaluate(
        self,
        content: str,
        doc_type: str,
        **kwargs
    ) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Evaluate content using the appropriate evaluator.

        Args:
            content: Content to evaluate
            doc_type: Document type
            **kwargs: Additional arguments passed to the evaluator

        Returns:
            Tuple of (evaluation_result, metrics)

        Raises:
            ValueError: If no evaluator is registered for the document type
        """
        if doc_type not in self.evaluators:
            raise ValueError(f"No evaluator registered for document type: {doc_type}")

        evaluator = self.evaluators[doc_type]

        # Create a sample with the content
        sample_id = kwargs.get("sample_id", f"{doc_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        filename = kwargs.get("filename", f"{doc_type}.md")

        sample = {
            "id": sample_id,
            "content": content,
            "filename": filename,
            "metadata": kwargs
        }

        # Evaluate the sample
        sample_result = evaluator.eval_sample(sample)

        # Return the evaluation result and metrics
        return sample_result.result, sample_result.metrics

    def improve(
        self,
        content: str,
        evaluation_result: Dict[str, Any],
        doc_type: str,
        **kwargs
    ) -> ImprovementResult:
        """Improve content based on evaluation results.

        Args:
            content: Content to improve
            evaluation_result: Results from evaluation
            doc_type: Document type
            **kwargs: Additional arguments passed to the improver

        Returns:
            Improvement result

        Raises:
            ValueError: If no improver is registered for the document type
        """
        if doc_type not in self.improvers:
            raise ValueError(f"No improver registered for document type: {doc_type}")

        improver = self.improvers[doc_type]

        # Improve the content
        improved_content, details = improver.improve(content, evaluation_result, **kwargs)

        # Create improvement result (without eval_after yet)
        result = ImprovementResult(
            original_content=content,
            improved_content=improved_content,
            improvement_details=details,
            eval_before=evaluation_result
        )

        # Track the improvement in history if requested
        if kwargs.get("track_history", True):
            doc_id = kwargs.get("doc_id", f"{doc_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}")

            self.history.add_improvement(
                doc_type=doc_type,
                doc_id=doc_id,
                score_before=evaluation_result.get("total_score", 0),
                score_after=0,  # Will be updated after re-evaluation
                content_before_hash=hash(content),
                content_after_hash
=hash(improved_content),
                details=details,
                metadata=kwargs
            )
        
        return result
    
    def run_cycle(
        self,
        content: str,
        doc_type: str,
        max_iterations: int = 3,
        min_improvement: float = 0.0,
        target_score: Optional[float] = None,
        **kwargs
    ) -> CycleResult:
        """Run a complete improvement cycle.
        
        Args:
            content: Initial content
            doc_type: Document type
            max_iterations: Maximum number of improvement iterations
            min_improvement: Minimum score improvement required to continue
            target_score: Target score to achieve (stops when reached)
            **kwargs: Additional arguments passed to evaluator and improver
            
        Returns:
            Cycle result
        """
        cycle_id = kwargs.get("cycle_id", f"{doc_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        logger.info(f"Starting improvement cycle {cycle_id}")
        
        iteration_results = []
        current_content = content
        best_content = content
        best_score = 0
        
        for i in range(max_iterations):
            logger.info(f"Iteration {i+1}/{max_iterations}")
            
            # Evaluate current content
            eval_result, eval_metrics = self.evaluate(
                current_content,
                doc_type,
                iteration=i,
                cycle_id=cycle_id,
                **kwargs
            )
            
            current_score = eval_result.get("total_score", 0)
            logger.info(f"Current score: {current_score}")
            
            # Track the best content so far
            if current_score > best_score:
                best_score = current_score
                best_content = current_content
            
            # Check if we've reached the target score
            if target_score is not None and current_score >= target_score:
                logger.info(f"Reached target score {target_score}, stopping")
                break
            
            # Improve content
            improvement_result = self.improve(
                current_content,
                eval_result,
                doc_type,
                iteration=i,
                cycle_id=cycle_id,
                **kwargs
            )
            
            # Evaluate improved content
            improved_content = improvement_result.improved_content
            eval_after, metrics_after = self.evaluate(
                improved_content,
                doc_type,
                iteration=i,
                cycle_id=cycle_id,
                **kwargs
            )
            
            # Update improvement result with evaluation after
            improvement_result.eval_after = eval_after
            
            # Calculate improvement
            score_after = eval_after.get("total_score", 0)
            improvement = score_after - current_score
            logger.info(f"New score: {score_after} (improvement: {improvement:+.1f})")
            
            # Track the iteration result
            iteration_results.append(improvement_result)
            
            # Update the improvement in history if requested
            if kwargs.get("track_history", True):
                doc_id = kwargs.get("doc_id", f"{doc_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
                
                # Update the last improvement with the new score
                for imp in reversed(self.history.improvements):
                    if (imp.get("doc_type") == doc_type and 
                        imp.get("doc_id") == doc_id and
                        imp.get("score_after") == 0):
                        imp["score_after"] = score_after
                        imp["improvement"] = score_after - current_score
                        break
            
            # Track the best content so far
            if score_after > best_score:
                best_score = score_after
                best_content = improved_content
            
            # Check if we've reached the target score
            if target_score is not None and score_after >= target_score:
                logger.info(f"Reached target score {target_score}, stopping")
                break
            
            # Check if we've made enough improvement to continue
            if improvement <= min_improvement:
                logger.info(f"Improvement ({improvement}) below threshold ({min_improvement}), stopping")
                break
            
            # Update current content for next iteration
            current_content = improved_content
        
        # Create cycle result
        cycle_result = CycleResult(
            cycle_id=cycle_id,
            iteration_results=iteration_results,
            initial_content=content,
            final_content=best_content,
            metadata=kwargs
        )
        
        # Track the cycle in history if requested
        if kwargs.get("track_history", True):
            doc_id = kwargs.get("doc_id", f"{doc_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
            
            iterations_data = []
            for i, result in enumerate(iteration_results):
                iterations_data.append({
                    "iteration": i + 1,
                    "score_before": result.metrics.get("score_before", 0),
                    "score_after": result.metrics.get("score_after", 0),
                    "improvement": result.metrics.get("score_improvement", 0)
                })
            
            initial_score = (iteration_results[0].metrics.get("score_before", 0) 
                            if iteration_results else 0)
            final_score = best_score
            
            self.history.add_cycle(
                doc_type=doc_type,
                doc_id=doc_id,
                iterations=iterations_data,
                initial_score=initial_score,
                final_score=final_score,
                metadata=kwargs
            )
        
        # Save results if requested
        if kwargs.get("save_results", True):
            self._save_cycle_results(cycle_result, doc_type)
        
        return cycle_result
    
    def _save_cycle_results(self, cycle_result: CycleResult, doc_type: str) -> None:
        """Save cycle results to disk.
        
        Args:
            cycle_result: Cycle result
            doc_type: Document type
        """
        cycle_dir = self.results_dir / doc_type / cycle_result.cycle_id
        os.makedirs(cycle_dir, exist_ok=True)
        
        # Save cycle report
        report_path = cycle_dir / "report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(cycle_result.format_report())
        
        # Save original and final content
        original_path = cycle_dir / "original.md"
        with open(original_path, "w", encoding="utf-8") as f:
            f.write(cycle_result.initial_content)
        
        final_path = cycle_dir / "final.md"
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(cycle_result.final_content)
        
        # Save iteration results
        for i, result in enumerate(cycle_result.iteration_results):
            iter_dir = cycle_dir / f"iteration_{i+1}"
            os.makedirs(iter_dir, exist_ok=True)
            
            # Save iteration report
            iter_report_path = iter_dir / "report.md"
            with open(iter_report_path, "w", encoding="utf-8") as f:
                f.write(result.format_report())
            
            # Save before and after content
            before_path = iter_dir / "before.md"
            with open(before_path, "w", encoding="utf-8") as f:
                f.write(result.original_content)
            
            after_path = iter_dir / "after.md"
            with open(after_path, "w", encoding="utf-8") as f:
                f.write(result.improved_content)
            
            # Save evaluation results
            if result.eval_before:
                eval_before_path = iter_dir / "eval_before.json"
                with open(eval_before_path, "w", encoding="utf-8") as f:
                    json.dump(result.eval_before, f, indent=2)
            
            if result.eval_after:
                eval_after_path = iter_dir / "eval_after.json"
                with open(eval_after_path, "w", encoding="utf-8") as f:
                    json.dump(result.eval_after, f, indent=2)
    
    def _get_default_readme_prompt(self) -> str:
        """Get the default prompt template for README improvement.
        
        Returns:
            Prompt template
        """
        return """You are an expert technical writer specializing in README files for software projects.
Your task is to improve the provided README based on the evaluation feedback.

CURRENT README:
```
{content}
```

EVALUATION RESULTS:
{evaluation_result}

AREAS TO FOCUS ON:
{focus_areas}

INSTRUCTIONS:
1. Keep the project's intended audience and purpose in mind.
2. Maintain the existing structure unless reorganization would significantly improve clarity.
3. Preserve any existing links, code snippets, and technical information.
4. Address all the issues mentioned in the evaluation, especially in the focus areas.
5. Keep a similar tone but improve clarity and conciseness.
6. Do not invent
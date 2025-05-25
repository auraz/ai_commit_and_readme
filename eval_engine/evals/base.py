"""Base Evaluator Class for Documentation Evaluation.

This module defines the base evaluator interface following the OpenAI Evals pattern.
All document evaluators must implement this interface to be compatible with the framework.
"""

import logging
import json
import os
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, TypeVar, Generic

import numpy as np

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Type for input samples
U = TypeVar('U')  # Type for model outputs
V = TypeVar('V')  # Type for eval results


class CompletionFn:
    """Function for getting completions from models."""
    
    def __init__(self, client, model: str, temperature: float = 0.0):
        """Initialize the completion function.
        
        Args:
            client: The client used to call the model (e.g., OpenAI client)
            model: Model identifier to use
            temperature: Temperature parameter for generation
        """
        self.client = client
        self.model = model
        self.temperature = temperature
    
    def __call__(self, prompt: str, **kwargs) -> str:
        """Call the model with the given prompt.
        
        Args:
            prompt: The prompt to send to the model
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            Model response as string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling model: {e}")
            return ""


class EvalSpec:
    """Specification for an evaluation."""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        prompt_template: str,
        metrics: List[str],
    ):
        """Initialize the evaluation specification.
        
        Args:
            id: Unique identifier for this evaluation
            name: Human-readable name
            description: Detailed description of what's being evaluated
            prompt_template: Template for the eval prompt
            metrics: List of metrics this evaluator produces
        """
        self.id = id
        self.name = name
        self.description = description
        self.prompt_template = prompt_template
        self.metrics = metrics


class SampleResult(Generic[V]):
    """Result of evaluating a single sample."""
    
    def __init__(
        self,
        spec: EvalSpec,
        sample_id: str,
        result: V,
        metrics: Dict[str, float],
    ):
        """Initialize the sample result.
        
        Args:
            spec: The evaluation specification
            sample_id: Identifier for the sample
            result: Raw evaluation result
            metrics: Metrics computed from the result
        """
        self.spec = spec
        self.sample_id = sample_id
        self.result = result
        self.metrics = metrics


class BaseEvaluator(Generic[T, U, V], ABC):
    """Base class for all document evaluators.
    
    This abstract base class defines the interface for document evaluators
    following the OpenAI Evals pattern.
    """
    
    def __init__(
        self,
        spec: EvalSpec,
        completion_fn: Optional[CompletionFn] = None,
        registry_path: Optional[Path] = None,
        cache_results: bool = True,
    ):
        """Initialize the evaluator.
        
        Args:
            spec: The evaluation specification
            completion_fn: Function to get completions from a model
            registry_path: Path to the registry directory
            cache_results: Whether to cache evaluation results
        """
        self.spec = spec
        self.completion_fn = completion_fn
        self.registry_path = registry_path
        self.cache_results = cache_results
        self.results_cache = {}
    
    @abstractmethod
    def eval_sample(self, sample: T, model_output: Optional[U] = None) -> SampleResult[V]:
        """Evaluate a single sample.
        
        Args:
            sample: The sample to evaluate
            model_output: Optional pre-generated model output for this sample
            
        Returns:
            Evaluation result for this sample
        """
        pass
    
    def eval_sample_batch(self, samples: List[T], model_outputs: Optional[List[U]] = None) -> List[SampleResult[V]]:
        """Evaluate a batch of samples.
        
        Args:
            samples: List of samples to evaluate
            model_outputs: Optional list of pre-generated model outputs
            
        Returns:
            List of evaluation results
        """
        results = []
        
        if model_outputs is None:
            model_outputs = [None] * len(samples)
        
        for sample, model_output in zip(samples, model_outputs):
            results.append(self.eval_sample(sample, model_output))
        
        return results
    
    def compute_metrics(self, results: List[SampleResult[V]]) -> Dict[str, float]:
        """Compute aggregate metrics from a list of results.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Dictionary of metric names to values
        """
        metrics = {}
        
        # Aggregate metrics across all results
        for metric in self.spec.metrics:
            values = [r.metrics.get(metric, 0.0) for r in results if metric in r.metrics]
            if values:
                metrics[metric] = float(np.mean(values))
                metrics[f"{metric}_std"] = float(np.std(values))
                metrics[f"{metric}_min"] = float(np.min(values))
                metrics[f"{metric}_max"] = float(np.max(values))
                metrics[f"{metric}_count"] = len(values)
        
        return metrics
    
    def load_prompt_template(self) -> str:
        """Load the prompt template from the registry.
        
        Returns:
            Prompt template as string
        """
        # If spec has a prompt template, use it
        if self.spec.prompt_template:
            return self.spec.prompt_template
        
        # Otherwise try to load from file
        if self.registry_path:
            template_path = self.registry_path / "prompts" / f"{self.spec.id}.md"
            if template_path.exists():
                with open(template_path, "r", encoding="utf-8") as f:
                    return f.read()
        
        # Fall back to default
        logger.warning(f"No prompt template found for {self.spec.id}")
        return "{content}"
    
    def prepare_prompt(self, content: str, **kwargs) -> str:
        """Prepare a prompt for evaluation.
        
        Args:
            content: The document content to evaluate
            **kwargs: Additional variables to substitute in the prompt
            
        Returns:
            The prepared prompt
        """
        template = self.load_prompt_template()
        
        # Replace content placeholder
        prompt = template.replace("{content}", content)
        
        # Replace any other placeholders
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))
        
        return prompt
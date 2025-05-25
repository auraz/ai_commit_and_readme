"""Registry for evaluations.

This module implements a registry for evaluations, allowing evaluations to be
registered, discovered, and loaded from a central location.
"""

import os
import json
import logging
import importlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Type, Union

from ..evals.base import BaseEvaluator, EvalSpec, CompletionFn

logger = logging.getLogger(__name__)


class Registry:
    """Registry for evaluations.
    
    The registry maintains a collection of evaluation specifications and
    completion functions, allowing them to be looked up by name.
    """
    
    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize the registry.
        
        Args:
            registry_path: Path to the registry directory
        """
        self.registry_path = registry_path or Path(__file__).parent
        
        # Create registry directories if they don't exist
        self.prompts_path = self.registry_path / "prompts"
        self.specs_path = self.registry_path / "specs"
        self.results_path = self.registry_path / "results"
        
        os.makedirs(self.prompts_path, exist_ok=True)
        os.makedirs(self.specs_path, exist_ok=True)
        os.makedirs(self.results_path, exist_ok=True)
        
        # Initialize registries
        self.evaluators: Dict[str, Type[BaseEvaluator]] = {}
        self.completion_fns: Dict[str, CompletionFn] = {}
        self.specs: Dict[str, EvalSpec] = {}
        
        # Load specs from disk
        self._load_specs()
    
    def _load_specs(self):
        """Load all evaluation specifications from disk."""
        if not self.specs_path.exists():
            return
        
        for spec_file in self.specs_path.glob("*.json"):
            try:
                with open(spec_file, "r", encoding="utf-8") as f:
                    spec_data = json.load(f)
                
                spec = EvalSpec(
                    id=spec_data.get("id", spec_file.stem),
                    name=spec_data.get("name", spec_file.stem),
                    description=spec_data.get("description", ""),
                    prompt_template=spec_data.get("prompt_template", ""),
                    metrics=spec_data.get("metrics", []),
                )
                
                self.specs[spec.id] = spec
                logger.debug(f"Loaded evaluation spec: {spec.id}")
                
            except Exception as e:
                logger.error(f"Error loading spec from {spec_file}: {e}")
    
    def register_evaluator(self, 
                          evaluator_id: str, 
                          evaluator_cls: Type[BaseEvaluator]):
        """Register an evaluator class.
        
        Args:
            evaluator_id: ID for the evaluator
            evaluator_cls: Evaluator class
        """
        self.evaluators[evaluator_id] = evaluator_cls
        logger.info(f"Registered evaluator: {evaluator_id}")
    
    def register_completion_fn(self, 
                             name: str, 
                             completion_fn: CompletionFn):
        """Register a completion function.
        
        Args:
            name: Name for the completion function
            completion_fn: Completion function
        """
        self.completion_fns[name] = completion_fn
        logger.info(f"Registered completion function: {name}")
    
    def register_eval_spec(self, spec: EvalSpec, save: bool = True):
        """Register an evaluation specification.
        
        Args:
            spec: Evaluation specification
            save: Whether to save the spec to disk
        """
        self.specs[spec.id] = spec
        logger.info(f"Registered evaluation spec: {spec.id}")
        
        if save:
            self._save_spec(spec)
    
    def _save_spec(self, spec: EvalSpec):
        """Save an evaluation specification to disk.
        
        Args:
            spec: Evaluation specification
        """
        spec_path = self.specs_path / f"{spec.id}.json"
        
        try:
            spec_data = {
                "id": spec.id,
                "name": spec.name,
                "description": spec.description,
                "metrics": spec.metrics,
            }
            
            with open(spec_path, "w", encoding="utf-8") as f:
                json.dump(spec_data, f, indent=2)
            
            # Save prompt template separately if non-empty
            if spec.prompt_template:
                prompt_path = self.prompts_path / f"{spec.id}.md"
                with open(prompt_path, "w", encoding="utf-8") as f:
                    f.write(spec.prompt_template)
            
            logger.debug(f"Saved evaluation spec: {spec.id}")
            
        except Exception as e:
            logger.error(f"Error saving spec {spec.id}: {e}")
    
    def get_evaluator(self, 
                     evaluator_id: str, 
                     spec_id: str, 
                     completion_fn_name: Optional[str] = None) -> BaseEvaluator:
        """Get an instance of an evaluator.
        
        Args:
            evaluator_id: ID for the evaluator
            spec_id: ID for the evaluation specification
            completion_fn_name: Name of the completion function to use
            
        Returns:
            Evaluator instance
            
        Raises:
            ValueError: If the evaluator, spec, or completion function is not found
        """
        if evaluator_id not in self.evaluators:
            raise ValueError(f"Evaluator not found: {evaluator_id}")
        
        if spec_id not in self.specs:
            raise ValueError(f"Evaluation spec not found: {spec_id}")
        
        evaluator_cls = self.evaluators[evaluator_id]
        spec = self.specs[spec_id]
        
        # Get completion function if specified
        completion_fn = None
        if completion_fn_name:
            if completion_fn_name not in self.completion_fns:
                raise ValueError(f"Completion function not found: {completion_fn_name}")
            completion_fn = self.completion_fns[completion_fn_name]
        
        return evaluator_cls(
            spec=spec,
            completion_fn=completion_fn,
            registry_path=self.registry_path,
        )
    
    def get_eval_spec(self, spec_id: str) -> Optional[EvalSpec]:
        """Get an evaluation specification.
        
        Args:
            spec_id: ID for the evaluation specification
            
        Returns:
            Evaluation specification or None if not found
        """
        return self.specs.get(spec_id)
    
    def list_evaluators(self) -> List[str]:
        """List all registered evaluators.
        
        Returns:
            List of evaluator IDs
        """
        return list(self.evaluators.keys())
    
    def list_specs(self) -> List[str]:
        """List all registered evaluation specifications.
        
        Returns:
            List of specification IDs
        """
        return list(self.specs.keys())
    
    def list_completion_fns(self) -> List[str]:
        """List all registered completion functions.
        
        Returns:
            List of completion function names
        """
        return list(self.completion_fns.keys())


# Global registry instance
default_registry = Registry()


def get_registry() -> Registry:
    """Get the default registry.
    
    Returns:
        Default registry instance
    """
    return default_registry
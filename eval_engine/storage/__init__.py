"""Storage module for the evaluation engine.

This module provides storage capabilities for tracking evaluation and improvement history,
making it possible to analyze trends and improvements over time.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import json
import os
import logging

logger = logging.getLogger(__name__)


class EvaluationHistory:
    """Store and retrieve evaluation and improvement history.
    
    This class provides a unified interface for tracking the history of document
    evaluations and improvements, making it possible to analyze trends over time.
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize the evaluation history.
        
        Args:
            storage_dir: Directory for storing history files (if None, uses default)
        """
        self.storage_dir = storage_dir or Path("eval_engine/storage/history")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize history dictionaries
        self.evaluations = []  # List of all evaluation entries
        self.improvements = []  # List of all improvement entries
        
    def add_evaluation(self, 
                      doc_type: str,
                      doc_id: str, 
                      score: int, 
                      results: Dict[str, Any],
                      metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add an evaluation entry to history.
        
        Args:
            doc_type: Document type (e.g., "readme", "wiki")
            doc_id: Document identifier (filename, hash, etc.)
            score: Evaluation score
            results: Evaluation results
            metadata: Additional metadata
        """
        import datetime
        
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "doc_type": doc_type,
            "doc_id": doc_id,
            "score": score,
            "results": results,
            "metadata": metadata or {}
        }
        
        self.evaluations.append(entry)
    
    def add_improvement(self,
                       doc_type: str,
                       doc_id: str,
                       score_before: int,
                       score_after: int,
                       details: Dict[str, Any],
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add an improvement entry to history.
        
        Args:
            doc_type: Document type (e.g., "readme", "wiki")
            doc_id: Document identifier (filename, hash, etc.)
            score_before: Evaluation score before improvement
            score_after: Evaluation score after improvement
            details: Improvement details
            metadata: Additional metadata
        """
        import datetime
        
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "doc_type": doc_type,
            "doc_id": doc_id,
            "score_before": score_before,
            "score_after": score_after,
            "improvement": score_after - score_before,
            "details": details,
            "metadata": metadata or {}
        }
        
        self.improvements.append(entry)
    
    def save(self) -> bool:
        """Save all history to disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.storage_dir / "evaluations.json", "w", encoding="utf-8") as f:
                json.dump(self.evaluations, f, indent=2)
                
            with open(self.storage_dir / "improvements.json", "w", encoding="utf-8") as f:
                json.dump(self.improvements, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error saving history: {e}")
            return False
    
    def load(self) -> bool:
        """Load all history from disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            eval_path = self.storage_dir / "evaluations.json"
            if eval_path.exists():
                with open(eval_path, "r", encoding="utf-8") as f:
                    self.evaluations = json.load(f)
            
            imp_path = self.storage_dir / "improvements.json"
            if imp_path.exists():
                with open(imp_path, "r", encoding="utf-8") as f:
                    self.improvements = json.load(f)
                    
            return True
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            return False
    
    def get_evaluation_history(self, 
                             doc_type: Optional[str] = None, 
                             doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get evaluation history, optionally filtered.
        
        Args:
            doc_type: Filter by document type
            doc_id: Filter by document ID
            
        Returns:
            List of evaluation entries
        """
        if not doc_type and not doc_id:
            return self.evaluations
            
        return [
            entry for entry in self.evaluations
            if (not doc_type or entry.get("doc_type") == doc_type) and
               (not doc_id or entry.get("doc_id") == doc_id)
        ]
    
    def get_improvement_history(self,
                              doc_type: Optional[str] = None,
                              doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get improvement history, optionally filtered.
        
        Args:
            doc_type: Filter by document type
            doc_id: Filter by document ID
            
        Returns:
            List of improvement entries
        """
        if not doc_type and not doc_id:
            return self.improvements
            
        return [
            entry for entry in self.improvements
            if (not doc_type or entry.get("doc_type") == doc_type) and
               (not doc_id or entry.get("doc_id") == doc_id)
        ]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get overall metrics from history.
        
        Returns:
            Dictionary of metrics
        """
        metrics = {
            "total_evaluations": len(self.evaluations),
            "total_improvements": len(self.improvements),
            "average_evaluation_score": 0,
            "average_improvement": 0,
            "by_doc_type": {}
        }
        
        # Calculate average evaluation score
        if self.evaluations:
            total_score = sum(entry.get("score", 0) for entry in self.evaluations)
            metrics["average_evaluation_score"] = total_score / len(self.evaluations)
        
        # Calculate average improvement
        if self.improvements:
            total_improvement = sum(entry.get("improvement", 0) for entry in self.improvements)
            metrics["average_improvement"] = total_improvement / len(self.improvements)
        
        # Calculate metrics by document type
        doc_types = set(entry.get("doc_type") for entry in self.evaluations)
        doc_types.update(entry.get("doc_type") for entry in self.improvements)
        
        for doc_type in doc_types:
            type_evals = [e for e in self.evaluations if e.get("doc_type") == doc_type]
            type_imps = [i for i in self.improvements if i.get("doc_type") == doc_type]
            
            type_metrics = {
                "evaluations": len(type_evals),
                "improvements": len(type_imps),
                "average_score": 0,
                "average_improvement": 0
            }
            
            if type_evals:
                total_score = sum(e.get("score", 0) for e in type_evals)
                type_metrics["average_score"] = total_score / len(type_evals)
            
            if type_imps:
                total_imp = sum(i.get("improvement", 0) for i in type_imps)
                type_metrics["average_improvement"] = total_imp / len(type_imps)
            
            metrics["by_doc_type"][doc_type] = type_metrics
        
        return metrics
"""History storage for evaluation and improvement cycles.

This module provides persistent storage for evaluation and improvement
history data, making it possible to track documentation quality improvements
over time and analyze trends.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

logger = logging.getLogger(__name__)


class EvaluationHistory:
    """Store and retrieve evaluation and improvement history.
    
    This class provides a unified interface for tracking the history of document
    evaluations and improvements, making it possible to analyze trends over time
    and implement closed-loop improvement cycles.
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize the evaluation history.
        
        Args:
            storage_dir: Directory for storing history files (if None, uses default)
        """
        self.storage_dir = storage_dir or Path(__file__).parent / "history"
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize history collections
        self.evaluations = []  # List of all evaluation entries
        self.improvements = []  # List of all improvement entries
        self.cycles = []       # List of complete improvement cycles
        
    def add_evaluation(self, 
                      doc_type: str,
                      doc_id: str, 
                      score: int, 
                      results: Dict[str, Any],
                      content_hash: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add an evaluation entry to history.
        
        Args:
            doc_type: Document type (e.g., "readme", "wiki")
            doc_id: Document identifier (filename, hash, etc.)
            score: Evaluation score
            results: Evaluation results
            content_hash: Optional hash of document content
            metadata: Additional metadata
            
        Returns:
            Unique evaluation ID
        """
        eval_id = f"{doc_type}_{doc_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        entry = {
            "evaluation_id": eval_id,
            "timestamp": datetime.now().isoformat(),
            "doc_type": doc_type,
            "doc_id": doc_id,
            "score": score,
            "results": results,
            "content_hash": content_hash,
            "metadata": metadata or {}
        }
        
        self.evaluations.append(entry)
        return eval_id
    
    def add_improvement(self,
                       doc_type: str,
                       doc_id: str,
                       score_before: int,
                       score_after: int,
                       content_before_hash: Optional[str] = None,
                       content_after_hash: Optional[str] = None,
                       details: Optional[Dict[str, Any]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add an improvement entry to history.
        
        Args:
            doc_type: Document type (e.g., "readme", "wiki")
            doc_id: Document identifier (filename, hash, etc.)
            score_before: Evaluation score before improvement
            score_after: Evaluation score after improvement
            content_before_hash: Optional hash of document content before
            content_after_hash: Optional hash of document content after
            details: Improvement details
            metadata: Additional metadata
            
        Returns:
            Unique improvement ID
        """
        imp_id = f"{doc_type}_{doc_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        entry = {
            "improvement_id": imp_id,
            "timestamp": datetime.now().isoformat(),
            "doc_type": doc_type,
            "doc_id": doc_id,
            "score_before": score_before,
            "score_after": score_after,
            "improvement": score_after - score_before,
            "content_before_hash": content_before_hash,
            "content_after_hash": content_after_hash,
            "details": details or {},
            "metadata": metadata or {}
        }
        
        self.improvements.append(entry)
        return imp_id
    
    def add_cycle(self,
                 doc_type: str,
                 doc_id: str,
                 iterations: List[Dict[str, Any]],
                 initial_score: int,
                 final_score: int,
                 metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a complete improvement cycle to history.
        
        Args:
            doc_type: Document type (e.g., "readme", "wiki")
            doc_id: Document identifier (filename, hash, etc.)
            iterations: List of iteration data (evaluation and improvement pairs)
            initial_score: Score at start of cycle
            final_score: Score at end of cycle
            metadata: Additional metadata
            
        Returns:
            Unique cycle ID
        """
        cycle_id = f"{doc_type}_{doc_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        entry = {
            "cycle_id": cycle_id,
            "timestamp": datetime.now().isoformat(),
            "doc_type": doc_type,
            "doc_id": doc_id,
            "iterations": iterations,
            "iteration_count": len(iterations),
            "initial_score": initial_score,
            "final_score": final_score,
            "total_improvement": final_score - initial_score,
            "metadata": metadata or {}
        }
        
        self.cycles.append(entry)
        return cycle_id
    
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
                
            with open(self.storage_dir / "cycles.json", "w", encoding="utf-8") as f:
                json.dump(self.cycles, f, indent=2)
                
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
                    
            cycle_path = self.storage_dir / "cycles.json"
            if cycle_path.exists():
                with open(cycle_path, "r", encoding="utf-8") as f:
                    self.cycles = json.load(f)
                    
            return True
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            return False
    
    def get_evaluation_history(self, 
                             doc_type: Optional[str] = None, 
                             doc_id: Optional[str] = None,
                             limit: Optional[int] = None,
                             sort_by_score: bool = False) -> List[Dict[str, Any]]:
        """Get evaluation history, optionally filtered.
        
        Args:
            doc_type: Filter by document type
            doc_id: Filter by document ID
            limit: Maximum number of entries to return
            sort_by_score: Whether to sort by score (highest first)
            
        Returns:
            List of evaluation entries
        """
        # Filter entries
        filtered = [
            entry for entry in self.evaluations
            if (not doc_type or entry.get("doc_type") == doc_type) and
               (not doc_id or entry.get("doc_id") == doc_id)
        ]
        
        # Sort if requested
        if sort_by_score:
            filtered.sort(key=lambda x: x.get("score", 0), reverse=True)
        else:
            # Default sort by timestamp (newest first)
            filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply limit if specified
        if limit is not None and limit > 0:
            return filtered[:limit]
            
        return filtered
    
    def get_improvement_history(self,
                              doc_type: Optional[str] = None,
                              doc_id: Optional[str] = None,
                              limit: Optional[int] = None,
                              sort_by_improvement: bool = False) -> List[Dict[str, Any]]:
        """Get improvement history, optionally filtered.
        
        Args:
            doc_type: Filter by document type
            doc_id: Filter by document ID
            limit: Maximum number of entries to return
            sort_by_improvement: Whether to sort by improvement magnitude
            
        Returns:
            List of improvement entries
        """
        # Filter entries
        filtered = [
            entry for entry in self.improvements
            if (not doc_type or entry.get("doc_type") == doc_type) and
               (not doc_id or entry.get("doc_id") == doc_id)
        ]
        
        # Sort if requested
        if sort_by_improvement:
            filtered.sort(key=lambda x: x.get("improvement", 0), reverse=True)
        else:
            # Default sort by timestamp (newest first)
            filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply limit if specified
        if limit is not None and limit > 0:
            return filtered[:limit]
            
        return filtered
    
    def get_cycle_history(self,
                        doc_type: Optional[str] = None,
                        doc_id: Optional[str] = None,
                        limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get improvement cycle history, optionally filtered.
        
        Args:
            doc_type: Filter by document type
            doc_id: Filter by document ID
            limit: Maximum number of entries to return
            
        Returns:
            List of cycle entries
        """
        # Filter entries
        filtered = [
            entry for entry in self.cycles
            if (not doc_type or entry.get("doc_type") == doc_type) and
               (not doc_id or entry.get("doc_id") == doc_id)
        ]
        
        # Sort by timestamp (newest first)
        filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply limit if specified
        if limit is not None and limit > 0:
            return filtered[:limit]
            
        return filtered
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get overall metrics from history.
        
        Returns:
            Dictionary of metrics
        """
        metrics = {
            "total_evaluations": len(self.evaluations),
            "total_improvements": len(self.improvements),
            "total_cycles": len(self.cycles),
            "average_evaluation_score": 0,
            "average_improvement": 0,
            "most_improved_documents": [],
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
        
        # Find most improved documents
        doc_improvements = {}
        for entry in self.improvements:
            doc_key = f"{entry.get('doc_type')}:{entry.get('doc_id')}"
            improvement = entry.get("improvement", 0)
            
            if doc_key not in doc_improvements:
                doc_improvements[doc_key] = 0
            doc_improvements[doc_key] += improvement
        
        # Sort and get top 5 most improved documents
        most_improved = sorted(
            [{"doc": k, "total_improvement": v} for k, v in doc_improvements.items()],
            key=lambda x: x["total_improvement"],
            reverse=True
        )
        metrics["most_improved_documents"] = most_improved[:5]
        
        # Calculate metrics by document type
        doc_types = set(entry.get("doc_type") for entry in self.evaluations)
        doc_types.update(entry.get("doc_type") for entry in self.improvements)
        
        for doc_type in doc_types:
            type_evals = [e for e in self.evaluations if e.get("doc_type") == doc_type]
            type_imps = [i for i in self.improvements if i.get("doc_type") == doc_type]
            type_cycles = [c for c in self.cycles if c.get("doc_type") == doc_type]
            
            type_metrics = {
                "evaluations": len(type_evals),
                "improvements": len(type_imps),
                "cycles": len(type_cycles),
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
    
    def get_document_history(self, doc_type: str, doc_id: str) -> Dict[str, Any]:
        """Get comprehensive history for a specific document.
        
        Args:
            doc_type: Document type
            doc_id: Document ID
            
        Returns:
            Dictionary with complete document history
        """
        evals = self.get_evaluation_history(doc_type, doc_id)
        imps = self.get_improvement_history(doc_type, doc_id)
        cycles = self.get_cycle_history(doc_type, doc_id)
        
        # Calculate timeline of scores
        timeline = []
        for entry in sorted(evals, key=lambda x: x.get("timestamp", "")):
            timeline.append({
                "timestamp": entry.get("timestamp"),
                "score": entry.get("score"),
                "type": "evaluation"
            })
        
        # Calculate improvement stats
        total_improvement = sum(entry.get("improvement", 0) for entry in imps)
        improvements_count = len(imps)
        avg_improvement = total_improvement / improvements_count if improvements_count else 0
        
        return {
            "doc_type": doc_type,
            "doc_id": doc_id,
            "evaluations": evals,
            "improvements": imps,
            "cycles": cycles,
            "timeline": timeline,
            "total_evaluations": len(evals),
            "total_improvements": improvements_count,
            "total_cycles": len(cycles),
            "first_evaluated": evals[0].get("timestamp") if evals else None,
            "last_evaluated": evals[-1].get("timestamp") if evals else None,
            "initial_score": evals[0].get("score") if evals else None,
            "latest_score": evals[-1].get("score") if evals else None,
            "total_improvement": total_improvement,
            "average_improvement_per_iteration": avg_improvement
        }
"""Crew for improving documentation."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from evcrew import DocumentCrew

from .evaluation import EvaluationCrew


class ImprovementCrew(DocumentCrew):
    """Crew for iteratively improving documentation using evcrew."""

    def __init__(self, target_score: Optional[int] = None, max_iterations: Optional[int] = None):
        """Initialize improvement crew."""
        target_score = target_score or int(os.getenv("AUTODOC_TARGET_SCORE", "85"))
        max_iterations = max_iterations or int(os.getenv("AUTODOC_MAX_ITERATIONS", "3"))
        super().__init__(target_score=target_score, max_iterations=max_iterations)
        self.evaluation_crew = EvaluationCrew()

    def run(self, doc_path: str, output_dir: str = "./improved", doc_type: Optional[str] = None) -> Dict[str, Any]:
        """Iteratively improve a document until target score is reached."""
        # Since we don't inherit from BaseCrew, use file reading directly
        try:
            with open(doc_path, encoding="utf-8") as f:
                content = f.read()
        except Exception:
            content = None
        if not content:
            return {"error": f"Document not found or empty: {doc_path}"}

        filename = os.path.basename(doc_path)
        doc_name = Path(filename).stem

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Detect type if not provided
        if not doc_type:
            doc_type = self.evaluation_crew._detect_doc_type(content, filename)

        # Use auto_improve_one with custom evaluator
        print(f"\n🚀 Starting iterative improvement for {filename} ({doc_type} documentation)")
        print(f"   Target score: {self.target_score}%, Max iterations: {self.max_iterations}\n")

        iterator = self.auto_improve_one(content=content, output_dir=output_dir, doc_name=doc_name, doc_path=doc_path)

        # Create improvement summary
        summary = {
            "document": filename,
            "type": doc_type,
            "initial_score": iterator._iterations[0].score if iterator._iterations else 0,
            "final_score": iterator.final_score,
            "total_improvement": iterator.total_improvement,
            "iterations": len(iterator._iterations) - 1,  # Exclude initial evaluation
            "target_reached": iterator.final_score >= self.target_score,
            "output_files": {"improved_document": str(output_path / f"{doc_name}_final.md"), "results": str(output_path / f"{doc_name}_results.json")},
        }

        return summary

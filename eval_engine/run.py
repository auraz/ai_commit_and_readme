#!/usr/bin/env python3
"""
Evaluation Engine Runner for Documentation Quality

This script provides a command-line interface for running the closed-loop
document evaluation and improvement system.

Usage:
  python run.py evaluate path/to/document.md --type readme
  python run.py improve path/to/document.md --iterations 3
  python run.py run-cycle path/to/document.md --iterations 3
  python run.py evaluate-dir path/to/wiki/ --type wiki
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("eval-engine")

# Add parent directory to sys.path if running as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_commit_and_readme.eval_engine import (
    EvaluationEngine, 
    ClosedLoopRunner, 
    BaseEvaluator, 
    BaseImprover
)
from ai_commit_and_readme.eval_engine.evaluators.readme_evaluator import ReadmeEvaluator
from ai_commit_and_readme.eval_engine.improvers.readme_improver import ReadmeImprover


def setup_engine() -> Tuple[EvaluationEngine, ClosedLoopRunner]:
    """Set up the evaluation engine and closed-loop runner with default evaluators and improvers.
    
    Returns:
        Tuple of (evaluation_engine, closed_loop_runner)
    """
    # Create evaluation engine
    engine = EvaluationEngine()
    
    # Register evaluators
    engine.register_evaluator("readme", ReadmeEvaluator())
    
    # Create closed-loop runner
    runner = ClosedLoopRunner(engine)
    
    # Register improvers
    runner.register_improver("readme", ReadmeImprover())
    
    return engine, runner


def evaluate_file(args: argparse.Namespace) -> None:
    """Evaluate a single file.
    
    Args:
        args: Command-line arguments
    """
    engine, _ = setup_engine()
    
    try:
        score, results = engine.evaluate_file(args.path, args.type)
        
        # Get evaluator to format the report
        evaluator = engine.get_evaluator(args.type)
        if evaluator:
            report = evaluator.format_evaluation_report(
                results, f"{args.type.title()} Evaluation: {os.path.basename(args.path)}"
            )
        else:
            # Fallback if evaluator doesn't have format_evaluation_report
            report = json.dumps(results, indent=2)
        
        # Print report
        print(report)
        
        # Save to file if requested
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"Evaluation report saved to: {args.output}")
        
    except Exception as e:
        logger.error(f"Error evaluating file: {e}")
        sys.exit(1)


def evaluate_directory(args: argparse.Namespace) -> None:
    """Evaluate all documents in a directory.
    
    Args:
        args: Command-line arguments
    """
    engine, _ = setup_engine()
    
    # Find all markdown files in the directory
    dir_path = Path(args.path)
    if not dir_path.exists() or not dir_path.is_dir():
        logger.error(f"Directory not found: {args.path}")
        sys.exit(1)
    
    markdown_files = list(dir_path.glob("**/*.md"))
    logger.info(f"Found {len(markdown_files)} markdown files in {args.path}")
    
    # Create output directory if needed
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
    
    # Evaluate each file
    results = []
    for file_path in markdown_files:
        relative_path = file_path.relative_to(dir_path)
        logger.info(f"Evaluating: {relative_path}")
        
        try:
            score, eval_results = engine.evaluate_file(str(file_path), args.type)
            
            result = {
                "file": str(relative_path),
                "score": score,
                "evaluation": eval_results
            }
            results.append(result)
            
            # Save individual report if output directory is specified
            if args.output_dir:
                evaluator = engine.get_evaluator(args.type)
                if evaluator:
                    report = evaluator.format_evaluation_report(
                        eval_results, f"{args.type.title()} Evaluation: {file_path.name}"
                    )
                else:
                    report = json.dumps(eval_results, indent=2)
                
                output_path = Path(args.output_dir) / f"{relative_path.stem}_evaluation.md"
                os.makedirs(output_path.parent, exist_ok=True)
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(report)
            
            logger.info(f"Score: {score}")
            
        except Exception as e:
            logger.error(f"Error evaluating {relative_path}: {e}")
            results.append({
                "file": str(relative_path),
                "error": str(e)
            })
    
    # Save summary report
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Evaluation summary saved to: {args.output}")
    
    # Print summary
    print("\nEvaluation Summary:")
    print("-" * 50)
    
    for result in sorted(results, key=lambda x: x.get("score", 0) if "score" in x else -1, reverse=True):
        filename = result.get("file", "Unknown file")
        if "score" in result:
            print(f"{filename}: {result['score']}")
        else:
            print(f"{filename}: Error - {result.get('error', 'Unknown error')}")


def improve_file(args: argparse.Namespace) -> None:
    """Improve a single file.
    
    Args:
        args: Command-line arguments
    """
    engine, runner = setup_engine()
    
    try:
        # Read file content
        with open(args.path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Determine document type
        doc_type = args.type
        if not doc_type:
            doc_type = engine._infer_doc_type(args.path)
        
        # Get evaluator and improver
        evaluator = engine.get_evaluator(doc_type)
        improver = runner.get_improver(doc_type)
        
        if not evaluator:
            raise ValueError(f"No evaluator registered for document type: {doc_type}")
        if not improver:
            raise ValueError(f"No improver registered for document type: {doc_type}")
        
        # Evaluate content
        score_before, eval_results = evaluator.evaluate(content, filename=os.path.basename(args.path))
        logger.info(f"Initial evaluation score: {score_before}")
        
        # Improve content
        improved_content, improve_details = improver.improve(content, eval_results, filename=os.path.basename(args.path))
        
        # Re-evaluate improved content
        score_after, eval_after = evaluator.evaluate(improved_content, filename=os.path.basename(args.path))
        logger.info(f"After improvement: {score_after} ({score_after - score_before:+.1f})")
        
        # Save improved content if requested
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(improved_content)
            logger.info(f"Improved content saved to: {args.output}")
        else:
            # Print improvement summary
            summary = improver.create_improvement_summary(content, improved_content, eval_results, eval_after)
            print(summary)
        
    except Exception as e:
        logger.error(f"Error improving file: {e}")
        sys.exit(1)


def run_improvement_cycle(args: argparse.Namespace) -> None:
    """Run a complete improvement cycle for a file.
    
    Args:
        args: Command-line arguments
    """
    _, runner = setup_engine()
    
    try:
        # Run improvement cycle
        improved_content, cycle_results = runner.run_file_improvement_cycle(
            args.path,
            doc_type=args.type,
            iterations=args.iterations,
            output_file=args.output
        )
        
        # Print cycle results summary
        print("\nImprovement Cycle Summary:")
        print("-" * 50)
        
        for i, result in enumerate(cycle_results):
            iteration = i + 1
            score_before = result.get("score_before", 0)
            score_after = result.get("score_after", 0)
            improvement = result.get("improvement", 0)
            
            print(f"Iteration {iteration}: {score_before} → {score_after} ({improvement:+.1f})")
        
        # Print final result
        if cycle_results:
            final_score = cycle_results[-1].get("score_after", 0)
            initial_score = cycle_results[0].get("score_before", 0)
            total_improvement = final_score - initial_score
            
            print(f"\nTotal Improvement: {initial_score} → {final_score} ({total_improvement:+.1f})")
        
        # Save detailed results if requested
        if args.details:
            with open(args.details, "w", encoding="utf-8") as f:
                json.dump(cycle_results, f, indent=2)
            logger.info(f"Detailed cycle results saved to: {args.details}")
        
    except Exception as e:
        logger.error(f"Error running improvement cycle: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Documentation Evaluation Engine")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Evaluate command
    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate a document")
    evaluate_parser.add_argument("path", help="Path to document file")
    evaluate_parser.add_argument("--type", required=True, help="Document type (readme, wiki, etc.)")
    evaluate_parser.add_argument("--output", "-o", help="Save evaluation report to file")
    
    # Evaluate directory command
    evaluate_dir_parser = subparsers.add_parser("evaluate-dir", help="Evaluate all documents in a directory")
    evaluate_dir_parser.add_argument("path", help="Path to directory")
    evaluate_dir_parser.add_argument("--type", required=True, help="Document type for all files")
    evaluate_dir_parser.add_argument("--output", "-o", help="Save evaluation summary to file")
    evaluate_dir_parser.add_argument("--output-dir", "-d", help="Save individual evaluation reports to directory")
    
    # Improve command
    improve_parser = subparsers.add_parser("improve", help="Improve a document")
    improve_parser.add_argument("path", help="Path to document file")
    improve_parser.add_argument("--type", help="Document type (if not provided, will be inferred)")
    improve_parser.add_argument("--output", "-o", help="Save improved document to file")
    
    # Run improvement cycle command
    cycle_parser = subparsers.add_parser("run-cycle", help="Run a complete improvement cycle")
    cycle_parser.add_argument("path", help="Path to document file")
    cycle_parser.add_argument("--type", help="Document type (if not provided, will be inferred)")
    cycle_parser.add_argument("--iterations", "-i", type=int, default=3, help="Maximum number of improvement iterations")
    cycle_parser.add_argument("--output", "-o", help="Save final improved document to file")
    cycle_parser.add_argument("--details", "-d", help="Save detailed cycle results to file")
    
    args = parser.parse_args()
    
    if args.command == "evaluate":
        evaluate_file(args)
    elif args.command == "evaluate-dir":
        evaluate_directory(args)
    elif args.command == "improve":
        improve_file(args)
    elif args.command == "run-cycle":
        run_improvement_cycle(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
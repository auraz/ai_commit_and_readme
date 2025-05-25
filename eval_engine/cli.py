#!/usr/bin/env python3
"""
Command-line interface for Documentation Evaluation Engine.

This module provides a CLI for the Documentation Evaluation Engine,
allowing users to evaluate documents, improve them, and run closed-loop
improvement cycles from the command line.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import openai

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

from ai_commit_and_readme.eval_engine.evals.base import CompletionFn
from ai_commit_and_readme.eval_engine.evals.readme_eval import ReadmeEvaluator
from ai_commit_and_readme.eval_engine.runner import ClosedLoopRunner, Improver


def setup_openai_client() -> openai.OpenAI:
    """Set up and return an OpenAI client.
    
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


def setup_runner() -> ClosedLoopRunner:
    """Set up and return a ClosedLoopRunner with default evaluators and improvers.
    
    Returns:
        ClosedLoopRunner instance
    """
    runner = ClosedLoopRunner()
    
    # Set up OpenAI client
    client = setup_openai_client()
    
    # Create completion function
    completion_fn = CompletionFn(client, model="gpt-4")
    
    # Register README evaluator
    readme_evaluator = ReadmeEvaluator(completion_fn=completion_fn)
    runner.register_evaluator("readme", readme_evaluator)
    
    # Create and register README improver
    runner.create_default_improver("readme", completion_fn)
    
    return runner


def read_file(path: str) -> str:
    """Read the content of a file.
    
    Args:
        path: Path to the file
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    """Write content to a file.
    
    Args:
        path: Path to the file
        content: Content to write
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def cmd_evaluate(args) -> None:
    """Handle evaluate command.
    
    Args:
        args: Command-line arguments
    """
    runner = setup_runner()
    
    if args.dir:
        # Evaluate directory
        directory = Path(args.path)
        if not directory.is_dir():
            logger.error(f"Not a directory: {args.path}")
            sys.exit(1)
        
        results = []
        for file_path in directory.glob("**/*.md"):
            relative_path = file_path.relative_to(directory)
            logger.info(f"Evaluating {relative_path}")
            
            try:
                content = read_file(str(file_path))
                
                # Infer document type if not specified
                doc_type = args.type
                if not doc_type:
                    if file_path.name.lower() == "readme.md":
                        doc_type = "readme"
                    else:
                        doc_type = "generic"
                
                eval_result, metrics = runner.evaluate(
                    content, 
                    doc_type,
                    filename=file_path.name
                )
                
                results.append({
                    "path": str(relative_path),
                    "doc_type": doc_type,
                    "score": eval_result.get("total_score", 0),
                    "metrics": metrics
                })
                
                # Save individual evaluation report if requested
                if args.output_dir:
                    output_dir = Path(args.output_dir)
                    output_file = output_dir / f"{relative_path.stem}_evaluation.md"
                    os.makedirs(output_file.parent, exist_ok=True)
                    
                    evaluator = runner.evaluators.get(doc_type)
                    if evaluator:
                        report = evaluator.format_result(eval_result, file_path.name)
                        write_file(str(output_file), report)
                
            except Exception as e:
                logger.error(f"Error evaluating {relative_path}: {e}")
                results.append({
                    "path": str(relative_path),
                    "error": str(e)
                })
        
        # Print summary
        print("\nEvaluation Summary:")
        print("-" * 50)
        
        for result in sorted(results, key=lambda x: x.get("score", 0) if "score" in x else -1, reverse=True):
            path = result["path"]
            if "score" in result:
                print(f"{path}: {result['score']}")
            else:
                print(f"{path}: Error - {result.get('error', 'Unknown error')}")
        
        # Save summary if requested
        if args.output:
            write_file(args.output, json.dumps(results, indent=2))
            logger.info(f"Summary saved to {args.output}")
    
    else:
        # Evaluate single file
        if not os.path.isfile(args.path):
            logger.error(f"File not found: {args.path}")
            sys.exit(1)
        
        try:
            content = read_file(args.path)
            
            # Infer document type if not specified
            doc_type = args.type
            if not doc_type:
                if os.path.basename(args.path).lower() == "readme.md":
                    doc_type = "readme"
                else:
                    doc_type = "generic"
            
            eval_result, metrics = runner.evaluate(
                content, 
                doc_type,
                filename=os.path.basename(args.path)
            )
            
            # Format and print the report
            evaluator = runner.evaluators.get(doc_type)
            if evaluator:
                report = evaluator.format_result(eval_result, os.path.basename(args.path))
                print(report)
            else:
                print(json.dumps(eval_result, indent=2))
            
            # Save report if requested
            if args.output:
                if evaluator:
                    report = evaluator.format_result(eval_result, os.path.basename(args.path))
                    write_file(args.output, report)
                else:
                    write_file(args.output, json.dumps(eval_result, indent=2))
                logger.info(f"Evaluation saved to {args.output}")
        
        except Exception as e:
            logger.error(f"Error evaluating {args.path}: {e}")
            sys.exit(1)


def cmd_improve(args) -> None:
    """Handle improve command.
    
    Args:
        args: Command-line arguments
    """
    runner = setup_runner()
    
    if not os.path.isfile(args.path):
        logger.error(f"File not found: {args.path}")
        sys.exit(1)
    
    try:
        content = read_file(args.path)
        
        # Infer document type if not specified
        doc_type = args.type
        if not doc_type:
            if os.path.basename(args.path).lower() == "readme.md":
                doc_type = "readme"
            else:
                doc_type = "generic"
        
        # Evaluate first
        logger.info(f"Evaluating {args.path}")
        eval_result, metrics = runner.evaluate(
            content, 
            doc_type,
            filename=os.path.basename(args.path)
        )
        
        logger.info(f"Current score: {eval_result.get('total_score', 0)}")
        
        # Improve
        logger.info(f"Improving {args.path}")
        improvement_result = runner.improve(
            content, 
            eval_result, 
            doc_type,
            filename=os.path.basename(args.path)
        )
        
        # Evaluate improvement
        improved_content = improvement_result.improved_content
        eval_after, metrics_after = runner.evaluate(
            improved_content, 
            doc_type,
            filename=os.path.basename(args.path)
        )
        
        # Update improvement result with evaluation after
        improvement_result.eval_after = eval_after
        
        # Print improvement report
        print(improvement_result.format_report())
        
        # Save improved content if requested
        if args.output:
            write_file(args.output, improved_content)
            logger.info(f"Improved content saved to {args.output}")
        
        # Save report if requested
        if args.report:
            write_file(args.report, improvement_result.format_report())
            logger.info(f"Improvement report saved to {args.report}")
    
    except Exception as e:
        logger.error(f"Error improving {args.path}: {e}")
        sys.exit(1)


def cmd_run_cycle(args) -> None:
    """Handle run-cycle command.
    
    Args:
        args: Command-line arguments
    """
    runner = setup_runner()
    
    if not os.path.isfile(args.path):
        logger.error(f"File not found: {args.path}")
        sys.exit(1)
    
    try:
        content = read_file(args.path)
        
        # Infer document type if not specified
        doc_type = args.type
        if not doc_type:
            if os.path.basename(args.path).lower() == "readme.md":
                doc_type = "readme"
            else:
                doc_type = "generic"
        
        # Run improvement cycle
        logger.info(f"Running improvement cycle for {args.path}")
        cycle_result = runner.run_cycle(
            content, 
            doc_type,
            max_iterations=args.iterations,
            min_improvement=args.min_improvement,
            target_score=args.target_score,
            filename=os.path.basename(args.path),
            save_results=args.save_results
        )
        
        # Print cycle report
        print(cycle_result.format_report())
        
        # Save final content if requested
        if args.output:
            write_file(args.output, cycle_result.final_content)
            logger.info(f"Final content saved to {args.output}")
        
        # Save report if requested
        if args.report:
            write_file(args.report, cycle_result.format_report())
            logger.info(f"Cycle report saved to {args.report}")
    
    except Exception as e:
        logger.error(f"Error running cycle for {args.path}: {e}")
        sys.exit(1)


def cmd_list(args) -> None:
    """Handle list command.
    
    Args:
        args: Command-line arguments
    """
    runner = setup_runner()
    
    print("Available Evaluators:")
    for doc_type in runner.evaluators:
        print(f"- {doc_type}")
    
    print("\nAvailable Improvers:")
    for doc_type in runner.improvers:
        print(f"- {doc_type}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Documentation Evaluation Engine - Closed-loop improvement system"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate document quality")
    eval_parser.add_argument("path", help="Path to document file or directory")
    eval_parser.add_argument("--dir", action="store_true", help="Evaluate all documents in directory")
    eval_parser.add_argument("--type", help="Document type (readme, generic, etc.)")
    eval_parser.add_argument("--output", "-o", help="Output file for evaluation report")
    eval_parser.add_argument("--output-dir", "-d", help="Output directory for evaluation reports when evaluating a directory")
    eval_parser.set_defaults(func=cmd_evaluate)
    
    # Improve command
    improve_parser = subparsers.add_parser("improve", help="Improve document based on evaluation")
    improve_parser.add_argument("path", help="Path to document file")
    improve_parser.add_argument("--type", help="Document type (readme, generic, etc.)")
    improve_parser.add_argument("--output", "-o", help="Output file for improved content")
    improve_parser.add_argument("--report", "-r", help="Output file for improvement report")
    improve_parser.set_defaults(func=cmd_improve)
    
    # Run cycle command
    cycle_parser = subparsers.add_parser("run-cycle", help="Run complete evaluation and improvement cycle")
    cycle_parser.add_argument("path", help="Path to document file")
    cycle_parser.add_argument("--type", help="Document type (readme, generic, etc.)")
    cycle_parser.add_argument("--iterations", "-i", type=int, default=3, help="Maximum number of iterations")
    cycle_parser.add_argument("--min-improvement", type=float, default=1.0, help="Minimum score improvement to continue")
    cycle_parser.add_argument("--target-score", type=float, help="Target score to achieve")
    cycle_parser.add_argument("--output", "-o", help="Output file for final content")
    cycle_parser.add_argument("--report", "-r", help="Output file for cycle report")
    cycle_parser.add_argument("--save-results", action="store_true", help="Save detailed results to disk")
    cycle_parser.set_defaults(func=cmd_run_cycle)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available evaluators and improvers")
    list_parser.set_defaults(func=cmd_list)
    
    args = parser.parse_args()
    
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
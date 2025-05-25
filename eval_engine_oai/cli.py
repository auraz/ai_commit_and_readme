#!/usr/bin/env python3
"""
Command-line interface for Document Evaluation Engine.

This module provides a CLI for the Document Evaluation Engine,
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("eval-engine")

# Make sure the package is importable
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import openai
    from ai_commit_and_readme.eval_engine_oai.evaluator import DocEvaluator, evaluate_document
    from ai_commit_and_readme.eval_engine_oai.improver import DocImprover, improve_document
    from ai_commit_and_readme.eval_engine_oai.runner import ClosedLoopRunner, run_improvement_cycle
except ImportError as e:
    logger.error(f"Error importing required modules: {e}")
    logger.error("Please make sure the required packages are installed.")
    sys.exit(1)


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
    try:
        # Set up OpenAI client
        client = setup_openai_client()
        
        # Create evaluator
        evaluator = DocEvaluator(
            client=client,
            model=args.model
        )
        
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
                    
                    eval_result, metrics = evaluator.evaluate(
                        content, 
                        doc_type=doc_type,
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
            
            content = read_file(args.path)
            
            # Infer document type if not specified
            doc_type = args.type
            if not doc_type:
                if os.path.basename(args.path).lower() == "readme.md":
                    doc_type = "readme"
                else:
                    doc_type = "generic"
            
            eval_result, metrics = evaluator.evaluate(
                content, 
                doc_type=doc_type,
                filename=os.path.basename(args.path)
            )
            
            # Format and print the report
            report = evaluator.format_result(eval_result, os.path.basename(args.path))
            print(report)
            
            # Save report if requested
            if args.output:
                write_file(args.output, report)
                logger.info(f"Evaluation saved to {args.output}")
                
            # Save raw results if requested
            if args.json:
                json_output = json.dumps({
                    "evaluation": eval_result,
                    "metrics": metrics
                }, indent=2)
                write_file(args.json, json_output)
                logger.info(f"Raw results saved to {args.json}")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_improve(args) -> None:
    """Handle improve command.
    
    Args:
        args: Command-line arguments
    """
    try:
        # Set up OpenAI client
        client = setup_openai_client()
        
        # Create evaluator and improver
        evaluator = DocEvaluator(
            client=client,
            model=args.eval_model
        )
        
        improver = DocImprover(
            client=client,
            model=args.improve_model
        )
        
        if not os.path.isfile(args.path):
            logger.error(f"File not found: {args.path}")
            sys.exit(1)
        
        content = read_file(args.path)
        
        # Infer document type if not specified
        doc_type = args.type
        if not doc_type:
            if os.path.basename(args.path).lower() == "readme.md":
                doc_type = "readme"
            else:
                doc_type = "generic"
        
        # Step 1: Evaluate
        logger.info(f"Evaluating {args.path}")
        eval_result, metrics = evaluator.evaluate(
            content, 
            doc_type=doc_type,
            filename=os.path.basename(args.path)
        )
        
        logger.info(f"Current score: {eval_result.get('total_score', 0)}")
        
        # Step 2: Improve
        logger.info(f"Improving {args.path}")
        improved_content, improve_details = improver.improve(
            content, 
            eval_result, 
            doc_type=doc_type,
            filename=os.path.basename(args.path)
        )
        
        # Step 3: Re-evaluate (optional)
        if not args.skip_reeval:
            logger.info("Re-evaluating improved content")
            eval_after, metrics_after = evaluator.evaluate(
                improved_content, 
                doc_type=doc_type,
                filename=os.path.basename(args.path)
            )
            
            score_before = eval_result.get("total_score", 0)
            score_after = eval_after.get("total_score", 0)
            
            logger.info(f"Score improvement: {score_before} → {score_after} ({score_after - score_before:+d})")
            
            # Format and print improvement report
            report = improver.format_improvement_report(
                content,
                improved_content,
                eval_result,
                eval_after
            )
        else:
            # Format basic report without re-evaluation
            report = improver.format_improvement_report(
                content,
                improved_content,
                eval_result
            )
        
        print(report)
        
        # Save improved content if requested
        if args.output:
            write_file(args.output, improved_content)
            logger.info(f"Improved content saved to {args.output}")
        
        # Save report if requested
        if args.report:
            write_file(args.report, report)
            logger.info(f"Improvement report saved to {args.report}")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_run_cycle(args) -> None:
    """Handle run-cycle command.
    
    Args:
        args: Command-line arguments
    """
    try:
        # Set up OpenAI client
        client = setup_openai_client()
        
        # Create runner
        runner = ClosedLoopRunner(
            client=client,
            evaluation_model=args.eval_model,
            improvement_model=args.improve_model
        )
        
        if not os.path.isfile(args.path):
            logger.error(f"File not found: {args.path}")
            sys.exit(1)
        
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
            doc_type=doc_type,
            max_iterations=args.iterations,
            min_improvement=args.min_improvement,
            target_score=args.target_score,
            save_results=args.save_results,
            filename=os.path.basename(args.path)
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
            
        # Save raw results if requested
        if args.json:
            json_output = json.dumps(cycle_result.to_dict(), indent=2, default=str)
            write_file(args.json, json_output)
            logger.info(f"Raw results saved to {args.json}")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_list(args) -> None:
    """Handle list command.
    
    Args:
        args: Command-line arguments
    """
    print("Document Types:")
    print("- readme: README file evaluation (default for files named README.md)")
    print("- generic: Generic markdown document evaluation (default for other .md files)")
    
    print("\nAvailable Models:")
    print("- gpt-4: Best for accurate evaluation and high-quality improvements")
    print("- gpt-3.5-turbo: Faster and more economical option")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Document Evaluation Engine - Closed-loop improvement system"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate document quality")
    eval_parser.add_argument("path", help="Path to document file or directory")
    eval_parser.add_argument("--dir", action="store_true", help="Evaluate all documents in directory")
    eval_parser.add_argument("--type", help="Document type (readme, generic)")
    eval_parser.add_argument("--model", default="gpt-4", help="Model to use for evaluation")
    eval_parser.add_argument("--output", "-o", help="Output file for evaluation report")
    eval_parser.add_argument("--output-dir", "-d", help="Output directory for evaluation reports when evaluating a directory")
    eval_parser.add_argument("--json", "-j", help="Save raw evaluation results as JSON")
    eval_parser.set_defaults(func=cmd_evaluate)
    
    # Improve command
    improve_parser = subparsers.add_parser("improve", help="Improve document based on evaluation")
    improve_parser.add_argument("path", help="Path to document file")
    improve_parser.add_argument("--type", help="Document type (readme, generic)")
    improve_parser.add_argument("--eval-model", default="gpt-4", help="Model to use for evaluation")
    improve_parser.add_argument("--improve-model", default="gpt-4", help="Model to use for improvement")
    improve_parser.add_argument("--output", "-o", help="Output file for improved content")
    improve_parser.add_argument("--report", "-r", help="Output file for improvement report")
    improve_parser.add_argument("--skip-reeval", action="store_true", help="Skip re-evaluation after improvement")
    improve_parser.set_defaults(func=cmd_improve)
    
    # Run cycle command
    cycle_parser = subparsers.add_parser("run-cycle", help="Run complete evaluation and improvement cycle")
    cycle_parser.add_argument("path", help="Path to document file")
    cycle_parser.add_argument("--type", help="Document type (readme, generic)")
    cycle_parser.add_argument("--eval-model", default="gpt-4", help="Model to use for evaluation")
    cycle_parser.add_argument("--improve-model", default="gpt-4", help="Model to use for improvement")
    cycle_parser.add_argument("--iterations", "-i", type=int, default=3, help="Maximum number of iterations")
    cycle_parser.add_argument("--min-improvement", type=float, default=1.0, help="Minimum score improvement to continue")
    cycle_parser.add_argument("--target-score", type=float, help="Target score to achieve")
    cycle_parser.add_argument("--output", "-o", help="Output file for final content")
    cycle_parser.add_argument("--report", "-r", help="Output file for cycle report")
    cycle_parser.add_argument("--json", "-j", help="Save raw cycle results as JSON")
    cycle_parser.add_argument("--save-results", action="store_true", help="Save detailed results to disk")
    cycle_parser.set_defaults(func=cmd_run_cycle)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available document types and models")
    list_parser.set_defaults(func=cmd_list)
    
    args = parser.parse_args()
    
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
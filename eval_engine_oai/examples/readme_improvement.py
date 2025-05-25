#!/usr/bin/env python3
"""
README Improvement Example

This script demonstrates how to use the Document Evaluation Engine to
evaluate and improve README files through single-step improvement and
multi-step improvement cycles.

Usage:
  python readme_improvement.py [path/to/readme.md]

If no path is provided, the script will use a sample README.
"""

import argparse
import os
import sys
from pathlib import Path

# Make sure the package is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    import openai
    from ai_commit_and_readme.eval_engine_oai import (
        DocEvaluator,
        DocImprover,
        ClosedLoopRunner,
        evaluate_document,
        improve_document,
        run_improvement_cycle
    )
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure the required packages are installed.")
    sys.exit(1)

# Sample README content for demonstration
SAMPLE_README = """# My Project

A simple project.

## Installation

Install it.

## Usage

Use it.
"""

def setup_openai_client():
    """Set up and return an OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set it with your OpenAI API key.")
        sys.exit(1)
    
    return openai.OpenAI(api_key=api_key)

def read_file(path):
    """Read the content of a file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return None

def write_file(path, content):
    """Write content to a file."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing to file {path}: {e}")
        return False

def example_evaluate(content, client):
    """Example of evaluating a README."""
    print("\n" + "="*80)
    print("EVALUATING README")
    print("="*80)
    
    # Method 1: Using the evaluate_document function
    evaluation_result, metrics = evaluate_document(
        content,
        doc_type="readme",
        client=client
    )
    
    # Print evaluation results
    print(f"\nEvaluation Score: {evaluation_result['total_score']}/100")
    print(f"Grade: {evaluation_result['grade']}")
    print("\nCategory Scores:")
    
    for category, data in evaluation_result["category_scores"].items():
        category_name = category.replace("_", " ").title()
        score = data["score"]
        max_score = data["max_score"]
        print(f"- {category_name}: {score}/{max_score}")
    
    print("\nTop Recommendations:")
    for rec in evaluation_result["top_recommendations"]:
        print(f"- {rec}")
    
    # Method 2: Using the DocEvaluator class directly
    print("\nUsing DocEvaluator class directly:")
    evaluator = DocEvaluator(client=client)
    result, _ = evaluator.evaluate(content, doc_type="readme")
    print(f"Score: {result['total_score']}/100")
    
    return evaluation_result, metrics

def example_improve(content, evaluation_result, client):
    """Example of improving a README."""
    print("\n" + "="*80)
    print("IMPROVING README")
    print("="*80)
    
    # Method 1: Using the improve_document function
    improved_content, details = improve_document(
        content,
        evaluation_result,
        doc_type="readme",
        client=client
    )
    
    # Print improvement details
    print(f"\nOriginal length: {len(content.split())} words")
    print(f"Improved length: {len(improved_content.split())} words")
    word_change = len(improved_content.split()) - len(content.split())
    if word_change > 0:
        print(f"Added {word_change} words")
    else:
        print(f"Removed {abs(word_change)} words")
    
    # Method 2: Using the DocImprover class directly
    print("\nUsing DocImprover class directly:")
    improver = DocImprover(client=client)
    improved_content_alt, _ = improver.improve(content, evaluation_result)
    print(f"Improvement complete: {len(improved_content_alt)} characters")
    
    # Re-evaluate the improved content
    print("\nRe-evaluating improved content:")
    eval_after, _ = evaluate_document(improved_content, doc_type="readme", client=client)
    print(f"Original score: {evaluation_result['total_score']}/100")
    print(f"Improved score: {eval_after['total_score']}/100")
    print(f"Improvement: {eval_after['total_score'] - evaluation_result['total_score']:+d} points")
    
    return improved_content, eval_after

def example_run_cycle(content, client):
    """Example of running a complete improvement cycle."""
    print("\n" + "="*80)
    print("RUNNING IMPROVEMENT CYCLE")
    print("="*80)
    
    # Method 1: Using the run_improvement_cycle function
    improved_content, cycle_results = run_improvement_cycle(
        content,
        doc_type="readme",
        max_iterations=2,
        min_improvement=1.0,
        client=client
    )
    
    # Print cycle results
    initial_score = cycle_results['metrics']['initial_score']
    final_score = cycle_results['metrics']['final_score']
    total_improvement = cycle_results['metrics']['total_improvement']
    iterations = cycle_results['metrics']['iterations']
    
    print(f"\nCompleted {iterations} improvement iterations")
    print(f"Initial score: {initial_score}/100")
    print(f"Final score: {final_score}/100")
    print(f"Total improvement: {total_improvement:+.1f} points")
    
    # Method 2: Using the ClosedLoopRunner class directly
    print("\nUsing ClosedLoopRunner class directly:")
    runner = ClosedLoopRunner(client=client)
    cycle_result = runner.run_cycle(
        content,
        doc_type="readme",
        max_iterations=2
    )
    
    print(f"Final score: {cycle_result.final_score}/100")
    print(f"Improvement: {cycle_result.final_score - cycle_result.initial_score:+d} points")
    
    return improved_content, cycle_result

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="README Improvement Example")
    parser.add_argument("path", nargs="?", help="Path to README.md file (optional)")
    parser.add_argument("--output-dir", "-o", default="results", help="Directory to save results")
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Set up OpenAI client
    try:
        client = setup_openai_client()
    except Exception as e:
        print(f"Error setting up OpenAI client: {e}")
        sys.exit(1)
    
    # Get README content
    if args.path and os.path.isfile(args.path):
        content = read_file(args.path)
        if not content:
            print(f"Error reading {args.path}, using sample README")
            content = SAMPLE_README
    else:
        print("No path provided or file not found, using sample README")
        content = SAMPLE_README
    
    try:
        # Example 1: Evaluate README
        evaluation_result, metrics = example_evaluate(content, client)
        
        # Save evaluation results
        eval_path = os.path.join(args.output_dir, "evaluation.json")
        with open(eval_path, "w", encoding="utf-8") as f:
            import json
            json.dump(evaluation_result, f, indent=2)
        print(f"\nEvaluation results saved to {eval_path}")
        
        # Example 2: Improve README
        improved_content, eval_after = example_improve(content, evaluation_result, client)
        
        # Save improved content
        improved_path = os.path.join(args.output_dir, "improved_readme.md")
        write_file(improved_path, improved_content)
        print(f"\nImproved README saved to {improved_path}")
        
        # Example 3: Run improvement cycle
        cycle_content, cycle_result = example_run_cycle(content, client)
        
        # Save cycle results
        cycle_path = os.path.join(args.output_dir, "cycle_improved_readme.md")
        write_file(cycle_path, cycle_content)
        print(f"\nCycle-improved README saved to {cycle_path}")
        
        print("\nAll examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
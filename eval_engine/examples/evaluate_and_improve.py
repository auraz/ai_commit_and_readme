#!/usr/bin/env python3
"""
Example usage of the Documentation Evaluation Engine.

This script demonstrates how to use the eval_engine for:
1. Evaluating README files
2. Improving them based on evaluation results
3. Running closed-loop improvement cycles
"""

import os
import logging
from pathlib import Path
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("eval-example")

# Import eval_engine components
from ai_commit_and_readme.eval_engine.evals.base import CompletionFn
from ai_commit_and_readme.eval_engine.evals.readme_eval import ReadmeEvaluator
from ai_commit_and_readme.eval_engine.runner import ClosedLoopRunner, Improver


def setup_evaluator():
    """Set up and configure an evaluator for README files."""
    # Make sure we have an API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable")
    
    # Import OpenAI client
    import openai
    client = openai.OpenAI(api_key=api_key)
    
    # Create a completion function using GPT-4
    completion_fn = CompletionFn(client, model="gpt-4", temperature=0.2)
    
    # Create a README evaluator
    evaluator = ReadmeEvaluator(completion_fn=completion_fn)
    
    return evaluator


def setup_runner():
    """Set up a complete ClosedLoopRunner with evaluators and improvers."""
    # Make sure we have an API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable")
    
    # Import OpenAI client
    import openai
    client = openai.OpenAI(api_key=api_key)
    
    # Create a completion function
    completion_fn = CompletionFn(client, model="gpt-4", temperature=0.7)
    
    # Create the runner
    runner = ClosedLoopRunner()
    
    # Register README evaluator
    evaluator = ReadmeEvaluator(completion_fn=completion_fn)
    runner.register_evaluator("readme", evaluator)
    
    # Create and register README improver
    runner.create_default_improver("readme", completion_fn)
    
    return runner


def example_evaluate_readme(file_path):
    """Example of evaluating a README file."""
    logger.info(f"Evaluating README file: {file_path}")
    
    # Set up evaluator
    evaluator = setup_evaluator()
    
    # Read the file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Create a sample for evaluation
    sample = {
        "id": "example_readme",
        "content": content,
        "filename": os.path.basename(file_path),
        "metadata": {"repository": "example_repo"}
    }
    
    # Evaluate the sample
    result = evaluator.eval_sample(sample)
    
    # Print the evaluation results
    print("\nEvaluation Results:")
    print(f"Score: {result.result.get('total_score', 0)}/100")
    print(f"Grade: {result.result.get('grade', 'N/A')}")
    print("\nCategory Scores:")
    
    for category, data in result.result.get("category_scores", {}).items():
        category_display = category.replace("_", " ").title()
        score = data.get("score", 0)
        max_score = data.get("max_score", 10)
        print(f"- {category_display}: {score}/{max_score}")
    
    print("\nTop Recommendations:")
    for rec in result.result.get("top_recommendations", []):
        print(f"- {rec}")
    
    return result.result


def example_improve_readme(file_path):
    """Example of improving a README file based on evaluation."""
    logger.info(f"Improving README file: {file_path}")
    
    # Set up runner
    runner = setup_runner()
    
    # Read the file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # First evaluate the README
    eval_result, metrics = runner.evaluate(
        content, 
        "readme",
        filename=os.path.basename(file_path)
    )
    
    logger.info(f"Initial evaluation score: {eval_result.get('total_score', 0)}")
    
    # Improve the README
    improvement_result = runner.improve(
        content, 
        eval_result, 
        "readme",
        filename=os.path.basename(file_path)
    )
    
    # Re-evaluate the improved README
    improved_content = improvement_result.improved_content
    eval_after, metrics_after = runner.evaluate(
        improved_content, 
        "readme",
        filename=os.path.basename(file_path)
    )
    
    # Update the improvement result
    improvement_result.eval_after = eval_after
    
    # Print improvement results
    print("\nImprovement Results:")
    print(improvement_result.format_report())
    
    # Save improved README
    output_path = f"{os.path.splitext(file_path)[0]}_improved.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(improved_content)
    
    logger.info(f"Improved README saved to: {output_path}")
    
    return improvement_result


def example_run_cycle(file_path, iterations=3):
    """Example of running a complete improvement cycle."""
    logger.info(f"Running improvement cycle for: {file_path}")
    
    # Set up runner
    runner = setup_runner()
    
    # Read the file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Run improvement cycle
    cycle_result = runner.run_cycle(
        content, 
        "readme",
        max_iterations=iterations,
        min_improvement=1.0,
        filename=os.path.basename(file_path),
        save_results=True
    )
    
    # Print cycle results
    print("\nImprovement Cycle Results:")
    print(cycle_result.format_report())
    
    # Save final improved content
    output_path = f"{os.path.splitext(file_path)[0]}_cycle_improved.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cycle_result.final_content)
    
    logger.info(f"Final improved content saved to: {output_path}")
    
    return cycle_result


def main():
    """Main entry point."""
    # Path to README file
    readme_path = "README.md"
    
    # Check if file exists
    if not os.path.exists(readme_path):
        # Try to find a README in the current directory
        for file in os.listdir():
            if file.lower() == "readme.md":
                readme_path = file
                break
        else:
            # Create a simple README for demonstration
            readme_path = "example_readme.md"
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write("# Example Project\n\nThis is a simple example README.\n")
    
    # Run examples
    try:
        # Simple evaluation
        print("\n===== EVALUATING README =====")
        evaluation_result = example_evaluate_readme(readme_path)
        
        # Simple improvement
        print("\n===== IMPROVING README =====")
        improvement_result = example_improve_readme(readme_path)
        
        # Run improvement cycle
        print("\n===== RUNNING IMPROVEMENT CYCLE =====")
        cycle_result = example_run_cycle(readme_path, iterations=2)
        
        # Print final metrics
        print("\n===== FINAL METRICS =====")
        initial_score = cycle_result.metrics.get("initial_score", 0)
        final_score = cycle_result.metrics.get("final_score", 0)
        improvement = cycle_result.metrics.get("total_improvement", 0)
        
        print(f"Initial Score: {initial_score}")
        print(f"Final Score: {final_score}")
        print(f"Total Improvement: {improvement:+.1f} points")
        
    except Exception as e:
        logger.error(f"Error in example: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
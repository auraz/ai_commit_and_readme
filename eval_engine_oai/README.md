# Document Evaluation Engine (OpenAI Evals-based)

A closed-loop documentation evaluation and improvement system built with the architectural patterns from OpenAI Evals. This system automatically evaluates documentation quality, generates improvements, and tracks progress through multiple iterations.

## Overview

This package provides:

- **Document Evaluation**: Assessment of documentation quality against standardized criteria
- **Document Improvement**: AI-driven improvement of documentation based on evaluation results
- **Closed-Loop Workflow**: Complete cycle of evaluation → improvement → re-evaluation
- **Metrics Tracking**: Comprehensive metrics to track improvements over time

## Installation

```bash
# Clone the repository and install
git clone https://github.com/yourusername/ai_commit_and_readme.git
cd ai_commit_and_readme
pip install -e .

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

## Quick Start

### Evaluating a Document

```python
from ai_commit_and_readme.eval_engine_oai import evaluate_document

# Evaluate a README file
with open("README.md", "r") as f:
    content = f.read()
    
evaluation_result, metrics = evaluate_document(
    content, 
    doc_type="readme", 
    model="gpt-4"
)

print(f"Score: {evaluation_result['total_score']}/100")
print(f"Grade: {evaluation_result['grade']}")
```

### Improving a Document

```python
from ai_commit_and_readme.eval_engine_oai import evaluate_document, improve_document

# First evaluate
with open("README.md", "r") as f:
    content = f.read()
    
evaluation_result, _ = evaluate_document(content, doc_type="readme")

# Then improve based on evaluation results
improved_content, improvement_details = improve_document(
    content, 
    evaluation_result, 
    doc_type="readme"
)

# Save improved content
with open("README.improved.md", "w") as f:
    f.write(improved_content)
```

### Running a Complete Improvement Cycle

```python
from ai_commit_and_readme.eval_engine_oai import run_improvement_cycle

with open("README.md", "r") as f:
    content = f.read()

improved_content, cycle_results = run_improvement_cycle(
    content,
    doc_type="readme",
    max_iterations=3,
    min_improvement=1.0,
    target_score=90
)

# Save final improved content
with open("README.improved.md", "w") as f:
    f.write(improved_content)
```

## Command Line Interface

The package provides a command-line interface for easy use:

```bash
# Evaluate a document
python -m ai_commit_and_readme.eval_engine_oai.cli evaluate README.md --output eval_report.md

# Improve a document
python -m ai_commit_and_readme.eval_engine_oai.cli improve README.md --output README.improved.md

# Run a complete improvement cycle
python -m ai_commit_and_readme.eval_engine_oai.cli run-cycle README.md --iterations 3 --output README.improved.md
```

### Available Commands

- `evaluate`: Evaluate the quality of a document
- `improve`: Generate an improved version of a document
- `run-cycle`: Run a complete evaluation-improvement cycle
- `list`: List available document types and models

## Architecture

This implementation follows the architectural patterns from OpenAI Evals with three primary components:

1. **DocEvaluator**: Assesses documentation quality against standardized criteria
2. **DocImprover**: Generates improved content based on evaluation results
3. **ClosedLoopRunner**: Orchestrates the evaluation-improvement cycle

## Document Types

The system supports different document types with specialized evaluation criteria:

- `readme`: README file evaluation (optimized for project documentation)
- `generic`: Generic markdown document evaluation

## Models and Configuration

By default, the system uses:

- `gpt-4` for evaluation (high precision)
- `gpt-4` for improvement (high creativity)

You can customize models and other parameters through the Python API or CLI arguments.

## Customization

You can customize evaluation criteria, improvement prompts, and workflow parameters:

```python
from ai_commit_and_readme.eval_engine_oai import DocEvaluator, DocImprover, ClosedLoopRunner

# Create a custom evaluator
evaluator = DocEvaluator(
    model="gpt-4",
    temperature=0.2,
    cache_results=True
)

# Create a custom improver
improver = DocImprover(
    model="gpt-4",
    temperature=0.7
)

# Create a runner with custom components
runner = ClosedLoopRunner(
    evaluator=evaluator,
    improver=improver,
    results_dir="custom_results"
)

# Run custom cycle
cycle_result = runner.run_cycle(
    content,
    doc_type="readme",
    max_iterations=5,
    min_improvement=0.5,
    target_score=95
)
```

## License

MIT
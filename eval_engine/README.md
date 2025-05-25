# Documentation Eval Engine

A closed-loop evaluation and improvement framework for documentation quality, built on the OpenAI Evals framework architecture.

## Overview

Built on the OpenAI Evals framework architecture, this system provides automated evaluation and improvement of documentation assets, implementing a continuous improvement loop:

1. **Evaluate**: Assess documentation quality using standardized criteria
2. **Improve**: Generate targeted improvements based on evaluation results
3. **Re-evaluate**: Measure improvement impact and identify areas for further enhancement
4. **Repeat**: Continue the cycle until quality thresholds are met or improvement plateaus

## Features

- Built on OpenAI Evals framework architecture
- Specialized evaluation criteria for different documentation types (README, wiki, API docs, etc.)
- Customizable evaluation scoring with weighted categories
- Persistent tracking of improvement history
- Closed-loop workflow for continuous enhancement
- Support for batch processing of multiple documents

## Installation

```bash
# From project root
pip install -e .
```

## Quick Start

```python
import openai
from ai_commit_and_readme.eval_engine.evals.base import CompletionFn
from ai_commit_and_readme.eval_engine.evals.readme_eval import ReadmeEvaluator
from ai_commit_and_readme.eval_engine.runner import ClosedLoopRunner, Improver

# Setup OpenAI client and completion function
client = openai.OpenAI(api_key="your-api-key")
completion_fn = CompletionFn(client, model="gpt-4")

# Initialize runner and register evaluators
runner = ClosedLoopRunner()
runner.register_evaluator("readme", ReadmeEvaluator(completion_fn=completion_fn))
runner.create_default_improver("readme", completion_fn)

# Simple evaluation
with open("README.md", "r") as f:
    content = f.read()
    
eval_result, metrics = runner.evaluate(
    content, 
    "readme", 
    filename="README.md"
)
print(f"Documentation Score: {eval_result['total_score']}/100")

# Simple improvement
improvement_result = runner.improve(
    content, 
    eval_result, 
    "readme"
)
print(improvement_result.format_report())

# Run complete improvement cycle
cycle_result = runner.run_cycle(
    content, 
    "readme",
    max_iterations=3
)
print(cycle_result.format_report())

# Save improved content
with open("README.improved.md", "w") as f:
    f.write(cycle_result.final_content)
```

## Command Line Usage

```bash
# Evaluate a single file
python -m ai_commit_and_readme.eval_engine.cli evaluate README.md --type readme --output eval_report.md

# Improve a file
python -m ai_commit_and_readme.eval_engine.cli improve README.md --output README.improved.md --report improvement_report.md

# Run complete improvement cycle
python -m ai_commit_and_readme.eval_engine.cli run-cycle README.md --iterations 3 --output README.improved.md --min-improvement 1.0 --target-score 90 --save-results

# Evaluate all docs in a directory
python -m ai_commit_and_readme.eval_engine.cli evaluate --dir ./wiki/ --type wiki --output-dir ./eval_results/

# List available evaluators and improvers
python -m ai_commit_and_readme.eval_engine.cli list
```

## Architecture

Based on the OpenAI Evals framework, the system consists of four primary components:

1. **Evaluators**: Document-specific assessment modules that evaluate quality using the BaseEvaluator interface
2. **Improvers**: Enhancement modules that generate improved content based on evaluation results
3. **Registry**: Central repository for evaluators, improvers, and evaluation specifications
4. **Closed-Loop Runner**: Orchestrator that manages the evaluation-improvement cycle

Evaluations are performed against standardized criteria including:
- Content quality and accuracy
- Structure and organization
- Completeness and coverage
- Technical accuracy and correctness
- User-friendliness and accessibility
- Formatting and presentation
- Cross-referencing and linking

## Custom Evaluators

Create custom evaluators by extending the OpenAI Evals-based `BaseEvaluator` class:

```python
from typing import TypedDict, Dict, Any, Optional
from ai_commit_and_readme.eval_engine.evals.base import BaseEvaluator, EvalSpec, SampleResult

# Define types for your evaluator
class MyDocumentSample(TypedDict):
    id: str
    content: str
    metadata: Dict[str, Any]

class MyEvalResult(TypedDict):
    total_score: int
    category_scores: Dict[str, Dict[str, Any]]
    recommendations: list[str]

class CustomEvaluator(BaseEvaluator[MyDocumentSample, None, MyEvalResult]):
    def __init__(self, completion_fn=None):
        spec = EvalSpec(
            id="custom_evaluator",
            name="Custom Document Evaluator",
            description="Evaluates specialized documentation against custom criteria",
            prompt_template="Your evaluation prompt template here...",
            metrics=["total_score", "clarity", "completeness"]
        )
        super().__init__(spec, completion_fn)
    
    def eval_sample(self, sample: MyDocumentSample, model_output: Optional[None] = None) -> SampleResult[MyEvalResult]:
        # Implement evaluation logic using the completion function
        prompt = self.prepare_prompt(sample["content"])
        response = self.completion_fn(prompt, response_format={"type": "json_object"})
        
        # Parse results and calculate metrics
        # ...
        
        return SampleResult(
            spec=self.spec,
            sample_id=sample["id"],
            result=result,
            metrics=metrics
        )
```

The framework also supports:

```python
# Creating custom improvers
from ai_commit_and_readme.eval_engine.runner import Improver

# Custom prompt template for improvements
prompt_template = """
Your custom improvement prompt...
{content}
{evaluation_result}
"""

# Create an improver with custom prompt
improver = Improver(completion_fn, prompt_template, "custom_improver")
runner.register_improver("custom_doc", improver)
```

## License

MIT
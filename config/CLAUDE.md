# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`ai_commit_and_readme` is an AI-powered tool that automates commit message generation and documentation enrichment using OpenAI's API. It analyzes git diffs to generate meaningful commit messages and automatically updates README.md and Wiki documentation based on code changes.

## Key Commands

### Development Setup

```bash
make dev-install    # Set up development environment with all dependencies
```

### Code Quality

```bash
make lint           # Run ruff linter
make format         # Format code with ruff
make check          # Run both lint and format
```

### Testing

```bash
make coverage       # Run tests with coverage report (also runs lint/format)
```

### Build & Deploy

```bash
make build          # Build distribution packages
make upload-pypi    # Upload to PyPI
make tag            # Create git tag for current version
make github-release # Create GitHub release
make deploy         # Full deployment: changelog, build, PyPI, tag, release
```

### Workflow Commands

```bash
make cm             # Stage all changes, run AI enrichment, commit, and push
```

## Architecture

The project follows a modular pipeline architecture:

1. **Git Content Extraction** (`tools.py`): Interfaces with git to extract diffs and file contents
2. **Text Processing Pipeline** (`tools.py`): Filters and truncates content for API constraints
3. **OpenAI API Client** (`tools.py`): Manages API communication with error handling
4. **CLI Interface** (`cli.py`): Entry point with command parsing and workflow orchestration
5. **Evaluation System** (`evals/`): Specialized evaluators for README and Wiki documentation

Key modules:

- `main.py`: Core enrichment pipeline logic
- `tools.py`: Utility functions for git operations, AI interactions, and file handling
- `evals/readme_eval.py` & `evals/wiki_eval.py`: Documentation quality evaluation
- `prompts/`: AI prompt templates for different operations

## Important Configuration

- **OpenAI API Key**: Required environment variable `OPENAI_API_KEY`
- **Python Version**: Requires Python >=3.7
- **Main Dependencies**: openai, tiktoken, rich, pipetools

## Testing Approach

The project uses pytest for testing. Test files are located in `ai_commit_and_readme/tests/` and cover:

- CLI functionality (`test_cli.py`)
- Main pipeline logic (`test_main.py`)
- Utility tools (`test_tools.py`)
- Evaluators (`test_evaluators.py`)

Run tests with coverage using `make coverage`.

### instructions

- If there is comment in the code, make sure it is inline, and goes after code
- Line length is 170
- If whole expression can sit in single string, do not split it into multiline one.
- Use one liners for all docstrings
- Remove multi line comments in the code, if they are needed, create function
- Add type annotations
- Be consice and refactor code
- Update README.md in each commit
- Use Just https://just.systems/ as command runner
- use ruff as linter
- use uv instaead pip or twine
- uses Miller https://miller.readthedocs.io/en/6.13.0/
- each function and module and file should have 1-line docstring
- used functional programming style where possible
- avoid one-line functions
- commit after each change
- update documentation when commit
- always use virtualenv
- do not use fallbacks
- do not support backward compatibility
- use short and consice function and method names
- avoid redefinitions
- promts max lenghs is 100
- tests should be located within respectful moodule
- when writing python or justfile code, be pythonic

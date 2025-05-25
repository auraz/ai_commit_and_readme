# Command runner for ai_commit_and_readme

# Default recipe
default:
    @just --list

# Install project
install:
    uv venv
    uv pip install .
    brew install aicommit

# Development install
dev:
    uv venv  
    uv pip install -e ".[dev]"

# Run linter and formatter
check:
    ruff check --fix .
    ruff format .

# Run tests with coverage
test: check
    coverage run -m pytest
    coverage report
    coverage html

# Clean build artifacts
clean:
    rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov
    find . -type d -name "__pycache__" -exec rm -rf {} +

# Commit with AI
cm:
    git add .
    @if git diff --cached --quiet; then echo "No changes to commit"; else just enrich && aicommit; fi
    git push

# Build packages
build: clean
    uv build

# Deploy to PyPI
deploy: build
    uv publish
    git tag -a v$(just version) -m "Release v$(just version)"
    git push origin v$(just version)
    gh release create v$(just version) --title "v$(just version)" --notes "Release v$(just version)" ./dist/*

# Get current version
version:
    @grep -m1 'version = ' pyproject.toml | cut -d'"' -f2

# Enrich README and Wiki with AI
enrich:
    python -m ai_commit_and_readme.process

# Generate summary of changes
summary:
    python -c "from ai_commit_and_readme.process import generate_summary; print(generate_summary())"

# Evaluate document quality
eval path:
    python -c "from ai_commit_and_readme.doc_eval import evaluate_doc; _, report = evaluate_doc('{{path}}'); print(report)"

# Evaluate document with extra criteria
eval-with-prompt path prompt:
    python -c "from ai_commit_and_readme.doc_eval import evaluate_doc; _, report = evaluate_doc('{{path}}', extra_prompt='{{prompt}}'); print(report)"

# Evaluate all documents in directory
eval-all path:
    #!/usr/bin/env python3
    from ai_commit_and_readme.doc_eval import evaluate_all
    results = evaluate_all("{{path}}")
    for filename, (score, _) in sorted(results.items(), key=lambda x: x[1][0], reverse=True):
        print(f"{filename}: {score}")
    print(f"\nEvaluated {len(results)} documents")
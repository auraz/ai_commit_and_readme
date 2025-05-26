# Command runner for autodoc_ai

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
    #!/usr/bin/env python3
    import sys
    from autodoc_ai.crews.pipeline import PipelineCrew
    crew = PipelineCrew()
    result = crew.run()
    if not result.get("success"):
        print(f"Enrichment failed: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

# Generate summary of changes
summary:
    python -c "from autodoc_ai.crews.pipeline import PipelineCrew; crew = PipelineCrew(); print(crew.generate_summary())"

# Evaluate document quality
eval path:
    python -c "from autodoc_ai.crews.evaluation import EvaluationCrew; crew = EvaluationCrew(); _, report = crew.run('{{path}}'); print(report)"

# Evaluate document with extra criteria
eval-with-prompt path prompt:
    python -c "from autodoc_ai.crews.evaluation import EvaluationCrew; crew = EvaluationCrew(); _, report = crew.run('{{path}}', extra_criteria='{{prompt}}'); print(report)"

# Evaluate all documents in directory
eval-all path:
    #!/usr/bin/env python3
    from pathlib import Path
    from autodoc_ai.crews.evaluation import EvaluationCrew
    crew = EvaluationCrew()
    results = {}
    for file_path in Path("{{path}}").glob("**/*.md"):
        if file_path.is_file():
            score, _ = crew.run(str(file_path))
            results[file_path.name] = score
    for filename, score in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"{filename}: {score}")
    print(f"\nEvaluated {len(results)} documents")

# Improve document iteratively
improve path:
    python -c "from autodoc_ai.crews.improvement import ImprovementCrew; import json; crew = ImprovementCrew(); print(json.dumps(crew.run('{{path}}'), indent=2))"

# Improve document with custom settings
improve-with-settings path target_score="85" max_iterations="3":
    python -c "from autodoc_ai.crews.improvement import ImprovementCrew; import json; crew = ImprovementCrew(target_score={{target_score}}, max_iterations={{max_iterations}}); print(json.dumps(crew.run('{{path}}'), indent=2))"

# Improve all documents in directory
improve-all path:
    #!/usr/bin/env python3
    from pathlib import Path
    from autodoc_ai.crews.improvement import ImprovementCrew
    crew = ImprovementCrew()
    for file_path in Path("{{path}}").glob("**/*.md"):
        if file_path.is_file():
            print(f"\n{'='*60}")
            print(f"Processing: {file_path.name}")
            print('='*60)
            result = crew.run(str(file_path))
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Improved from {result['initial_score']}% to {result['final_score']}%")
                print(f"   Iterations: {result['iterations']}")
                print(f"   Target reached: {'Yes' if result['target_reached'] else 'No'}")
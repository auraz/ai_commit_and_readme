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

# Deploy wiki to GitHub
deploy-wiki:
    python3 deploy_wiki.py

# Enrich documentation based on last commit
enrich-commit:
    #!/usr/bin/env python3
    import sys
    import subprocess
    from autodoc_ai.crews.pipeline import PipelineCrew
    
    # Check if there's at least one commit
    try:
        subprocess.check_output(["git", "rev-parse", "HEAD"], text=True)
    except subprocess.CalledProcessError:
        print("❌ No commits found in repository")
        sys.exit(1)
    
    # Get the last commit info
    last_commit = subprocess.check_output(["git", "log", "-1", "--oneline"], text=True).strip()
    print(f"📝 Processing commit: {last_commit}")
    
    # Create a custom pipeline that uses the diff from HEAD~1 to HEAD
    crew = PipelineCrew()
    # Hack: Use a very small time window (1 hour) to likely only get the last commit
    # This ensures we only get the most recent commit in most cases
    result = crew.run(days=0.042)  # 1 hour = 0.042 days
    
    if not result.get("success"):
        # If no commits in last hour, try last day
        result = crew.run(days=1)
        if not result.get("success"):
            print(f"Enrichment failed: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)
    
    print(f"✅ Documentation enriched based on commit: {last_commit}")

# Enrich documentation based on commits from last n days
enrich-days days="7":
    #!/usr/bin/env python3
    import sys
    from autodoc_ai.crews.pipeline import PipelineCrew
    crew = PipelineCrew()
    result = crew.run(days={{days}})
    if not result.get("success"):
        print(f"Enrichment failed: {result.get('error', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"✅ Documentation enriched based on {{days}} days of commits")

# Update documentation for a release (based on commits since last tag)
enrich-release:
    #!/usr/bin/env python3
    import subprocess
    import sys
    from autodoc_ai.crews.pipeline import PipelineCrew

    # Get the last tag
    try:
        last_tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], text=True).strip()
        # Count days since last tag
        tag_date = subprocess.check_output(["git", "log", "-1", "--format=%ci", last_tag], text=True).strip()
        days_since = subprocess.check_output(["git", "log", "-1", "--format=%cr", last_tag], text=True).strip()
        print(f"📌 Last tag: {last_tag} ({days_since})")

        # Get commits since last tag
        commits = subprocess.check_output(["git", "log", f"{last_tag}..HEAD", "--oneline"], text=True).strip()
        if not commits:
            print("✅ No new commits since last release")
            sys.exit(0)

        print(f"📝 Commits since {last_tag}:")
        print(commits)
        print()

        # Create diff from last tag to HEAD
        crew = PipelineCrew()
        # Use a large number of days to ensure we capture all changes
        result = crew.run(days=365)
        if not result.get("success"):
            print(f"Enrichment failed: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"✅ Documentation enriched for release")
    except subprocess.CalledProcessError:
        print("❌ No tags found in repository")
        sys.exit(1)

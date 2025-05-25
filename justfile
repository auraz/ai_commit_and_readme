# Command runner configuration for ai_commit_and_readme

# Set shell for Windows compatibility
set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# Colors
GREEN := "\\033[92m"
CYAN := "\\033[96m"
YELLOW := "\\033[93m"
RESET := "\\033[0m"

# Default recipe
default:
    @just --list

# Install project
install:
    uv venv
    uv pip install .
    brew install aicommit

# Development install
dev-install:
    uv venv
    uv pip install -r requirements-dev.txt
    @echo "{{GREEN}}✅ Development environment ready!{{RESET}}"

# Run linter
lint:
    @echo "{{CYAN}}🔍 Running linter checks...{{RESET}}"
    ruff check .
    @echo "{{GREEN}}✅ Linting passed!{{RESET}}"

# Format code
format:
    @echo "{{CYAN}}🎨 Formatting code...{{RESET}}"
    ruff format .
    @echo "{{GREEN}}✅ Code formatted!{{RESET}}"

# Run all checks
check: lint format
    @echo "{{GREEN}}✅ All checks passed!{{RESET}}"

# Clean build artifacts
clean:
    rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache
    find . -type d -name "__pycache__" -exec rm -rf {} +

# Commit with AI
cm:
    @echo "{{CYAN}}ℹ️ This command will stage all changes, run AI enrichment, generate an AI commit message, and push to the remote repository.{{RESET}}"
    @echo "🔄 Staging all changes..."
    git add .
    @if git diff --cached --quiet; then \
        echo "{{YELLOW}}✅ No staged changes detected. Skipping enrichment and commit.{{RESET}}"; \
    else \
        echo "{{CYAN}}🤖 Running AI enrichment...{{RESET}}"; \
        ai-commit-and-readme; \
        echo "{{CYAN}}✍️  Generating AI commit message...{{RESET}}"; \
        aicommit; \
    fi
    @echo "{{GREEN}}🚀 Pushing to remote repository...{{RESET}}"
    git push

# Run tests with coverage
coverage:
    @echo "{{CYAN}}📊 Running test coverage...{{RESET}}"
    ruff check --fix .
    ruff format
    coverage run -m pytest
    coverage report
    coverage html
    @echo "{{GREEN}}✅ Coverage report generated!{{RESET}}"

# Deploy wiki
deploy-wiki:
    git clone https://github.com/auraz/ai_commit_and_readme.wiki.git tmp_wiki
    cp -r wiki/* tmp_wiki/
    cd tmp_wiki && git add . && (git commit -m "Update wiki docs" || true) && git push
    rm -rf tmp_wiki

# Get current version
version:
    @grep -m1 'version = ' pyproject.toml | cut -d'"' -f2

# Generate changelog
changelog:
    #!/usr/bin/env bash
    set -euo pipefail
    VERSION=$(just version)
    echo "{{CYAN}}📝 Generating changelog for v${VERSION} from git commits...{{RESET}}"
    echo "{{CYAN}}🔍 Finding previous git tag...{{RESET}}"
    PREV_TAG=$(git describe --abbrev=0 --tags 2>/dev/null || echo "")
    if [ -z "${PREV_TAG}" ]; then
        echo "{{YELLOW}}⚠️  No previous tag found. Using all commits.{{RESET}}"
        COMMITS=$(git log --pretty=format:"- %s" --no-merges)
    else
        echo "{{CYAN}}📋 Generating changelog from ${PREV_TAG} to current version...{{RESET}}"
        COMMITS=$(git log ${PREV_TAG}..HEAD --pretty=format:"- %s" --no-merges)
    fi
    if [ -z "${COMMITS}" ]; then
        echo "{{YELLOW}}⚠️  No commits found. Using ai-commit-and-readme to generate summary.{{RESET}}"
        COMMITS="- $(ai-commit-and-readme --summary-only)"
    fi
    tempfile=$(mktemp)
    echo "${COMMITS}" > ${tempfile}
    sed -i.bak "2i\\\\n## v${VERSION}" wiki/Changelog.md
    sed -i.bak "3r ${tempfile}" wiki/Changelog.md
    rm ${tempfile} wiki/Changelog.md.bak*
    echo "{{GREEN}}✅ Changelog updated successfully!{{RESET}}"

# Build packages
build: clean
    @echo "{{CYAN}}🔨 Building packages...{{RESET}}"
    uv build
    @echo "{{GREEN}}✅ Build completed successfully!{{RESET}}"

# Upload to PyPI
upload-pypi: build
    @echo "{{CYAN}}🚀 Uploading to PyPI...{{RESET}}"
    uv publish
    @echo "{{GREEN}}✅ Package successfully deployed to PyPI!{{RESET}}"

# Create git tag
tag:
    #!/usr/bin/env bash
    VERSION=$(just version)
    echo "{{CYAN}}🏷️  Creating git tag v${VERSION}...{{RESET}}"
    git tag -a v${VERSION} -m "Release v${VERSION}"
    git push origin v${VERSION}
    echo "{{GREEN}}✅ Git tag created and pushed!{{RESET}}"

# Create GitHub release
github-release: build tag
    #!/usr/bin/env bash
    VERSION=$(just version)
    echo "{{CYAN}}📝 Creating GitHub release for v${VERSION}...{{RESET}}"
    gh release create v${VERSION} --title "v${VERSION}" --notes "Release v${VERSION}" ./dist/*
    echo "{{GREEN}}✅ GitHub release v${VERSION} created successfully!{{RESET}}"

# Full deployment
deploy: changelog build upload-pypi tag github-release
    @echo "{{CYAN}}📦 Building and deploying package to PyPI...{{RESET}}"
    @echo "{{GREEN}}🎉 Deployment completed successfully!{{RESET}}"
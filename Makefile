.PHONY: install dev-install lint format test clean aicommit venv cm coverage docs deploy-wiki deploy check version changelog build upload-pypi tag github-release

# Define colors
GREEN := \033[92m
CYAN := \033[96m
YELLOW := \033[93m
RESET := \033[0m

install:
	python3 -m venv .venv
	source .venv/bin/activate
	pip install .
	brew install aicommit

dev-install:
	python3 -m venv .venv
	source .venv/bin/activate
	pip install -r requirements-dev.txt
	@echo "$(GREEN)✅ Development environment ready!$(RESET)"

lint:
	@echo "$(CYAN)🔍 Running linter checks...$(RESET)"
	ruff check .
	@echo "$(GREEN)✅ Linting passed!$(RESET)"

format:
	@echo "$(CYAN)🎨 Formatting code...$(RESET)"
	ruff format .
	@echo "$(GREEN)✅ Code formatted!$(RESET)"

check: lint format
	@echo "$(GREEN)✅ All checks passed!$(RESET)"

clean:
	rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

cm:
	@echo "$(CYAN)ℹ️ This command will stage all changes, run AI enrichment, generate an AI commit message, and push to the remote repository.$(RESET)"
	@echo "🔄 Staging all changes..."
	git add .
	@if git diff --cached --quiet; then \
		echo "$(YELLOW)✅ No staged changes detected. Skipping enrichment and commit.$(RESET)"; \
	else \
		echo "$(CYAN)🤖 Running AI enrichment...$(RESET)"; \
		ai-commit-and-readme; \
		echo "$(CYAN)✍️  Generating AI commit message...$(RESET)"; \
		aicommit; \
	fi
	@echo "$(GREEN)🚀 Pushing to remote repository...$(RESET)"
	git push

coverage:
	@echo "$(CYAN)📊 Running test coverage...$(RESET)"
	ruff check --fix .
	ruff format
	coverage run -m pytest
	coverage report
	coverage html
	@echo "$(GREEN)✅ Coverage report generated!$(RESET)"

deploy-wiki:
	git clone https://github.com/auraz/ai_commit_and_readme.wiki.git tmp_wiki
	cp -r wiki/* tmp_wiki/
	cd tmp_wiki && git add . && (git commit -m "Update wiki docs" || true) && git push
	rm -rf tmp_wiki


version:
	$(eval VERSION := $(shell grep -m1 'version = ' pyproject.toml | cut -d'"' -f2))
	@echo "$(CYAN)📌 Current version: $(VERSION)$(RESET)"

changelog: version
	@echo "$(CYAN)📝 Generating changelog for v$(VERSION) from git commits...$(RESET)"
	@echo "$(CYAN)🔍 Finding previous git tag...$(RESET)"
	$(eval PREV_TAG := $(shell git describe --abbrev=0 --tags 2>/dev/null || echo ""))
	@if [ -z "$(PREV_TAG)" ]; then \
		echo "$(YELLOW)⚠️  No previous tag found. Using all commits.$(RESET)"; \
		COMMITS=$$(git log --pretty=format:"- %s" --no-merges); \
	else \
		echo "$(CYAN)📋 Generating changelog from $(PREV_TAG) to current version...$(RESET)"; \
		COMMITS=$$(git log $(PREV_TAG)..HEAD --pretty=format:"- %s" --no-merges); \
	fi; \
	if [ -z "$$COMMITS" ]; then \
		echo "$(YELLOW)⚠️  No commits found. Using ai-commit-and-readme to generate summary.$(RESET)"; \
		COMMITS="- $$(ai-commit-and-readme --summary-only)"; \
	fi; \
	tempfile=$$(mktemp) && echo "$$COMMITS" > $$tempfile && \
	sed -i.bak "2i\\\\n## v$(VERSION)" wiki/Changelog.md && \
	sed -i.bak "3r $$tempfile" wiki/Changelog.md && \
	rm $$tempfile wiki/Changelog.md.bak*
	@echo "$(GREEN)✅ Changelog updated successfully!$(RESET)"

build: clean
	@echo "$(CYAN)🔨 Building packages...$(RESET)"
	python -m build
	@echo "$(CYAN)✅ Verifying package...$(RESET)"
	python -m twine check dist/*
	@echo "$(GREEN)✅ Build completed successfully!$(RESET)"

upload-pypi: build
	@echo "$(CYAN)🚀 Uploading to PyPI...$(RESET)"
	python -m twine upload dist/*
	@echo "$(GREEN)✅ Package successfully deployed to PyPI!$(RESET)"

tag: version
	@echo "$(CYAN)🏷️  Creating git tag v$(VERSION)...$(RESET)"
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	git push origin v$(VERSION)
	@echo "$(GREEN)✅ Git tag created and pushed!$(RESET)"

github-release: version build tag
	@echo "$(CYAN)📝 Creating GitHub release for v$(VERSION)...$(RESET)"
	gh release create v$(VERSION) --title "v$(VERSION)" --notes "Release v$(VERSION)" ./dist/*
	@echo "$(GREEN)✅ GitHub release v$(VERSION) created successfully!$(RESET)"

deploy: version changelog build upload-pypi tag github-release
	@echo "$(CYAN)📦 Building and deploying package to PyPI...$(RESET)"
	@echo "$(GREEN)🎉 Deployment completed successfully!$(RESET)"

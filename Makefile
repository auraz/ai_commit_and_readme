.PHONY: install lint format test clean aicommit venv cm coverage docs deploy-wiki

install:
	python3 -m venv .venv
	source .venv/bin/activate
	pip install .
	brew install aicommit
	@if [ ! -f README.md ]; then touch README.md; fi
	@if [ ! -d wiki ]; then mkdir wiki; fi
	@if [ ! -f wiki/Home.md ]; then touch wiki/Home.md; fi
	@if [ ! -f wiki/Changelog.md ]; then touch wiki/Changelog.md; fi
	@if [ ! -f wiki/Usage.md ]; then touch wiki/Usage.md; fi
	@if [ ! -f wiki/Configuration.md ]; then touch wiki/Configuration.md; fi
	@if [ ! -f wiki/FAQ.md ]; then touch wiki/FAQ.md; fi
	@if [ ! -f wiki/Contributing.md ]; then touch wiki/Contributing.md; fi
	@if [ ! -f wiki/API.md ]; then touch wiki/API.md; fi
	@if [ ! -f wiki/Installation.md ]; then touch wiki/Installation.md; fi

clean:
	rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

cm:
	@echo "\033[96mℹ️ This command will stage all changes, run AI enrichment, generate an AI commit message, and push to the remote repository.\033[0m"
	@echo "🔄 Staging all changes..."
	git add .
	@if git diff --cached --quiet; then \
		echo "\033[93m✅ No staged changes detected. Skipping enrichment and commit.\033[0m"; \
	else \
		echo "\033[96m🤖 Running AI enrichment...\033[0m"; \
		ai-commit-and-readme; \
		echo "\033[96m✍️  Generating AI commit message...\033[0m"; \
		aicommit; \
	fi
	@echo "\033[92m🚀 Pushing to remote repository...\033[0m"
	git push

coverage:
	ruff check --fix .
	ruff format
	coverage run -m pytest
	coverage report
	coverage html

deploy-wiki:
	git clone https://github.com/auraz/ai_commit_and_readme.wiki.git tmp_wiki
	cp -r wiki/* tmp_wiki/
	cd tmp_wiki && git add . && (git commit -m "Update wiki docs" || true) && git push
	rm -rf tmp_wiki

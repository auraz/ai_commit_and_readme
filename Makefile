.PHONY: install lint format test clean aicommit

install:
	pip install .
	make aicommit

aicommit:
	brew install aicommit

lint:
	ruff ai_commit_and_readme

format:
	ruff format ai_commit_and_readme

test:
	pytest

clean:
	rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

cm:
	git add . && aicommit --autopush

.PHONY: install lint format test clean aicommit venv cm coverage coverage-report

install:
	pip install .
	make aicommit

aicommit:
	brew install aicommit

lint:
	ruff check .

format:
	ruff format ai_commit_and_readme

test:
	pytest

clean:
	rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

cm:
	git add .
	python -m ai_commit_and_readme.main
	aicommit
	git push

venv:
	python3 -m venv .venv

coverage:
	coverage run -m pytest

coverage-report:
	coverage report
	coverage html

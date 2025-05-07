.PHONY: install lint format test clean aicommit venv cm coverage docs deploy-wiki

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
	ai-commit-and-readme
	aicommit
	git push

venv:
	python3 -m venv .venv

coverage:
	coverage run -m pytest
	coverage report
	coverage html

docs:
	#todo

deploy-wiki:
	git clone https://github.com/auraz/ai_commit_and_readme.wiki.git tmp_wiki
	cp -r wiki/* tmp_wiki/
	cd tmp_wiki && git add . && git commit -m "Update wiki docs" && git push
	rm -rf tmp_wiki

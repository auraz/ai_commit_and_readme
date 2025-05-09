.PHONY: install lint format test clean aicommit venv cm coverage docs deploy-wiki

install:
	python3 -m venv .venv
	source .venv/bin/activate
	pip install .
	brew install aicommit

clean:
	rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

cm:
	git add .

	if git diff --cached --quiet; then \
		echo "No staged changes, skipping aicommit."; \
	else \
		ai-commit-and-readme; \
        aicommit; \
	fi
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
	cd tmp_wiki && git add . && git commit -m "Update wiki docs" && git push
	rm -rf tmp_wiki

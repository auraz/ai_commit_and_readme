# Deploying to PyPI

This guide covers the process of deploying the `autodoc_ai` package to the Python Package Index (PyPI), making it available for installation via pip.

## Prerequisites

Before deploying to PyPI, ensure you have the following:

1. A PyPI account - register at [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. Required Python packaging tools:
   ```bash
   pip install build twine
   ```
3. (Optional) A TestPyPI account for testing - register at [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)

## Version Management

Before each release, update the version number in:

1. `pyproject.toml`:
   ```toml
   [project]
   name = "autodoc_ai"
   version = "1.0.2"  # Update this version
   ```

2. `setup.py`:
   ```python
   setup(
       name="autodoc_ai",
       version="1.0.2",  # Update this version to match pyproject.toml
       # ...
   )
   ```

Follow [Semantic Versioning](https://semver.org/) guidelines:
- MAJOR version for incompatible API changes
- MINOR version for backward-compatible functionality
- PATCH version for backward-compatible bug fixes

## Preparing for Release

1. Ensure all tests pass:
   ```bash
   make coverage
   ```

2. Update the changelog in `wiki/Changelog.md` with the new version and changes

3. Clean previous build artifacts:
   ```bash
   make clean
   # or manually:
   rm -rf dist build *.egg-info
   ```

## Building Distribution Packages

Build both wheel and source distribution:

```bash
python -m build
```

This will create the distribution files in the `dist/` directory:
- `autodoc_ai-x.y.z-py3-none-any.whl` (wheel package)
- `autodoc_ai-x.y.z.tar.gz` (source archive)

## Testing with TestPyPI (Recommended)

Before publishing to the main PyPI repository, it's good practice to test with TestPyPI:

1. Upload to TestPyPI:
   ```bash
   twine upload --repository-url https://test.pypi.org/legacy/ dist/*
   ```

2. Install from TestPyPI in a clean environment:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --no-deps autodoc_ai
   pip install openai tiktoken rich pipetools  # Install dependencies separately
   ```

3. Verify the package works correctly

## Deploying to PyPI

Once you've verified everything works correctly:

```bash
twine upload dist/*
```

You'll be prompted for your PyPI username and password. For automation, you can use environment variables:
```bash
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-xxxx twine upload dist/*
```

## Post-Deployment Verification

Verify the package can be installed from PyPI:

```bash
pip install --no-cache-dir autodoc_ai
```

Test that the installed package works correctly:

```bash
# Run a basic test with your CLI
autodoc-ai --help
```

After deployment, confirm that:
1. The changelog has been updated with your changes
2. The GitHub release has been created with the correct version
3. The Git tag has been created and pushed

## GitHub Releases

As part of the deployment process, a GitHub release is now automatically created. This provides a convenient way to:

1. Tag the code at a specific version
2. Provide release notes
3. Make distribution artifacts available for download directly from GitHub

## Changelog Updates

The deployment process now fully automates changelog generation using git commit history and AI:

1. The current version is automatically extracted from `pyproject.toml`
2. The system finds the previous git tag (or uses all commits if no tag exists)
3. Commit messages between the previous tag and current HEAD are extracted
4. If no commits are found, the tool automatically invokes `autodoc-ai --summary-only` 
   - This feature uses AI to analyze code changes and generate a meaningful summary
   - It's completely automated and requires no user input
5. The changelog is automatically updated with the new version and generated entries
6. Changes are formatted following the project's existing changelog format

This ensures the changelog is always updated with each release, maintains a consistent format, and provides meaningful, human-readable descriptions of changes even when commit messages aren't ideal.

### Prerequisites

1. The GitHub CLI (`gh`) must be installed:
   ```bash
   # For macOS
   brew install gh
   
   # For Linux
   sudo apt install gh
   
   # For Windows
   choco install gh
   ```

2. You must be authenticated with GitHub:
   ```bash
   gh auth login
   ```

3. You must have write permissions to the GitHub repository

### Release Process

The GitHub release process:

1. Extracts the current version from `pyproject.toml`
2. Creates a Git tag for the version (e.g., v1.0.4)
3. Pushes the tag to GitHub
4. Creates a GitHub release with the built distribution files attached

## Modular Deployment Commands

The project includes a set of modular commands that can be used independently or combined as part of the full deployment process:

### Individual Commands

1. **`version`**: Extracts and displays the current version from `pyproject.toml`
   ```make
   version:
       $(eval VERSION := $(shell grep -m1 'version = ' pyproject.toml | cut -d'"' -f2))
       @echo "$(CYAN)📌 Current version: $(VERSION)$(RESET)"
   ```

2. **`changelog`**: Automatically updates the changelog with commits since the last tag
   ```make
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
           echo "$(YELLOW)⚠️  No commits found. Using AI to generate summary.$(RESET)"; \
           COMMITS="- $$(autodoc-ai --summary-only)"; \
       fi; \
       tempfile=$$(mktemp) && echo "$$COMMITS" > $$tempfile && \
       sed -i.bak "2i\\\\n## v$(VERSION)" wiki/Changelog.md && \
       sed -i.bak "3r $$tempfile" wiki/Changelog.md && \
       rm $$tempfile wiki/Changelog.md.bak*
       @echo "$(GREEN)✅ Changelog updated successfully!$(RESET)"
   ```

3. **`build`**: Cleans previous builds and builds new distribution packages
   ```make
   build: clean
       @echo "$(CYAN)🔨 Building packages...$(RESET)"
       python -m build
       @echo "$(CYAN)✅ Verifying package...$(RESET)"
       python -m twine check dist/*
       @echo "$(GREEN)✅ Build completed successfully!$(RESET)"
   ```

4. **`upload-pypi`**: Uploads the built packages to PyPI
   ```make
   upload-pypi: build
       @echo "$(CYAN)🚀 Uploading to PyPI...$(RESET)"
       python -m twine upload dist/*
       @echo "$(GREEN)✅ Package successfully deployed to PyPI!$(RESET)"
   ```

5. **`tag`**: Creates a git tag for the current version and pushes it
   ```make
   tag: version
       @echo "$(CYAN)🏷️  Creating git tag v$(VERSION)...$(RESET)"
       git tag -a v$(VERSION) -m "Release v$(VERSION)"
       git push origin v$(VERSION)
       @echo "$(GREEN)✅ Git tag created and pushed!$(RESET)"
   ```

6. **`github-release`**: Creates a GitHub release with the built packages
   ```make
   github-release: version build tag
       @echo "$(CYAN)📝 Creating GitHub release for v$(VERSION)...$(RESET)"
       gh release create v$(VERSION) --title "v$(VERSION)" --notes "Release v$(VERSION)" ./dist/*
       @echo "$(GREEN)✅ GitHub release v$(VERSION) created successfully!$(RESET)"
   ```

### Combined Deployment Command

The `deploy` command combines all the individual commands:

```make
deploy: version changelog build upload-pypi tag github-release
    @echo "$(CYAN)📦 Building and deploying package to PyPI...$(RESET)"
    @echo "$(GREEN)🎉 Deployment completed successfully!$(RESET)"
```

You can also add these additional individual targets:

```make
# Define colors
GREEN := \033[92m
CYAN := \033[96m
YELLOW := \033[93m
RESET := \033[0m

deploy-test-pypi: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

## CI/CD Integration

For GitHub Actions, you can add a workflow file `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build and publish
      env:
        TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
        TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
      run: |
        python -m build
        twine upload dist/*
```

Remember to set `PYPI_USERNAME` and `PYPI_PASSWORD` secrets in your GitHub repository settings.

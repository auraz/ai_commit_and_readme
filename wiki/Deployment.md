# Deploying to PyPI

This guide covers the process of deploying the `ai_commit_and_readme` package to the Python Package Index (PyPI), making it available for installation via pip.

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
   name = "ai_commit_and_readme"
   version = "1.0.1"  # Update this version
   ```

2. `setup.py`:
   ```python
   setup(
       name="ai_commit_and_readme",
       version="0.1.0",  # Update this version to match pyproject.toml
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
- `ai_commit_and_readme-x.y.z-py3-none-any.whl` (wheel package)
- `ai_commit_and_readme-x.y.z.tar.gz` (source archive)

## Testing with TestPyPI (Recommended)

Before publishing to the main PyPI repository, it's good practice to test with TestPyPI:

1. Upload to TestPyPI:
   ```bash
   twine upload --repository-url https://test.pypi.org/legacy/ dist/*
   ```

2. Install from TestPyPI in a clean environment:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --no-deps ai_commit_and_readme
   pip install ai_commit_and_readme[test]  # If you have test extras
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
pip install --no-cache-dir ai_commit_and_readme
```

Test that the installed package works correctly:

```bash
# Run a basic test with your CLI
ai-commit-and-readme --help
```

## Automating Deployment

Add this target to your Makefile:

```make
deploy-pypi: clean
	python -m build
	twine upload dist/*

deploy-test-pypi: clean
	python -m build
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

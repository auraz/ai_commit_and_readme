# Continuous Integration and Continuous Deployment (CI/CD)

This guide explains the CI/CD setup for the `ai_commit_and_readme` project, helping contributors understand how automated testing and deployment works.

## Overview

Continuous Integration (CI) automatically builds and tests code changes, while Continuous Deployment (CD) automatically deploys approved changes to production environments. For `ai_commit_and_readme`, we use GitHub Actions to automate these processes.

## CI/CD Pipeline Architecture

Our CI/CD pipeline follows this workflow:

1. **Code Push/PR**: Triggered when code is pushed or a pull request is opened
2. **Static Analysis**: Code quality checks using Ruff and type checking with Pyright
3. **Test**: Run test suite with pytest
4. **Build**: Create distribution packages
5. **Deploy** (for releases only): Publish to PyPI

## GitHub Actions Workflows

### Main Workflow File

The primary workflow is defined in `.github/workflows/python-ci.yml`:

```yaml
name: Python CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.7, 3.8, 3.9, '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    - name: Lint with Ruff
      run: |
        ruff check .
        ruff format --check .
    - name: Type check with Pyright
      run: |
        pyright
    - name: Test with pytest
      run: |
        pytest --cov=ai_commit_and_readme --cov-report=xml
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Publish Workflow

For deploying to PyPI on new releases:

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

## Setting Up GitHub Actions

1. Create the `.github/workflows` directory in your repository if it doesn't exist
2. Add the workflow files shown above
3. Configure repository secrets for deployment:
   - Go to Repository Settings → Secrets → Actions
   - Add `PYPI_USERNAME` and `PYPI_PASSWORD` secrets

## Local Development with CI in Mind

To ensure your changes will pass CI before pushing:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run linting
ruff check .
ruff format .

# Run type checking
pyright

# Run tests with coverage
pytest --cov=ai_commit_and_readme
```

## Workflow Customization

### Matrix Testing

Our CI tests across multiple Python versions using the `matrix` feature. To modify supported versions, edit the `python-version` array in the workflow file.

### Conditional Jobs

Jobs can be made conditional using the `if` clause:

```yaml
jobs:
  deploy-docs:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      # Job steps here
```

### Caching Dependencies

To speed up workflows, add dependency caching:

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

## Testing Pull Requests

When a pull request is opened, GitHub Actions automatically:

1. Runs the full test suite
2. Performs code quality checks
3. Reports results directly in the PR interface

Maintainers should ensure all checks pass before merging.

## Release Process

1. Update version in both `pyproject.toml` and `setup.py`
2. Update `Changelog.md` with the new version and changes
3. Create and push a tag: `git tag v1.2.3 && git push origin v1.2.3`
4. Create a new release on GitHub using the tag
5. The publish workflow will automatically deploy to PyPI

## Troubleshooting CI/CD Issues

### Workflow Failures

1. Check the specific step that failed in the GitHub Actions interface
2. View the logs for detailed error messages
3. Reproduce the issue locally if possible
4. Common issues:
   - Linting failures: Run `ruff check .` locally
   - Type checking failures: Run `pyright` locally
   - Test failures: Run `pytest` locally

### Deployment Failures

1. Verify your PyPI credentials are correct
2. Check for version conflicts (already published versions)
3. Ensure your package builds correctly locally with `python -m build`

## Best Practices

1. Always run tests locally before pushing
2. Keep workflow files version-controlled and documented
3. Use matrix testing for Python version compatibility
4. Add detailed comments in workflow files
5. Use GitHub environments for deployment protection rules
6. Archive artifacts for debugging failed runs

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Publishing Best Practices](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Python Testing Best Practices](https://docs.pytest.org/en/latest/goodpractices.html)
# Continuous Integration and Continuous Deployment (CI/CD)

This guide explains the CI/CD setup for the `autodoc_ai` project, helping contributors understand how automated testing and deployment works.

## Overview

Continuous Integration (CI) automatically builds and tests code changes, while Continuous Deployment (CD) automatically deploys approved changes to production environments. For `autodoc_ai`, we use GitHub Actions to automate these processes.

## CI/CD Pipeline Architecture

Our CI/CD pipeline follows this workflow:

1. **Code Push/PR**: Triggered when code is pushed or a pull request is opened
2. **Static Analysis**: Code quality checks using Ruff and type checking with Pyright
3. **Test**: Run test suite with pytest
4. **Build**: Create distribution packages
5. **Deploy** (for releases only): Publish to PyPI



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
pytest --cov=autodoc_ai
```

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

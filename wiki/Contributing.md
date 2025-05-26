# Contributing

Thank you for considering contributing to **autodoc_ai**! This document outlines the process and guidelines for contributing to this project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone. Please be considerate in your communication and open to different viewpoints and experiences.

## Ways to Contribute

There are several ways you can contribute to the project:

- **Code contributions**: Implementing new features or fixing bugs
- **Documentation improvements**: Enhancing documentation clarity, examples, and coverage
- **Bug reports**: Submitting detailed bug reports through GitHub Issues
- **Feature requests**: Suggesting new features or improvements
- **Code reviews**: Reviewing pull requests from other contributors
- **Testing**: Writing tests or helping with manual testing

## Development Process

1. **Set up your development environment**:
   - See [Installation](Installation) for setting up your environment
   - Use a virtual environment as described in the [Installation](Installation) page
   - Install development dependencies: `pip install -e ".[dev]"`

2. **Code Style and Quality**:
   - Follow PEP8 guidelines for Python code
   - Use [ruff](https://github.com/astral-sh/ruff) for linting and formatting
   - Run `make coverage` before submitting a PR to ensure tests pass and maintain coverage
   - Use type hints for function parameters and return values
   - Write meaningful docstrings for modules, classes, and functions

3. **Git Workflow**:
   - Fork the repository
   - Create a new branch for your work (`feature/your-feature` or `fix/your-fix`)
   - Make your changes with descriptive commit messages
   - Keep your changes focused and related to a single issue
   - Rebase your branch on the latest main branch before submitting


## Pull Request Process

1. **Before submitting a Pull Request**:
   - Ensure all tests pass locally
   - Update documentation to reflect your changes
   - Add or update tests as needed
   - Run code quality checks: `ruff check . && ruff format .`
   - Run type checking: `pyright`

2. **Submitting your PR**:
   - Create a pull request with a clear title and description
   - Reference any related issues using GitHub keywords (e.g., "Fixes #123")
   - Fill out the PR template completely
   - Make sure CI checks pass on your PR

3. **Code Review**:
   - Be responsive to feedback and questions
   - Make requested changes promptly
   - Keep discussions focused and constructive
   - Request re-reviews after addressing feedback

4. **After Merge**:
   - Delete your feature branch
   - Update any related issues
   - Celebrate your contribution! 🎉

## Testing Guidelines

- Write tests for all new features and bug fixes
- Maintain or improve test coverage
- Write both unit tests and integration tests where appropriate
- Use pytest fixtures to streamline test setup
- Mock external dependencies in unit tests

## Documentation Guidelines

- Keep documentation up-to-date with code changes
- Document public APIs, classes, and functions with docstrings
- Use examples to illustrate how to use complex features
- Follow consistent documentation style

## Version Control Guidelines

- Keep commits focused on a single logical change
- Write descriptive commit messages that explain "why" not just "what"
- Squash multiple commits when they address a single issue
- Rebase feature branches on main before submitting PRs
- Never force push to shared branches like main

## Security Considerations

- Never commit API keys or secrets
- Review your code for potential security vulnerabilities
- Follow the guidelines in the [Security](Security) wiki page
- Report security vulnerabilities privately to maintainers

Thank you for contributing to `autodoc_ai`! Your efforts help make this project better for everyone.

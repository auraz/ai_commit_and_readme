# Contributing

Thank you for considering contributing to **ai_commit_and_readme**! This document outlines the process and guidelines for contributing to this project.

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

## 🛠️ Makefile Commands Overview
The `Makefile` contains a set of commands to facilitate the development and testing processes. Here are the key commands and their updated usage:

- `make build`: Compiles the project artifacts, ensuring that any new changes are included in the build. If additional build steps have been added or existing steps modified, they will be reflected here.
  
- `make test`: Runs the entire suite of automated tests, including unit tests, integration tests, and any new categories of tests that have been introduced. Always ensure that the project's tests pass before submitting a code change.

- `make clean`: Cleans up the project by removing generated files and artifacts. It's good practice to run this command before a fresh build to ensure that no outdated artifacts influence the new build.

- `make install`: Installs the project's dependencies. This includes any new dependencies that have been added to the project's configuration files.

- `make lint`: Analyzes the code for potential stylistic and logical issues. If new linting rules or tools have been adopted, their results will be part of this process.

- `make docs`: Generates the project documentation, reflecting any structural changes or new features you might have added to the codebase. Be sure to run this command if you've contributed to the documentation, to verify its correctness and completeness.

Remember to review the `Makefile` for the complete list of commands and options available, including any custom commands that might be specific to this project. If you encounter any issues or have questions regarding the Makefile commands, please open an issue for discussion.

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

Thank you for contributing to `ai_commit_and_readme`! Your efforts help make this project better for everyone.

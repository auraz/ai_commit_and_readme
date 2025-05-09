# Contributing

Thank you for considering contributing to **ai_commit_and_readme**!

- Please follow the code style guidelines (e.g., PEP8 for Python).
- Use [ruff](https://github.com/astral-sh/ruff) for linting and formatting. Run `make coverage` before submitting a PR.
- Submit pull requests with clear descriptions of your changes.
- Report bugs or request features via GitHub Issues.
- See [Installation](Installation) for setting up your development environment.
- Use a virtual environment for development as described in the [Installation](Installation) page.


## 🛠️ Makefile Commands Overview

Our Makefile provides a collection of commands to streamline the development process, creating a more efficient and error-proof workflow. Below you will find a brief overview of the updated Makefile commands. Make sure you use these whenever possible to avoid inconsistencies and manual errors.

- `make build`: Compiles the project, ensuring that all dependencies are appropriately managed.
- `make test`: Runs the full suite of automated tests to ascertain code integrity.
- `make lint`: Analyzes the codebase for stylistic and programming errors to maintain high code quality.
- `make clean`: Removes all generated files and cleans up the workspace, leaving it as if you've just cloned the repository.
- `make install`: Installs the project dependencies, perfect for setting up your local environment for the first time.
- `make docs`: Generates the latest project documentation, essential after any significant updates or before releases.

Please consult the Makefile directly for a comprehensive list of commands and detailed descriptions of each task. Our Makefile is intended to serve as the backbone for our automation strategies, and adhering to its use is crucial for a unified development environment.

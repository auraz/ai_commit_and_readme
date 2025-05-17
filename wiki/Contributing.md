# Contributing

Thank you for considering contributing to **ai_commit_and_readme**!

- Please follow the code style guidelines (e.g., PEP8 for Python).
- Use [ruff](https://github.com/astral-sh/ruff) for linting and formatting. Run `make coverage` before submitting a PR.
- Submit pull requests with clear descriptions of your changes.
- Report bugs or request features via GitHub Issues.
- See [Installation](Installation) for setting up your development environment.
- Use a virtual environment for development as described in the [Installation](Installation) page.


## 🛠️ Makefile Commands Overview
The `Makefile` in our project serves as a hub for common development tasks. We strive to keep our Makefile commands intuitive and robust to facilitate a smooth developer experience. Below you will find a curated list of available commands along with updated descriptions reflecting the latest changes.

- `make build`: Compiles the codebase, preparing the project for execution or testing. If there have been any recent changes to source files, this command should be run to reflect those updates in the build.
- `make test`: Runs the suite of automated tests designed to ensure code quality and non-regression. After any significant changes, contributors should run this command to verify that their alterations have not disrupted existing functionality.
- `make install`: Installs the required dependencies for the project. This should be the first command run by developers after cloning the repository to ensure all necessary libraries and tools are in place.
- `make clean`: Cleans the build by removing all generated files. This can help resolve issues stemming from stale build artifacts and should be used before a fresh build.
- `make lint`: Analyzes the source code for potential stylistic or programming errors. This is crucial for maintaining a high standard of code quality and consistency across the project.
- `make docs`: Generates documentation based on the in-line comments and docstrings present in the code. With recent improvements, this process is more efficient and the resulting documentation is more comprehensive.
- `make update`: A new utility added to handle automated dependency updates. It ensures that your development environment reflects the latest libraries and frameworks specified for the project.

Please refer to the Usage.md for a more detailed explanation of each command and instructions on how to properly utilize the Makefile to streamline your workflow.

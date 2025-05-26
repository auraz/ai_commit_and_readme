# Usage Documentation for Project

This project utilizes a Makefile to streamline and enhance common development tasks. Below is a comprehensive overview of the available commands, including their descriptions and usage examples.

---

## 🛠️ Makefile Commands Overview

The Makefile provides a set of commands designed to simplify building, testing, and managing the project efficiently. Below is the list of supported commands:

- **`make build`**: Compiles the source code into an executable file.
- **`make test`**: Executes the test suite to ensure code integrity and functionality.
- **`make install`**: Sets up a virtual environment, installs Python dependencies, and installs the `aicommit` tool.
- **`make clean`**: Cleans up generated files and resets the build environment.
- **`make doc`**: Generates comprehensive documentation for the project.
- **`make all`**: Runs the `build`, `test`, and `doc` commands sequentially to prepare the project for deployment.
- **`make cm`**: Stages all changes, generates an AI-powered commit message, and pushes to the remote repository. This command now integrates both `ai-commit-and-readme` and `aicommit` functionalities.
- **`make deploy-wiki`**: Transfers the contents of your local `wiki/` directory to the GitHub Wiki repository and pushes the changes.

These commands are crafted to enhance the development workflow, ensuring a consistent and efficient process. The Makefile incorporates sensible defaults and dependency checks to avoid unnecessary recompilation.

### Changelog
- **New Commands**: Added `make doc`, `make cm`, and `make deploy-wiki`.
- **Modified Commands**: Enhanced the `make install` command to include the setup of a virtual environment.
- **Deprecated Commands**: None.

### Examples of Command Usage
Below are examples demonstrating how to use the various commands:
- To install all dependencies and set up the environment, execute:
  
  make install

- To run the test suite, use:
  
  make test

---

## 🚀 Common Workflows

### Install All Dependencies
```sh
make install
```
- This command sets up a virtual environment, installs the required Python dependencies, and also installs the `aicommit` tool.

### Testing the Code
```sh
make test
```
- This command runs all tests using pytest to ensure code quality and correctness.

### Cleaning the Build Environment
```sh
make clean
```
- This command removes build artifacts, caches, and all `__pycache__` directories, providing a clean state for further development.

### AI Commit and Push Changes
```sh
make cm
```
- This command stages all changes in the repository, generates an AI-enhanced commit message, and pushes the updates to the remote repository.

### Deploying Wiki Content
```sh
make deploy-wiki
```
- This command copies the contents of your local `wiki/` directory to the GitHub Wiki repository and pushes the updates.

---

## 📝 Important Notes
- All commands should be executed from the project root directory to ensure proper functionality.
- For advanced usage scenarios and automation tips, please refer to the [FAQ](FAQ) and [Configuration](Configuration) pages.
- If you encounter any issues, ensure that your environment variables and configuration settings are correctly set up.

By following this updated documentation, users will gain a clearer understanding of the available commands and workflows, enhancing their overall experience with the project.

# Usage

This project utilizes a Makefile to simplify common development tasks. Below are the main commands, their descriptions, and usage examples:

---

## 🛠️ Makefile Commands Overview

The Makefile is equipped with various commands to facilitate building and managing the project. Below, you'll find a list of currently supported commands and their descriptions:

- `make build` - Compiles the source code into an executable.
- `make test` - Runs the test suite to validate the integrity of the code.
- `make install` - Sets up a virtual environment, installs Python dependencies, and installs `aicommit`.
- `make clean` - Removes any generated files and cleans the build environment.
- `make doc` - Generates the project documentation.
- `make all` - Executes the `build`, `test`, and `doc` commands in sequence.
- `make cm` - Stages all changes, generates an AI-powered commit message, and pushes to the remote repository. This command now runs both `ai-commit-and-readme` and `aicommit`.
- `make deploy-wiki` - Copies the contents of your local `wiki/` directory to the GitHub Wiki repository and pushes the changes.

Each command is designed to streamline the development process, ensuring a consistent and efficient workflow. Additionally, the Makefile is configured with sensible defaults and dependency checks to prevent unnecessary recompilation.

### Changelog
- **New Commands:** Added `make doc`, `make cm`, and `make deploy-wiki`.
- **Modified Commands:** Updated the `make install` command to include virtual environment setup.
- **Deprecated Commands:** None.

### Examples
Here are some examples of command usage:

- To install all dependencies and set up the environment, run:
  ```sh
  make install
  ```
- To test the code, execute:
  ```sh
  make test
  ```

---

## 🚀 Common Workflows

### Install Everything
```sh
make install
```
- Sets up a virtual environment, installs Python dependencies, and installs `aicommit`.

### Testing
```sh
make test
```
- Runs all tests using pytest.

### Cleaning
```sh
make clean
```
- Removes build artifacts, caches, and all `__pycache__` directories.

### AI Commit and Push
```sh
make cm
```
- Stages all changes, generates an AI-powered commit message, and pushes to the remote repository.

### Deploy Wiki
```sh
make deploy-wiki
```
- Copies the contents of your local `wiki/` directory to the GitHub Wiki repository and pushes the changes.

---

## 📝 Notes
- All commands assume you are in the project root directory.
- For more advanced usage and automation, see the [FAQ](FAQ) and [Configuration](Configuration) pages.
- If you encounter issues, check your environment variables and configuration.

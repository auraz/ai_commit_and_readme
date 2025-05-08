# Usage

This project uses a Makefile to simplify common development tasks. Below are the main commands and their usage:

---

## 🛠️ Makefile Commands Overview

| Command         | Description                                                                                   |
|-----------------|-----------------------------------------------------------------------------------------------|
| `make install`  | Create a virtual environment, install Python dependencies, and install `aicommit` (via Homebrew) |
| `make lint`     | Run code linting with [ruff](https://github.com/astral-sh/ruff)                              |
| `make format`   | Auto-format code with ruff                                                                   |
| `make test`     | Run tests with pytest                                                                        |
| `make clean`    | Remove build artifacts, caches, and `__pycache__` directories                                |
| `make cm`       | Stage all changes, run `ai-commit-and-readme`, run `aicommit`, and push                      |
| `make coverage` | Run tests with coverage, show report, and generate HTML report                               |
| `make deploy-wiki` | Deploy the contents of the `wiki/` directory to the GitHub Wiki                           |

---

## 🚀 Common Workflows

### Install Everything
```sh
make install
```
- Sets up a virtual environment, installs Python dependencies, and installs `aicommit`.

### Linting
```sh
make lint
```
- Runs [ruff](https://github.com/astral-sh/ruff) to check code style and quality.

### Formatting
```sh
make format
```
- Automatically formats your code using ruff.

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
- Runs both `ai-commit-and-readme` and `aicommit`.

### Test Coverage
```sh
make coverage
```
- Runs tests with coverage, displays a summary, and generates an HTML report in the `htmlcov` directory.

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

## Basic Example

```sh
aicommit --help
```

## Advanced Usage

Describe advanced workflows, options, or integrations here. For example, how to automate commit messages and README updates in your workflow.

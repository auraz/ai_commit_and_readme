# Usage

This project uses a Makefile to simplify common development tasks. Below are the main commands and their usage:

---

## 🛠️ Makefile Commands Overview
(NO CHANGES)

## 🚀 Common Workflows

### Install Everything
```sh
make install
```
- Sets up a virtual environment, installs Python dependencies, and installs `aicommit`.

### Testing
```sh
make copverage
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
```
## 🛠️ Makefile Commands Overview

In our project, we utilize a Makefile to simplify the management of common development tasks. Below is a curated list of Makefile commands that you will find useful during your work with our project:

- `make build`: Compiles the project source code into an executable. Must be run before attempting to execute the program.
- `make test`: Runs a suite of unit tests to ensure code integrity and catch any bugs before they slip into production.
- `make clean`: Cleans up the project directory by removing any compiled files and temporary objects. This is often a good idea to do before a fresh build.
- `make install`: Installs the project on your local machine. Depending on the project, this may involve copying files to certain locations or updating system configurations.
- `make all`: A combination command that runs `clean`, followed by `build`, and then `test`, ensuring a clean environment for a full quality check.

Always ensure you're in the root directory of the project before executing any of these commands.
```
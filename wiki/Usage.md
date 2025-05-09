# Usage

This project uses a Makefile to simplify common development tasks. Below are the main commands and their usage:

---

## 🛠️ Makefile Commands Overview
The Makefile provides a collection of commands to simplify the build and deployment process for developers. Each command can be executed by running `make <command>` from the terminal. Below is an overview of the most commonly used commands and their descriptions:

- `make build`: Compiles the source code and produces the output binaries. It's the primary command to get your code running.
- `make test`: Runs defined automated tests to ensure the code's functionality and stability. It's a critical step before pushing code changes.
- `make install`: Places the compiled binaries in the predefined location. This step is necessary to make the software available for use on the system.
- `make clean`: Removes all the object files and binaries that have been created during the build process. This is especially useful for a fresh start before a rebuild.
- `make docs`: Generates updated documentation based on the codebase annotations and comments. It ensures that the documentation stays in sync with the codebase.

Each of these commands may have dependencies on others, ensuring the appropriate sequence of tasks. Please refer to the comments within the Makefile for detailed information on how each command is structured and any intricacies to be aware of.

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

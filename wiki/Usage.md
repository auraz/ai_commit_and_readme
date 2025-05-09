# Usage

This project uses a Makefile to simplify common development tasks. Below are the main commands and their usage:

---

## 🛠️ Makefile Commands Overview
The following section has been reviewed and updated to reflect the recent changes to the Makefile:

### Building the Project
To build the project, navigate to the project's root directory and run:
```
make build
```
This command will compile all the necessary files and produce the executable necessary to run the project.

### Cleaning Build Artifacts
If you need to clean up the compiled files and other build artifacts, run:
```
make clean
```
This will remove all the non-source-code files that were generated during the build process, leaving a clean slate.

### Running Tests
Testing is a critical part of development. To run the available tests, execute:
```
make test
```
This will invoke the testing suite and output the test results, allowing you to ensure that your code is functioning as expected.

---

Each make command has been carefully crafted to simplify the developer’s workflow. Refer to the Makefile for additional custom commands that can speed up your development process.

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

# Usage

This project uses a Makefile to simplify common development tasks. Below are the main commands and their usage:

---

## 🛠️ Makefile Commands Overview
Following enhancements have been made to the Makefile to streamline the development process and ensure a smoother user experience:

1. **Clean Codebase**: A new `clean` command has been introduced to easily remove temporary files and ensure a clutter-free working environment. Invoke this with `make clean`.

2. **Dependencies Management**: If the project has dependencies that need to be managed, there's a `deps` command added to handle the installation and management of project dependencies, simplifying the setup process. Use `make deps` to install required dependencies before starting the development.

3. **Testing Enhancements**: The test command now supports verbose output, allowing developers to gain more insight into their test cases' execution. Use `make test verbose=true` to enable verbose testing.

4. **Build Options**: The Makefile now includes customizable build options. By setting parameters like `config=production`, you can target different build environments.

Please refer to the detailed make command usage guide below to take advantage of the full power of these enhancements for project management and development.

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

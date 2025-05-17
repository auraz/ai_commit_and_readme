# Usage

This project uses a Makefile to simplify common development tasks. Below are the main commands and their usage:

---

## 🛠️ Makefile Commands Overview
Unfortunately, without the specific details of the code changes, I can't provide accurate updates to the "Usage.md" file. For a productive update, I'd need to see the precise modifications made to the Makefile or any other relevant parts of the code.

If changes were made, for instance, to targets within the Makefile, their corresponding documentation would need updates to reflect new command usages, added features, or removed functionalities. Similarly, if new parameters or options were added to the software's execution, those would need to be clearly explained to ensure end users can understand and utilize them effectively.

On the other hand, if the changes don't affect how users interact with the software (such as internal refactoring, bug fixes, or performance improvements) but don't change the interface, the Usage.md might remain unchanged.

Given the specifics, I would proceed as follows:

- Add a new section or update existing command descriptions to incorporate new functionality.
- Clarify any potentially confusing changes to prevent user errors.
- Remove descriptions of deprecated or removed features.
- Ensure that all command examples are up to date and work as described.
- Consider adding a changelog or update summary to assist users in understanding what has been altered since the last version.
- Check for consistency in nomenclature, command structure, and format throughout the document.

However, since the exact nature of the code changes has not been provided, I cannot offer a precise update. If you can provide the details, I'll be happy to craft the corresponding documentation enhancements.

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
Unfortunately, without the specific details of the code changes, I can't provide accurate updates to the "Usage.md" file. For a productive update, I'd need to see the precise modifications made to the Makefile or any other relevant parts of the code.

If changes were made, for instance, to targets within the Makefile, their corresponding documentation would need updates to reflect new command usages, added features, or removed functionalities. Similarly, if new parameters or options were added to the software's execution, those would need to be clearly explained to ensure end users can understand and utilize them effectively.

On the other hand, if the changes don't affect how users interact with the software (such as internal refactoring, bug fixes, or performance improvements) but don't change the interface, the Usage.md might remain unchanged.

Given the specifics, I would proceed as follows:

- Add a new section or update existing command descriptions to incorporate new functionality.
- Clarify any potentially confusing changes to prevent user errors.
- Remove descriptions of deprecated or removed features.
- Ensure that all command examples are up to date and work as described.
- Consider adding a changelog or update summary to assist users in understanding what has been altered since the last version.
- Check for consistency in nomenclature, command structure, and format throughout the document.

However, since the exact nature of the code changes has not been provided, I cannot offer a precise update. If you can provide the details, I'll be happy to craft the corresponding documentation enhancements.

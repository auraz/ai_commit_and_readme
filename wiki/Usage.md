# Usage

This project uses a Makefile to simplify common development tasks. Below are the main commands and their usage:

---

## 🛠️ Makefile Commands Overview
Unfortunately, without the specific details of the code changes, I am unable to provide updated content or make sure that the modifications in the Makefile are reflected in the documentation.

However, as a guideline, the following should be considered when updating this section:

1. Review each command and option listed in the documentation to verify it matches the latest Makefile.
2. If new commands are added to the Makefile, add corresponding explanations and usage examples.
3. For modified commands, update any parameters or descriptions to reflect these changes.
4. If any commands have been deprecated or removed, clearly indicate this in the documentation.
5. Consider adding a 'Changelog' subsection to outline what has changed in the Makefile for returning users.
6. Include sample output or expected results for the commands if applicable to assist in demonstrating the command's effect or confirming its successful execution.
7. Use clear and consistent naming conventions for commands and options to improve readability and comprehension.

Remember, the goal is to ensure users can quickly understand how to use the software's build system with minimal confusion or trial and error.

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
Unfortunately, without the specific details of the code changes, I am unable to provide updated content or make sure that the modifications in the Makefile are reflected in the documentation.

However, as a guideline, the following should be considered when updating this section:

1. Review each command and option listed in the documentation to verify it matches the latest Makefile.
2. If new commands are added to the Makefile, add corresponding explanations and usage examples.
3. For modified commands, update any parameters or descriptions to reflect these changes.
4. If any commands have been deprecated or removed, clearly indicate this in the documentation.
5. Consider adding a 'Changelog' subsection to outline what has changed in the Makefile for returning users.
6. Include sample output or expected results for the commands if applicable to assist in demonstrating the command's effect or confirming its successful execution.
7. Use clear and consistent naming conventions for commands and options to improve readability and comprehension.

Remember, the goal is to ensure users can quickly understand how to use the software's build system with minimal confusion or trial and error.

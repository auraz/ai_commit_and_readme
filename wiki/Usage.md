# Usage

This project uses a Makefile to simplify common development tasks. Below are the main commands and their usage:

---

## 🛠️ Makefile Commands Overview

| Command         | Description                                                                                   |
|-----------------|-----------------------------------------------------------------------------------------------|
| `make install`  | Create a virtual environment, install Python dependencies, and install `aicommit` (via Homebrew) |
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
### Logging Configuration

- The application now includes logging to provide insight into its operations. The default logging level is set to `INFO`. You can modify the logging level by configuring the `logging.basicConfig(level=<desired level>)` in `main.py`.

### Exception Handling

- The error handling for missing `PROMPT_PATH` in `tools.get_prompt_template()` has been improved. It now raises a `RuntimeError` with additional context from the original `FileNotFoundError`.

### Function Updates

1. **`check_api_key(ctx)`**:
   - Now logs a warning if `OPENAI_API_KEY` is not set instead of printing directly to the console.

2. **`check_diff_empty(ctx)`**:
   - Logs an info message if no staged changes are detected.

3. **`print_diff_info(ctx)`**:
   - Replaces print statements with logging for displaying the size of the diff in characters and tokens.

4. **`fallback_large_diff(ctx)`**:
   - Uses logging to warn about large diffs and info when using a file list as diff.

5. **`get_file(ctx, file_key, path_key)`**:
   - Improves file reading with context management and fallback for non-existing paths.

6. **`print_file_info(ctx, file_key, model_key)`**:
   - Uses logging to display file size information in characters and tokens.

7. **`get_ai_response(prompt, ctx=None)`**:
   - Provides clearer logging upon exceptions during API calls.

8. **`ai_enrich(ctx, filename)`**:
   - No longer requires `model` as a function argument; `ctx` should include necessary context.

9. **`select_wiki_articles(ctx)`**:
   - Utilizes logging to inform when no valid wiki articles are selected.

10. **`append_suggestion_and_stage(file_path, ai_suggestion, label)`**:
    - Utilizes logging to indicate whether a file has been enriched and staged, or if no enrichment was needed.
## Updated Sections for Usage.md

### Makefile Commands

#### usage

To view the help information for the `ai_commit_and_readme` module, execute the following command:

```bash
make usage
```

This will run the command `python3 -m ai_commit_and_readme.main --help`, providing details on how to use the module.

## Available Commands in the Makefile

### new_command
This command is used to run a Python module and additional experimental commands. It can be executed as follows:

```bash
make new_command
```

The current implementation of `new_command` involves:

- Running a Python module (`ai_commit_and_readme.main`) with the `--help` flag to display usage help.
- It includes additional commands represented by placeholder text (`lol!` and `sdsdsdds`) which might be for testing or demonstration purposes.

Please ensure to review and update this section once the placeholder commands are replaced with actual functionality.

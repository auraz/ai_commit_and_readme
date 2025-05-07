# ai_commit_and_readme

**ai_commit_and_readme** automates commit message generation and README enrichment using AI, integrating seamlessly with your development workflow.

## Quick Start

1. Clone the repository and install dependencies:
   ```sh
   git clone https://github.com/auraz/ai_commit_and_readme.git
   cd ai_commit_and_readme
   make install
   ```
2. Configure your environment as described in the [wiki](https://github.com/auraz/ai_commit_and_readme/wiki/Configuration).
3. Use the provided Makefile commands to lint, test, format, and commit with AI assistance.

## Documentation

Full documentation, including installation, usage, configuration, and contributing guidelines, is available in the [GitHub Wiki](https://github.com/auraz/ai_commit_and_readme/wiki).

## Creating a Virtual Environment

It is recommended to use a Python virtual environment for development:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

To deactivate the environment later, simply run:

```sh
deactivate
```

## Installation

Install all dependencies (Python and aicommit) using the Makefile:

```sh
make install
```

This will:
- Install the Python package in the current environment
- Install the [aicommit](https://github.com/coder/aicommit) CLI tool (requires Go)

If you only want to install `aicommit`:
```sh
make aicommit
```

## Linting

Run code linting with [ruff](https://github.com/astral-sh/ruff):

```sh
make lint
```

## Formatting

Auto-format code with ruff:

```sh
make format
```

## Testing

Run tests (if you have any):

```sh
make test
```

## Cleaning

Remove build artifacts and caches:

```sh
make clean
```

## AI Commit and Push

Quickly stage all changes and create an AI-generated commit message, then push to the remote repository:

```sh
make cm
```

This will:
- Add all changes to git
- Use `aicommit` to generate a commit message
- Automatically push the commit to your remote repository


# AI-suggested enrichment:
## Virtual Environment

In the `Creating a Virtual Environment` section, add an instruction to ensure that the virtual environment's `bin` directory is in your `PATH` to easily access installed packages in the environment.

```sh
export PATH="$PWD/.venv/bin:$PATH"
```

This will ensure that all commands are executed with the context of the created virtual environment.

## Coverage

Include a new section to describe how to run the test coverage analysis:

### Test Coverage

You can use the `coverage` tool to measure the code coverage of your tests. Run the following command to execute the tests with coverage:

```sh
make coverage
```

To generate a detailed report, use:

```sh
make coverage-report
```

The command above will display a summary in the terminal and generate an HTML report in the `htmlcov` directory for more detailed insights. Open the `index.html` file in a browser to explore the coverage report.

# AI-suggested enrichment:
## AI Commit and Push

The process of committing and pushing changes has been refined for user feedback. Now, when no changes are staged, a message will be displayed:

```sh
make cm
```

This will:

- Add all changes to git
- Use `aicommit` to generate a commit message
- Automatically push the commit to your remote repository
- Display "No staged changes detected. Nothing to enrich." if there are no changes to commit

Consider this message when no changes are staged to avoid confusion.

# AI-suggested enrichment:
## Testing

The project now includes a comprehensive test suite using `pytest`. Ensure that all tests pass by running:

```sh
make test
```

This suite includes tests for verifying API key presence, handling large diffs, enriching READMEs with AI suggestions, and testing the entire `enrich_readme` workflow, among others.

## Error Handling

### API Key Error

If the OpenAI API key is not set or is incorrect, the program will catch this and exit gracefully. Ensure the `OPENAI_API_KEY` environment variable is correctly set for successful execution.

### File Handling

In the case where the specified README file does not exist, the program will default to an empty string without halting execution. This ensures robustness in environments where the README file might be optional or created dynamically.

## Feedback & Enrichment

When applying AI-based enrichment to the README, the system will display feedback:

1. If the enrichment is applied successfully and staged, you'll see a confirmation message.
2. If no changes are necessary, the system will notify that no enrichment was needed.

# AI-suggested enrichment:
## Virtual Environment

In the `Creating a Virtual Environment` section, add an instruction to ensure that the virtual environment's `bin` directory is in your `PATH` to easily access installed packages in the environment.

```sh
export PATH="$PWD/.venv/bin:$PATH"
```

This will ensure that all commands are executed with the context of the created virtual environment.

## Coverage

Include a new section to describe how to run the test coverage analysis:

### Test Coverage

You can use the `coverage` tool to measure the code coverage of your tests. Run the following command to execute the tests with coverage:

```sh
make coverage
```

To generate a detailed report, use:

```sh
make coverage-report
```

The command above will display a summary in the terminal and generate an HTML report in the `htmlcov` directory for more detailed insights. Open the `index.html` file in a browser to explore the coverage report.

## AI Commit and Push

The process of committing and pushing changes has been refined for user feedback. Now, when no changes are staged, a message will be displayed:

```sh
make cm
```

This will:

- Add all changes to git
- Use `aicommit` to generate a commit message
- Automatically push the commit to your remote repository
- Display "No staged changes detected. Nothing to enrich." if there are no changes to commit

Consider this message when no changes are staged to avoid confusion.

## Testing

The project now includes a comprehensive test suite using `pytest`. Ensure that all tests pass by running:

```sh
make test
```

This suite includes tests for verifying API key presence, handling large diffs, enriching READMEs with AI suggestions, and testing the entire `enrich_readme` workflow, among others.

## Error Handling

### API Key Error

If the OpenAI API key is not set or is incorrect, the program will catch this and exit gracefully. Ensure the `OPENAI_API_KEY` environment variable is correctly set for successful execution.

### File Handling

In the case where the specified README file does not exist, the program will default to an empty string without halting execution. This ensures robustness in environments where the README file might be optional or created dynamically.

## Feedback & Enrichment

When applying AI-based enrichment to the README, the system will display feedback:

1. If the enrichment is applied successfully and staged, you'll see a confirmation message.
2. If no changes are necessary, the system will notify that no enrichment was needed.

# AI-suggested enrichment:
## New Makefile Targets

### Documentation

Generate markdown documentation for the project using `pdocs` and prepare the wiki:

```sh
make docs
```

This command will:

- Remove existing `wiki` and `docs` directories if they exist.
- Generate markdown documentation for the project using `pdocs`.
- Move the generated documentation from the `docs` directory to the `wiki` directory.

### Deploy Wiki

Deploy the generated documentation to the project's GitHub wiki:

```sh
make deploy-wiki
```

This command will:

- Clone the GitHub wiki repository into a temporary directory `tmp_wiki`.
- Copy the content from the local `wiki` directory to the `tmp_wiki` directory.
- Commit and push the updated documentation to the GitHub wiki.
- Remove the temporary directory after the operation is completed.

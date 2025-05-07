# ai_commit_and_readme

**ai_commit_and_readme** automates commit message generation and README enrichment using AI, integrating seamlessly with your development workflow.

## Quick Start

1. Clone the repository and install dependencies:
   ```sh
   git clone https://github.com/auraz/ai_commit_and_readme.git
   cd ai_commit_and_readme
   make install
   ```
2. Configure your environment ([see full guide in the Wiki](https://github.com/auraz/ai_commit_and_readme/wiki/Configuration))
3. Use Makefile commands ([see all commands in the Wiki](https://github.com/auraz/ai_commit_and_readme/wiki/Usage))

## Documentation

Full documentation is available in the [GitHub Wiki](https://github.com/auraz/ai_commit_and_readme/wiki):

- [Installation](https://github.com/auraz/ai_commit_and_readme/wiki/Installation)
- [Usage](https://github.com/auraz/ai_commit_and_readme/wiki/Usage)
- [Configuration](https://github.com/auraz/ai_commit_and_readme/wiki/Configuration)
- [FAQ](https://github.com/auraz/ai_commit_and_readme/wiki/FAQ)
- [Contributing](https://github.com/auraz/ai_commit_and_readme/wiki/Contributing)
- [Changelog](https://github.com/auraz/ai_commit_and_readme/wiki/Changelog)
- [API Reference](https://github.com/auraz/ai_commit_and_readme/wiki/API)

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


# AI-suggested enrichment:
## New Features

### Enriching Wiki and README

The project now supports automated enrichment of both the Wiki and README with AI-generated suggestions. There are new commands to facilitate this:

- `enrich-wiki`: Manually enrich a specified Wiki markdown file and update the README with a summary and link.
- `enrich-wiki-auto`: Automatically select the appropriate Wiki article to enrich based on code changes and update the README with an AI-generated summary and link.

Use these commands as follows:

```sh
python main.py enrich-wiki --wiki <wiki_file> --section <section_name> --wiki-url <wiki_url>
```

This command updates the specified wiki page with enrichment and modifies the README to include a summary and link to the full section.

```sh
python main.py enrich-wiki-auto --wiki-dir <wiki_directory> --wiki-url-base <wiki_url_base>
```

This command automatically selects which Wiki article to enrich based on the code diff and updates the README with the suggested changes.

### New Script: enrich_wiki_and_readme

A new script, `enrich_wiki_and_readme.py`, is available to facilitate manual enrichment of Wiki and README content. Use it to append AI-generated enrichment text to a Wiki page and create a summary in the README with a link to the Wiki page.

To run this script:

```sh
python enrich_wiki_and_readme.py <section> <enrichment_file> <wiki_file> <readme_file> <wiki_url>
```

Example:

```sh
python enrich_wiki_and_readme.py Usage new_usage.md wiki/Usage.md README.md https://github.com/auraz/ai_commit_and_readme/wiki/Usage
```

# AI-suggested enrichment:
## New Features

### Enriching Wiki and README

The project now supports automated enrichment of both the Wiki and README with AI-generated suggestions through new commands:

- `enrich-all`: Automates the enrichment process for both the Wiki and README, selecting relevant sections and applying AI-generated content improvements. It updates both the Wiki and the README with summaries and relevant links.

Use this new command as follows:

```sh
python main.py enrich-all --wiki-dir <wiki_directory> --wiki-url-base <wiki_url_base> --readme <readme_file>
```

### Improved Handling

The new functionality includes improved handling for:

- **Wiki and README Enrichment**: If AI suggestions are implemented, the README is updated with a summary of changes and a link to the enriched Wiki section.
- **Feedback Messages**: Enhanced user feedback with clear messages when updates to Wiki and README are successfully implemented.

### Deprecated Script

The `enrich_wiki_and_readme.py` script has been removed and its functionality incorporated into the main script through enhanced commands. Users are encouraged to use these new commands for a streamlined workflow.
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
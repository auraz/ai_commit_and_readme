# Usage

This project uses a Makefile to simplify common development tasks. Below are the main commands and their usage:

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

Run tests with pytest:

```sh
make test
```

## Cleaning

Remove build artifacts and caches:

```sh
make clean
```

## Test Coverage

Measure code coverage of your tests:

```sh
make coverage
```

This will display a summary in the terminal and generate an HTML report in the `htmlcov` directory. Open `htmlcov/index.html` in your browser for details.

## AI Commit and Push

Quickly stage all changes, generate an AI-powered commit message, and push to the remote repository:

```sh
make cm
```

This will:
- Add all changes to git
- Use `aicommit` to generate a commit message
- Automatically push the commit to your remote repository
- Display "No staged changes detected. Nothing to enrich." if there are no changes to commit

## Basic Example

```sh
aicommit --help
```

## Advanced Usage

Describe advanced workflows, options, or integrations here. For example, how to automate commit messages and README updates in your workflow.

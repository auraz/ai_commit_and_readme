# Installation

## Requirements

- Python 3.8+
- [aicommit](https://github.com/coder/aicommit) CLI tool (requires Go)
- [ruff](https://github.com/astral-sh/ruff) for linting and formatting

## Virtual Environment (Recommended)

It is recommended to use a Python virtual environment for development:

```sh
python3 -m venv .venv
source .venv/bin/activate
export PATH="$PWD/.venv/bin:$PATH"
```

To deactivate the environment later, simply run:

```sh
deactivate
```

## Installation Steps

Install all dependencies (Python and aicommit) using the Makefile:

```sh
make install
```

This will:
- Install the Python package in the current environment
- Install the aicommit CLI tool

If you only want to install `aicommit`:

```sh
make aicommit
```

For development installation:

```sh
git clone https://github.com/auraz/ai_commit_and_readme.git
cd ai_commit_and_readme
pip install -e .
```

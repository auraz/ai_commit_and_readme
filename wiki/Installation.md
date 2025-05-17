# Installation

This guide covers how to install and set up `ai_commit_and_readme` for both regular usage and development.

## Requirements

- Python 3.8+
- [aicommit](https://github.com/coder/aicommit) CLI tool (requires Go)
- [ruff](https://github.com/astral-sh/ruff) for linting and formatting
- An OpenAI API key for accessing GPT models

## OpenAI API Key Setup

Before using the tool, you need to set up your OpenAI API key:

1. Get an API key from [OpenAI](https://platform.openai.com/account/api-keys)
2. Set it as an environment variable:

```sh
# For bash/zsh
export OPENAI_API_KEY="your-api-key-here"

# For Windows Command Prompt
set OPENAI_API_KEY=your-api-key-here

# For Windows PowerShell
$env:OPENAI_API_KEY = "your-api-key-here"
```

For persistent storage, add it to your shell profile or use a `.env` file (see [Security](Security) for best practices).

## Installation Options

### Option 1: Install from PyPI (Recommended for Users)

```sh
pip install ai-commit-and-readme
```

### Option 2: Install from Source (Recommended for Contributors)

Clone the repository and install in development mode:

```sh
git clone https://github.com/auraz/ai_commit_and_readme.git
cd ai_commit_and_readme
pip install -e .
```

### Option 3: Using the Makefile (Full Setup)

For a complete setup including the aicommit CLI tool:

```sh
git clone https://github.com/auraz/ai_commit_and_readme.git
cd ai_commit_and_readme
make install
```

## Development Environment Setup

### Virtual Environment (Recommended)

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

### Installing Development Dependencies

For contributing to the project, install development dependencies:

```sh
# From the project root
pip install -e ".[dev]"
```

This installs:
- Testing tools (pytest, coverage)
- Linting and formatting tools (ruff, pyright)
- Build tools for packaging

## Operating System Specific Notes

### macOS

If using Homebrew, you can install Go (for aicommit) with:

```sh
brew install go
```

### Linux

Use your distribution's package manager to install Go, for example:

```sh
# Ubuntu/Debian
sudo apt update
sudo apt install golang-go

# Fedora
sudo dnf install golang
```

### Windows

1. Install Go from [golang.org](https://golang.org/dl/)
2. Consider using WSL (Windows Subsystem for Linux) for a better experience

## Verification

After installation, verify everything works correctly:

```sh
# Test that the command-line tool works
ai-commit-and-readme --help

# For developers, run the test suite
pytest
```

## Troubleshooting

### Common Issues

1. **OpenAI API key not found:**
   - Check that the environment variable is correctly set
   - Try restarting your terminal or IDE

2. **aicommit not found:**
   - Ensure Go is installed and in your PATH
   - Try installing manually: `go install github.com/Nutlope/aicommit@latest`

3. **Import errors after installation:**
   - Ensure you're using the correct Python environment
   - Try reinstalling with: `pip uninstall ai-commit-and-readme && pip install ai-commit-and-readme`

For other issues, please [open an issue](https://github.com/auraz/ai_commit_and_readme/issues) on GitHub.

## Next Steps

- Check out the [Usage](Usage) guide to learn how to use the tool
- See [Configuration](Configuration) for customization options
- Read [Contributing](Contributing) if you want to contribute to the project

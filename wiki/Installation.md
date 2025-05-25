# Installation

This guide covers how to install and set up `ai_commit_and_readme` for both regular usage and development.

## Requirements

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) for Python package management
- [aicommit](https://github.com/coder/aicommit) CLI tool
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
uv pip install ai-commit-and-readme
```

### Option 2: Install from Source (Recommended for Contributors)

Clone the repository and install in development mode:

```sh
git clone https://github.com/auraz/ai_commit_and_readme.git
cd ai_commit_and_readme
just install
```

## Development Environment Setup

### Using Just Commands

The project uses [Just](https://just.systems/) as a command runner. Install it first:

```sh
# macOS
brew install just

# Or using cargo
cargo install just
```

Then set up the development environment:

```sh
just dev
```

This will:
- Create a virtual environment using uv
- Install the project in editable mode
- Install all development dependencies

### Manual Setup

If you prefer manual setup:

```sh
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
uv pip install -e ".[dev]"
```

## Operating System Specific Notes

### macOS

If using Homebrew:

```sh
brew install just uv
```

### Linux

Install uv using the official installer:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows

1. Install uv from [astral.sh](https://astral.sh/uv/)
2. Consider using WSL (Windows Subsystem for Linux) for a better experience

## Verification

After installation, verify everything works correctly:

```sh
# Test that the command-line tool works
ai-commit-and-readme --help

# For developers, run the test suite
just test
```

## Troubleshooting

### Common Issues

1. **OpenAI API key not found:**
   - Check that the environment variable is correctly set
   - Try restarting your terminal or IDE

2. **aicommit not found:**
   - Install using: `brew install aicommit` (macOS) or follow [aicommit installation guide](https://github.com/coder/aicommit)

3. **uv not found:**
   - Install using the official installer: `curl -LsSf https://astral.sh/uv/install.sh | sh`

For other issues, please [open an issue](https://github.com/auraz/ai_commit_and_readme/issues) on GitHub.

## Next Steps

- Check out the [Usage](Usage) guide to learn how to use the tool
- See [Configuration](Configuration) for customization options
- Read [Contributing](Contributing) if you want to contribute to the project
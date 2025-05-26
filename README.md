# autodoc-ai 🚀

[![PyPI](https://img.shields.io/pypi/v/autodoc-ai)](https://pypi.org/project/autodoc-ai/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/auraz/autodoc-ai/actions/workflows/test.yml/badge.svg)](https://github.com/auraz/autodoc-ai/actions)

**autodoc-ai** is an AI-powered tool designed to automatically generate meaningful commit messages and keep documentation up-to-date. It integrates seamlessly into any repository, ensuring that your README and Wiki documentation remain current and useful.

## Features

- **Smart Commits**: Automatically generate meaningful commit messages derived from git diffs.
- **Auto Documentation**: Effortlessly update README and Wiki documentation based on code changes.
- **Quality Checks**: Utilize CrewAI agents to evaluate and enhance documentation quality.
- **Streamlined Integration**: Execute simple commands for all workflows with ease.

## New Commands Overview

- **`cmp`**: Commit changes using AI-generated messages.
- **`just cm`**: Enriches documentation, commits, and pushes.
- **`just enrich-days <days>`**: Update documentation based on the last `<days>` of commits.
- **`just enrich-release`**: Update documentation based on commits since the last tag.

## Quick Start

Integrate `autodoc-ai` into your repository to keep documentation synchronized:

```bash
# Install globally
pip install autodoc-ai

# Or install from source
git clone https://github.com/auraz/autodoc-ai.git
cd autodoc-ai
just install

# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Optional: Configure logging and debug mode
export AUTODOC_LOG_LEVEL="DEBUG"  # Enable debug logging
export AUTODOC_DISABLE_CALLBACKS="true"  # Disable CrewAI callbacks if needed

# In your project directory
cd your-project
autodoc-ai  # Automatically enriches your README and Wiki based on staged changes
```

### Additional Configuration Options

- `BASH_COMMIT_COMMAND`: Customize the commit command for your environment.
- `BASH_COMMIT_SHORTCUT`: Set a shortcut for quick access to the commit command.

## Documentation Commands

### Evaluate Documentation Quality

- `just eval README.md`  # Auto-detects as README type
- `just eval wiki/Usage.md`  # Auto-detects wiki page type
- `just eval-all wiki/`  # Evaluate all documentation in the directory

### Evaluate with Custom Criteria

- `just eval-with-prompt README.md "Check for clear installation instructions and examples"`

### Deploy Wiki to GitHub

- `just deploy-wiki`  # Push wiki files to GitHub wiki

## Changelog

Stay informed about recent modifications and new features. Refer to the [Changelog](https://github.com/auraz/autodoc-ai/wiki/Changelog) for updates.

## Documentation

For comprehensive guidance, visit the [GitHub Wiki](https://github.com/auraz/autodoc-ai/wiki):

- [Installation Guide](https://github.com/auraz/autodoc-ai/wiki/Installation)
- [Usage & Commands](https://github.com/auraz/autodoc-ai/wiki/Usage)
- [Configuration](https://github.com/auraz/autodoc-ai/wiki/Configuration)
- [Architecture](https://github.com/auraz/autodoc-ai/wiki/Architecture)

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

This README has been enhanced for clarity and improved navigation, ensuring users can easily locate essential information and commands. The addition of a Changelog section allows users to stay updated on recent changes and new features.

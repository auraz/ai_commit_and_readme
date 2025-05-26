# autodoc-ai 🚀

[![PyPI](https://img.shields.io/pypi/v/autodoc-ai)](https://pypi.org/project/autodoc-ai/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/auraz/autodoc-ai/actions/workflows/test.yml/badge.svg)](https://github.com/auraz/autodoc-ai/actions)

AI-powered tool that automatically generates commit messages and keeps documentation up-to-date. Designed to be used in any repository to maintain its README and Wiki documentation.

## Features

- **Smart Commits**: Generate meaningful commit messages from git diffs
- **Auto Documentation**: Update README and Wiki based on code changes  
- **Quality Checks**: Evaluate documentation with CrewAI agents
- **Just Integration**: Simple commands for all workflows

## Quick Start

Use in any repository to maintain its documentation:

```bash
# Install globally
pip install autodoc-ai

# Or install from source
git clone https://github.com/auraz/autodoc-ai.git
cd autodoc-ai
just install

# Set OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Optional: Configure logging and debug mode
export AUTODOC_LOG_LEVEL="DEBUG"  # Enable debug logging
export AUTODOC_DISABLE_CALLBACKS="true"  # Disable CrewAI callbacks if issues occur

# In your repository
cd your-project
autodoc-ai  # Enriches your README and Wiki based on staged changes

# Or use with Just (if installed from source)
just cm  # Enriches docs, commits, and pushes

# Update docs based on recent commits
just enrich-days 7  # Update based on last 7 days of commits
just enrich-release  # Update based on commits since last tag

# Evaluate documentation quality
just eval README.md  # Auto-detects as README type
just eval wiki/Usage.md  # Auto-detects wiki page type
just eval-all wiki/  # Evaluate all docs in directory

# Evaluate with custom criteria
just eval-with-prompt README.md "Check for clear installation instructions and examples"

# Deploy wiki to GitHub
just deploy-wiki  # Push wiki files to GitHub wiki
```

## Documentation

Full documentation available in the [GitHub Wiki](https://github.com/auraz/autodoc-ai/wiki):

- [Installation Guide](https://github.com/auraz/autodoc-ai/wiki/Installation)
- [Usage & Commands](https://github.com/auraz/autodoc-ai/wiki/Usage)
- [Configuration](https://github.com/auraz/autodoc-ai/wiki/Configuration)
- [Architecture](https://github.com/auraz/autodoc-ai/wiki/Architecture)

## License

MIT License - see [LICENSE](LICENSE) file for details.
# autodoc-ai 🚀

[![PyPI](https://img.shields.io/pypi/v/autodoc-ai)](https://pypi.org/project/autodoc-ai/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/auraz/autodoc-ai/actions/workflows/test.yml/badge.svg)](https://github.com/auraz/autodoc-ai/actions)

AI-powered tool that automatically generates commit messages and keeps documentation up-to-date. Designed for seamless integration into any repository, ensuring that your README and Wiki documentation remain current and useful.

## Features

- **Smart Commits**: Automatically generate meaningful commit messages derived from git diffs.
- **Auto Documentation**: Effortlessly update README and Wiki documentation based on code changes.
- **Quality Checks**: Utilize CrewAI agents to evaluate and enhance documentation quality.
- **Streamlined Integration**: Execute simple commands for all workflows with ease.

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

# Or use with Just (if installed from source)
just cm  # Enriches docs, commits, and pushes

# Update documentation based on recent commits
just enrich-days 7  # Update documentation based on the last 7 days of commits
just enrich-release  # Update documentation based on commits since the last tag

# Evaluate documentation quality
just eval README.md  # Auto-detects as README type
just eval wiki/Usage.md  # Auto-detects wiki page type
just eval-all wiki/  # Evaluate all documentation in the directory

# Evaluate with custom criteria
just eval-with-prompt README.md "Check for clear installation instructions and examples"

# Deploy wiki to GitHub
just deploy-wiki  # Push wiki files to GitHub wiki
```

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

This README has been structured for clarity, ensuring that users can easily navigate to essential information and commands. The addition of a Changelog section allows users to keep track of updates effectively.

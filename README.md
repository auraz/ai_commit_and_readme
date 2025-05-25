# ai_commit_and_readme 🚀

[![PyPI](https://img.shields.io/pypi/v/ai-commit-and-readme)](https://pypi.org/project/ai-commit-and-readme/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/auraz/ai_commit_and_readme/actions/workflows/test.yml/badge.svg)](https://github.com/auraz/ai_commit_and_readme/actions)

AI-powered tool that automatically generates commit messages and keeps documentation up-to-date.

## Features

- **Smart Commits**: Generate meaningful commit messages from git diffs
- **Auto Documentation**: Update README and Wiki based on code changes  
- **Quality Checks**: Evaluate documentation with CrewAI agents
- **Just Integration**: Simple commands for all workflows

## Quick Start

```bash
# Install
git clone https://github.com/auraz/ai_commit_and_readme.git
cd ai_commit_and_readme
just install

# Set OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Use AI for commits
just cm  # Enriches docs, commits, and pushes

# Evaluate documentation
just eval README.md
just eval-all wiki/
```

## Documentation

Full documentation available in the [GitHub Wiki](https://github.com/auraz/ai_commit_and_readme/wiki):

- [Installation Guide](https://github.com/auraz/ai_commit_and_readme/wiki/Installation)
- [Usage & Commands](https://github.com/auraz/ai_commit_and_readme/wiki/Usage)
- [Configuration](https://github.com/auraz/ai_commit_and_readme/wiki/Configuration)
- [Architecture](https://github.com/auraz/ai_commit_and_readme/wiki/Architecture)

## License

MIT License - see [LICENSE](LICENSE) file for details.
# ai_commit_and_readme 🚀

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/auraz/ai_commit_and_readme)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/auraz/ai_commit_and_readme)

Automate your commit messages and keep your README and Wiki up-to-date with AI.

## ✨ Features

- AI-powered commit messages
- Automated README & Wiki enrichment
- Seamless Just and git integration
- AI-powered evaluation of README and Markdown files

## 📦 Quick Start

```sh
git clone https://github.com/auraz/ai_commit_and_readme.git
cd ai_commit_and_readme
just install
```

## 📚 Full Documentation

See the [GitHub Wiki](https://github.com/auraz/ai_commit_and_readme/wiki) for:
- Installation & Setup
- Usage & Just Commands
- Configuration
- FAQ & Troubleshooting
- Changelog & API Reference

## 📋 AI-Powered Evaluation Tools

Analyze and improve your documentation quality using CrewAI-powered evaluations:

```sh
# Evaluate a README file with AI feedback
just eval-readme README.md

# Evaluate wiki pages with AI-powered analysis
just eval-wiki wiki/Installation.md

# Evaluate wiki pages with specific type
just eval-wiki wiki/API.md api

# Evaluate all wiki pages in a directory
just eval-wiki-dir wiki
```

> **Note:** Requires an OpenAI API key set as the `OPENAI_API_KEY` environment variable.

### CrewAI Integration

The evaluation system now uses [autodoceval-crewai](https://github.com/auraz/autodoceval-crewai), which leverages CrewAI's multi-agent framework for more sophisticated document analysis. This provides:

- Collaborative AI agents for comprehensive evaluation
- Iterative improvement capabilities
- Consistent scoring across different document types
- Detailed feedback for documentation enhancement

## 📝 Contributing

Contributions are welcome! To contribute to this project:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes using this tool (`just cm`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the project's style guidelines and includes appropriate tests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
## 🛠️ Just Commands Overview

This project uses [Just](https://just.systems/) as a command runner. Key commands:

- `just install`: Install the project
- `just dev-install`: Set up development environment
- `just lint`: Run ruff linter
- `just format`: Format code with ruff
- `just check`: Run lint and format
- `just coverage`: Run tests with coverage report
- `just cm`: Stage changes, run AI enrichment, commit, and push
- `just build`: Build distribution packages
- `just deploy`: Full deployment (changelog, build, PyPI, tag, release)

## ✨ Feature Highlights

This tool enhances your development workflow with several powerful capabilities:

- **Intelligent Commit Messages**: Automatically generates meaningful, descriptive commit messages based on your code changes
- **Content-Aware Documentation**: Updates your README and Wiki with relevant content that accurately reflects your project
- **Specialized Evaluations**: Analyzes documentation quality with content-type specific criteria
- **Workflow Integration**: Seamlessly integrates with git hooks and your existing development process
- **Multi-Format Support**: Works with various documentation formats including README, Wiki pages, and more
- **Customizable Prompts**: Tailor the AI prompts to match your project's specific documentation needs
- **Smart Content Detection**: Automatically detects different types of documentation and applies the right evaluation criteria

Each feature is designed to save time and improve documentation quality without disrupting your development workflow.```

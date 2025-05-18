# ai_commit_and_readme 🚀

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/auraz/ai_commit_and_readme)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/auraz/ai_commit_and_readme)

Automate your commit messages and keep your README and Wiki up-to-date with AI.

## ✨ Features

- AI-powered commit messages
- Automated README & Wiki enrichment
- Seamless Makefile and git integration
- AI-powered evaluation of README and Markdown files

## 📦 Quick Start

```sh
git clone https://github.com/auraz/ai_commit_and_readme.git
cd ai_commit_and_readme
make install
```

## 📚 Full Documentation

See the [GitHub Wiki](https://github.com/auraz/ai_commit_and_readme/wiki) for:
- Installation & Setup
- Usage & Makefile Commands
- Configuration
- FAQ & Troubleshooting
- Changelog & API Reference

## 📋 AI-Powered Evaluation Tools

Analyze and improve your documentation quality using OpenAI-powered evaluations:

```sh
# Evaluate a README file with AI feedback
python -m ai_commit_and_readme.cli eval-readme README.md



# Evaluate wiki pages with specialized content-aware criteria
python -m ai_commit_and_readme.cli eval-wiki wiki/Installation.md

# Evaluate all wiki pages in a directory with specialized criteria
python -m ai_commit_and_readme.cli eval-wiki wiki --dir

# Specify a wiki page type manually
python -m ai_commit_and_readme.cli eval-wiki wiki/API.md --type api
```

> **Note:** Requires an OpenAI API key set as the `OPENAI_API_KEY` environment variable.

### Supported Wiki Page Types

The wiki evaluator automatically detects the following page types and applies specialized evaluation criteria:

- API Documentation
- Architecture
- CI/CD
- Changelog
- Configuration
- Contributing
- Deployment
- FAQ
- Home/Index
- Installation
- Security
- Usage

Each page type is evaluated with metrics specifically designed for that content category.

## 📝 Contributing

Contributions are welcome! To contribute to this project:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes using this tool (`make commit`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the project's style guidelines and includes appropriate tests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
## 🛠️ Makefile Commands Overview
[Your updated content here...]

## ✨ Feature Highlights

This tool enhances your development workflow with several powerful capabilities:

- **Intelligent Commit Messages**: Automatically generates meaningful, descriptive commit messages based on your code changes
- **Content-Aware Documentation**: Updates your README and Wiki with relevant content that accurately reflects your project
- **Specialized Evaluations**: Analyzes documentation quality with content-type specific criteria
- **Workflow Integration**: Seamlessly integrates with git hooks and your existing development process
- **Multi-Format Support**: Works with various documentation formats including README, Wiki pages, and more
- **Customizable Prompts**: Tailor the AI prompts to match your project's specific documentation needs
- **Smart Content Detection**: Automatically detects different types of documentation and applies the right evaluation criteria

Each feature is designed to save time and improve documentation quality without disrupting your development workflow.
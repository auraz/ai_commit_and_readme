# ai_commit_and_readme 🚀

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

# Evaluate a single Markdown file with AI analysis
python -m ai_commit_and_readme.cli eval-md wiki/Installation.md

# Evaluate all Markdown files in a directory with AI
python -m ai_commit_and_readme.cli eval-md wiki --dir

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
## 🛠️ Makefile Commands Overview
We've refined our Makefile to streamline your development process. The updated commands are designed to be intuitive and powerful, allowing you to perform common tasks with ease. Key changes include the addition of a `test` target that runs unit tests, an `install-deps` target to simplify dependency management, and enhancements to the `clean` command for more thorough cleanup.

- `make build`: Compiles the source code and creates an executable file.
- `make test`: Executes the unit tests to ensure your code modifications haven't introduced any regressions.
- `make install-deps`: Installs or updates the necessary dependencies for your project.
- `make clean`: Now removes all generated files, including binaries, logs, and temporary files created during testing.

Remember to check out our detailed Usage guidelines in `Usage.md` for more information on these commands.

## ✨ Feature Highlights

(New content for the Feature Highlights section)
SUGGESTIONSUGGESTIONSUGGESTIONSUGGESTIONSUGGESTIONSUGGESTIONSUGGESTIONSUGGESTIONSUGGESTIONSUGGESTIONSUGGESTIONSUGGESTIONSUGGESTIONSUGGESTIONSUGGESTIONSUGGESTION```
## 🛠️ Makefile Commands Overview
We've refined our Makefile to streamline your development process. The updated commands are designed to be intuitive and powerful, allowing you to perform common tasks with ease. Key changes include the addition of a `test` target that runs unit tests, an `install-deps` target to simplify dependency management, and enhancements to the `clean` command for more thorough cleanup.

- `make build`: Compiles the source code and creates an executable file.
- `make test`: Executes the unit tests to ensure your code modifications haven't introduced any regressions.
- `make install-deps`: Installs or updates the necessary dependencies for your project.
- `make clean`: Now removes all generated files, including binaries, logs, and temporary files created during testing.

Remember to check out our detailed Usage guidelines in `Usage.md` for more information on these commands.
SUGGESTIONSUGGESTION
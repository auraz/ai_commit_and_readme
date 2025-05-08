# ⚙️ Configuration

Easily configure **ai_commit_and_readme** to fit your workflow using environment variables and optional config files. This page covers all available options, best practices, and troubleshooting tips.

---

## 🌍 Environment Variables

| Variable              | Description                                              | Required | Default                                      |
|-----------------------|----------------------------------------------------------|----------|----------------------------------------------|
| `OPENAI_API_KEY`      | API key for OpenAI (enables AI features)                | Yes      | –                                            |
| `AICOMMIT_API_KEY`    | API key for aicommit (if different from OpenAI)         | No       | –                                            |
| `AICOMMIT_CONFIG_PATH`| Path to a custom aicommit config file                   | No       | `.aicommit/config.toml`                      |
| `WIKI_PATH`           | Path to your Wiki directory                            | No       | `wiki`                                       |
| `README_PATH`         | Path to your README file                               | No       | `README.md`                                  |
| `WIKI_URL`            | Base URL for your Wiki (for links in README)           | No       | `https://github.com/auraz/ai_commit_and_readme/wiki/` |
| `WIKI_URL_BASE`       | Base URL for Wiki articles                             | No       | –                                            |
| `MODEL`               | OpenAI model to use (e.g., `gpt-4o`, `gpt-4`)          | No       | `gpt-4o`                                     |

---

## 📝 Example Usage

Set environment variables in your shell or `.env` file:

```sh
export OPENAI_API_KEY=sk-...
export WIKI_PATH=docs/wiki
export MODEL=gpt-4o
```

Or use a `.env` file (with [python-dotenv](https://pypi.org/project/python-dotenv/) or similar):

```env
OPENAI_API_KEY=sk-...
WIKI_PATH=docs/wiki
MODEL=gpt-4o
```

---

## 💡 Best Practices

- **Keep your API keys secret!** Never commit them to version control.
- Use a `.env` file for local development and set variables in your CI/CD environment for production.
- If you use a custom Wiki or README location, set `WIKI_PATH` and `README_PATH` accordingly.
- For advanced AI features, you can experiment with different `MODEL` values.

---

## 🛠️ Troubleshooting

- **Missing API Key:**
  - If `OPENAI_API_KEY` is not set, AI features will be disabled and you'll see a warning or the program will exit gracefully.
- **File Not Found:**
  - If the specified README or Wiki file does not exist, the tool will use an empty string and continue.
- **Permission Errors:**
  - Ensure your user has read/write access to the configured files and directories.
- **Unexpected Output?**
  - Double-check your environment variables and config file paths.

---

For more advanced configuration, see the [Usage](Usage) and [FAQ](FAQ) pages.


## 🛠️ Makefile Commands Overview

(Output the new or updated content for the "Makefile Commands Overview" section here.)

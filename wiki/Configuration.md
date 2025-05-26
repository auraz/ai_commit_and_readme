# ⚙️ Configuration

Easily configure **autodoc_ai** to fit your workflow using environment variables and optional config files. This page covers all available options, best practices, and troubleshooting tips.

---

## 🌍 Environment Variables

| Variable              | Description                                              | Required | Default                                      |
|-----------------------|----------------------------------------------------------|----------|----------------------------------------------|
| `OPENAI_API_KEY`      | API key for OpenAI (enables AI features)                | Yes      | –                                            |
| `AICOMMIT_API_KEY`    | API key for aicommit (if different from OpenAI)         | No       | –                                            |
| `AICOMMIT_CONFIG_PATH`| Path to a custom aicommit config file                   | No       | `.aicommit/config.toml`                      |
| `WIKI_PATH`           | Path to your Wiki directory                            | No       | `wiki`                                       |
| `README_PATH`         | Path to your README file                               | No       | `README.md`                                  |
| `WIKI_URL`            | Base URL for your Wiki (for links in README)           | No       | `https://github.com/auraz/autodoc_ai/wiki/` |
| `WIKI_URL_BASE`       | Base URL for Wiki articles                             | No       | –                                            |
| `MODEL`               | OpenAI model to use (e.g., `gpt-4o`, `gpt-4`)          | No       | `gpt-4.1`                                     |

---

## 🛠️ Troubleshooting

- **Missing API Key:**
  - If `OPENAI_API_KEY` is not set, AI features will be disabled and you'll see a warning or the program will exit gracefully.
- **Permission Errors:**
  - Ensure your user has read/write access to the configured files and directories.
- **Unexpected Output?**
  - Double-check your environment variables and config file paths.

---

For more advanced configuration, see the [Usage](Usage) and [FAQ](FAQ) pages.


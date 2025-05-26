# ⚙️ Configuration

Easily configure **autodoc_ai** to fit your workflow using environment variables and optional config files. This page covers all available options, best practices, and troubleshooting tips.

---

## 🌍 Environment Variables

| Variable              | Description                                              | Required | Default                                      |
|-----------------------|----------------------------------------------------------|----------|----------------------------------------------|
| `OPENAI_API_KEY`      | API key for OpenAI (enables AI features)                | Yes      | –                                            |
| `AUTODOC_MODEL`       | OpenAI model to use (see supported models below)       | No       | `gpt-4o`                                     |
| `AICOMMIT_API_KEY`    | API key for aicommit (if different from OpenAI)         | No       | –                                            |
| `AICOMMIT_CONFIG_PATH`| Path to a custom aicommit config file                   | No       | `.aicommit/config.toml`                      |
| `WIKI_PATH`           | Path to your Wiki directory                            | No       | `wiki`                                       |
| `README_PATH`         | Path to your README file                               | No       | `README.md`                                  |
| `WIKI_URL`            | Base URL for your Wiki (for links in README)           | No       | `https://github.com/auraz/autodoc_ai/wiki/` |
| `WIKI_URL_BASE`       | Base URL for Wiki articles                             | No       | –                                            |
| `AUTODOC_TARGET_SCORE`| Target score for document improvement (0-100)          | No       | `85`                                         |
| `AUTODOC_MAX_ITERATIONS`| Max iterations for document improvement              | No       | `3`                                          |

---

## 🤖 Supported Models

- `gpt-4o` (default) - 128K context window
- `gpt-4o-mini` - 128K context window, faster and cheaper
- `gpt-4-turbo` - 128K context window
- `gpt-4` - 8K context window
- `gpt-3.5-turbo` - 16K context window

**Note**: When using time-based enrichment (`just enrich-days`), large diffs may exceed model context limits. For very large diffs, reduce the time period or use staged changes instead.

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


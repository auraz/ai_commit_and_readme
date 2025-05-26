# ⚙️ Configuration

Easily configure **autodoc_ai** to fit your workflow using environment variables and optional config files. This page covers all available options, best practices, and troubleshooting tips, including new Bash command integrations.

---

## 🌍 Environment Variables

| Variable                  | Description                                              | Required | Default                                      |
|---------------------------|----------------------------------------------------------|----------|----------------------------------------------|
| `OPENAI_API_KEY`         | API key for OpenAI (enables AI features)                | Yes      | –                                            |
| `AUTODOC_MODEL`          | OpenAI model to use (see supported models below)       | No       | `gpt-4o-mini`                                |
| `AICOMMIT_API_KEY`       | API key for aicommit (if different from OpenAI)         | No       | –                                            |
| `AICOMMIT_CONFIG_PATH`   | Path to a custom aicommit config file                   | No       | `.aicommit/config.toml`                      |
| `WIKI_PATH`              | Path to your Wiki directory                            | No       | `wiki`                                       |
| `README_PATH`            | Path to your README file                               | No       | `README.md`                                  |
| `WIKI_URL`               | Base URL for your Wiki (for links in README)           | No       | `https://github.com/auraz/autodoc_ai/wiki/` |
| `WIKI_URL_BASE`          | Base URL for Wiki articles                             | No       | –                                            |
| `AUTODOC_TARGET_SCORE`    | Target score for document improvement (0-100)          | No       | `85`                                         |
| `AUTODOC_MAX_ITERATIONS` | Max iterations for document improvement                  | No       | `3`                                          |
| `AUTODOC_LOG_LEVEL`      | Logging level (DEBUG, INFO, WARNING, ERROR)           | No       | `INFO`                                       |
| `AUTODOC_DISABLE_CALLBACKS` | Disable CrewAI callbacks (troubleshooting)         | No       | `false`                                      |
| `BASH_COMMIT_COMMAND`    | Bash command for committing changes                     | No       | `Bash(just commit:*)`                        |
| `BASH_COMMIT_SHORTCUT`   | Short Bash command for committing changes               | No       | `Bash(just cm:*)`                            |

---

## 🤖 Supported Models

- `gpt-4o-mini` (default) - 128K context window, faster and cheaper
- `gpt-4o` - 128K context window
- `gpt-4-turbo` - 128K context window
- `gpt-4` - 8K context window
- `gpt-3.5-turbo` - 16K context window

**Note**: When using time-based enrichment (`just enrich-days`), large diffs may exceed model context limits. For very large diffs, reduce the time period or use staged changes instead.

---

## 🐛 Debug Logging

To enable maximum verbose debug logging for troubleshooting:

```bash
export AUTODOC_LOG_LEVEL="DEBUG"
```

This will enable the most verbose output for:
- All autodoc_ai components with full details
- CrewAI agent execution steps with complete traces
- LiteLLM API calls with request/response details
- Git diff processing with full content preview
- Task execution callbacks with complete output
- Agent reasoning and decision-making process
- Step-by-step execution flow
- Complete API payloads and responses

Additional debug features in DEBUG mode:
- Timestamps and file paths in logs
- Extended agent iterations (10 vs 5)
- Full task and agent object details
- Complete diff content (first 1000 chars)

**Warning**: Debug mode generates VERY extensive output. Use it only when troubleshooting complex issues or understanding the AI's decision process.

---

## 🛠️ Troubleshooting

- **Missing API Key:**
  - If `OPENAI_API_KEY` is not set, AI features will be disabled and you'll see a warning or the program will exit gracefully.
- **Permission Errors:**
  - Ensure your user has read/write access to the configured files and directories.
- **Unexpected Output?**
  - Double-check your environment variables and config file paths.
- **CrewAI Callback Errors:**
  - If you encounter issues with CrewAI callbacks returning None or causing errors, set `AUTODOC_DISABLE_CALLBACKS="true"` to disable them temporarily.
  - This disables step-by-step execution tracking but allows the crews to complete successfully.
- **Bash Command Issues:**
  - If you encounter issues with the new Bash commands, ensure they are formatted correctly and match the expected patterns.
  - Verify that your environment is set up to support these Bash commands.

---

For more advanced configuration, see the [Usage](Usage) and [FAQ](FAQ) pages.

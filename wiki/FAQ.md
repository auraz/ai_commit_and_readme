# ❓ Frequently Asked Questions (FAQ)

Find answers to common questions about **autodoc_ai**. For more details, see the [Wiki](Home).

---

### 🚀 Getting Started

**Q: How do I set up autodoc_ai for my project?**
- **A:** Follow the [Installation](Installation) and [Configuration](Configuration) guides in the Wiki.

**Q: How do I create and activate a virtual environment?**
- **A:**
  ```sh
  python3 -m venv .venv
  source .venv/bin/activate
  export PATH="$PWD/.venv/bin:$PATH"
  ```

**Q: How do I install the aicommit CLI tool?**
- **A:** Run `make aicommit` or see [Installation](Installation).

---

### ⚙️ Configuration & Customization

**Q: Can I customize the commit message format?**
- **A:** Yes! See the [Configuration](Configuration) page for options and environment variables.

**Q: How do I use a custom Wiki or README location?**
- **A:** Set the `WIKI_PATH` and `README_PATH` environment variables.

**Q: Can I use a different OpenAI model?**
- **A:** Yes, set the `MODEL` environment variable (e.g., `gpt-4o`, `gpt-4`).

---

### 🧠 AI & Enrichment

**Q: What happens if my API key is missing or incorrect?**
- **A:** The program will exit gracefully with an error message. Make sure to set the `OPENAI_API_KEY` environment variable.

**Q: What if there are no changes to commit?**
- **A:** The system will display "No staged changes detected. Nothing to enrich." when running `make cm` if there are no changes to commit.

**Q: How does the AI decide what to enrich?**
- **A:** It analyzes your git diff and current documentation, then suggests only relevant improvements.

**Q: Can I preview AI suggestions before applying them?**
- **A:** Not yet, but you can review changes in your git diff before committing.

---

### 🛠️ Troubleshooting

**Q: The tool says a file is missing—what should I do?**
- **A:** If the README or Wiki file does not exist, -- create them

**Q: I get a permission error.**
- **A:** Ensure you have read/write access to the relevant files and directories.

**Q: The AI output is not what I expected.**
- **A:** Try updating your prompt templates or experiment with a different model.

---

### 🌟 Advanced & More Help

- See [Usage](Usage) for advanced workflows and automation.
- For more help, open an [issue on GitHub](https://github.com/auraz/autodoc_ai/issues) or join the discussion!

---

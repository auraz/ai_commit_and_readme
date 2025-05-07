# FAQ

**Q:** How do I set up ai_commit_and_readme for my project?
**A:** Follow the instructions in the [Installation](Installation) and [Configuration](Configuration) pages.

**Q:** Can I customize the commit message format?
**A:** Yes, see the [Configuration](Configuration) page for options.

**Q:** How do I create and activate a virtual environment?
**A:**
```sh
python3 -m venv .venv
source .venv/bin/activate
export PATH="$PWD/.venv/bin:$PATH"
```

**Q:** How do I install the aicommit CLI tool?
**A:** Run `make aicommit` or follow the instructions in the [Installation](Installation) page.

**Q:** What happens if my API key is missing or incorrect?
**A:** The program will exit gracefully with an error message. Make sure to set the `OPENAI_API_KEY` environment variable.

**Q:** What if there are no changes to commit?
**A:** The system will display "No staged changes detected. Nothing to enrich." when running `make cm` if there are no changes to commit.

Add more questions and answers as needed.

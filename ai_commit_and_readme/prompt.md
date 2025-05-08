## enrich

You are an expert software documenter.
Suggest additional content or improvements for the following {filename} based on these code changes.
If the code changes include updates to the Makefile, carefully review and update Usage.md or any documentation that describes project commands to ensure it reflects the latest Makefile changes.
Only output new or updated sections, not the full {filename}.
If you update an existing section, start with the section header (the line beginning with '## ' and matching exactly as it appears in the file), followed by the new content for that section.
If you update multiple sections, output each section header and its new content, one after another.
If nothing should be changed, reply with 'NO CHANGES'.

Example:
If you want to update the section '## 🛠️ Makefile Commands Overview', output:

## 🛠️ Makefile Commands Overview

<new content for this section>

Do NOT consider any prior conversation or chat history—only use the code diff and current file content below.

Code changes:
{diff}

Current {filename}:
{{{filename}}}

## select_articles

You are an expert software documenter.
Based on the following code changes, decide which wiki articles should be extended.
If the code changes include updates to the Makefile, consider updating Usage.md or any documentation that describes project commands.

Code changes:
{diff}

Here are the available wiki articles (filenames):
{article_list}

Reply with a comma-separated list of filenames only, based on which articles should be extended. If none, reply with an empty string or 'NO CHANGES'.

#!/usr/bin/env python3
"""
AI Commit and README tool main module.
Provides subcommands for enriching README.md with AI suggestions based on git diffs.
"""

import argparse
import openai
import subprocess
import os
import sys
import tiktoken
import glob
from pathlib import Path
from .tools import get_enrich_prompt, chain_handler
from .constants import README_PATH, WIKI_PATH


@chain_handler
def check_api_key(ctx):
    """Check for the presence of the OpenAI API key in context or environment."""
    ctx["api_key"] = ctx.get("api_key") or os.getenv("OPENAI_API_KEY")
    if not ctx["api_key"]:
        print("OPENAI_API_KEY not set. Skipping README update.") or sys.exit(0)

@chain_handler
def get_diff(ctx, diff_args=None):
    """Retrieve the staged git diff (or file list) and store it in context."""
    ctx["diff"] = subprocess.check_output(diff_args or ["git", "diff", "--cached", "-U1"]).decode()

@chain_handler
def check_diff_empty(ctx):
    """Exit if the diff is empty, with a message."""
    if not ctx["diff"].strip():
        print("No staged changes detected. Nothing to enrich.")
        sys.exit(0)

@chain_handler
def print_diff_info(ctx):
    """Print the size of the diff in characters and tokens."""
    print(f"[INFO] Diff size: {len(ctx['diff'])} characters")
    enc = tiktoken.encoding_for_model(ctx["model"])
    diff_tokens = len(enc.encode(ctx["diff"]))
    print(f"[INFO] Diff size: {diff_tokens} tokens")
    ctx["diff_tokens"] = diff_tokens

@chain_handler
def fallback_large_diff(ctx):
    """Fallback to file list if the diff is too large."""
    if len(ctx["diff"]) > 100000:
        print("[WARNING] Diff is too large (>100000 characters). Falling back to 'git diff --cached --name-only'.")
        get_diff(ctx, ["git", "diff", "--cached", "--name-only"])
        print(f"[INFO] Using file list as diff: {ctx['diff'].strip()}")

@chain_handler
def get_file(ctx, file_key, path_key):
    """Read the file at ctx[path_key] and store its contents in ctx[file_key]."""
    path = ctx[path_key]
    ctx[file_key] = open(path).read() if os.path.exists(path) else ""

@chain_handler
def print_file_info(ctx, file_key, model_key):
    """Print the size of the file in characters and tokens."""
    content = ctx[file_key]
    print(f"[INFO] {file_key} size: {len(content)} characters")
    enc = tiktoken.encoding_for_model(ctx[model_key])
    tokens = len(enc.encode(content))
    print(f"[INFO] {file_key} size: {tokens} tokens")
    ctx[f"{file_key}_tokens"] = tokens

def get_ai_response(prompt, model):
    """Return an OpenAI client response for the given prompt and model."""
    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(model=ctx["model"], messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        print(f"Error from OpenAI API: {e}")
        sys.exit(1)
    return response

@chain_handler
def ai_enrich(ctx):
    """Call the OpenAI API to get README enrichment suggestions."""
    prompt = get_enrich_prompt("README.md", "readme").format(diff=ctx["diff"], readme=ctx["readme"])
    response = get_ai_response(prompt, ctx["model"])
    ai_suggestion = response.choices[0].message.content.strip()
    ctx["ai_suggestion"] = ai_suggestion

def write_enrichment_outputs(ctx):
    """
    Write AI suggestions to README and/or Wiki, and update README with wiki summary and link if needed.
    Always uses the root-level README.md from constants.
    """
    readme_path = README_PATH
    wiki_path = ctx.get("wiki_path") or WIKI_PATH
    wiki_url = ctx.get("wiki_url")
    section = ctx.get("section")
    ai_suggestion = ctx.get("ai_suggestion")

    # Write enrichment to README if path is provided
    if ai_suggestion != "NO CHANGES":
        with open(readme_path, "a") as f:
            f.write("\n\n# AI-suggested enrichment:\n")
            f.write(ai_suggestion)
        print(f"{readme_path} enriched and staged with AI suggestions.")
        subprocess.run(["git", "add", readme_path])
    else:
        print("No enrichment needed for README.md.")

    # Write enrichment to Wiki if path is provided
    if wiki_path and ai_suggestion != "NO CHANGES":
        with open(wiki_path, "a") as f:
            f.write("\n\n---\n\n# AI-suggested enrichment:\n")
            f.write(ai_suggestion)
        print(f"\n[INFO] Wiki page enriched: {wiki_path}")
        # Optionally update README with summary and link
        if wiki_url and section:
            import re
            summary = ai_suggestion.strip().split('\n\n')[0]
            content = open(readme_path).read()
            pattern = rf"## {section}.*?(?=## |\Z)"
            replacement = f"## {section}\n\n{summary}\n\nSee the [full {section} guide in the Wiki]({wiki_url}).\n"
            new_content, n = re.subn(pattern, replacement, content, flags=re.DOTALL)
            if n == 0:
                new_content = content + f"\n## {section}\n\n{summary}\n\nSee the [full {section} guide in the Wiki]({wiki_url}).\n"
            with open(readme_path, "w") as f:
                f.write(new_content)
            print("[INFO] README updated with summary and link to wiki.")
    elif wiki_path:
        print("No enrichment needed for wiki.")

def enrich_docs(readme_path=None, wiki_path=None, section=None, wiki_url=None, api_key=None, model="gpt-4o"):
    """
    Enrich README.md, a wiki files, or all, with AI-generated suggestions using a handler chain.
    Always uses the root-level README.md for README operations.
    """
    ctx = {
        "readme_path": README_PATH,
        "wiki_path": wiki_path or WIKI_PATH,
        "section": section,
        "wiki_url": wiki_url,
        "api_key": api_key,
        "model": model,
    }
    for handler in [
        check_api_key,
        get_diff,
        check_diff_empty,
        print_diff_info,
        fallback_large_diff,
        get_file,
        print_file_info,
        ai_enrich,
    ]:
        ctx = handler(ctx)

    write_enrichment_outputs(ctx)


def select_wiki_article(ctx):
    """Ask the AI which wiki article to extend based on the diff"""
    wiki_dir = ctx["wiki_dir"]
    wiki_files = [f for f in glob.glob(f"{wiki_dir}/*.md") if not f.endswith("Home.md")]
    article_list = "\n".join([os.path.basename(f) for f in wiki_files])
    prompt = f"Here are the available wiki articles (filenames):\n{article_list}\nBased on the code changes, which article should be extended? Reply with the filename only.\n" + get_enrich_prompt(
        "README.md", "readme"
    )
    response = get_ai_response(prompt, ctx["model"])
    filename = response.choices[0].message.content.strip()
    # Validate filename
    if filename not in [os.path.basename(f) for f in wiki_files]:
        print(f"AI selected invalid wiki article: {filename}. Defaulting to Usage.md.")
        filename = "Usage.md"
    ctx["wiki_path"] = os.path.join(wiki_dir, filename)
    ctx["section"] = os.path.splitext(filename)[0]
    ctx["wiki_url"] = ctx["wiki_url_base"] + filename.replace(".md", "")
    print(f"AI selected wiki article: {filename}")
    return ctx


def enrich_wiki_auto(wiki_dir, wiki_url_base, readme_path="README.md", api_key=None, model="gpt-4o"):
    ctx = {
        "wiki_dir": wiki_dir,
        "wiki_url_base": wiki_url_base,
        "readme_path": readme_path,
        "api_key": api_key,
        "model": model,
    }
    for handler in [
        check_api_key,
        get_diff,
        check_diff_empty,
        print_diff_info,
        fallback_large_diff,
        get_file,
        print_file_info,
        select_wiki_article,
        ai_enrich,
        enrich_docs,
    ]:
        ctx = handler(ctx)


def enrich_all(wiki_dir, wiki_url_base, readme_path="README.md", api_key=None, model="gpt-4o"):
    ctx = {
        "wiki_dir": wiki_dir,
        "wiki_url_base": wiki_url_base,
        "readme_path": readme_path,
        "api_key": api_key,
        "model": model,
    }
    # Handler chain up to AI suggestion and wiki selection
    for handler in [
        check_api_key,
        get_diff,
        check_diff_empty,
        print_diff_info,
        fallback_large_diff,
        get_file,
        print_file_info,
        select_wiki_article,
        ai_enrich,
    ]:
        ctx = handler(ctx)
    # Write enrichment to wiki
    if ctx["ai_suggestion"] != "NO CHANGES":
        with open(ctx["wiki_path"], "a") as f:
            f.write("\n\n---\n\n# AI-suggested enrichment:\n")
            f.write(ctx["ai_suggestion"])
        print(f"\n[INFO] Wiki page enriched: {ctx['wiki_path']}")
        # Update README with summary and link
        import re

        readme_path = ctx["readme_path"]
        wiki_url = ctx["wiki_url"]
        section = ctx["section"]
        summary = ctx["ai_suggestion"].strip().split("\n\n")[0]
        content = open(readme_path).read()
        pattern = rf"## {section}.*?(?=## |\Z)"
        replacement = f"## {section}\n\n{summary}\n\nSee the [full {section} guide in the Wiki]({wiki_url}).\n"
        new_content, n = re.subn(pattern, replacement, content, flags=re.DOTALL)
        if n == 0:
            new_content = content + f"\n## {section}\n\n{summary}\n\nSee the [full {section} guide in the Wiki]({wiki_url}).\n"
        with open(readme_path, "w") as f:
            f.write(new_content)
        print("[INFO] README updated with summary and link to wiki.")
    else:
        print("No enrichment needed for wiki or README.")


def update_wiki(wiki_file, enrichment_text):
    wiki_path = Path(wiki_file)
    content = wiki_path.read_text(encoding="utf-8")
    # Simple append; customize as needed
    content += f"\n\n---\n\n{enrichment_text}\n"
    wiki_path.write_text(content, encoding="utf-8")


def update_readme(readme_file, section, summary, wiki_url):
    readme_path = Path(readme_file)
    content = readme_path.read_text(encoding="utf-8")
    # Replace or insert section with summary and link
    import re

    pattern = rf"## {section}.*?(?=## |\Z)"
    replacement = f"## {section}\n\n{summary}\n\nSee the [full {section} guide in the Wiki]({wiki_url}).\n"
    new_content, n = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if n == 0:
        # Section not found, append at end
        new_content = content + f"\n## {section}\n\n{summary}\n\nSee the [full {section} guide in the Wiki]({wiki_url}).\n"
    readme_path.write_text(new_content, encoding="utf-8")


def enrich_wiki_and_readme_script():
    if len(sys.argv) == 6:
        section, enrichment_file, wiki_file, readme_file, wiki_url = sys.argv[1:6]
        enrichment_text = Path(enrichment_file).read_text(encoding="utf-8")
        # For README, use the first paragraph as summary
        summary = enrichment_text.strip().split("\n\n")[0]
        update_wiki(wiki_file, enrichment_text)
        update_readme(readme_file, section, summary, wiki_url)
        print(f"Updated {wiki_file} and {readme_file} for section '{section}'.")
        sys.exit(0)
    # ... existing code ...

#!/usr/bin/env python3
"""
AI Commit and README tool main module.
Provides subcommands for enriching README.md with AI suggestions based on git diffs.
test222
"""

import logging
import os
import re
import subprocess
import sys

import openai
import tiktoken
from rich.logging import RichHandler

from .constants import README_PATH, WIKI_PATH  # noqa: F401
from .tools import chain_handler, get_prompt_template

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True, markup=True)])


@chain_handler
def check_api_key(ctx):
    """Check for the presence of the OpenAI API key in context or environment."""
    ctx["api_key"] = ctx.get("api_key") or os.getenv("OPENAI_API_KEY")
    if not ctx["api_key"]:
        logging.warning("🔑 OPENAI_API_KEY not set. Skipping README update.")
        sys.exit(0)


@chain_handler
def get_diff(ctx, diff_args=None):
    """Retrieve the staged git diff (or file list) and store it in context."""
    ctx["diff"] = subprocess.check_output(diff_args or ["git", "diff", "--cached", "-U1"]).decode()


@chain_handler
def check_diff_empty(ctx):
    """Exit if the diff is empty, with a message."""
    if not ctx["diff"].strip():
        logging.info("✅ No staged changes detected. Nothing to enrich.")
        sys.exit(0)


@chain_handler
def print_diff_info(ctx):
    """Print the size of the diff in characters and tokens."""
    logging.info(f"📏 Your staged changes are {len(ctx['diff']):,} characters long!")
    enc = tiktoken.encoding_for_model(ctx["model"])
    diff_tokens = len(enc.encode(ctx["diff"]))
    logging.info(f"🔢 That's about {diff_tokens:,} tokens for the AI to read.")
    ctx["diff_tokens"] = diff_tokens


@chain_handler
def fallback_large_diff(ctx):
    """Fallback to file list if the diff is too large."""
    if len(ctx["diff"]) > 100000:
        logging.warning('⚠️  Diff is too large (>100000 characters). Falling back to "git diff --cached --name-only".')
        get_diff(ctx, ["git", "diff", "--cached", "--name-only"])
        logging.info(f"📄 Using file list as diff: {ctx['diff'].strip()}")


@chain_handler
def get_file(ctx, file_key, path_key):
    """Read the file at path_key and store its contents in ctx[file_key]."""
    with open(path_key) as f:
        ctx[file_key] = f.read()


@chain_handler
def print_file_info(ctx, file_key, model_key):
    """Print the size of the file update in characters and tokens."""
    content = ctx[file_key]
    logging.info(f"📄 Update to {file_key} is currently {len(content):,} characters.")
    enc = tiktoken.encoding_for_model(ctx[model_key])
    tokens = len(enc.encode(content))
    logging.info(f"🔢 That's {tokens:,} tokens in update to {file_key}!")
    ctx[f"{file_key}_tokens"] = tokens


def get_ai_response(prompt, ctx=None):
    """Return an OpenAI client response for the given prompt and model."""
    api_key = ctx["api_key"] if ctx and "api_key" in ctx else None
    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(model=ctx["model"], messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        logging.error(f"❌ Error from OpenAI API: {e}")
        sys.exit(1)
    return response


@chain_handler
def ai_enrich(ctx, filename):
    """Call the OpenAI API to get enrichment suggestions for any file."""
    prompt = get_prompt_template("enrich").format(filename=filename, diff=ctx["diff"], **{filename: ctx[filename]})
    response = get_ai_response(prompt, ctx)
    ai_suggestion = response.choices[0].message.content.strip()
    ctx["ai_suggestions"][filename] = ai_suggestion
    return ctx


def select_wiki_articles(ctx):
    """Ask the AI which wiki articles to extend based on the diff, return a list."""
    wiki_files = ctx["wiki_files"]
    article_list = "\n".join(wiki_files)
    prompt = get_prompt_template("select_articles").format(diff=ctx["diff"], article_list=article_list)
    response = get_ai_response(prompt, ctx)
    filenames = [fn.strip() for fn in response.choices[0].message.content.split(",") if fn.strip()]
    valid_filenames = [fn for fn in filenames if fn in wiki_files]
    if not valid_filenames:
        logging.info("[i] No valid wiki articles selected. Using Usage.md as fallback.")
        valid_filenames = ["Usage.md"]
    ctx["selected_wiki_articles"] = valid_filenames
    return ctx


def enrich_readme(ctx):
    """Enrich the README file with AI suggestions."""
    return ai_enrich(ctx, "README.md")


def enrich_selected_wikis(ctx):
    """Enrich the selected wiki articles."""
    if "wiki" not in ctx["ai_suggestions"] or not isinstance(ctx["ai_suggestions"]["wiki"], dict):
        ctx["ai_suggestions"]["wiki"] = {}
    for filename in ctx["selected_wiki_articles"]:
        suggestion_ctx = ai_enrich(ctx, filename)
        ctx["ai_suggestions"]["wiki"][filename] = suggestion_ctx["ai_suggestions"][filename]
    return ctx


def append_suggestion_and_stage(file_path, ai_suggestion, label):
    """Enrich the file by replacing the relevant section if possible, otherwise append, and stage it with git."""
    if ai_suggestion and ai_suggestion != "NO CHANGES":
        # Try to find a section header in the suggestion (e.g., '## Section Header')
        section_header_match = re.match(r"^(## .+)$", ai_suggestion.strip(), re.MULTILINE)
        if section_header_match:
            section_header = section_header_match.group(1)
            with open(file_path, encoding="utf-8") as f:
                file_content = f.read()
            # Replace the section if it exists, otherwise append
            pattern = rf"({re.escape(section_header)}\n)(.*?)(?=\n## |\Z)"
            replacement = f"\\1{ai_suggestion.strip().split('\n', 1)[1].strip()}\n"
            new_content, count = re.subn(pattern, replacement, file_content, flags=re.DOTALL)
            if count == 0:
                # Section not found, append at the end
                new_content = file_content + f"\n\n{ai_suggestion.strip()}\n"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        else:
            # No section header, just append
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(ai_suggestion)
        logging.info(f"🎉✨ SUCCESS: {file_path} enriched and staged with AI suggestions for {label}! ✨🎉")
        subprocess.run(["git", "add", file_path])
    else:
        logging.info(f"👍 No enrichment needed for {file_path}.")


def write_enrichment_outputs(ctx):
    """Write AI suggestions to their corresponding files, and update README with wiki summary and link if needed."""
    file_path = ctx["file_paths"]["README.md"]
    ai_suggestion = ctx["ai_suggestions"]["README.md"]
    append_suggestion_and_stage(file_path, ai_suggestion, "README")
    for filename, ai_suggestion in ctx["ai_suggestions"].get("wiki", {}).items():
        file_path = ctx["file_paths"]["wiki"][filename]
        append_suggestion_and_stage(file_path, ai_suggestion, filename)


def print_selected_wiki_files(ctx):
    """Print file info for each selected wiki article."""
    for filename in ctx["selected_wiki_articles"]:
        print_file_info(ctx, filename, "model")
    return ctx


def get_selected_wiki_files(ctx):
    """Read each selected wiki file and store its contents in the context."""
    for filename in ctx["selected_wiki_articles"]:
        get_file(ctx, filename, ctx["wiki_file_paths"][filename])
    return ctx


def enrich():
    """Handler chain for enriching wiki and readme (multi-wiki support)."""
    ctx = {}
    for handler in [
        check_api_key,
        get_diff,
        check_diff_empty,
        print_diff_info,
        fallback_large_diff,
        lambda ctx: get_file(ctx, "README.md", ctx["readme_path"]),
        lambda ctx: print_file_info(ctx, "README.md", "model"),
        select_wiki_articles,
        enrich_readme,
        get_selected_wiki_files,
        print_selected_wiki_files,
        enrich_selected_wikis,
    ]:
        ctx = handler(ctx)
    write_enrichment_outputs(ctx)

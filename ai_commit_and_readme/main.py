#!/usr/bin/env python3
"""
AI Commit and README tool main module.
Provides subcommands for enriching README.md with AI suggestions based on git diffs.
"""

import logging
import os
import re
import subprocess
import sys
from typing import Any, Callable, Optional

import openai
import tiktoken
from pipetools import pipe
from rich.logging import RichHandler

from .tools import CtxDict, ensure_initialized, get_prompt_template, initialize_context

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True, markup=True)])


def check_api_key(ctx: CtxDict) -> CtxDict:
    """Check for the presence of the OpenAI API key in context or environment."""
    ctx["api_key"] = ctx.get("api_key") or os.getenv("OPENAI_API_KEY")
    if not ctx["api_key"]:
        logging.warning("🔑 OPENAI_API_KEY not set. Skipping README update.")
        sys.exit(0)
    return ctx


check_api_key = ensure_initialized(check_api_key)


def get_diff(diff_args: Optional[list[str]] = None):
    """Retrieve the staged git diff (or file list) and store it in context."""

    def _get_diff(ctx: CtxDict) -> CtxDict:
        ctx["diff"] = subprocess.check_output(diff_args or ["git", "diff", "--cached", "-U1"]).decode()
        return ctx

    return ensure_initialized(_get_diff)


def check_diff_empty(ctx: CtxDict) -> CtxDict:
    """Exit if the diff is empty, with a message."""
    if not ctx["diff"].strip():
        logging.info("✅ No staged changes detected. Nothing to enrich.")
        sys.exit(0)
    return ctx


check_diff_empty = ensure_initialized(check_diff_empty)


def print_diff_info(ctx: CtxDict) -> CtxDict:
    """Print the size of the diff in characters and tokens."""
    logging.info(f"📏 Your staged changes are {len(ctx['diff']):,} characters long!")
    enc = tiktoken.encoding_for_model(ctx["model"])
    diff_tokens: int = len(enc.encode(ctx["diff"]))
    logging.info(f"🔢 That's about {diff_tokens:,} tokens for the AI to read.")
    ctx["diff_tokens"] = diff_tokens
    return ctx

print_diff_info = ensure_initialized(print_diff_info)


def fallback_large_diff(ctx: CtxDict) -> CtxDict:
    """Fallback to file list if the diff is too large."""
    if len(ctx["diff"]) > 100000:
        logging.warning('⚠️  Diff is too large (>100000 characters). Falling back to "git diff --cached --name-only".')
        return get_diff(["git", "diff", "--cached", "--name-only"])(ctx)
    return ctx


fallback_large_diff = ensure_initialized(fallback_large_diff)


def get_file(file_key: str, path_key: str):
    """Read the file at path_key and store its contents in ctx[file_key]."""

    def _get_file(ctx: CtxDict) -> CtxDict:
        path = ctx[path_key]
        with open(path) as f:
            ctx[file_key] = f.read()
        return ctx

    return ensure_initialized(_get_file)


def print_file_info(file_key: str, model_key: str):
    """Print the size of the file update in characters and tokens."""
    def _print_file_info(ctx: CtxDict) -> CtxDict:
        content: str = ctx[file_key]
        logging.info(f"📄 Update to {file_key} is currently {len(content):,} characters.")
        enc = tiktoken.encoding_for_model(ctx[model_key])
        tokens: int = len(enc.encode(content))
        logging.info(f"🔢 That's {tokens:,} tokens in update to {file_key}!")
        ctx[f"{file_key}_tokens"] = tokens
        return ctx
    return ensure_initialized(_print_file_info)

def get_ai_response(prompt: str, ctx: Optional[CtxDict] = None) -> Any:
    """Return an OpenAI client response for the given prompt and model."""
    api_key: Optional[str] = ctx["api_key"] if ctx and "api_key" in ctx else None
    client = openai.OpenAI(api_key=api_key)
    try:
        model_name = ctx["model"] if ctx and "model" in ctx else "gpt-4"
        response = client.chat.completions.create(model=model_name, messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        logging.error(f"❌ Error from OpenAI API: {e}")
        sys.exit(1)
    return response


def ai_enrich(filename: str):
    """Call the OpenAI API to get enrichment suggestions for any file."""
    def _ai_enrich(ctx: CtxDict) -> CtxDict:
        prompt: str = get_prompt_template("enrich").format(filename=filename, diff=ctx["diff"], **{filename: ctx[filename]})
        response = get_ai_response(prompt, ctx)
        # Access the content safely
        ai_suggestion = ""
        if hasattr(response, "choices") and response.choices and hasattr(response.choices[0], "message") and hasattr(response.choices[0].message, "content") and response.choices[0].message.content:
            ai_suggestion = response.choices[0].message.content.strip()
        ctx["ai_suggestions"][filename] = ai_suggestion
        return ctx
    return ensure_initialized(_ai_enrich)

def select_wiki_articles(ctx: CtxDict) -> CtxDict:
    """Ask the AI which wiki articles to extend based on the diff, return a list."""
    wiki_files: list[str] = ctx["wiki_files"]
    article_list: str = "\n".join(wiki_files)
    prompt: str = get_prompt_template("select_articles").format(diff=ctx["diff"], article_list=article_list)
    response = get_ai_response(prompt, ctx)

    # Extract filenames safely
    filenames: list[str] = []
    if hasattr(response, "choices") and response.choices and hasattr(response.choices[0], "message") and hasattr(response.choices[0].message, "content") and response.choices[0].message.content:
        content = response.choices[0].message.content
        filenames = [fn.strip() for fn in content.split(",") if fn.strip()]
    valid_filenames: list[str] = [fn for fn in filenames if fn in wiki_files]
    if not valid_filenames:
        logging.info("[i] No valid wiki articles selected. Using Usage.md as fallback.")
        valid_filenames = ["Usage.md"]
    ctx["selected_wiki_articles"] = valid_filenames
    return ctx

select_wiki_articles = ensure_initialized(select_wiki_articles)


def enrich_readme() -> Callable[[CtxDict], CtxDict]:
    """Enrich the README file with AI suggestions."""
    return ai_enrich("README.md")


def enrich_selected_wikis(ctx: CtxDict) -> CtxDict:
    """Enrich the selected wiki articles."""
    if "wiki" not in ctx["ai_suggestions"] or not isinstance(ctx["ai_suggestions"]["wiki"], dict):
        ctx["ai_suggestions"]["wiki"] = {}
    for filename in ctx["selected_wiki_articles"]:
        updated_ctx = ai_enrich(filename)(ctx)
        ctx["ai_suggestions"]["wiki"][filename] = updated_ctx["ai_suggestions"][filename]
    return ctx


enrich_selected_wikis = ensure_initialized(enrich_selected_wikis)


def append_suggestion_and_stage(file_path: str, ai_suggestion: Optional[str], label: str) -> None:
    """Enrich the file by replacing the relevant section if possible, otherwise append, and stage it with git."""
    if ai_suggestion and ai_suggestion != "NO CHANGES":
        # Try to find a section header in the suggestion (e.g., '## Section Header')
        section_header_match: Optional[re.Match[str]] = re.match(r"^(## .+)$", ai_suggestion.strip(), re.MULTILINE)
        if section_header_match:
            section_header: str = section_header_match.group(1)
            with open(file_path, encoding="utf-8") as f:
                file_content: str = f.read()
            # Replace the section if it exists, otherwise append
            pattern: str = rf"({re.escape(section_header)}\n)(.*?)(?=\n## |\Z)"
            replacement: str = "\\1" + ai_suggestion.strip().split("\n", 1)[1].strip() + "\n"
            new_content: str
            count: int
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


def write_enrichment_outputs(ctx: CtxDict) -> CtxDict:
    """Write AI suggestions to their corresponding files, and update README with wiki summary and link if needed."""
    file_path: str = ctx["file_paths"]["README.md"]
    ai_suggestion: Optional[str] = ctx["ai_suggestions"]["README.md"]
    append_suggestion_and_stage(file_path, ai_suggestion, "README")
    for filename, ai_suggestion in ctx["ai_suggestions"].get("wiki", {}).items():
        file_path = ctx["file_paths"]["wiki"][filename]
        append_suggestion_and_stage(file_path, ai_suggestion, filename)
    return ctx

write_enrichment_outputs = ensure_initialized(write_enrichment_outputs)


def print_selected_wiki_files(ctx: CtxDict) -> CtxDict:
    """Print file info for each selected wiki article."""
    updated_ctx = ctx
    for filename in ctx["selected_wiki_articles"]:
        updated_ctx = print_file_info(filename, "model")(updated_ctx)
    return updated_ctx


print_selected_wiki_files = ensure_initialized(print_selected_wiki_files)


def get_selected_wiki_files(ctx: CtxDict) -> CtxDict:
    """Read each selected wiki file and store its contents in the context."""
    for filename in ctx["selected_wiki_articles"]:
        path = ctx["wiki_file_paths"][filename]
        with open(path) as f:
            ctx[filename] = f.read()
    return ctx


get_selected_wiki_files = ensure_initialized(get_selected_wiki_files)


def enrich() -> None:
    """Pipeline for enriching wiki and readme (multi-wiki support)."""
    # Create a pipeline of operations using the pipe operator
    empty_ctx = {}

    # Define pipeline steps for README handling
    read_readme = get_file("README.md", "readme_path")
    print_readme_info = print_file_info("README.md", "model")

    # Build and execute the pipeline
    p = (
        pipe
        | initialize_context
        | check_api_key
        | get_diff()
        | check_diff_empty
        | print_diff_info
        | fallback_large_diff
        | read_readme
        | print_readme_info
        | select_wiki_articles
        | enrich_readme()
        | get_selected_wiki_files
        | print_selected_wiki_files
        | enrich_selected_wikis
        | write_enrichment_outputs
    )

    # Execute the pipeline with an empty context
    p(empty_ctx)

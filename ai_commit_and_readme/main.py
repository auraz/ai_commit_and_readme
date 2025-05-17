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
from typing import Any, Optional

import openai
import tiktoken
from pipetools import pipe
from rich.logging import RichHandler

from .constants import README_PATH
from .tools import CtxDict, ensure_initialized, get_prompt_template, initialize_context

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True, markup=True)])


@ensure_initialized
def check_api_key(ctx: CtxDict) -> CtxDict:
    """Check for the presence of the OpenAI API key in context or environment."""
    ctx["api_key"] = ctx.get("api_key") or os.getenv("OPENAI_API_KEY")
    if not ctx["api_key"]:
        logging.warning("🔑 OPENAI_API_KEY not set. Skipping README update.")
        sys.exit(0)
    return ctx


@ensure_initialized
def get_diff(ctx: CtxDict, diff_args: Optional[list[str]] = None) -> CtxDict:
    """Retrieve the staged git diff (or file list) and store it in context."""
    ctx["diff"] = subprocess.check_output(diff_args or ["git", "diff", "--cached", "-U1"]).decode()
    return ctx


@ensure_initialized
def check_diff_empty(ctx: CtxDict) -> CtxDict:
    """Exit if the diff is empty, with a message."""
    if not ctx["diff"].strip():
        logging.info("✅ No staged changes detected. Nothing to enrich.")
        sys.exit(0)
    return ctx


@ensure_initialized
def print_diff_info(ctx: CtxDict) -> CtxDict:
    """Print the size of the diff in characters and tokens."""
    logging.info(f"📏 Your staged changes are {len(ctx['diff']):,} characters long!")
    enc = tiktoken.encoding_for_model(ctx["model"])
    diff_tokens: int = len(enc.encode(ctx["diff"]))
    logging.info(f"🔢 That's about {diff_tokens:,} tokens for the AI to read.")
    ctx["diff_tokens"] = diff_tokens
    return ctx


@ensure_initialized
def fallback_large_diff(ctx: CtxDict) -> CtxDict:
    """Fallback to file list if the diff is too large."""
    if len(ctx["diff"]) > 100000:
        logging.warning('⚠️  Diff is too large (>100000 characters). Falling back to "git diff --cached --name-only".')
        result = get_diff(ctx, ["git", "diff", "--cached", "--name-only"])
        logging.info(f"📄 Using file list as diff: {result['diff'].strip()}")
        return result
    return ctx


@ensure_initialized
def get_file(ctx: CtxDict, file_key: str, path_key: str) -> CtxDict:
    """Read the file at path_key and store its contents in ctx[file_key]."""
    with open(path_key) as f:
        ctx[file_key] = f.read()
    return ctx


@ensure_initialized
def print_file_info(ctx: CtxDict, file_key: str, model_key: str) -> CtxDict:
    """Print the size of the file update in characters and tokens."""
    content: str = ctx[file_key]
    logging.info(f"📄 Update to {file_key} is currently {len(content):,} characters.")
    enc = tiktoken.encoding_for_model(ctx[model_key])
    tokens: int = len(enc.encode(content))
    logging.info(f"🔢 That's {tokens:,} tokens in update to {file_key}!")
    ctx[f"{file_key}_tokens"] = tokens
    return ctx


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


@ensure_initialized
def ai_enrich(ctx: CtxDict, filename: str) -> CtxDict:
    """Call the OpenAI API to get enrichment suggestions for any file."""
    prompt: str = get_prompt_template("enrich").format(filename=filename, diff=ctx["diff"], **{filename: ctx[filename]})
    response = get_ai_response(prompt, ctx)
    # Access the content safely
    ai_suggestion = ""
    if hasattr(response, "choices") and response.choices and hasattr(response.choices[0], "message") and hasattr(response.choices[0].message, "content") and response.choices[0].message.content:
        ai_suggestion = response.choices[0].message.content.strip()
    ctx["ai_suggestions"][filename] = ai_suggestion
    return ctx


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


def enrich_readme(ctx: CtxDict) -> CtxDict:
    """Enrich the README file with AI suggestions."""
    return ai_enrich(ctx, "README.md")


def enrich_selected_wikis(ctx: CtxDict) -> CtxDict:
    """Enrich the selected wiki articles."""
    if "wiki" not in ctx["ai_suggestions"] or not isinstance(ctx["ai_suggestions"]["wiki"], dict):
        ctx["ai_suggestions"]["wiki"] = {}
    for filename in ctx["selected_wiki_articles"]:
        suggestion_ctx: CtxDict = ai_enrich(ctx, filename)
        ctx["ai_suggestions"]["wiki"][filename] = suggestion_ctx["ai_suggestions"][filename]
    return ctx


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
            replacement: str = "\\1" + ai_suggestion.strip().split('\n', 1)[1].strip() + "\n"
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


def print_selected_wiki_files(ctx: CtxDict) -> CtxDict:
    """Print file info for each selected wiki article."""
    for filename in ctx["selected_wiki_articles"]:
        print_file_info(ctx, filename, "model")
    return ctx


def get_selected_wiki_files(ctx: CtxDict) -> CtxDict:
    """Read each selected wiki file and store its contents in the context."""
    for filename in ctx["selected_wiki_articles"]:
        get_file(ctx, filename, ctx["wiki_file_paths"][filename])
    return ctx


def enrich() -> None:
    """Pipeline for enriching wiki and readme (multi-wiki support)."""
    # Create a pipeline of operations using the pipe operator
    empty_ctx = {}
    
    # Define a function to handle README file reading
    def read_readme(ctx: CtxDict) -> CtxDict:
        return get_file(ctx, "README.md", ctx["readme_path"])
        
    # Define a function to print README file info
    def print_readme_info(ctx: CtxDict) -> CtxDict:
        return print_file_info(ctx, "README.md", "model")
        
    # Build and execute the pipeline
    empty_ctx | pipe(
        initialize_context,
        check_api_key,
        get_diff,
        check_diff_empty,
        print_diff_info,
        fallback_large_diff,
        # README.md handling
        read_readme,
        print_readme_info,
        # Wiki handling
        select_wiki_articles,
        enrich_readme,
        get_selected_wiki_files,
        print_selected_wiki_files,
        enrich_selected_wikis,
        # Output
        write_enrichment_outputs
    )

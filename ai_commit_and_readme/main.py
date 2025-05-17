#!/usr/bin/env python3
"""AI-powered README and wiki enrichment pipeline."""

import os
import subprocess
import sys
from typing import Optional

from pipetools import pipe

from .logging_setup import LogMessages, get_logger
from .tools import (
    CtxDict,
    append_suggestion_and_stage,
    count_tokens,
    extract_ai_content,
    get_ai_response,
    get_prompt_template,
    initialize_context,
)

logger = get_logger(__name__)


def check_api_key(ctx: CtxDict) -> CtxDict:
    ctx["api_key"] = ctx.get("api_key") or os.getenv("OPENAI_API_KEY")
    if not ctx["api_key"]:
        logger.warning(LogMessages.NO_API_KEY)
        sys.exit(0)
    return ctx


def get_diff(ctx: CtxDict, diff_args: Optional[list[str]] = None) -> CtxDict:
    # Get diff output
    diff_cmd = diff_args or ["git", "diff", "--cached", "-U1"]
    ctx["diff"] = subprocess.check_output(diff_cmd).decode()
    
    # Exit if no changes
    if not ctx["diff"].strip():
        logger.info(LogMessages.NO_CHANGES)
        sys.exit(0)
        
    # Fallback to file list for large diffs
    if len(ctx["diff"]) > 100000:
        logger.warning(LogMessages.LARGE_DIFF)
        return get_diff(ctx, ["git", "diff", "--cached", "--name-only"])
    
    return ctx


def read_file(ctx: CtxDict, file_key: str, file_path: str = None) -> CtxDict:
    # Find path from different possible sources
    path = file_path
    if not path:
        if file_key == "README.md" and "readme_path" in ctx:
            path = ctx["readme_path"]
        elif f"{file_key}_path" in ctx:
            path = ctx[f"{file_key}_path"]
        elif "file_paths" in ctx and file_key in ctx["file_paths"]:
            path = ctx["file_paths"][file_key]
            
    if not path:
        raise ValueError(f"Could not find path for {file_key}")
        
    # Read the file and log stats
    with open(path, encoding="utf-8") as f:
        ctx[file_key] = f.read()
    return log_file_info(ctx, file_key)


def log_and_count_diff_tokens(ctx: CtxDict) -> CtxDict:
    logger.info(LogMessages.DIFF_SIZE.format(len(ctx["diff"])))
    ctx["diff_tokens"] = count_tokens(ctx["diff"], ctx["model"])
    logger.info(LogMessages.DIFF_TOKENS.format(ctx["diff_tokens"]))
    return ctx




def log_file_info(ctx: CtxDict, file_key: str, model_key: str = "model") -> CtxDict:
    content: str = ctx[file_key]
    logger.info(LogMessages.FILE_SIZE.format(file_key, len(content)))
    tokens = count_tokens(content, ctx[model_key])
    logger.info(LogMessages.FILE_TOKENS.format(tokens, file_key))
    ctx[f"{file_key}_tokens"] = tokens
    return ctx


def ai_enrich(ctx: CtxDict, filename: str) -> CtxDict:
    prompt = get_prompt_template("enrich").format(
        filename=filename, 
        diff=ctx["diff"], 
        **{filename: ctx[filename]}
    )
    response = get_ai_response(prompt, ctx)
    ctx["ai_suggestions"][filename] = extract_ai_content(response)
    return ctx


def enrich_readme(ctx: CtxDict) -> CtxDict:
    return ai_enrich(ctx, "README.md")


def select_wiki_articles(ctx: CtxDict) -> CtxDict:
    wiki_files: list[str] = ctx["wiki_files"]
    article_list: str = "\n".join(wiki_files)
    prompt: str = get_prompt_template("select_articles").format(diff=ctx["diff"], article_list=article_list)
    response = get_ai_response(prompt, ctx)

    # Extract and validate filenames
    content = extract_ai_content(response)
    filenames = [fn.strip() for fn in content.split(",") if fn.strip()]
    valid_filenames = [fn for fn in filenames if fn in wiki_files]

    if not valid_filenames:
        logger.info(LogMessages.NO_WIKI_ARTICLES)
        valid_filenames = ["Usage.md"]

    ctx["selected_wiki_articles"] = valid_filenames
    return ctx


def enrich_selected_wikis(ctx: CtxDict) -> CtxDict:
    # Initialize wiki suggestions as a dictionary
    if "wiki" not in ctx["ai_suggestions"] or not isinstance(ctx["ai_suggestions"]["wiki"], dict):
        ctx["ai_suggestions"]["wiki"] = {}

    # Process each selected wiki article
    for filename in ctx["selected_wiki_articles"]:
        ai_enrich(ctx, filename)
        ctx["ai_suggestions"]["wiki"][filename] = ctx["ai_suggestions"][filename]

    return ctx


def write_enrichment_outputs(ctx: CtxDict) -> CtxDict:
    # Handle README file
    append_suggestion_and_stage(
        ctx["file_paths"]["README.md"],
        ctx["ai_suggestions"]["README.md"],
        "README"
    )

    # Handle wiki files
    for filename, ai_suggestion in ctx["ai_suggestions"].get("wiki", {}).items():
        append_suggestion_and_stage(
            ctx["file_paths"]["wiki"][filename],
            ai_suggestion,
            filename
        )

    return ctx


def read_selected_wiki_files(ctx: CtxDict) -> CtxDict:
    for filename in ctx["selected_wiki_articles"]:
        # Store path in context then read file
        ctx[f"{filename}_path"] = ctx["wiki_file_paths"][filename]
        read_file(ctx, filename)
    return ctx


def enrich() -> None:
    # Define function for reading README to avoid lambda in pipeline
    def read_readme(ctx: CtxDict) -> CtxDict:
        return read_file(ctx, "README.md")
        
    # Pipeline definition - each step processes and passes context to the next
    enrichment_pipeline = (
        pipe
        | initialize_context
        | check_api_key
        | get_diff
        | log_and_count_diff_tokens
        | read_readme
        | select_wiki_articles
        | enrich_readme
        | read_selected_wiki_files
        | enrich_selected_wikis
        | write_enrichment_outputs
    )

    enrichment_pipeline({})

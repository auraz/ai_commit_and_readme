#!/usr/bin/env python3
"""AI-powered README and wiki enrichment pipeline."""

import os
import sys

from pipetools import pipe

from .logging_setup import LogMessages, get_logger
from .tools import (
    CtxDict,
    append_suggestion_and_stage,
    count_tokens,
    extract_ai_content,
    get_ai_response,
    get_diff,
    get_diff_text,
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


def generate_summary() -> str:
    """
    Generate a summary of changes based on git diff.

    Returns:
        str: A concise summary of the changes.
    """
    # Initialize context and check for API key
    ctx = initialize_context({})
    ctx = check_api_key(ctx)

    # Get git diff
    try:
        # Try staged changes first
        diff = get_diff_text()
    except SystemExit:
        # If that exits with no changes, try looking at the last commit
        try:
            diff = get_diff_text(["git", "diff", "HEAD~1", "-U1"])
        except SystemExit:
            logger.info("No changes detected in staged files or last commit.")
            sys.exit(0)

    # Get prompt and generate response
    prompt = get_prompt_template("summary").format(diff=diff)
    response = get_ai_response(prompt, ctx)
    return extract_ai_content(response)


def log_diff_stats(ctx: CtxDict) -> CtxDict:
    logger.info(LogMessages.DIFF_SIZE.format(len(ctx["diff"])))
    ctx["diff_tokens"] = count_tokens(ctx["diff"], ctx["model"])
    logger.info(LogMessages.DIFF_TOKENS.format(ctx["diff_tokens"]))
    return ctx


def ai_enrich(ctx: CtxDict, filename: str) -> CtxDict:
    prompt = get_prompt_template("enrich").format(filename=filename, diff=ctx["diff"], **{filename: ctx[filename]})
    response = get_ai_response(prompt, ctx)
    ctx["ai_suggestions"][filename] = extract_ai_content(response)
    return ctx


def read_file(ctx: CtxDict, file_key: str, file_path: str) -> CtxDict:
    # Read the file and log stats
    with open(file_path, encoding="utf-8") as f:
        ctx[file_key] = f.read()

    # Log file info
    content = ctx[file_key]
    logger.info(LogMessages.FILE_SIZE.format(file_key, len(content)))
    tokens = count_tokens(content, ctx["model"])
    logger.info(LogMessages.FILE_TOKENS.format(tokens, file_key))
    ctx[f"{file_key}_tokens"] = tokens
    return ctx


def select_wiki_articles(ctx: CtxDict) -> CtxDict:
    wiki_files = ctx["wiki_files"]
    article_list = "\n".join(wiki_files)
    prompt = get_prompt_template("select_articles").format(diff=ctx["diff"], article_list=article_list)
    response = get_ai_response(prompt, ctx)

    # Extract and validate filenames
    content = extract_ai_content(response)
    filenames = [fn.strip() for fn in content.split(",") if fn.strip()]
    valid_filenames = [fn for fn in filenames if fn in wiki_files]

    if not valid_filenames:
        logger.info(LogMessages.NO_WIKI_ARTICLES)

    ctx["selected_wiki_articles"] = valid_filenames
    return ctx


def read_selected_wiki_files(ctx: CtxDict) -> CtxDict:
    # Skip processing if no wiki articles were selected
    if not ctx["selected_wiki_articles"]:
        return ctx
        
    for filename in ctx["selected_wiki_articles"]:
        read_file(ctx, filename, ctx["wiki_file_paths"][filename])
    return ctx


def enrich_selected_wikis(ctx: CtxDict) -> CtxDict:
    # Initialize wiki suggestions as a dictionary
    if "wiki" not in ctx["ai_suggestions"] or not isinstance(ctx["ai_suggestions"]["wiki"], dict):
        ctx["ai_suggestions"]["wiki"] = {}

    # Skip processing if no wiki articles were selected
    if not ctx["selected_wiki_articles"]:
        return ctx
        
    # Process each selected wiki article
    for filename in ctx["selected_wiki_articles"]:
        ai_enrich(ctx, filename)
        ctx["ai_suggestions"]["wiki"][filename] = ctx["ai_suggestions"][filename]

    return ctx


def write_enrichment_outputs(ctx: CtxDict) -> CtxDict:
    # Handle README file
    append_suggestion_and_stage(ctx["file_paths"]["README.md"], ctx["ai_suggestions"]["README.md"], "README")

    # Handle wiki files
    for filename, ai_suggestion in ctx["ai_suggestions"].get("wiki", {}).items():
        append_suggestion_and_stage(ctx["file_paths"]["wiki"][filename], ai_suggestion, filename)

    return ctx


def enrich() -> None:
    # Define readme functions for the pipeline
    def read_readme(ctx: CtxDict) -> CtxDict:
        return read_file(ctx, "README.md", ctx["readme_path"])

    def enrich_readme(ctx: CtxDict) -> CtxDict:
        return ai_enrich(ctx, "README.md")

    # Pipeline definition - each step processes and passes context to the next
    enrichment_pipeline = (
        pipe
        | initialize_context
        | check_api_key
        | get_diff
        | log_diff_stats
        | read_readme
        | select_wiki_articles
        | enrich_readme
        | read_selected_wiki_files
        | enrich_selected_wikis
        | write_enrichment_outputs
    )

    # Execute the pipeline
    enrichment_pipeline({})

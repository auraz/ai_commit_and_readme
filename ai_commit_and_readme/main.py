#!/usr/bin/env python3
"""AI-powered README and wiki enrichment pipeline."""

import os
import sys
from typing import Dict, Any

from pipetools import pipe

from .logging_setup import LogMessages, get_logger
from .tools import (append_suggestion_and_stage, count_tokens, extract_ai_content, get_ai_response, 
                    get_diff, get_diff_text, get_prompt_template, initialize_context)

logger = get_logger(__name__)


def check_api_key(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure OpenAI API key is available."""
    ctx["api_key"] = ctx.get("api_key") or os.getenv("OPENAI_API_KEY")
    if not ctx["api_key"]:
        logger.warning(LogMessages.NO_API_KEY)
        sys.exit(0)
    return ctx


def generate_summary() -> str:
    """Generate a summary of changes based on git diff."""
    ctx = check_api_key(initialize_context({}))
    
    try:
        diff = get_diff_text()  # Try staged changes first
    except SystemExit:
        try:
            diff = get_diff_text(["git", "diff", "HEAD~1", "-U1"])  # Try last commit
        except SystemExit:
            logger.info("No changes detected in staged files or last commit.")
            sys.exit(0)

    prompt = get_prompt_template("summary").format(diff=diff)
    return extract_ai_content(get_ai_response(prompt, ctx))


def log_diff_stats(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Log statistics about the git diff."""
    logger.info(LogMessages.DIFF_SIZE.format(len(ctx["diff"])))
    ctx["diff_tokens"] = count_tokens(ctx["diff"], ctx["model"])
    logger.info(LogMessages.DIFF_TOKENS.format(ctx["diff_tokens"]))
    return ctx


def read_file(ctx: Dict[str, Any], file_key: str, file_path: str) -> Dict[str, Any]:
    """Read a file and calculate token count."""
    with open(file_path, encoding="utf-8") as f:
        ctx[file_key] = f.read()
    
    content = ctx[file_key]
    logger.info(LogMessages.FILE_SIZE.format(file_key, len(content)))
    tokens = count_tokens(content, ctx["model"])
    logger.info(LogMessages.FILE_TOKENS.format(tokens, file_key))
    ctx[f"{file_key}_tokens"] = tokens
    return ctx


def ai_enrich(ctx: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """Get AI suggestions for a file."""
    prompt = get_prompt_template("enrich").format(filename=filename, diff=ctx["diff"], **{filename: ctx[filename]})
    response = get_ai_response(prompt, ctx)
    ctx["ai_suggestions"][filename] = extract_ai_content(response)
    return ctx


def select_wiki_articles(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Select relevant wiki articles based on the diff."""
    article_list = "\n".join(ctx["wiki_files"])
    prompt = get_prompt_template("select_articles").format(diff=ctx["diff"], article_list=article_list)
    response = get_ai_response(prompt, ctx)
    
    content = extract_ai_content(response)
    filenames = [fn.strip() for fn in content.split(",") if fn.strip()]
    ctx["selected_wiki_articles"] = [fn for fn in filenames if fn in ctx["wiki_files"]]
    
    if not ctx["selected_wiki_articles"]:
        logger.info(LogMessages.NO_WIKI_ARTICLES)
    
    return ctx


def process_selected_wikis(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Read and enrich selected wiki files."""
    if not ctx["selected_wiki_articles"]:
        return ctx
    
    ctx["ai_suggestions"]["wiki"] = {}
    for filename in ctx["selected_wiki_articles"]:
        ctx = read_file(ctx, filename, ctx["wiki_file_paths"][filename])
        ctx = ai_enrich(ctx, filename)
        ctx["ai_suggestions"]["wiki"][filename] = ctx["ai_suggestions"][filename]
    
    return ctx


def write_outputs(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Write AI suggestions to files and stage them."""
    append_suggestion_and_stage(ctx["file_paths"]["README.md"], ctx["ai_suggestions"]["README.md"], "README")
    
    for filename, suggestion in ctx["ai_suggestions"].get("wiki", {}).items():
        append_suggestion_and_stage(ctx["file_paths"]["wiki"][filename], suggestion, filename)
    
    return ctx


def enrich() -> None:
    """Main enrichment pipeline."""
    enrichment_pipeline = (
        pipe
        | initialize_context
        | check_api_key
        | get_diff
        | log_diff_stats
        | (lambda ctx: read_file(ctx, "README.md", ctx["readme_path"]))
        | select_wiki_articles
        | (lambda ctx: ai_enrich(ctx, "README.md"))
        | process_selected_wikis
        | write_outputs
    )
    
    enrichment_pipeline({})
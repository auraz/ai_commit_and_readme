#!/usr/bin/env python3
"""AI-powered README and wiki enrichment pipeline."""

import sys

from pipetools import pipe

from .enrich_agent import generate_commit_summary
from .process import ai_enrich, check_api_key, log_diff_stats, process_selected_wikis, read_file, select_wiki_articles, write_outputs
from .tools import create_context, get_diff, get_diff_text, get_logger

logger = get_logger(__name__)


def generate_summary() -> str:
    """Generate a summary of changes based on git diff."""
    ctx = check_api_key(create_context())

    try:
        diff = get_diff_text()  # Try staged changes first
    except SystemExit:
        try:
            diff = get_diff_text(["git", "diff", "HEAD~1", "-U1"])  # Try last commit
        except SystemExit:
            logger.info("No changes detected in staged files or last commit.")
            sys.exit(0)

    return generate_commit_summary(diff, model=ctx.get("model", "gpt-4o-mini"))


def enrich() -> None:
    """Main enrichment pipeline."""
    enrichment_pipeline = (
        pipe
        | check_api_key
        | get_diff
        | log_diff_stats
        | (lambda ctx: read_file(ctx, "README.md", ctx["readme_path"]))
        | select_wiki_articles
        | (lambda ctx: ai_enrich(ctx, "README.md"))
        | process_selected_wikis
        | write_outputs
    )

    enrichment_pipeline(create_context())

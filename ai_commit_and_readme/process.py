"""Processing functions for AI enrichment pipeline."""

import os
import sys
from typing import Any, Dict

from .enrich_agent import EnrichmentCrew, select_wiki_articles_with_agent
from .tools import LogMessages, append_suggestion_and_stage, count_tokens, get_logger

logger = get_logger(__name__)


def check_api_key(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure OpenAI API key is available."""
    ctx["api_key"] = ctx.get("api_key") or os.getenv("OPENAI_API_KEY")
    if not ctx["api_key"]:
        logger.warning(LogMessages.NO_API_KEY)
        sys.exit(0)
    return ctx


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
    """Get AI suggestions for a file using CrewAI agents."""
    crew = EnrichmentCrew(model=ctx.get("model", "gpt-4o-mini"))
    needs_update, suggestion = crew.enrich_documentation(
        diff=ctx["diff"], doc_content=ctx[filename], doc_type="README" if filename == "README.md" else "wiki", file_path=filename
    )
    ctx["ai_suggestions"][filename] = suggestion if needs_update else "NO CHANGES"
    return ctx


def select_wiki_articles(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Select relevant wiki articles based on the diff using CrewAI agent."""
    ctx["selected_wiki_articles"] = select_wiki_articles_with_agent(diff=ctx["diff"], wiki_files=ctx["wiki_files"], model=ctx.get("model", "gpt-4o-mini"))

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

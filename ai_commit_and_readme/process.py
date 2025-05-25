"""Document enrichment pipeline using CrewAI orchestration."""

import os
import subprocess
import sys
from typing import Any, Dict

from .agents import EnrichmentCrew, generate_commit_summary, select_wiki_articles_with_agent
from .tools import LogMessages, append_suggestion_and_stage, count_tokens, create_context, get_diff_text, get_logger

logger = get_logger(__name__)


class DocumentEnrichmentPipeline:
    """Simplified pipeline that uses CrewAI for the core enrichment logic."""

    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize the enrichment pipeline."""
        self.model = model
        self.enrichment_crew = EnrichmentCrew(model=model)

    def run(self) -> Dict[str, Any]:
        """Run the enrichment pipeline."""
        # Initialize context
        ctx = create_context(model=self.model)

        # Check API key
        if not ctx.get("api_key"):
            logger.warning(LogMessages.NO_API_KEY)
            return {"success": False, "error": "No API key available"}

        # Get git diff
        logger.info(LogMessages.GETTING_DIFF)
        try:
            diff = subprocess.check_output(["git", "diff", "--cached", "-U1"], text=True)
            if not diff:
                logger.info(LogMessages.NO_CHANGES)
                return {"success": False, "error": "No staged changes"}
        except subprocess.CalledProcessError as e:
            logger.error(LogMessages.DIFF_ERROR.format(e))
            return {"success": False, "error": f"Git diff error: {e}"}

        # Log diff stats
        logger.info(LogMessages.DIFF_SIZE.format(len(diff)))
        diff_tokens = count_tokens(diff, self.model)
        logger.info(LogMessages.DIFF_TOKENS.format(diff_tokens))

        # Read README
        try:
            with open(ctx["readme_path"], encoding="utf-8") as f:
                readme_content = f.read()
            logger.info(LogMessages.FILE_SIZE.format("README.md", len(readme_content)))
            readme_tokens = count_tokens(readme_content, self.model)
            logger.info(LogMessages.FILE_TOKENS.format(readme_tokens, "README.md"))
        except Exception as e:
            logger.error(f"Failed to read README: {e}")
            return {"success": False, "error": f"Failed to read README: {e}"}

        # Select wiki articles
        selected_wiki_articles = []
        if ctx["wiki_files"]:
            selected_wiki_articles = select_wiki_articles_with_agent(diff, ctx["wiki_files"], self.model)
            if not selected_wiki_articles:
                logger.info(LogMessages.NO_WIKI_ARTICLES)

        # Enrich README
        ai_suggestions = {}
        needs_update, suggestion = self.enrichment_crew.enrich_documentation(diff=diff, doc_content=readme_content, doc_type="README", file_path="README.md")

        if needs_update and suggestion != "NO CHANGES":
            ai_suggestions["README.md"] = suggestion

        # Process wiki articles
        ai_suggestions["wiki"] = {}
        for filename in selected_wiki_articles:
            filepath = ctx["wiki_file_paths"].get(filename)
            if filepath:
                try:
                    with open(filepath, encoding="utf-8") as f:
                        content = f.read()

                    logger.info(LogMessages.FILE_SIZE.format(filename, len(content)))
                    tokens = count_tokens(content, self.model)
                    logger.info(LogMessages.FILE_TOKENS.format(tokens, filename))

                    needs_update, suggestion = self.enrichment_crew.enrich_documentation(diff=diff, doc_content=content, doc_type="wiki", file_path=filename)

                    if needs_update and suggestion != "NO CHANGES":
                        ai_suggestions["wiki"][filename] = suggestion

                except Exception as e:
                    logger.error(f"Error processing {filename}: {e}")

        # Write outputs
        if "README.md" in ai_suggestions:
            append_suggestion_and_stage(ctx["readme_path"], ai_suggestions["README.md"], "README")

        for filename, suggestion in ai_suggestions.get("wiki", {}).items():
            filepath = ctx["wiki_file_paths"].get(filename)
            if filepath:
                append_suggestion_and_stage(filepath, suggestion, filename)

        return {"success": True, "suggestions": ai_suggestions, "selected_wiki_articles": selected_wiki_articles}


def enrich() -> None:
    """Main enrichment pipeline entry point."""
    pipeline = DocumentEnrichmentPipeline()
    result = pipeline.run()

    if not result.get("success"):
        error = result.get("error", "Unknown error")
        logger.error(f"Enrichment failed: {error}")
        sys.exit(1)


def generate_summary() -> str:
    """Generate a summary of changes based on git diff."""
    ctx = create_context()
    api_key = ctx.get("api_key") or os.getenv("OPENAI_API_KEY")

    if not api_key:
        logger.warning(LogMessages.NO_API_KEY)
        sys.exit(0)

    try:
        diff = get_diff_text()  # Try staged changes first
    except SystemExit:
        try:
            diff = get_diff_text(["git", "diff", "HEAD~1", "-U1"])  # Try last commit
        except SystemExit:
            logger.info("No changes detected in staged files or last commit.")
            sys.exit(0)

    return generate_commit_summary(diff, model=ctx.get("model", "gpt-4o-mini"))

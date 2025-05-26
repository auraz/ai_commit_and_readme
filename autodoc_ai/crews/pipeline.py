"""Main pipeline crew for orchestrating document enrichment."""

import contextlib
import subprocess
from typing import Any, Dict, Optional

from ..settings import Settings
from ..tools import LogMessages, append_suggestion_and_stage, count_tokens, create_context, get_logger, load_file
from .base import BaseCrew
from .commit_summary import CommitSummaryCrew
from .enrichment import EnrichmentCrew
from .wiki_selector import WikiSelectorCrew

logger = get_logger(__name__)


class PipelineCrew(BaseCrew):
    """Orchestrates the document enrichment pipeline."""

    def __init__(self):
        """Initialize pipeline with sub-crews."""
        super().__init__()
        self.enrichment_crew = EnrichmentCrew()
        self.wiki_selector_crew = WikiSelectorCrew()
        self.commit_summary_crew = CommitSummaryCrew()
        self.model = Settings.get_model()

    def _get_git_diff(self) -> str:
        """Get git diff from staged changes."""
        logger.info(LogMessages.GETTING_DIFF)
        try:
            diff = subprocess.check_output(["git", "diff", "--cached", "-U1"], text=True)
            if not diff:
                logger.info(LogMessages.NO_CHANGES)
                raise ValueError("No staged changes")
            return diff
        except subprocess.CalledProcessError as e:
            logger.error(LogMessages.DIFF_ERROR.format(e))
            raise ValueError(f"Git diff error: {e}") from e

    def _process_documents(self, diff: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Process README and wiki documents."""
        ai_suggestions = {"README.md": None, "wiki": {}}

        # Process README
        readme_content = load_file(ctx["readme_path"])
        if readme_content:
            logger.info(LogMessages.FILE_SIZE.format("README.md", len(readme_content)))
            logger.info(LogMessages.FILE_TOKENS.format(count_tokens(readme_content, self.model), "README.md"))

            needs_update, suggestion = self.enrichment_crew.run(diff=diff, doc_content=readme_content, doc_type="README", file_path="README.md")

            if needs_update and suggestion != "NO CHANGES":
                ai_suggestions["README.md"] = suggestion

        # Select and process wiki articles
        selected_articles = []
        if ctx["wiki_files"]:
            selected_articles = self.wiki_selector_crew.run(diff, ctx["wiki_files"])
            if not selected_articles:
                logger.info(LogMessages.NO_WIKI_ARTICLES)

            for filename in selected_articles:
                filepath = ctx["wiki_file_paths"].get(filename)
                if filepath:
                    content = load_file(filepath)
                    if content:
                        logger.info(LogMessages.FILE_SIZE.format(filename, len(content)))
                        logger.info(LogMessages.FILE_TOKENS.format(count_tokens(content, self.model), filename))

                        needs_update, suggestion = self.enrichment_crew.run(diff=diff, doc_content=content, doc_type="wiki", file_path=filename)

                        if needs_update and suggestion != "NO CHANGES":
                            ai_suggestions["wiki"][filename] = suggestion

        return {"suggestions": ai_suggestions, "selected_articles": selected_articles}

    def _write_outputs(self, ai_suggestions: Dict[str, Any], ctx: Dict[str, Any]) -> None:
        """Write suggestions to files and stage them."""
        if ai_suggestions.get("README.md"):
            append_suggestion_and_stage(ctx["readme_path"], ai_suggestions["README.md"], "README")

        for filename, suggestion in ai_suggestions.get("wiki", {}).items():
            filepath = ctx["wiki_file_paths"].get(filename)
            if filepath:
                append_suggestion_and_stage(filepath, suggestion, filename)

    def _execute(self) -> Dict[str, Any]:
        """Execute the enrichment pipeline."""
        # Create context
        ctx = create_context(model=self.model)

        # Check API key
        if not ctx.get("api_key"):
            logger.warning(LogMessages.NO_API_KEY)
            return {"success": False, "error": "No API key available"}

        # Get git diff
        try:
            diff = self._get_git_diff()
        except ValueError as e:
            return {"success": False, "error": str(e)}

        # Log diff stats
        logger.info(LogMessages.DIFF_SIZE.format(len(diff)))
        logger.info(LogMessages.DIFF_TOKENS.format(count_tokens(diff, self.model)))

        # Process documents
        result = self._process_documents(diff, ctx)

        # Write outputs
        self._write_outputs(result["suggestions"], ctx)

        return {
            "success": True,
            "suggestions": result["suggestions"],
            "selected_wiki_articles": result["selected_articles"],
        }

    def _handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle pipeline errors."""
        return {"success": False, "error": str(error)}

    def generate_summary(self, diff: Optional[str] = None) -> str:
        """Generate commit summary from diff."""
        if not diff:
            # Try staged changes first
            with contextlib.suppress(subprocess.CalledProcessError):
                diff = subprocess.check_output(["git", "diff", "--cached", "-U1"], text=True)

            if not diff:
                # Try last commit
                try:
                    diff = subprocess.check_output(["git", "diff", "HEAD~1", "-U1"], text=True)
                except subprocess.CalledProcessError:
                    logger.info("No changes detected in staged files or last commit.")
                    return "No changes to summarize"

        return self.commit_summary_crew.run(diff)

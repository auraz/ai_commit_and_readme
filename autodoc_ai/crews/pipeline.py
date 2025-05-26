"""Main pipeline crew for orchestrating document enrichment."""

import contextlib
import glob
import os
import subprocess
from typing import Any, Dict, List, Optional, Tuple

import tiktoken

from .. import logger
from .base import BaseCrew
from .commit_summary import CommitSummaryCrew
from .enrichment import EnrichmentCrew
from .wiki_selector import WikiSelectorCrew


class PipelineCrew(BaseCrew):
    """Orchestrates the document enrichment pipeline."""

    def __init__(self):
        """Initialize pipeline with sub-crews."""
        super().__init__()
        self.enrichment_crew = EnrichmentCrew()
        self.wiki_selector_crew = WikiSelectorCrew()
        self.commit_summary_crew = CommitSummaryCrew()
        self.model = os.getenv("AUTODOC_MODEL", "gpt-4o-mini")

    def _get_wiki_files(self, wiki_path: str) -> Tuple[List[str], Dict[str, str]]:
        """Get list of wiki files and their paths."""
        files = glob.glob(f"{wiki_path}/*.md")
        filenames = [os.path.basename(f) for f in files]
        file_paths = {os.path.basename(f): f for f in files}
        return filenames, file_paths

    def _create_context(self) -> Dict[str, Any]:
        """Create pipeline context with all required fields."""
        api_key = os.getenv("OPENAI_API_KEY")
        readme_path = os.path.join(os.getcwd(), "README.md")
        wiki_path = os.getenv("WIKI_PATH", "wiki")

        wiki_files, wiki_file_paths = self._get_wiki_files(wiki_path)
        return {
            "readme_path": readme_path,
            "wiki_path": wiki_path,
            "api_key": api_key,
            "model": self.model,
            "wiki_files": wiki_files,
            "wiki_file_paths": wiki_file_paths,
        }

    def _write_suggestion_and_stage(self, file_path: str, ai_suggestion: Optional[str], label: str) -> None:
        """Write AI suggestion to file and stage it."""
        if not ai_suggestion or ai_suggestion == "NO CHANGES":
            logger.info(f"👍 No enrichment needed for {file_path}.")
            return

        # Write complete document
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(ai_suggestion.strip() + "\n")

        # Stage the file
        logger.info(f"🎉✨ SUCCESS: {file_path} enriched and staged with AI suggestions for {label}! ✨🎉")
        subprocess.run(["git", "add", file_path])

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text for specific model."""
        # Try to get encoding for specific model
        try:
            enc = tiktoken.encoding_for_model(self.model)
        except KeyError:
            enc = tiktoken.get_encoding("cl100k_base")

        return len(enc.encode(text))

    def _get_git_diff(self) -> str:
        """Get git diff from staged changes."""
        logger.info("📊 Getting staged changes...")
        try:
            diff = subprocess.check_output(["git", "diff", "--cached", "-U1"], text=True)
            if not diff:
                logger.info("✅ No staged changes detected. Nothing to enrich.")
                raise ValueError("No staged changes")
            logger.debug(f"Git diff length: {len(diff)} characters")
            if os.getenv("AUTODOC_LOG_LEVEL", "INFO").upper() == "DEBUG":
                logger.debug(f"Git diff preview (first 1000 chars):")
                logger.debug("="*80)
                logger.debug(diff[:1000])
                logger.debug("="*80)
            return diff
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error getting diff: {e}")
            raise ValueError(f"Git diff error: {e}") from e

    def _get_commits_diff(self, days: int) -> str:
        """Get combined diff from commits in the last n days."""
        logger.info(f"📅 Getting commits from the last {days} days...")
        try:
            # Get commit hashes from the last n days
            since_date = f"{days}.days.ago"
            commit_hashes = subprocess.check_output(["git", "log", f"--since={since_date}", "--format=%H"], text=True).strip().split("\n")

            if not commit_hashes or commit_hashes == [""]:
                logger.info(f"✅ No commits found in the last {days} days.")
                raise ValueError(f"No commits in the last {days} days")

            logger.info(f"📊 Found {len(commit_hashes)} commits in the last {days} days")
            logger.debug(f"Commit hashes: {commit_hashes[:5]}...")  # Show first 5

            # Get the oldest commit's parent to create a combined diff
            oldest_commit = commit_hashes[-1]
            try:
                base_commit = subprocess.check_output(["git", "rev-parse", f"{oldest_commit}^"], text=True).strip()
                logger.debug(f"Base commit: {base_commit}")
            except subprocess.CalledProcessError:
                # If oldest commit has no parent (initial commit), use empty tree
                base_commit = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
                logger.debug("Using empty tree as base (initial commit)")

            # Get combined diff from base to HEAD
            diff = subprocess.check_output(["git", "diff", base_commit, "HEAD", "-U1"], text=True)

            # Log commit summary
            commit_summary = subprocess.check_output(["git", "log", f"--since={since_date}", "--oneline"], text=True)
            logger.info(f"📝 Commits included:\n{commit_summary}")

            return diff

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error getting commits diff: {e}")
            raise ValueError(f"Git commits error: {e}") from e

    def _process_documents(self, diff: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Process README and wiki documents."""
        ai_suggestions = {"README.md": None, "wiki": {}}

        # Process README
        logger.info("📄 Processing README...")
        readme_content = self.load_file(ctx["readme_path"])
        if readme_content:
            logger.info(f"📄 Update to README.md is currently {len(readme_content):,} characters.")
            logger.info(f"🔢 That's {self._count_tokens(readme_content):,} tokens in update to README.md!")

            needs_update, suggestion = self.enrichment_crew.run(diff=diff, doc_content=readme_content, doc_type="README", file_path="README.md")

            if needs_update and suggestion != "NO CHANGES":
                ai_suggestions["README.md"] = suggestion

        # Select and process wiki articles
        selected_articles = []
        if ctx["wiki_files"]:
            logger.info("🔍 Selecting wiki articles...")
            selected_articles = self.wiki_selector_crew.run(diff, ctx["wiki_files"])
            if not selected_articles:
                logger.info("[i] No valid wiki articles selected.")

            # Build wiki context map to prevent duplication
            wiki_summaries = {}
            for filename in selected_articles:
                filepath = ctx["wiki_file_paths"].get(filename)
                if filepath:
                    content = self.load_file(filepath)
                    if content:
                        # Extract title and first paragraph as summary
                        lines = content.strip().split("\n")
                        title = lines[0].strip("# ") if lines else filename
                        first_para = next((p for p in content.split("\n\n")[1:3] if p.strip()), "")[:200]
                        wiki_summaries[filename] = f"{title}: {first_para}..."

            logger.info(f"📚 Processing {len(selected_articles)} wiki articles...")
            logger.debug(f"Selected articles: {selected_articles}")
            logger.debug(f"Wiki file paths: {ctx['wiki_file_paths']}")
            
            for idx, filename in enumerate(selected_articles, 1):
                logger.info(f"  [{idx}/{len(selected_articles)}] {filename}")
                filepath = ctx["wiki_file_paths"].get(filename)
                logger.debug(f"Looking for {filename} -> {filepath}")
                if filepath:
                    content = self.load_file(filepath)
                    if content:
                        logger.info(f"📄 Update to {filename} is currently {len(content):,} characters.")
                        logger.info(f"🔢 That's {self._count_tokens(content):,} tokens in update to {filename}!")

                        # Get summaries of other wiki files
                        other_wikis = {k: v for k, v in wiki_summaries.items() if k != filename}

                        needs_update, suggestion = self.enrichment_crew.run(diff=diff, doc_content=content, doc_type="wiki", file_path=filename, other_docs=other_wikis)

                        if needs_update and suggestion != "NO CHANGES":
                            ai_suggestions["wiki"][filename] = suggestion

        return {"suggestions": ai_suggestions, "selected_articles": selected_articles}

    def _write_outputs(self, ai_suggestions: Dict[str, Any], ctx: Dict[str, Any]) -> None:
        """Write suggestions to files and stage them."""
        if ai_suggestions.get("README.md"):
            self._write_suggestion_and_stage(ctx["readme_path"], ai_suggestions["README.md"], "README")

        for filename, suggestion in ai_suggestions.get("wiki", {}).items():
            filepath = ctx["wiki_file_paths"].get(filename)
            if filepath:
                self._write_suggestion_and_stage(filepath, suggestion, filename)

    def _execute(self, days: Optional[int] = None) -> Dict[str, Any]:
        """Execute the enrichment pipeline."""
        # Create context
        logger.info("🚀 Starting pipeline...")
        ctx = self._create_context()

        # Check API key
        if not ctx.get("api_key"):
            logger.warning("🔑 No API key found. Set OPENAI_API_KEY.")
            return {"success": False, "error": "No API key available"}

        # Get git diff based on mode
        try:
            diff = self._get_commits_diff(days) if days is not None else self._get_git_diff()
        except ValueError as e:
            return {"success": False, "error": str(e)}

        # Log diff stats
        logger.info(f"📏 Your changes are {len(diff):,} characters long!")
        logger.info(f"🔢 That's about {self._count_tokens(diff):,} tokens for the AI to read.")

        # Process documents
        logger.info("📝 Processing documents...")
        result = self._process_documents(diff, ctx)

        # Write outputs
        self._write_outputs(result["suggestions"], ctx)

        logger.info("✅ Pipeline complete!")
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

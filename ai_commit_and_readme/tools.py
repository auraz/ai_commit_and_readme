"""AI enrichment utilities and context management."""

import glob
import logging
import os
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple, TypedDict

import tiktoken
from openai import OpenAI
from rich.logging import RichHandler


class PipelineContext(TypedDict, total=False):
    """Type definition for pipeline context with all possible fields."""

    readme_path: str
    wiki_path: str
    api_key: Optional[str]
    wiki_url: str
    wiki_url_base: str
    model: str
    file_paths: Dict[str, Any]
    ai_suggestions: Dict[str, Any]
    wiki_files: List[str]
    wiki_file_paths: Dict[str, str]
    diff: str
    diff_tokens: int
    selected_wiki_articles: List[str]


# Configure logging on import
logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(markup=True)])


def get_logger(name: str) -> logging.Logger:
    """Get logger instance for module."""
    return logging.getLogger(name)


class LogMessages:
    """Centralized log message templates."""

    DIFF_SIZE = "📏 Your staged changes are {:,} characters long!"
    DIFF_TOKENS = "🔢 That's about {:,} tokens for the AI to read."
    FILE_SIZE = "📄 Update to {} is currently {:,} characters."
    FILE_TOKENS = "🔢 That's {:,} tokens in update to {}!"
    NO_CHANGES = "✅ No staged changes detected. Nothing to enrich."
    LARGE_DIFF = '⚠️  Diff is too large (>100000 characters). Falling back to "git diff --cached --name-only".'
    API_ERROR = "❌ Error from OpenAI API: {}"
    NO_API_KEY = "🔑 OPENAI_API_KEY not set. Skipping README update."
    SUCCESS = "🎉✨ SUCCESS: {} enriched and staged with AI suggestions for {}! ✨🎉"
    NO_ENRICHMENT = "👍 No enrichment needed for {}."
    NO_WIKI_ARTICLES = "[i] No valid wiki articles selected."
    GETTING_DIFF = "📊 Getting staged changes..."
    DIFF_ERROR = "❌ Error getting diff: {}"


logger = get_logger(__name__)


def create_context(
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    readme_path: Optional[str] = None,
    wiki_path: Optional[str] = None,
    wiki_url: str = "https://github.com/auraz/ai_commit_and_readme/wiki/",
    wiki_url_base: Optional[str] = None,
) -> PipelineContext:
    """Create fresh pipeline context with all required fields."""
    # Use environment variables as fallbacks
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    readme_path = readme_path or os.path.join(os.getcwd(), "README.md")
    wiki_path = wiki_path or os.getenv("WIKI_PATH", "wiki")
    wiki_url_base = wiki_url_base or os.getenv("WIKI_URL_BASE")

    wiki_files, wiki_file_paths = get_wiki_files(wiki_path)
    return {
        "readme_path": readme_path,
        "wiki_path": wiki_path,
        "api_key": api_key,
        "wiki_url": wiki_url,
        "wiki_url_base": wiki_url_base,
        "model": model,
        "file_paths": {"README.md": readme_path, "wiki": wiki_file_paths},
        "ai_suggestions": {"README.md": None, "wiki": {}},
        "wiki_files": wiki_files,
        "wiki_file_paths": wiki_file_paths,
        "diff": "",
        "diff_tokens": 0,
        "selected_wiki_articles": [],
    }


def get_wiki_files(wiki_path: str) -> Tuple[list[str], Dict[str, str]]:
    """Get list of wiki files and their paths."""
    files = glob.glob(f"{wiki_path}/*.md")
    filenames = [os.path.basename(f) for f in files]
    file_paths = {os.path.basename(f): f for f in files}
    return filenames, file_paths


def get_diff(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Get git diff and add to context."""
    diff_text = get_diff_text()
    ctx["diff"] = diff_text
    return ctx


def get_diff_text(cmd: Optional[list[str]] = None) -> str:
    """Get git diff text from staged changes."""
    logger.info(LogMessages.GETTING_DIFF)
    cmd = cmd or ["git", "diff", "--cached", "-U1"]

    try:
        diff = subprocess.check_output(cmd, text=True)
    except subprocess.CalledProcessError as e:
        logger.error(LogMessages.DIFF_ERROR.format(e))
        sys.exit(1)

    if not diff:
        logger.info(LogMessages.NO_CHANGES)
        sys.exit(0)

    return diff


def load_file(file_path: str) -> Optional[str]:
    """Load file content."""
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None


def get_ai_response(prompt: str, ctx: Optional[Dict[str, Any]] = None, json_response: bool = False, temperature: float = 0.5) -> Any:
    """Get response from OpenAI API."""
    api_key = ctx.get("api_key") if ctx else os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error(LogMessages.NO_API_KEY)
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    try:
        model_name = ctx.get("model", "gpt-4o-mini") if ctx else "gpt-4o-mini"
        kwargs = {"model": model_name, "messages": [{"role": "user", "content": prompt}], "temperature": temperature}
        if json_response:
            kwargs["response_format"] = {"type": "json_object"}
        response = client.chat.completions.create(**kwargs)
    except Exception as e:
        logger.error(LogMessages.API_ERROR.format(e))
        sys.exit(1)

    return response


def extract_ai_content(response: Any) -> str:
    """Extract content from OpenAI API response."""
    if (
        hasattr(response, "choices")
        and response.choices
        and hasattr(response.choices[0], "message")
        and hasattr(response.choices[0].message, "content")
        and response.choices[0].message.content
    ):
        return response.choices[0].message.content.strip()
    return ""


def append_suggestion_and_stage(file_path: str, ai_suggestion: Optional[str], label: str) -> None:
    """Append AI suggestion to file and stage it."""
    if not ai_suggestion or ai_suggestion == "NO CHANGES":
        logger.info(LogMessages.NO_ENRICHMENT.format(file_path))
        return

    section_header_match = re.match(r"^(## .+)$", ai_suggestion.strip(), re.MULTILINE)
    if section_header_match:
        _update_with_section_header(file_path, ai_suggestion, section_header_match.group(1))
    else:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(ai_suggestion)

    logger.info(LogMessages.SUCCESS.format(file_path, label))
    subprocess.run(["git", "add", file_path])


def _update_with_section_header(file_path: str, ai_suggestion: str, section_header: str) -> None:
    """Update file content with section replacement."""
    with open(file_path, encoding="utf-8") as f:
        file_content = f.read()

    suggestion_content = ai_suggestion.strip().split("\n", 1)[1].strip()
    pattern = rf"({re.escape(section_header)}\n)(.*?)(?=\n## |\Z)"
    replacement = f"\\1{suggestion_content}\n"
    new_content, count = re.subn(pattern, replacement, file_content, flags=re.DOTALL)

    if count == 0:
        new_content = file_content + f"\n\n{ai_suggestion.strip()}\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def count_tokens(text: str, model_name: str) -> int:
    """Count tokens in text for specific model."""
    enc = tiktoken.encoding_for_model(model_name)
    return len(enc.encode(text))

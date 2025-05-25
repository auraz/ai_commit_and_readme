"""AI enrichment utilities and context management."""

import glob
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import tiktoken
from openai import OpenAI

from .constants import API_KEY, MODEL, README_PATH, WIKI_PATH, WIKI_URL, WIKI_URL_BASE
from .logging_setup import LogMessages, get_logger

PROMPTS_DIR = Path(__file__).parent / "prompts"
logger = get_logger(__name__)


def initialize_context(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize pipeline context with default values."""
    if "context_initialized" not in ctx:
        wiki_files, wiki_file_paths = get_wiki_files()
        ctx.update(
            {
                "readme_path": README_PATH,
                "wiki_path": WIKI_PATH,
                "api_key": API_KEY,
                "wiki_url": WIKI_URL,
                "wiki_url_base": WIKI_URL_BASE,
                "model": MODEL,
                "file_paths": {"README.md": README_PATH, "wiki": wiki_file_paths},
                "ai_suggestions": {"README.md": None, "wiki": None},
                "wiki_files": wiki_files,
                "wiki_file_paths": wiki_file_paths,
                "context_initialized": True,
            }
        )
    return ctx


def get_wiki_files() -> Tuple[list[str], Dict[str, str]]:
    """Get list of wiki files and their paths."""
    files = glob.glob(f"{WIKI_PATH}/*.md")
    filenames = [os.path.basename(f) for f in files]
    file_paths = {os.path.basename(f): f for f in files}
    return filenames, file_paths


def get_prompt_template(section: str) -> str:
    """Get prompt template section from prompt files."""
    if not PROMPTS_DIR.exists():
        raise RuntimeError(f"Prompts directory not found: {PROMPTS_DIR}")

    prompt_files = list(PROMPTS_DIR.glob("*.md"))
    if not prompt_files:
        raise RuntimeError(f"No prompt files found in {PROMPTS_DIR}")

    section_header = f"## {section}"
    for prompt_file in prompt_files:
        try:
            with open(prompt_file, encoding="utf-8") as f:
                lines = f.readlines()

            in_section = False
            section_lines: list[str] = []

            for line in lines:
                if line.strip() == section_header:
                    in_section = True
                elif in_section and line.startswith("##"):
                    break
                elif in_section:
                    section_lines.append(line)

            if section_lines:
                return "".join(section_lines).strip()
        except Exception as e:
            logger.debug(f"Error reading {prompt_file}: {e}")

    raise ValueError(f"Section '{section}' not found in any prompt file")


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
    api_key = ctx.get("api_key", API_KEY) if ctx else API_KEY
    client = OpenAI(api_key=api_key)

    try:
        model_name = ctx.get("model", MODEL) if ctx else MODEL
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

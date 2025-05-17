"""AI enrichment utilities and context management."""

import glob
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Optional, Protocol

import openai
import tiktoken

from .constants import API_KEY, MODEL, README_PATH, WIKI_PATH, WIKI_URL, WIKI_URL_BASE
from .logging_setup import LogMessages, get_logger

PROMPT_PATH = Path(__file__).parent / "prompt.md"

# Get logger
logger = get_logger(__name__)

CtxDict = dict[str, Any]  # Pipeline context dictionary type


class PipeFunction(Protocol):
    def __call__(self, ctx: CtxDict) -> CtxDict: ...


def initialize_context(ctx: CtxDict) -> CtxDict:
    if "context_initialized" not in ctx:
        defaults = [
            ("readme_path", README_PATH),
            ("wiki_path", WIKI_PATH),
            ("api_key", API_KEY),
            ("wiki_url", WIKI_URL),
            ("wiki_url_base", WIKI_URL_BASE),
            ("model", MODEL),
        ]
        for key, value in defaults:
            ctx[key] = value
        wiki_files, wiki_file_paths = get_wiki_files()
        ctx["file_paths"] = {"README.md": README_PATH, "wiki": wiki_file_paths}
        ctx["ai_suggestions"] = {"README.md": None, "wiki": None}
        ctx["wiki_files"] = wiki_files
        ctx["wiki_file_paths"] = wiki_file_paths
        ctx["context_initialized"] = True
    return ctx


def ensure_initialized(func: Callable) -> PipeFunction:
    def wrapper(ctx: CtxDict) -> CtxDict:
        ctx = initialize_context(ctx)
        return func(ctx)

    return wrapper


def get_wiki_files() -> tuple[list[str], dict[str, str]]:
    files = glob.glob(f"{WIKI_PATH}/*.md")
    filenames = [os.path.basename(f) for f in files]
    file_paths = {os.path.basename(f): f for f in files}
    return filenames, file_paths


def get_prompt_template(section: str) -> str:
    try:
        with open(PROMPT_PATH, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError as err:
        raise RuntimeError(f"Prompt template file not found: {PROMPT_PATH}") from err
    section_header = f"## {section}"
    in_section = False
    section_lines: list[str] = []
    for line in lines:
        if line.strip().startswith("## "):
            if in_section:
                break
            in_section = line.strip() == section_header
            continue
        if in_section:
            section_lines.append(line)
    if section_lines:
        return "".join(section_lines).strip()
    raise ValueError(f'Prompt section "{section}" not found in prompt.md')


# AI Response Utilities
def get_ai_response(prompt: str, ctx: Optional[CtxDict] = None) -> Any:
    api_key: Optional[str] = ctx["api_key"] if ctx and "api_key" in ctx else None
    client = openai.OpenAI(api_key=api_key)
    try:
        model_name = ctx["model"] if ctx and "model" in ctx else "gpt-4"
        response = client.chat.completions.create(model=model_name, messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        logger.error(LogMessages.API_ERROR.format(e))
        sys.exit(1)
    return response


def extract_ai_content(response: Any) -> str:
    if hasattr(response, "choices") and response.choices and hasattr(response.choices[0], "message") and hasattr(response.choices[0].message, "content") and response.choices[0].message.content:
        return response.choices[0].message.content.strip()
    return ""


# File Manipulation Utilities
def _update_with_section_header(file_path: str, ai_suggestion: str, section_header: str) -> None:
    # Read the current file content
    with open(file_path, encoding="utf-8") as f:
        file_content: str = f.read()

    # Extract content after the header in the suggestion
    suggestion_content = ai_suggestion.strip().split("\n", 1)[1].strip()

    # Create pattern to match the section and its content
    pattern: str = rf"({re.escape(section_header)}\n)(.*?)(?=\n## |\Z)"
    replacement: str = f"\\1{suggestion_content}\n"

    # Try to replace the section
    new_content, count = re.subn(pattern, replacement, file_content, flags=re.DOTALL)

    # If section not found, append at the end
    if count == 0:
        new_content = file_content + f"\n\n{ai_suggestion.strip()}\n"

    # Write the updated content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def append_suggestion_and_stage(file_path: str, ai_suggestion: Optional[str], label: str) -> None:
    # Skip if there's no suggestion or it explicitly says no changes
    if not ai_suggestion or ai_suggestion == "NO CHANGES":
        logger.info(LogMessages.NO_ENRICHMENT.format(file_path))
        return

    # Try to find a section header in the suggestion (e.g., '## Section Header')
    section_header_match: Optional[re.Match[str]] = re.match(r"^(## .+)$", ai_suggestion.strip(), re.MULTILINE)

    if section_header_match:
        # Update with section replacement logic
        _update_with_section_header(file_path, ai_suggestion, section_header_match.group(1))
    else:
        # No section header, just append
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(ai_suggestion)

    # Log success and stage the file
    logger.info(LogMessages.SUCCESS.format(file_path, label))
    subprocess.run(["git", "add", file_path])


# Token and Size Utilities
def count_tokens(text: str, model_name: str) -> int:
    enc = tiktoken.encoding_for_model(model_name)
    return len(enc.encode(text))

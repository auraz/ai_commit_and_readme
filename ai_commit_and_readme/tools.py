"""AI enrichment utilities and context management."""

import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Protocol, Tuple, Union

import openai
import tiktoken
from openai import OpenAI

from .constants import API_KEY, MODEL, README_PATH, WIKI_PATH, WIKI_URL, WIKI_URL_BASE
from .logging_setup import LogMessages, get_logger, setup_logging

PROMPTS_DIR = Path(__file__).parent / "prompts"
EVALS_DIR = PROMPTS_DIR / "evals"
BASE_TEMPLATE_PATH = EVALS_DIR / "base_eval_template.md"

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
    """
    Get prompt template section from any prompt file in the prompts directory.

    Args:
        section: The prompt section to retrieve.

    Returns:
        The content of the section.

    Raises:
        ValueError: If section not found in any prompt file.
        RuntimeError: If prompts directory not found.
    """
    if not PROMPTS_DIR.exists():
        raise RuntimeError(f"Prompts directory not found: {PROMPTS_DIR}")

    # Look for the section in all markdown files in the prompts directory
    prompt_files = list(PROMPTS_DIR.glob("*.md"))
    if not prompt_files:
        raise RuntimeError(f"No prompt files found in {PROMPTS_DIR}")

    section_header = f"## {section}"

    # Try each prompt file
    for prompt_file in prompt_files:
        try:
            with open(prompt_file, encoding="utf-8") as f:
                lines = f.readlines()

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
        except Exception as e:
            logger.warning(f"Error reading prompt file {prompt_file}: {e}")

    # If we've checked all files and found nothing, raise an error
    raise ValueError(f'Prompt section "{section}" not found in any prompt file')


# File Operations
def load_file(file_path: str) -> Optional[str]:
    """Load a file's content from path.
    
    Args:
        file_path: Path to the file to load
        
    Returns:
        The file content as a string, or None if the file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return None
    
    with open(path, encoding="utf-8") as f:
        return f.read()


# Git Operations
def get_diff_text(diff_args: Optional[list[str]] = None) -> str:
    """
    Get git diff output as a string.

    Args:
        diff_args: Optional custom git diff command arguments.

    Returns:
        The git diff output as a string.

    Raises:
        SystemExit: If no changes are found or on subprocess error.
    """
    diff_cmd = diff_args or ["git", "diff", "--cached", "-U1"]
    try:
        diff = subprocess.check_output(diff_cmd).decode()

        # Check if there are any changes
        if not diff.strip():
            logger.info(LogMessages.NO_CHANGES)
            sys.exit(0)

        # Fallback to file list for large diffs
        if len(diff) > 100000:
            logger.warning(LogMessages.LARGE_DIFF)
            return get_diff_text(["git", "diff", "--cached", "--name-only"])

        return diff
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing git diff: {e}")
        sys.exit(1)


def get_diff(ctx: CtxDict, diff_args: Optional[list[str]] = None) -> CtxDict:
    """
    Get git diff output and store it in context.

    Args:
        ctx: The context dictionary.
        diff_args: Optional custom git diff command arguments.

    Returns:
        The updated context dictionary with diff output.
    """
    # Get diff output using the helper function
    ctx["diff"] = get_diff_text(diff_args)
    return ctx


# AI Response Utilities
def get_ai_response(prompt: str, ctx: Optional[CtxDict] = None, 
                   json_response: bool = False, 
                   temperature: float = 1.0) -> Any:
    """Get response from OpenAI API.
    
    Args:
        prompt: The prompt to send to OpenAI
        ctx: Optional context dictionary with API key and model
        json_response: Whether to request JSON response format
        temperature: Temperature parameter for generation
        
    Returns:
        The OpenAI API response
        
    Raises:
        SystemExit: On API error
    """
    api_key: Optional[str] = ctx["api_key"] if ctx and "api_key" in ctx else API_KEY
    client = OpenAI(api_key=api_key)
    
    try:
        model_name = ctx["model"] if ctx and "model" in ctx else MODEL
        kwargs = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        
        if json_response:
            kwargs["response_format"] = {"type": "json_object"}
            
        response = client.chat.completions.create(**kwargs)
    except Exception as e:
        logger.error(LogMessages.API_ERROR.format(e))
        sys.exit(1)
        
    return response


def extract_ai_content(response: Any) -> str:
    """Extract the content from an OpenAI API response.
    
    Args:
        response: The OpenAI API response
        
    Returns:
        The extracted content as a string
    """
    if hasattr(response, "choices") and response.choices and hasattr(response.choices[0], "message") and hasattr(response.choices[0].message, "content") and response.choices[0].message.content:
        return response.choices[0].message.content.strip()
    return ""


def get_ai_evaluation(prompt: str) -> Dict[str, Any]:
    """Get AI evaluation using OpenAI API with JSON response.
    
    Args:
        prompt: The evaluation prompt including the content to evaluate
        
    Returns:
        Dictionary with evaluation results
    """
    if not API_KEY:
        logger.error("No OpenAI API key found. Set the OPENAI_API_KEY environment variable.")
        return {
            "total_score": 0,
            "max_score": 100,
            "grade": "Improve",
            "summary": "Evaluation could not be performed: No OpenAI API key provided.",
            "top_recommendations": ["Set the OPENAI_API_KEY environment variable to enable evaluation."]
        }
    
    try:
        response = get_ai_response(prompt, json_response=True, temperature=0.2)
        result = json.loads(response.choices[0].message.content)
        return result
    
    except Exception as e:
        logger.error(f"Error during OpenAI evaluation: {e}")
        return {
            "total_score": 0,
            "max_score": 100,
            "grade": "Improve",
            "summary": f"Evaluation failed due to an error: {str(e)}",
            "top_recommendations": ["Check API key and network connection.", "Try again later."]
        }


def format_evaluation_results(evaluation: Dict[str, Any], 
                              title: str, 
                              categories: Dict[str, int]) -> str:
    """Format evaluation results as a readable string.
    
    Args:
        evaluation: The evaluation results dictionary
        title: The title to use in the formatted output
        categories: Dictionary of category names and their max scores
        
    Returns:
        Formatted evaluation report as a string
    """
    formatted = f"{title}\n"
    formatted += f"{'=' * len(title)}\n\n"
    formatted += f"Overall Score: {evaluation['total_score']}/{evaluation['max_score']} - Grade: {evaluation['grade']}\n\n"
    formatted += f"Summary: {evaluation['summary']}\n\n"
    
    # Results by category
    formatted += "Category Breakdown:\n"
    for category, (score, reason) in evaluation.get('scores', {}).items():
        max_score = categories.get(category, 10)  # Default to 10 if category not found
        category_display = category.replace('_', ' ').title()
        formatted += f"- {category_display}: {score}/{max_score} - {reason}\n"
    
    # Top recommendations
    formatted += "\nTop Improvement Recommendations:\n"
    for recommendation in evaluation.get('top_recommendations', []):
        formatted += f"- {recommendation}\n"
    
    return formatted


def evaluate_with_ai(file_path: str, prompt_filename: str, 
                     format_vars: Dict[str, str], 
                     categories: Dict[str, int],
                     report_title: str) -> Tuple[int, str]:
    """Evaluate a file using AI and return the results.
    
    Args:
        file_path: Path to the file to evaluate
        prompt_filename: Name of the prompt file to use
        format_vars: Variables to format the prompt with
        categories: Dictionary of category names and their max scores
        report_title: Title for the evaluation report
        
    Returns:
        Tuple of (score, formatted report)
    """
    setup_logging()
    
    # Load the file content
    content = load_file(file_path)
    if not content:
        return 0, f"File not found or empty: {file_path}"
    
    # Load and compose prompt template
    # Check if it's an evaluation prompt (should be in the evals subdirectory)
    if prompt_filename.endswith("_eval.md"):
        prompt_template = load_composite_template(prompt_filename, format_vars)
    else:
        prompt_path = PROMPTS_DIR / prompt_filename
        if not prompt_path.exists():
            logger.error(f"Prompt file not found: {prompt_path}")
            sys.exit(1)
            
        with open(prompt_path, encoding="utf-8") as f:
            prompt_template = f.read()
    
    # Format prompt
    prompt = prompt_template.format(**format_vars)
    
    # Get AI evaluation
    evaluation = get_ai_evaluation(prompt)
    
    # Format results
    report = format_evaluation_results(evaluation, report_title, categories)
    
    return evaluation.get('total_score', 0), report


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


# Template Utilities
def load_composite_template(prompt_filename: str, format_vars: Dict[str, str]) -> str:
    """Load and compose a prompt template from base and specific files.
    
    Args:
        prompt_filename: Name of the specific prompt file
        format_vars: Variables to format the prompt with
        
    Returns:
        The composed prompt template as a string
    """
    # Determine paths
    prompt_path = EVALS_DIR / prompt_filename
    
    # Check files exist
    if not BASE_TEMPLATE_PATH.exists():
        logger.error(f"Base template not found: {BASE_TEMPLATE_PATH}")
        sys.exit(1)
    
    if not prompt_path.exists():
        logger.error(f"Prompt file not found: {prompt_path}")
        sys.exit(1)
    
    # Load base template
    with open(BASE_TEMPLATE_PATH, encoding="utf-8") as f:
        base_template = f.read()
    
    # Load specific template
    with open(prompt_path, encoding="utf-8") as f:
        specific_template = f.read()
    
    # Extract prompt content (everything before FORMAT YOUR RESPONSE)
    prompt_content = specific_template.split("FORMAT YOUR RESPONSE AS JSON:")[0].strip()
    
    # Extract category scores part from the specific template
    category_scores_match = re.search(r'"scores": \{(.*?)\}', specific_template, re.DOTALL)
    category_scores = category_scores_match.group(1).strip() if category_scores_match else ""
    
    # Compose final prompt
    composed_prompt = f"{prompt_content}\n\nFORMAT YOUR RESPONSE AS JSON:\n{{\n  \"scores\": {{\n{category_scores}\n  }},\n  \"total_score\": total_score,\n  \"max_score\": 100,\n  \"grade\": \"Improve/OK/Good\",\n  \"summary\": \"Brief summary evaluation\",\n  \"top_recommendations\": [\n    \"First recommendation\",\n    \"Second recommendation\",\n    \"Third recommendation\"\n  ]\n}}\n\nEnsure your response is ONLY valid JSON that can be parsed."
    
    return composed_prompt

# Token and Size Utilities
def count_tokens(text: str, model_name: str) -> int:
    """Count the number of tokens in a text for a specific model.
    
    Args:
        text: The text to count tokens for
        model_name: The name of the model to use for tokenization
        
    Returns:
        The number of tokens in the text
    """
    enc = tiktoken.encoding_for_model(model_name)
    return len(enc.encode(text))

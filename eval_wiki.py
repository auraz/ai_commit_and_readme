#!/usr/bin/env python3
"""
Standalone script for evaluating wiki files with AI.

This script provides a robust way to evaluate wiki files individually or in batch,
automatically detecting content type and applying specialized evaluation criteria.

Usage:
    python eval_wiki.py path/to/wiki/file.md [--type TYPE]
    python eval_wiki.py path/to/wiki/directory --dir
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import openai
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("eval-wiki")

# Constants
PROMPTS_DIR = Path(__file__).parent / "ai_commit_and_readme" / "prompts" / "evals"
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4")

# Wiki page types and their corresponding prompt files
WIKI_PAGE_TYPES = {
    "api": "api_eval.md",
    "architecture": "architecture_eval.md",
    "cicd": "cicd_eval.md",
    "changelog": "changelog_eval.md",
    "configuration": "configuration_eval.md",
    "contributing": "contributing_eval.md",
    "deployment": "deployment_eval.md",
    "faq": "faq_eval.md",
    "home": "home_eval.md",
    "installation": "installation_eval.md",
    "security": "security_eval.md",
    "usage": "usage_eval.md",
    # Default - used when no specific type is detected
    "generic": "wiki_eval.md"
}

# Content patterns to detect wiki page types
CONTENT_PATTERNS = {
    "api": r"\bAPI\b|\bendpoint(s)?\b|\bREST\b|\bHTTP\b|\brequests?\b|\bresponses?\b",
    "architecture": r"\barchitecture\b|\bdesign\b|\bcomponent(s)?\b|\blayer(s)?\b|\btier(s)?\b",
    "cicd": r"\bCI(/|-)CD\b|\bcontinuous\s+(integration|deployment|delivery)\b|\bpipeline\b",
    "changelog": r"\bchangelog\b|\bversion\s+\d+\.\d+\b|\brelease(s|d)?\b",
    "configuration": r"\bconfiguration\b|\bsetting(s)?\b|\benv\s+var(iable)?s\b|\bconfig\s+file\b",
    "contributing": r"\bcontribut(e|ing|or)\b|\bpull\s+request\b|\bPR\b|\bcode\s+review\b",
    "deployment": r"\bdeployment\b|\bdeploy(ing)?\b|\brelease process\b|\bprovision(ing)?\b",
    "faq": r"\bFAQ\b|\bfrequently\s+asked\b|\bquestion(s)?\b|\bQ:\b|\bQ&A\b",
    "installation": r"\binstall(ation|ing)?\b|\bsetup\b|\bprerequisite(s)?\b|\brequirement(s)?\b",
    "security": r"\bsecurity\b|\bauth(entication|orization)?\b|\bvulnerabilit(y|ies)\b|\bcryptograph(y|ic)\b",
    "usage": r"\busage\b|\bhow\s+to\s+use\b|\bexample(s)?\b|\bcommand(s)?\b|\bguide\b"
}

def load_file(file_path: str) -> Optional[str]:
    """Load a file's content."""
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return None
    
    with open(path, encoding="utf-8") as f:
        return f.read()

def detect_wiki_type(content: str, filename: str) -> str:
    """Detect the type of wiki page based on content and filename."""
    # First check if filename directly indicates the type
    filename_lower = filename.lower()
    for page_type in WIKI_PAGE_TYPES.keys():
        if page_type != "generic" and page_type.lower() in filename_lower:
            return page_type
            
    # Otherwise, look for patterns in content
    content_lower = content.lower()
    matches = {}
    
    for page_type, pattern in CONTENT_PATTERNS.items():
        matches[page_type] = len(re.findall(pattern, content_lower, re.IGNORECASE))
    
    # Get the page type with the most matches
    if matches:
        best_match = max(matches.items(), key=lambda x: x[1])
        # Only use the match if it has a significant number of matches
        if best_match[1] >= 3:
            return best_match[0]
            
    # If no clear type is detected, return "generic"
    return "generic"

def evaluate_wiki(wiki_path: str, page_type: Optional[str] = None) -> Tuple[int, str]:
    """Evaluate a wiki page using the appropriate criteria."""
    # Load content
    content = load_file(wiki_path)
    if not content:
        return 0, f"Wiki page not found or empty: {wiki_path}"
    
    # Get filename for display and detection
    filename = os.path.basename(wiki_path)
    
    # Detect type if not provided
    if not page_type:
        page_type = detect_wiki_type(content, filename)
    
    logger.info(f"Evaluating {filename} as {page_type} content")
    
    # Get the prompt file for this type
    prompt_filename = WIKI_PAGE_TYPES.get(page_type, WIKI_PAGE_TYPES["generic"])
    prompt_path = PROMPTS_DIR / prompt_filename
    
    if not prompt_path.exists():
        logger.error(f"Prompt file not found: {prompt_path}")
        return 0, f"Error: Prompt file not found: {prompt_path}"
    
    # Load prompt template
    with open(prompt_path, encoding="utf-8") as f:
        prompt = f.read()
    
    # Replace content placeholder
    content_var = f"{page_type}_content"
    # First try the specific content variable
    if f"{{{content_var}}}" in prompt:
        prompt = prompt.replace(f"{{{content_var}}}", content)
    # Fall back to wiki_content if specific variable not found
    elif "{wiki_content}" in prompt:
        prompt = prompt.replace("{wiki_content}", content)
    else:
        logger.error(f"No content placeholder found in prompt: {prompt_filename}")
        return 0, "Error: Prompt template missing content placeholder"
    
    # Create a report title
    report_title = f"{page_type.title()} Wiki Evaluation: {filename}"
    
    # Evaluate using OpenAI
    score, report = evaluate_with_openai(prompt, report_title)
    return score, report

def evaluate_with_openai(prompt: str, report_title: str) -> Tuple[int, str]:
    """Send prompt to OpenAI and get evaluation."""
    if not API_KEY:
        logger.error("No OpenAI API key found. Set the OPENAI_API_KEY environment variable.")
        return 0, "Error: OPENAI_API_KEY not set"
    
    client = OpenAI(api_key=API_KEY)
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        # Parse JSON response
        result = json.loads(response.choices[0].message.content)
        
        # Format as report
        report = format_evaluation_report(result, report_title)
        return result.get("total_score", 0), report
        
    except Exception as e:
        logger.error(f"Error during OpenAI evaluation: {e}")
        return 0, f"Error during evaluation: {e}"

def format_evaluation_report(evaluation: Dict[str, Any], title: str) -> str:
    """Format evaluation results as string."""
    formatted = f"{title}\n"
    formatted += f"{'=' * len(title)}\n\n"
    formatted += f"Overall Score: {evaluation.get('total_score', 0)}/{evaluation.get('max_score', 100)} - Grade: {evaluation.get('grade', 'N/A')}\n\n"
    formatted += f"Summary: {evaluation.get('summary', 'No summary provided')}\n\n"
    
    # Results by category
    formatted += "Category Breakdown:\n"
    for category, (score, reason) in evaluation.get('scores', {}).items():
        category_display = category.replace("_", " ").title()
        formatted += f"- {category_display}: {score} - {reason}\n"
    
    # Top recommendations
    formatted += "\nTop Improvement Recommendations:\n"
    for recommendation in evaluation.get('top_recommendations', []):
        formatted += f"- {recommendation}\n"
    
    return formatted

def evaluate_directory(directory_path: str) -> Dict[str, Tuple[int, str]]:
    """Evaluate all wiki pages in a directory."""
    results = {}
    
    dir_path = Path(directory_path)
    if not dir_path.exists() or not dir_path.is_dir():
        logger.error(f"Directory not found: {directory_path}")
        return {}
    
    markdown_files = list(dir_path.glob("**/*.md"))
    logger.info(f"Found {len(markdown_files)} markdown files in {directory_path}")
    
    for file_path in markdown_files:
        logger.info(f"Evaluating {file_path.name}...")
        score, report = evaluate_wiki(str(file_path))
        relative_path = str(file_path.relative_to(dir_path))
        results[relative_path] = (score, report)
    
    return results

def main():
    """Main entry point for script."""
    parser = argparse.ArgumentParser(description="Evaluate wiki pages with AI")
    parser.add_argument("path", help="Path to wiki page or directory")
    parser.add_argument("--dir", action="store_true", help="Evaluate all wiki pages in directory")
    parser.add_argument("--type", help="Specify the wiki page type")
    args = parser.parse_args()
    
    if args.dir:
        results = evaluate_directory(args.path)
        for filename, (score, _) in sorted(results.items(), key=lambda x: x[1][0], reverse=True):
            print(f"{filename}: {score}")
        print(f"\nEvaluated {len(results)} wiki pages")
    else:
        score, report = evaluate_wiki(args.path, args.type)
        print(report)

if __name__ == "__main__":
    main()
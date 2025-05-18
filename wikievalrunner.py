#!/usr/bin/env python3
"""
Standalone script for evaluating wiki files with OpenAI.

This script provides a robust way to evaluate wiki or markdown files,
automatically detecting content type and applying specialized evaluation criteria.

Usage:
    python wikievalrunner.py wiki/Installation.md
    python wikievalrunner.py wiki/Architecture.md --type architecture
    python wikievalrunner.py wiki --dir
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("wiki-eval")

# Constants
SCRIPT_DIR = Path(__file__).parent
PROMPTS_DIR = SCRIPT_DIR / "ai_commit_and_readme" / "prompts" / "evals"
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4")

# Wiki page types mapping
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
    "generic": "wiki_eval.md"  # Default
}

# Content patterns for type detection
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

# Evaluation categories for wiki pages
WIKI_CATEGORIES = {
    "content_quality": 15,
    "structure_and_organization": 15,
    "clarity_and_readability": 15,
    "formatting_and_presentation": 10,
    "cross_referencing": 15,
    "completeness": 10,
    "technical_depth": 10,
    "user_focus": 10
}


def load_file(file_path: str) -> Optional[str]:
    """Load a file's content from path."""
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return None
    
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None


def detect_wiki_type(content: str, filename: str) -> str:
    """Detect the type of wiki page based on content and filename."""
    # First check filename for type hints
    filename_lower = filename.lower()
    for page_type in WIKI_PAGE_TYPES.keys():
        if page_type != "generic" and page_type.lower() in filename_lower:
            return page_type
            
    # Then look for content patterns
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
            
    # Default to generic if no clear type is detected
    return "generic"


def evaluate_with_openai(content: str, page_type: str, filename: str) -> Tuple[int, str]:
    """Evaluate wiki content using OpenAI API."""
    if not API_KEY:
        return 0, "Error: OPENAI_API_KEY environment variable not set"
    
    # Get the appropriate prompt file
    prompt_filename = WIKI_PAGE_TYPES.get(page_type, WIKI_PAGE_TYPES["generic"])
    prompt_path = PROMPTS_DIR / prompt_filename
    
    if not prompt_path.exists():
        return 0, f"Error: Prompt file not found: {prompt_path}"
    
    # Load the prompt template
    prompt_template = load_file(str(prompt_path))
    if not prompt_template:
        return 0, f"Error: Could not load prompt file: {prompt_path}"
    
    logger.debug(f"Using prompt template: {prompt_filename}")
    
    # Prepare the prompt by replacing content placeholders
    prompt = prompt_template
    
    # Try specific content variable first
    specific_var = f"{{{page_type}_content}}"
    generic_var = "{wiki_content}"
    
    logger.debug(f"Looking for content placeholder: '{specific_var}' or '{generic_var}'")
    
    if specific_var in prompt:
        logger.debug(f"Found specific placeholder: {specific_var}")
        # Safely replace the placeholder with content
        prompt = prompt.replace(specific_var, content)
    # Fall back to generic wiki_content
    elif generic_var in prompt:
        logger.debug(f"Found generic placeholder: {generic_var}")
        prompt = prompt.replace(generic_var, content)
    else:
        placeholders = re.findall(r'\{([^}]+)\}', prompt)
        logger.error(f"No recognized content placeholder found. Available placeholders: {placeholders}")
        return 0, f"Error: No content placeholder found in prompt: {prompt_filename}. Available placeholders: {placeholders}"
    
    logger.debug(f"Content length: {len(content)} characters")
    logger.debug(f"Final prompt length: {len(prompt)} characters")
    
    # Call OpenAI API
    client = OpenAI(api_key=API_KEY)
    try:
        logger.info(f"Sending request to OpenAI API using model: {MODEL}")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        # Get the raw response content
        raw_content = response.choices[0].message.content
        logger.debug(f"Raw API response: {raw_content[:500]}...")
        
        # Parse JSON response
        try:
            result = json.loads(raw_content)
            logger.debug(f"Parsed JSON successfully. Keys: {list(result.keys())}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Raw content: {raw_content}")
            return 0, f"Error: Failed to parse JSON response: {e}\n\nRaw response: {raw_content[:1000]}"
        
        # Validate essential fields
        required_fields = ["total_score", "max_score", "grade", "summary", "scores", "top_recommendations"]
        missing_fields = [field for field in required_fields if field not in result]
        if missing_fields:
            logger.warning(f"Missing fields in response: {missing_fields}")
        
        # Create report title
        report_title = f"{page_type.title()} Wiki Evaluation: {filename}"
        
        # Format the report
        report = format_evaluation_report(result, report_title)
        
        return result.get("total_score", 0), report
        
    except Exception as e:
        logger.error(f"Error during OpenAI evaluation: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 0, f"Error: {str(e)}\n\nTraceback: {traceback.format_exc()}"


def format_evaluation_report(evaluation: Dict[str, Any], title: str) -> str:
    """Format evaluation results as string."""
    formatted = f"{title}\n"
    formatted += f"{'=' * len(title)}\n\n"
    
    # Add debug information if scores are missing
    if 'total_score' not in evaluation:
        formatted += "WARNING: Missing 'total_score' in evaluation results\n"
        formatted += f"Available keys: {list(evaluation.keys())}\n\n"
    
    formatted += f"Overall Score: {evaluation.get('total_score', 0)}/{evaluation.get('max_score', 100)} - Grade: {evaluation.get('grade', 'N/A')}\n\n"
    formatted += f"Summary: {evaluation.get('summary', 'No summary provided')}\n\n"
    
    # Results by category
    formatted += "Category Breakdown:\n"
    if 'scores' in evaluation:
        try:
            for category, data in evaluation['scores'].items():
                # Handle different possible formats for score data
                if isinstance(data, list) and len(data) >= 2:
                    score, reason = data[0], data[1]
                elif isinstance(data, dict) and 'score' in data and 'reason' in data:
                    score, reason = data['score'], data['reason']
                else:
                    score, reason = str(data), "No reason provided"
                
                category_display = category.replace("_", " ").title()
                formatted += f"- {category_display}: {score} - {reason}\n"
        except Exception as e:
            formatted += f"Error formatting scores: {e}\n"
            formatted += f"Raw scores data: {evaluation.get('scores')}\n"
    else:
        formatted += "No scores data found in evaluation results\n"
    
    # Top recommendations
    formatted += "\nTop Improvement Recommendations:\n"
    if 'top_recommendations' in evaluation and evaluation['top_recommendations']:
        for recommendation in evaluation['top_recommendations']:
            formatted += f"- {recommendation}\n"
    else:
        formatted += "No recommendations provided\n"
    
    return formatted


def evaluate_wiki(wiki_path: str, page_type: Optional[str] = None) -> Tuple[int, str]:
    """Evaluate a wiki page."""
    # Load content
    content = load_file(wiki_path)
    if not content:
        return 0, f"Error: File not found or could not be read: {wiki_path}"
    
    # Get filename
    filename = os.path.basename(wiki_path)
    
    # Detect type if not provided
    if not page_type:
        page_type = detect_wiki_type(content, filename)
    
    logger.info(f"Evaluating {filename} as {page_type} content")
    
    # Evaluate using OpenAI
    return evaluate_with_openai(content, page_type, filename)


def evaluate_directory(directory_path: str) -> Dict[str, Tuple[int, str]]:
    """Evaluate all markdown files in a directory."""
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
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    parser.add_argument("--debug", "-d", action="store_true", help="Show debug information")
    args = parser.parse_args()
    
    # Set logging level based on args
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Check for API key
    if not API_KEY:
        logger.error("No OpenAI API key found. Set the OPENAI_API_KEY environment variable.")
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    logger.info(f"Using OpenAI model: {MODEL}")
    logger.info(f"Prompts directory: {PROMPTS_DIR}")
    
    try:
        if args.dir:
            results = evaluate_directory(args.path)
            for filename, (score, _) in sorted(results.items(), key=lambda x: x[1][0], reverse=True):
                print(f"{filename}: {score}")
            print(f"\nEvaluated {len(results)} wiki pages")
        else:
            logger.info(f"Evaluating single file: {args.path}")
            if args.type:
                logger.info(f"Using specified type: {args.type}")
            
            score, report = evaluate_wiki(args.path, args.type)
            print(report)
            
            # Print score as return code for scripting
            sys.exit(0 if score > 0 else 1)
    except KeyboardInterrupt:
        logger.info("Evaluation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
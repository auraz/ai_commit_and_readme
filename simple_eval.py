#!/usr/bin/env python3
"""
Simple Direct Evaluation Script for Wiki Pages, READMEs, and Markdown Files

This script provides a direct, robust way to evaluate documents with OpenAI,
bypassing the complexity of the main system.

Usage:
  python simple_eval.py path/to/file.md
  python simple_eval.py path/to/directory --dir
  python simple_eval.py path/to/file.md --type [readme|api|architecture|changelog|etc]
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

try:
    from openai import OpenAI
except ImportError:
    print("Error: OpenAI Python package not found. Please install it with:")
    print("  pip install openai")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("simple-eval")

# Constants
SCRIPT_DIR = Path(__file__).parent
PROMPTS_DIR = SCRIPT_DIR / "prompts" / "evals"
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4")

# Wiki/markdown document types and their corresponding prompt files
DOC_TYPES = {
    "readme": "readme_eval.md",
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
    "wiki": "wiki_eval.md",  # Generic wiki
    "generic": "wiki_eval.md"  # Fallback
}

# Content patterns for type detection
CONTENT_PATTERNS = {
    "readme": r"\bproject\b|\bquick\s+start\b|\binstallation\b|\bfeatures\b|\boverview\b|\bintroduction\b",
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


def read_file(path: str) -> Optional[str]:
    """Read a file's content safely."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return None


def write_file(path: str, content: str) -> bool:
    """Write content to a file safely."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing to file {path}: {e}")
        return False


def detect_doc_type(content: str, filename: str) -> str:
    """Detect document type from content and filename."""
    # Check filename for clues
    filename_lower = filename.lower()
    
    # Special case for README files
    if "readme" in filename_lower:
        return "readme"
    
    # Check other doc types based on filename
    for doc_type in DOC_TYPES:
        if doc_type in filename_lower and doc_type != "generic":
            return doc_type
    
    # Content-based detection
    match_counts = {}
    for doc_type, pattern in CONTENT_PATTERNS.items():
        match_counts[doc_type] = len(re.findall(pattern, content, re.IGNORECASE))
    
    # Find the type with the most matches
    if match_counts:
        best_match = max(match_counts.items(), key=lambda x: x[1])
        if best_match[1] >= 3:  # At least 3 matches to be confident
            return best_match[0]
    
    # Default to generic wiki evaluation
    return "generic"


def find_content_placeholder(prompt: str) -> Optional[str]:
    """Find content placeholder in prompt template."""
    # Look for common content placeholders
    placeholders = re.findall(r'\{(\w+_content)\}', prompt)
    if placeholders:
        return placeholders[0]
    
    # Look for generic content placeholder
    if "{content}" in prompt:
        return "content"
    
    return None


def evaluate_document(doc_path: str, doc_type: Optional[str] = None) -> Tuple[int, str]:
    """Evaluate a document with OpenAI."""
    # Check if file exists
    if not os.path.exists(doc_path):
        return 0, f"Error: File not found: {doc_path}"
    
    # Read file content
    content = read_file(doc_path)
    if not content:
        return 0, f"Error: Could not read file: {doc_path}"
    
    # Get filename for display and detection
    filename = os.path.basename(doc_path)
    
    # Detect document type if not specified
    if not doc_type:
        doc_type = detect_doc_type(content, filename)
    
    logger.info(f"Evaluating {filename} as {doc_type} content")
    
    # Get corresponding prompt file
    prompt_file = DOC_TYPES.get(doc_type, DOC_TYPES["generic"])
    prompt_path = PROMPTS_DIR / prompt_file
    
    if not prompt_path.exists():
        return 0, f"Error: Prompt file not found: {prompt_path}"
    
    # Read prompt template
    prompt_template = read_file(str(prompt_path))
    if not prompt_template:
        return 0, f"Error: Could not read prompt file: {prompt_path}"
    
    # Insert content directly into the prompt
    # First try type-specific placeholder
    specific_placeholder = f"{{{doc_type}_content}}"
    if specific_placeholder in prompt_template:
        prompt = prompt_template.replace(specific_placeholder, content)
    # Try other common placeholders
    elif "{content}" in prompt_template:
        prompt = prompt_template.replace("{content}", content)
    elif "{wiki_content}" in prompt_template:
        prompt = prompt_template.replace("{wiki_content}", content)
    elif "{readme_content}" in prompt_template:
        prompt = prompt_template.replace("{readme_content}", content)
    else:
        # Fallback - find any placeholder containing "content"
        placeholder = find_content_placeholder(prompt_template)
        if placeholder:
            prompt = prompt_template.replace(f"{{{placeholder}}}", content)
        else:
            return 0, f"Error: No content placeholder found in prompt: {prompt_file}"
    
    # Check if OpenAI API key is set
    if not API_KEY:
        return 0, "Error: OPENAI_API_KEY environment variable not set"
    
    # Call OpenAI API
    client = OpenAI(api_key=API_KEY)
    try:
        logger.info(f"Sending request to OpenAI API (model: {MODEL})")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        # Get raw response
        raw_response = response.choices[0].message.content
        
        # Save raw response to a file for debugging
        raw_output_path = f"{os.path.splitext(doc_path)[0]}_raw_output.json"
        write_file(raw_output_path, raw_response)
        logger.info(f"Raw API response saved to: {raw_output_path}")
        
        # Parse JSON response
        try:
            result = json.loads(raw_response)
        except json.JSONDecodeError as e:
            return 0, f"Error parsing API response: {e}\n\nRaw response: {raw_response[:500]}..."
        
        # Format and return results
        report = format_evaluation_report(result, doc_type, filename)
        
        # Get score
        score = result.get("total_score", 0)
        
        return score, report
        
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        import traceback
        tb = traceback.format_exc()
        logger.error(tb)
        return 0, f"Error during evaluation: {e}\n\n{tb}"


def format_evaluation_report(evaluation: Dict[str, Any], doc_type: str, filename: str) -> str:
    """Format evaluation results as a readable report."""
    # Create title
    title = f"{doc_type.title()} Evaluation: {filename}"
    report = [title, "=" * len(title), ""]
    
    # Add score and grade
    total_score = evaluation.get("total_score", 0)
    max_score = evaluation.get("max_score", 100)
    grade = evaluation.get("grade", "N/A")
    
    report.append(f"Overall Score: {total_score}/{max_score} - Grade: {grade}")
    report.append("")
    
    # Add summary
    summary = evaluation.get("summary", "No summary provided")
    report.append(f"Summary: {summary}")
    report.append("")
    
    # Add category breakdown
    report.append("Category Breakdown:")
    
    if "scores" in evaluation:
        scores = evaluation["scores"]
        try:
            for category, data in scores.items():
                # Handle different score formats
                if isinstance(data, list) and len(data) >= 2:
                    # Format: [score, "reason"]
                    score, reason = data[0], data[1]
                elif isinstance(data, dict) and "score" in data:
                    # Format: {"score": value, "reason": "text"}
                    score, reason = data.get("score", 0), data.get("reason", "No reason provided")
                else:
                    # Unknown format
                    score, reason = "?", str(data)
                
                # Format category name for display
                category_display = category.replace("_", " ").title()
                report.append(f"- {category_display}: {score} - {reason}")
        except Exception as e:
            report.append(f"Error formatting scores: {e}")
            report.append(f"Raw scores: {scores}")
    else:
        report.append("No category scores found in evaluation")
    
    report.append("")
    
    # Add recommendations
    report.append("Top Improvement Recommendations:")
    recommendations = evaluation.get("top_recommendations", [])
    if recommendations:
        for rec in recommendations:
            report.append(f"- {rec}")
    else:
        report.append("No recommendations provided")
    
    # Join all lines
    return "\n".join(report)


def evaluate_directory(directory_path: str) -> Dict[str, Tuple[int, str]]:
    """Evaluate all markdown files in a directory."""
    results = {}
    
    dir_path = Path(directory_path)
    if not dir_path.exists() or not dir_path.is_dir():
        logger.error(f"Directory not found: {directory_path}")
        return {}
    
    # Find all markdown files
    markdown_files = list(dir_path.glob("**/*.md"))
    logger.info(f"Found {len(markdown_files)} markdown files in {directory_path}")
    
    # Evaluate each file
    for file_path in markdown_files:
        logger.info(f"Evaluating: {file_path.name}")
        
        score, report = evaluate_document(str(file_path))
        
        # Save report to file
        report_path = f"{file_path.stem}_evaluation.md"
        report_full_path = file_path.parent / report_path
        write_file(str(report_full_path), report)
        
        # Add to results
        relative_path = str(file_path.relative_to(dir_path))
        results[relative_path] = (score, report)
        
        logger.info(f"Score: {score}, Report saved to: {report_path}")
    
    return results


def display_available_types():
    """Display all available document types."""
    print("Available document types:")
    for doc_type in sorted(DOC_TYPES.keys()):
        if doc_type != "generic":
            print(f"  - {doc_type}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Simple document evaluator using OpenAI",
        epilog="Set OPENAI_API_KEY environment variable before running"
    )
    
    parser.add_argument("path", help="Path to document or directory to evaluate")
    parser.add_argument("--type", "-t", help="Document type (readme, api, architecture, etc.)")
    parser.add_argument("--dir", "-d", action="store_true", help="Evaluate all documents in directory")
    parser.add_argument("--list-types", "-l", action="store_true", help="List available document types")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output", "-o", help="Save output to file")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Display available types
    if args.list_types:
        display_available_types()
        return
    
    # Check for API key
    if not API_KEY:
        print("Error: OPENAI_API_KEY environment variable not set")
        return 1
    
    # Evaluate directory
    if args.dir:
        try:
            results = evaluate_directory(args.path)
            
            # Print summary
            print("\nEvaluation Summary:")
            print("-" * 50)
            
            for filename, (score, _) in sorted(results.items(), key=lambda x: x[1][0], reverse=True):
                print(f"{filename}: {score}")
            
            print(f"\nEvaluated {len(results)} documents")
            print(f"Detailed reports saved to individual files")
            
            return 0
            
        except Exception as e:
            print(f"Error evaluating directory: {e}")
            return 1
    
    # Evaluate single file
    else:
        try:
            score, report = evaluate_document(args.path, args.type)
            
            # Print or save report
            if args.output:
                if write_file(args.output, report):
                    print(f"Evaluation report saved to: {args.output}")
                    print(f"Score: {score}")
                else:
                    print(f"Error writing to {args.output}")
                    print(report)
            else:
                print(report)
            
            # Return score for scripting
            return 0 if score > 0 else 1
            
        except Exception as e:
            print(f"Error evaluating document: {e}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == "__main__":
    sys.exit(main())
"""Wiki Evaluator

AI-powered evaluator for wiki pages that selects the most appropriate
evaluation criteria based on the content and filename.
"""

import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from ..tools import evaluate_with_ai, load_file

logger = logging.getLogger(__name__)

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

# Evaluation categories and their weights for generic wiki pages
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


class WikiEvaluator:
    """Wiki page evaluator that selects the appropriate evaluation criteria.
    
    This class analyzes a wiki page's filename and content to determine
    the most appropriate evaluation criteria, then performs an AI-powered
    evaluation using the specialized prompt.
    """
    
    def __init__(self):
        """Initialize the wiki evaluator."""
        pass
    
    def detect_wiki_type(self, content: str, filename: str) -> str:
        """Detect the type of wiki page based on content and filename.
        
        Args:
            content: The content of the wiki page
            filename: The filename of the wiki page
            
        Returns:
            The detected wiki page type
        """
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
    
    def get_categories_for_type(self, page_type: str) -> Dict[str, int]:
        """Get the evaluation categories for a specific wiki page type.
        
        Args:
            page_type: The wiki page type
            
        Returns:
            Dictionary of category names and their weights
        """
        # In the future, we could define specific category weights for each type
        # For now, using the same categories for all wiki pages
        return WIKI_CATEGORIES
    
    def evaluate(self, wiki_path: str, page_type: Optional[str] = None) -> Tuple[int, str]:
        """Evaluate a wiki page using AI.
        
        Args:
            wiki_path: Path to the wiki page to evaluate
            page_type: Optional specific page type to use
            
        Returns:
            Tuple of (score, formatted report)
        """
        # Load content
        content = load_file(wiki_path)
        if not content:
            return 0, f"Wiki page not found or empty: {wiki_path}"
        
        # Get filename for display and detection
        filename = os.path.basename(wiki_path)
        
        # Detect type if not provided
        if not page_type:
            page_type = self.detect_wiki_type(content, filename)
        
        # Get the prompt filename for this type
        prompt_filename = WIKI_PAGE_TYPES.get(page_type, WIKI_PAGE_TYPES["generic"])
        
        # Get categories for this type
        categories = self.get_categories_for_type(page_type)
        
        # Create a report title with the type and filename
        report_title = f"{page_type.title()} Wiki Evaluation: {filename}"
        
        # Set up format variables based on page type
        format_vars = {
            "wiki_content": content
        }
        
        # Add specific content variable based on page type
        specific_var = f"{page_type}_content" 
        format_vars[specific_var] = content
        
        # Evaluate the wiki page
        score, report = evaluate_with_ai(
            file_path=wiki_path,
            prompt_filename=prompt_filename,
            format_vars=format_vars,
            categories=categories,
            report_title=report_title
        )
        
        return score, report


def evaluate(wiki_path: str, page_type: Optional[str] = None) -> Tuple[int, str]:
    """Evaluate a wiki page using the WikiEvaluator.
    
    Args:
        wiki_path: Path to the wiki page to evaluate
        page_type: Optional specific page type to use
        
    Returns:
        Tuple of (score, formatted report)
    """
    evaluator = WikiEvaluator()
    return evaluator.evaluate(wiki_path, page_type)


def evaluate_directory(directory_path: str) -> Dict[str, Tuple[int, str]]:
    """Evaluate all wiki pages in a directory.
    
    Args:
        directory_path: Path to the directory containing wiki pages
        
    Returns:
        Dict of filename -> (score, report)
    """
    results = {}
    evaluator = WikiEvaluator()
    
    dir_path = Path(directory_path)
    if not dir_path.exists() or not dir_path.is_dir():
        logger.error(f"Directory not found: {directory_path}")
        return {}
    
    for file_path in dir_path.glob("**/*.md"):
        score, report = evaluator.evaluate(str(file_path))
        relative_path = str(file_path.relative_to(dir_path))
        results[relative_path] = (score, report)
    
    return results


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate wiki pages")
    parser.add_argument("path", help="Path to wiki page or directory")
    parser.add_argument("--dir", action="store_true", help="Evaluate all wiki pages in directory")
    parser.add_argument("--type", help="Specify the wiki page type")
    args = parser.parse_args()
    
    if args.dir:
        results = evaluate_directory(args.path)
        for filename, (score, _) in sorted(results.items(), key=lambda x: x[1][0], reverse=True):
            sys.stdout.write(f"{filename}: {score}\n")
        sys.stdout.write(f"\nEvaluated {len(results)} wiki pages\n")
    else:
        score, report = evaluate(args.path, args.type)
        sys.stdout.write(f"{report}\n")
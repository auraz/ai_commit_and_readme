#!/usr/bin/env python3
"""
Fix prompt files corrupted by incorrect brace escaping.
This script corrects JSON formatting in prompt markdown files.
"""

import os
import re
from pathlib import Path

# Path to prompts directory
PROMPTS_DIR = Path(__file__).parent / "ai_commit_and_readme" / "prompts"


def fix_prompt_file(file_path):
    """Fix a single prompt file to correct JSON formatting issues."""
    print(f"Fixing {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Fix content placeholder with extra closing braces
    content = re.sub(r'({[\w_]+})\}+', r'\1', content)
    
    # Fix the FORMAT YOUR RESPONSE section by replacing the entire section
    # First find where the format section starts
    format_section_match = re.search(r'FORMAT YOUR RESPONSE AS JSON:', content)
    if format_section_match:
        start_pos = format_section_match.start()
        
        # Find where it ends (before "Ensure your response...")
        ensure_match = re.search(r'Ensure your response', content[start_pos:])
        if ensure_match:
            end_pos = start_pos + ensure_match.start()
            
            # Extract variable name from pattern like {api_content}
            var_name_match = re.search(r'{(\w+_content)}', content)
            var_name = var_name_match.group(1) if var_name_match else "content"
            
            # Identify file type from filename to use correct format template
            file_type = os.path.basename(file_path).replace("_eval.md", "")
            
            # Get appropriate format section template based on the file type
            format_section = get_format_template(file_type)
            
            # Replace the section
            content = (
                content[:start_pos] + 
                "FORMAT YOUR RESPONSE AS JSON:\n" + 
                format_section + 
                content[end_pos:]
            )
    
    # Write corrected content back to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def get_format_template(file_type):
    """Get the appropriate JSON format template based on file type."""
    # Generic template
    template = """
{
  "scores": {
    "CATEGORY1": [score, "reason"],
    "CATEGORY2": [score, "reason"]
    // more categories based on file type
  },
  "total_score": total_score,
  "max_score": 100,
  "grade": "A/B/C/D/F",
  "summary": "Brief summary evaluation",
  "top_recommendations": [
    "First recommendation",
    "Second recommendation",
    "Third recommendation"
  ]
}
"""
    
    return template


def main():
    """Fix all prompt files in the prompts directory."""
    if not PROMPTS_DIR.exists():
        print(f"Error: Prompts directory not found at {PROMPTS_DIR}")
        return
    
    # Find all markdown files in the prompts directory
    prompt_files = list(PROMPTS_DIR.glob("*.md"))
    
    if not prompt_files:
        print("No prompt files found")
        return
    
    print(f"Found {len(prompt_files)} prompt files to fix")
    
    # Fix each file
    for file_path in prompt_files:
        fix_prompt_file(file_path)
    
    print("All prompt files have been fixed")


if __name__ == "__main__":
    main()
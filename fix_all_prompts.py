#!/usr/bin/env python3
"""
Fix formatting issues in all prompt markdown files.

This script locates all prompt markdown files in the prompts directory and:
1. Fixes content placeholders with extra braces
2. Corrects the JSON response format section
3. Ensures proper escaping of curly braces where needed
"""

import os
import re
from pathlib import Path

# Path to prompts directory
PROMPTS_DIR = Path(__file__).parent / "ai_commit_and_readme" / "prompts"


def fix_prompt_file(file_path):
    """Fix a single prompt file to correct JSON formatting issues."""
    print(f"Fixing {os.path.basename(file_path)}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Step 1: Fix content placeholders that have extra braces
    # Pattern: {var_name}} -> {var_name}
    content = re.sub(r'({[\w_]+})\}+', r'\1', content)
    
    # Step 2: Fix the FORMAT YOUR RESPONSE AS JSON section
    # Find the section
    format_section_match = re.search(r'FORMAT YOUR RESPONSE AS JSON:(.*?)Ensure your response', 
                                    content, re.DOTALL)
    
    if format_section_match:
        format_section = format_section_match.group(1).strip()
        
        # Fix incorrect braces in the format section
        fixed_format = re.sub(r'\{\{', '{', format_section)
        fixed_format = re.sub(r'\}\}', '}', fixed_format)
        fixed_format = re.sub(r'\}\}\}\}', '}', fixed_format)
        
        # Replace the entire section with the fixed version
        content = content.replace(format_section_match.group(1), 
                               "\n" + fixed_format + "\n\n")
    
    # Write the fixed content back to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """Find and fix all prompt files."""
    if not PROMPTS_DIR.exists():
        print(f"Error: Prompts directory not found at {PROMPTS_DIR}")
        return 1
    
    # Find all markdown files in the prompts directory
    prompt_files = list(PROMPTS_DIR.glob("*.md"))
    
    if not prompt_files:
        print("No prompt files found")
        return 0
    
    print(f"Found {len(prompt_files)} prompt files to fix")
    
    # Fix each file
    for file_path in prompt_files:
        fix_prompt_file(file_path)
    
    print("All prompt files have been fixed")
    return 0


if __name__ == "__main__":
    exit(main())
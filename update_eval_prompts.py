#!/usr/bin/env python3
"""
Script to update all evaluation prompts to use the base template.

This script removes the common JSON structure from all evaluation prompts,
keeping only the specific categories/scores sections, to work with the 
new composition approach that uses base_eval_template.md.
"""

import os
import re
from pathlib import Path

# Path to prompts directory
SCRIPT_DIR = Path(__file__).parent
PROMPTS_DIR = SCRIPT_DIR / "ai_commit_and_readme" / "prompts"
EVALS_DIR = PROMPTS_DIR / "evals"


def update_prompt_file(file_path):
    """Update a single prompt file to use the base template."""
    print(f"Updating {os.path.basename(file_path)}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if this file needs updating (contains the JSON response format)
    if "FORMAT YOUR RESPONSE AS JSON:" not in content:
        print(f"  Skipping {os.path.basename(file_path)} - already updated or not an eval prompt")
        return
    
    # Split content at FORMAT YOUR RESPONSE
    parts = content.split("FORMAT YOUR RESPONSE AS JSON:")
    if len(parts) != 2:
        print(f"  Warning: Unexpected format in {os.path.basename(file_path)}")
        return
    
    prompt_content = parts[0].strip()
    json_part = parts[1].strip()
    
    # Extract only the scores section
    scores_match = re.search(r'"scores":\s*{(.*?)}', json_part, re.DOTALL)
    if not scores_match:
        print(f"  Warning: Could not find scores section in {os.path.basename(file_path)}")
        return
    
    scores_content = scores_match.group(1).strip()
    
    # Create the new content with simplified JSON
    new_content = f"""{prompt_content}

FORMAT YOUR RESPONSE AS JSON:
{{
  "scores": {{
{scores_content}
  }}
}}
"""
    
    # Write back to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"  Updated {os.path.basename(file_path)}")


def main():
    """Update all evaluation prompt files."""
    if not EVALS_DIR.exists():
        print(f"Error: Evaluation prompts directory not found at {EVALS_DIR}")
        return 1
    
    # Find all markdown files in the evals directory
    prompt_files = list(EVALS_DIR.glob("*_eval.md"))
    
    if not prompt_files:
        print("No evaluation prompt files found")
        return 0
    
    print(f"Found {len(prompt_files)} evaluation prompt files to update")
    
    # Skip the base template itself
    base_template = EVALS_DIR / "base_eval_template.md"
    if base_template in prompt_files:
        prompt_files.remove(base_template)
    
    # Update each file
    for file_path in prompt_files:
        update_prompt_file(file_path)
    
    print("All evaluation prompt files have been updated")
    return 0


if __name__ == "__main__":
    exit(main())
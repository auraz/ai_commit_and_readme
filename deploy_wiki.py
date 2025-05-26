#!/usr/bin/env python3
"""Deploy wiki documentation to GitHub wiki."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def main():
    """Deploy wiki to GitHub."""
    # Get repository info
    remote_url = run_command("git remote get-url origin")
    if not remote_url:
        print("No git remote found")
        sys.exit(1)
    
    # Extract owner and repo from URL
    if remote_url.endswith('.git'):
        remote_url = remote_url[:-4]
    
    parts = remote_url.split('/')
    owner = parts[-2]
    repo = parts[-1]
    
    print(f"Deploying wiki to {owner}/{repo}")
    
    # Create temporary directory for wiki repo
    wiki_dir = Path.cwd() / ".wiki_deploy"
    if wiki_dir.exists():
        shutil.rmtree(wiki_dir)
    
    # Clone wiki repo
    wiki_url = f"https://github.com/{owner}/{repo}.wiki.git"
    print(f"Cloning wiki from {wiki_url}")
    
    result = subprocess.run(
        f"git clone {wiki_url} {wiki_dir}", 
        shell=True, 
        capture_output=True, 
        text=True
    )
    
    if result.returncode != 0:
        if "not found" in result.stderr.lower():
            print("Wiki not initialized. Creating new wiki...")
            wiki_dir.mkdir()
            run_command("git init", cwd=wiki_dir)
        else:
            print(f"Error cloning wiki: {result.stderr}")
            sys.exit(1)
    
    # Copy wiki files
    source_wiki = Path.cwd() / "wiki"
    if not source_wiki.exists():
        print("No wiki directory found")
        sys.exit(1)
    
    print("Copying wiki files...")
    for file in source_wiki.glob("*.md"):
        shutil.copy2(file, wiki_dir / file.name)
        print(f"  Copied {file.name}")
    
    # Commit and push changes
    os.chdir(wiki_dir)
    
    # Add all files
    run_command("git add -A")
    
    # Check if there are changes
    status = run_command("git status --porcelain")
    if not status:
        print("No changes to deploy")
        return
    
    # Commit changes
    commit_msg = "Update wiki documentation"
    run_command(f'git commit -m "{commit_msg}"')
    
    # Push to wiki
    print("Pushing to GitHub wiki...")
    run_command(f"git push {wiki_url} master || git push {wiki_url} main")
    
    print("✅ Wiki deployed successfully!")
    print(f"View at: https://github.com/{owner}/{repo}/wiki")
    
    # Cleanup
    os.chdir("..")
    shutil.rmtree(wiki_dir)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
AI Commit and README tool main module.
Provides subcommands for enriching README.md with AI suggestions based on git diffs.
"""
import argparse
import openai
import subprocess
import os
import sys
import tiktoken

AI_ENRICH_PROMPT = (
    "You are an expert software documenter. "
    "Suggest additional content or improvements for the following README.md based on these code changes. "
    "Only output new or updated sections, not the full README. "
    "If nothing should be changed, reply with 'NO CHANGES'. "
    "Do NOT consider any prior conversation or chat history—only use the code diff and README below.\n\n"
    "Code changes:\n{diff}\n\nCurrent README:\n{readme}\n"
)
def chain_handler(func):
    """Decorator to ensure handler returns ctx for chaining."""
    def wrapper(ctx, *args, **kwargs):
        func(ctx, *args, **kwargs)
        return ctx
    return wrapper

@chain_handler
def check_api_key(ctx):
    """Check for the presence of the OpenAI API key in context or environment."""
    ctx['api_key'] = ctx.get('api_key') or os.getenv("OPENAI_API_KEY")
    if not ctx['api_key']: print("OPENAI_API_KEY not set. Skipping README update.") or sys.exit(0)

@chain_handler
def get_diff(ctx, diff_args=None):
    """Retrieve the staged git diff (or file list) and store it in context."""
    ctx['diff'] = subprocess.check_output(diff_args or ["git", "diff", "--cached", "-U1"]).decode()

@chain_handler
def check_diff_empty(ctx):
    """Exit if the diff is empty, with a message."""
    if not ctx['diff'].strip():
        print("No staged changes detected. Nothing to enrich.")
        sys.exit(0)

@chain_handler
def print_diff_info(ctx):
    """Print the size of the diff in characters and tokens."""
    print(f"[INFO] Diff size: {len(ctx['diff'])} characters")
    enc = tiktoken.encoding_for_model(ctx['model'])
    diff_tokens = len(enc.encode(ctx['diff']))
    print(f"[INFO] Diff size: {diff_tokens} tokens")
    ctx['diff_tokens'] = diff_tokens

@chain_handler
def fallback_large_diff(ctx):
    """Fallback to file list if the diff is too large."""
    if len(ctx['diff']) > 100000:
        print("[WARNING] Diff is too large (>100000 characters). Falling back to 'git diff --cached --name-only'.")
        get_diff(ctx, ["git", "diff", "--cached", "--name-only"])
        print(f"[INFO] Using file list as diff: {ctx['diff'].strip()}")

@chain_handler
def get_readme(ctx):
    """Read the README file and store its contents in context."""
    path = ctx['readme_path']
    ctx['readme'] = open(path).read() if os.path.exists(path) else ""

@chain_handler
def print_readme_info(ctx):
    """Print the size of the README in characters and tokens."""
    print(f"[INFO] README size: {len(ctx['readme'])} characters")
    enc = tiktoken.encoding_for_model(ctx['model'])
    readme_tokens = len(enc.encode(ctx['readme']))
    print(f"[INFO] README size: {readme_tokens} tokens")
    ctx['readme_tokens'] = readme_tokens

@chain_handler
def ai_enrich(ctx):
    """Call the OpenAI API to get README enrichment suggestions."""
    prompt = AI_ENRICH_PROMPT.format(diff=ctx['diff'], readme=ctx['readme'])
    client = openai.OpenAI(api_key=ctx['api_key'])
    try:
        response = client.chat.completions.create(
            model=ctx['model'], messages=[{"role": "user", "content": prompt}]
        )
    except Exception as e:
        print(f"Error from OpenAI API: {e}")
        sys.exit(1)
    ai_suggestion = response.choices[0].message.content.strip()
    ctx['ai_suggestion'] = ai_suggestion

@chain_handler
def write_enrichment(ctx):
    """Write AI suggestions to the README and stage the file if needed."""
    if ctx['ai_suggestion'] != "NO CHANGES":
        with open(ctx['readme_path'], "a") as f:
            f.write("\n\n# AI-suggested enrichment:\n")
            f.write(ctx['ai_suggestion'])
        print(f"{ctx['readme_path']} enriched and staged with AI suggestions.")
        subprocess.run(["git", "add", ctx['readme_path']])
    else: print("No enrichment needed for README.md.")

def enrich_readme(readme_path="README.md", api_key=None, model="gpt-4o"):
    """Enrich the README.md file with AI-generated suggestions using a handler chain."""
    ctx = {
        'readme_path': readme_path,
        'api_key': api_key,
        'model': model,
    }
    for handler in [
        check_api_key,
        get_diff,
        check_diff_empty,
        print_diff_info,
        fallback_large_diff,
        get_readme,
        print_readme_info,
        ai_enrich,
        write_enrichment,
    ]:
        ctx = handler(ctx)


def main():
    """
    Command-line interface for the AI Commit and README tool.
    Dispatches subcommands using a dispatcher dictionary.
    """
    parser = argparse.ArgumentParser(description="AI Commit and README tool")
    parser.add_argument(
        "command",
        nargs="?",
        default="enrich-readme",
        help="Subcommand to run (default: enrich-readme)",
        choices=["enrich-readme"],
    )
    parser.add_argument(
        "--readme",
        type=str,
        default="README.md",
        help="Path to README.md (default: README.md)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API key (default: from env)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="OpenAI model (default: gpt-4o)",
    )
    args = parser.parse_args()

    # Dispatcher dictionary
    command_dispatcher = {
        "enrich-readme": lambda: enrich_readme(
            readme_path=args.readme, api_key=args.api_key, model=args.model
        ),
    }

    command_dispatcher[args.command]()

if __name__ == "__main__":
    main()


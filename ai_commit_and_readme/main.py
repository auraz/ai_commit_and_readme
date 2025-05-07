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


def enrich_readme(readme_path="README.md", api_key=None, model="gpt-4o"):
    """
    Enrich the README.md file with AI-generated suggestions based on the current staged git diff.
    - Uses OpenAI API to generate suggestions.
    - Appends suggestions to README.md if applicable and stages the file.
    Args:
        readme_path (str): Path to the README file to enrich.
        api_key (str): OpenAI API key. If None, uses OPENAI_API_KEY env var.
        model (str): OpenAI model to use.
    """
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set. Skipping README update.")
        sys.exit(0)

    client = openai.OpenAI(api_key=api_key)

    try:
        diff = subprocess.check_output(["git", "diff", "--cached", "-U1"]).decode()
    except Exception as e:
        print(f"Error getting staged diff: {e}")
        sys.exit(1)

    if not diff.strip():
        sys.exit(0)

    print(f"[INFO] Diff size: {len(diff)} characters")
    enc = tiktoken.encoding_for_model(model)
    diff_tokens = len(enc.encode(diff))
    print(f"[INFO] Diff size: {diff_tokens} tokens")

    if len(diff) > 100000:
        print(
            "[WARNING] Diff is too large (>100000 characters). Falling back to 'git diff --cached --name-only'."
        )
        try:
            diff = subprocess.check_output(
                ["git", "diff", "--cached", "--name-only"]
            ).decode()
        except Exception as e:
            print(f"Error getting staged diff file list: {e}")
            sys.exit(1)
        print(f"[INFO] Using file list as diff: {diff.strip()}")

    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            readme = f.read()
    else:
        readme = ""

    print(f"[INFO] README size: {len(readme)} characters")
    enc = tiktoken.encoding_for_model(model)
    readme_tokens = len(enc.encode(readme))
    print(f"[INFO] README size: {readme_tokens} tokens")

    prompt = (
        "You are an expert software documenter. "
        "Suggest additional content or improvements for the following README.md based on these code changes. "
        "Only output new or updated sections, not the full README. "
        "If nothing should be changed, reply with 'NO CHANGES'. "
        "Do NOT consider any prior conversation or chat history—only use the code diff and README below.\n\n"
        f"Code changes:\n{diff}\n\nCurrent README:\n{readme}\n"
    )

    try:
        response = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}]
        )
    except Exception as e:
        print(f"Error from OpenAI API: {e}")
        sys.exit(1)

    ai_suggestion = response.choices[0].message.content.strip()

    if ai_suggestion != "NO CHANGES":
        with open(readme_path, "a") as f:
            f.write("\n\n# AI-suggested enrichment:\n")
            f.write(ai_suggestion)
        subprocess.run(["git", "add", readme_path])
        print(f"{readme_path} enriched and staged with AI suggestions.")
    else:
        print("No enrichment needed for README.md.")


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

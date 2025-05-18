#!/usr/bin/env python3
"""
CLI entry point for AI Commit and README tool.
"""

import argparse
import sys

from .main import enrich, generate_summary
from .evals.readme_eval import evaluate as evaluate_readme
from .evals.wiki_eval import evaluate as evaluate_wiki
from .evals.wiki_eval import evaluate_directory as evaluate_wiki_dir


def main() -> None:
    """
    Command-line interface for the AI Commit and README tool.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="AI Commit and README tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Enrich command
    enrich_parser = subparsers.add_parser("enrich", help="Enrich README and Wiki with AI")
    enrich_parser.add_argument("--summary-only", action="store_true", help="Generate a summary of changes without updating files")

    # Eval README command
    eval_readme_parser = subparsers.add_parser("eval-readme", help="Evaluate README.md quality")
    eval_readme_parser.add_argument("path", help="Path to README.md file")

    # Eval Wiki command
    eval_wiki_parser = subparsers.add_parser("eval-wiki", help="Evaluate Wiki page quality with specialized criteria")
    eval_wiki_parser.add_argument("path", help="Path to Wiki page or directory")
    eval_wiki_parser.add_argument("--dir", action="store_true", help="Evaluate all Wiki pages in directory")
    eval_wiki_parser.add_argument("--type", help="Specify the Wiki page type (api, architecture, changelog, etc.)")
    
    args: argparse.Namespace = parser.parse_args()

    # Set default command if none specified
    if not args.command:
        args.command = "enrich"
        args.summary_only = False

    # Handle each command
    if args.command == "enrich":
        if args.summary_only:
            # Output summary directly to stdout
            sys.stdout.write(generate_summary() + "\n")
        else:
            enrich()

    elif args.command == "eval-readme":
        _, report = evaluate_readme(args.path)
        sys.stdout.write(report + "\n")

    elif args.command == "eval-wiki":
        if args.dir:
            results = evaluate_wiki_dir(args.path)
            for filename, (score, _) in sorted(results.items(), key=lambda x: x[1][0], reverse=True):
                sys.stdout.write(f"{filename}: {score}\n")
            sys.stdout.write(f"\nEvaluated {len(results)} wiki pages\n")
        else:
            _, report = evaluate_wiki(args.path, args.type)
            sys.stdout.write(report + "\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
CLI entry point for AI Commit and README tool.
"""

import argparse
from typing import Any, Callable

from .main import enrich, generate_summary


def main() -> None:
    """
    Command-line interface for the AI Commit and README tool.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="AI Commit and README tool")
    parser.add_argument("command", nargs="?", default="enrich", help="Default command", choices=["enrich"])
    parser.add_argument("--summary-only", action="store_true", help="Generate a summary of changes without updating files")
    args: argparse.Namespace = parser.parse_args()
    
    if args.summary_only:
        # Print summary directly to stdout
        print(generate_summary())
    else:
        command_dispatcher: dict[str, Callable[[], Any]] = {"enrich": enrich}
        command_dispatcher[args.command]()


if __name__ == "__main__":
    main()

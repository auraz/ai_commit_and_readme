#!/usr/bin/env python3
"""
CLI entry point for AI Commit and README tool.
"""

import argparse
from .main import enrich


def main():
    """
    Command-line interface for the AI Commit and README tool.
    """
    parser = argparse.ArgumentParser(description="AI Commit and README tool")
    parser.add_argument("command", nargs="?", default="enrichc", help="Subcommand to run (default: enrich)", choices=["enrich"])

    args = parser.parse_args()

    command_dispatcher = {
        "enrich": lambda: enrich(
            readme_path=args.readme,
            api_key=args.api_key,
            model=args.model,
        ),
    }

    command_dispatcher[args.command]()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
CLI entry point for AI Commit and README tool.
"""

import argparse
from typing import Any, Callable

from .main import enrich


def main() -> None:
    """
    Command-line interface for the AI Commit and README tool.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="AI Commit and README tool")
    parser.add_argument("command", nargs="?", default="enrich", help="Default command", choices=["enrich"])
    args: argparse.Namespace = parser.parse_args()
    command_dispatcher: dict[str, Callable[[], Any]] = {"enrich": enrich}
    command_dispatcher[args.command]()


if __name__ == "__main__":
    main()

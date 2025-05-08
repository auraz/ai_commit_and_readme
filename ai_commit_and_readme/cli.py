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
    parser.add_argument("command", nargs="?", default="enrich", help="Default command", choices=["enrich"])
    args = parser.parse_args()
    command_dispatcher = {"enrich": enrich}
    command_dispatcher[args.command]()


if __name__ == "__main__":
    main()

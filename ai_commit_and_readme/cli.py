#!/usr/bin/env python3
"""
CLI entry point for AI Commit and README tool.
"""
import argparse
from .main import enrich_readme, enrich_wiki, enrich_wiki_auto, enrich_all

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
        choices=["enrich-readme", "enrich-wiki", "enrich-wiki-auto", "enrich-all"],
    )
    parser.add_argument(
        "--readme",
        type=str,
        default="README.md",
        help="Path to README.md (default: README.md)",
    )
    parser.add_argument(
        "--wiki",
        type=str,
        default=None,
        help="Path to wiki markdown file (for enrich-wiki)",
    )
    parser.add_argument(
        "--section",
        type=str,
        default=None,
        help="Section name for README summary (for enrich-wiki)",
    )
    parser.add_argument(
        "--wiki-url",
        type=str,
        default=None,
        help="URL to the wiki page (for enrich-wiki)",
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
    parser.add_argument(
        "--wiki-dir",
        type=str,
        default=None,
        help="Path to wiki directory (for enrich-wiki-auto)",
    )
    parser.add_argument(
        "--wiki-url-base",
        type=str,
        default=None,
        help="Base URL to the wiki (for enrich-wiki-auto, e.g. https://github.com/auraz/ai_commit_and_readme/wiki/)",
    )
    args = parser.parse_args()

    command_dispatcher = {
        "enrich-readme": lambda: enrich_readme(
            readme_path=args.readme, api_key=args.api_key, model=args.model
        ),
        "enrich-wiki": lambda: enrich_wiki(
            wiki_path=args.wiki,
            section=args.section,
            readme_path=args.readme,
            wiki_url=args.wiki_url,
            api_key=args.api_key,
            model=args.model,
        ),
        "enrich-wiki-auto": lambda: enrich_wiki_auto(
            wiki_dir=args.wiki_dir,
            wiki_url_base=args.wiki_url_base,
            readme_path=args.readme,
            api_key=args.api_key,
            model=args.model,
        ),
        "enrich-all": lambda: enrich_all(
            wiki_dir=args.wiki_dir,
            wiki_url_base=args.wiki_url_base,
            readme_path=args.readme,
            api_key=args.api_key,
            model=args.model,
        ),
    }

    command_dispatcher[args.command]()

if __name__ == "__main__":
    main()

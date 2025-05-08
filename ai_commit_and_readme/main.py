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
import glob
from pathlib import Path

WIKI_PROMPT = (
    "You are an expert software documenter. "
    "Suggest additional content or improvements for the following Wiki article based on these code changes. "
    "Only output new or updated sections, not the full article. "
    "If nothing should be changed, reply with 'NO CHANGES'. "
    "Do NOT consider any prior conversation or chat history—only use the code diff and current Wiki content below.\n\n"
    "Code changes:\n{diff}\n\nCurrent Wiki article:\n{wiki}\n"
)
"""
WIKI_PROMPT: Used to instruct the AI to suggest improvements for a Wiki article based on code changes.
"""

README_PROMPT = (
    "You are an expert software documenter. "
    "Suggest additional content or improvements for the following README.md based on these code changes. "
    "Only output new or updated sections, not the full README. "
    "If nothing should be changed, reply with 'NO CHANGES'. "
    "Do NOT consider any prior conversation or chat history—only use the code diff and README below.\n\n"
    "Code changes:\n{diff}\n\nCurrent README:\n{readme}\n"
)
"""
README_PROMPT: Used to instruct the AI to suggest improvements for the README.md based on code changes.
"""

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

def write_wiki_enrichment(ctx):
    """Write AI suggestions to the wiki file and optionally update README with a summary and link."""
    if ctx['ai_suggestion'] != "NO CHANGES":
        # Append to wiki file
        with open(ctx['wiki_path'], "a") as f:
            f.write("\n\n---\n\n# AI-suggested enrichment:\n")
            f.write(ctx['ai_suggestion'])
        print(f"\n[INFO] Wiki page enriched: {ctx['wiki_path']}")
        print(f"\n[INFO] Wiki page enriched: {ctx['wiki_path']}")
        # Optionally update README with summary and link
        if ctx.get('readme_path') and ctx.get('wiki_url') and ctx.get('section'):
            import re
            readme_path = ctx['readme_path']
            wiki_url = ctx['wiki_url']
            section = ctx['section']
            summary = ctx['ai_suggestion'].strip().split('\n\n')[0]
            content = open(readme_path).read()
            pattern = rf"## {section}.*?(?=## |\Z)"
            replacement = f"## {section}\n\n{summary}\n\nSee the [full {section} guide in the Wiki]({wiki_url}).\n"
            new_content, n = re.subn(pattern, replacement, content, flags=re.DOTALL)
            if n == 0:
                new_content = content + f"\n## {section}\n\n{summary}\n\nSee the [full {section} guide in the Wiki]({wiki_url}).\n"
            with open(readme_path, "w") as f:
                f.write(new_content)
            print(f"[INFO] README updated with summary and link to wiki.")
            print(f"[INFO] README updated with summary and link to wiki.")
    else:
        print("No enrichment needed for wiki.")

def enrich_wiki(wiki_path, section, readme_path=None, wiki_url=None, api_key=None, model="gpt-4o"):
    ctx = {
        'wiki_path': wiki_path,
        'section': section,
        'readme_path': readme_path,
        'wiki_url': wiki_url,
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
        write_wiki_enrichment,
    ]:
        ctx = handler(ctx)

def select_wiki_article(ctx):
    """Ask the AI which wiki article to extend based on the diff and README."""
    wiki_dir = ctx['wiki_dir']
    wiki_files = [f for f in glob.glob(f"{wiki_dir}/*.md") if not f.endswith('Home.md')]
    article_list = '\n'.join([os.path.basename(f) for f in wiki_files])
    prompt = (
        f"Here are the available wiki articles (filenames):\n{article_list}\n"
        "Based on the code changes, which article should be extended? Reply with the filename only.\n" +
        AI_ENRICH_PROMPT
        f"Here are the available wiki articles (filenames):\n{article_list}\n"
        "Based on the code changes, which article should be extended? Reply with the filename only.\n" +
        AI_ENRICH_PROMPT
    )
    client = openai.OpenAI(api_key=ctx['api_key'])
    try:
        response = client.chat.completions.create(
            model=ctx['model'], messages=[{"role": "user", "content": prompt}]
        )
    except Exception as e:
        print(f"Error from OpenAI API: {e}")
        sys.exit(1)
    filename = response.choices[0].message.content.strip()
    # Validate filename
    if filename not in [os.path.basename(f) for f in wiki_files]:
        print(f"AI selected invalid wiki article: {filename}. Defaulting to Usage.md.")
        filename = "Usage.md"
    ctx['wiki_path'] = os.path.join(wiki_dir, filename)
    ctx['section'] = os.path.splitext(filename)[0]
    ctx['wiki_url'] = ctx['wiki_url_base'] + filename.replace('.md', '')
    print(f"AI selected wiki article: {filename}")
    return ctx

def enrich_wiki_auto(wiki_dir, wiki_url_base, readme_path="README.md", api_key=None, model="gpt-4o"):
    ctx = {
        'wiki_dir': wiki_dir,
        'wiki_url_base': wiki_url_base,
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
        select_wiki_article,
        ai_enrich,
        write_wiki_enrichment,
    ]:
        ctx = handler(ctx)

def enrich_all(wiki_dir, wiki_url_base, readme_path="README.md", api_key=None, model="gpt-4o"):
    ctx = {
        'wiki_dir': wiki_dir,
        'wiki_url_base': wiki_url_base,
        'readme_path': readme_path,
        'api_key': api_key,
        'model': model,
    }
    # Handler chain up to AI suggestion and wiki selection
    for handler in [
        check_api_key,
        get_diff,
        check_diff_empty,
        print_diff_info,
        fallback_large_diff,
        get_readme,
        print_readme_info,
        select_wiki_article,
        ai_enrich,
    ]:
        ctx = handler(ctx)
    # Write enrichment to wiki
    if ctx['ai_suggestion'] != "NO CHANGES":
        with open(ctx['wiki_path'], "a") as f:
            f.write("\n\n---\n\n# AI-suggested enrichment:\n")
            f.write(ctx['ai_suggestion'])
        print(f"\n[INFO] Wiki page enriched: {ctx['wiki_path']}")
        # Update README with summary and link
        import re
        readme_path = ctx['readme_path']
        wiki_url = ctx['wiki_url']
        section = ctx['section']
        summary = ctx['ai_suggestion'].strip().split('\n\n')[0]
        content = open(readme_path).read()
        pattern = rf"## {section}.*?(?=## |\Z)"
        replacement = f"## {section}\n\n{summary}\n\nSee the [full {section} guide in the Wiki]({wiki_url}).\n"
        new_content, n = re.subn(pattern, replacement, content, flags=re.DOTALL)
        if n == 0:
            new_content = content + f"\n## {section}\n\n{summary}\n\nSee the [full {section} guide in the Wiki]({wiki_url}).\n"
        with open(readme_path, "w") as f:
            f.write(new_content)
        print(f"[INFO] README updated with summary and link to wiki.")
    else:
        print("No enrichment needed for wiki or README.")

def update_wiki(wiki_file, enrichment_text):
    wiki_path = Path(wiki_file)
    content = wiki_path.read_text(encoding='utf-8')
    # Simple append; customize as needed
    content += f"\n\n---\n\n{enrichment_text}\n"
    wiki_path.write_text(content, encoding='utf-8')

def update_readme(readme_file, section, summary, wiki_url):
    readme_path = Path(readme_file)
    content = readme_path.read_text(encoding='utf-8')
    # Replace or insert section with summary and link
    import re
    pattern = rf"## {section}.*?(?=## |\Z)"
    replacement = f"## {section}\n\n{summary}\n\nSee the [full {section} guide in the Wiki]({wiki_url}).\n"
    new_content, n = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if n == 0:
        # Section not found, append at end
        new_content = content + f"\n## {section}\n\n{summary}\n\nSee the [full {section} guide in the Wiki]({wiki_url}).\n"
    readme_path.write_text(new_content, encoding='utf-8')

def enrich_wiki_and_readme_script():
    if len(sys.argv) == 6:
        section, enrichment_file, wiki_file, readme_file, wiki_url = sys.argv[1:6]
        enrichment_text = Path(enrichment_file).read_text(encoding='utf-8')
        # For README, use the first paragraph as summary
        summary = enrichment_text.strip().split('\n\n')[0]
        update_wiki(wiki_file, enrichment_text)
        update_readme(readme_file, section, summary, wiki_url)
        print(f"Updated {wiki_file} and {readme_file} for section '{section}'.")
        sys.exit(0)
    # ... existing code ...

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


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
from .tools import chain_handler, get_prompt_template
from .constants import README_PATH, WIKI_PATH


@chain_handler
def check_api_key(ctx):
    """Check for the presence of the OpenAI API key in context or environment."""
    ctx["api_key"] = ctx.get("api_key") or os.getenv("OPENAI_API_KEY")
    if not ctx["api_key"]:
        print("OPENAI_API_KEY not set. Skipping README update.") or sys.exit(0)

@chain_handler
def get_diff(ctx, diff_args=None):
    """Retrieve the staged git diff (or file list) and store it in context."""
    ctx["diff"] = subprocess.check_output(diff_args or ["git", "diff", "--cached", "-U1"]).decode()

@chain_handler
def check_diff_empty(ctx):
    """Exit if the diff is empty, with a message."""
    if not ctx["diff"].strip():
        print("No staged changes detected. Nothing to enrich.")
        sys.exit(0)

@chain_handler
def print_diff_info(ctx):
    """Print the size of the diff in characters and tokens."""
    print(f"[INFO] Diff size: {len(ctx['diff'])} characters")
    enc = tiktoken.encoding_for_model(ctx["model"])
    diff_tokens = len(enc.encode(ctx["diff"]))
    print(f"[INFO] Diff size: {diff_tokens} tokens")
    ctx["diff_tokens"] = diff_tokens

@chain_handler
def fallback_large_diff(ctx):
    """Fallback to file list if the diff is too large."""
    if len(ctx["diff"]) > 100000:
        print("[WARNING] Diff is too large (>100000 characters). Falling back to 'git diff --cached --name-only'.")
        get_diff(ctx, ["git", "diff", "--cached", "--name-only"])
        print(f"[INFO] Using file list as diff: {ctx['diff'].strip()}")

@chain_handler
def get_file(ctx, file_key, path_key):
    """Read the file at ctx[path_key] and store its contents in ctx[file_key]."""
    path = ctx[path_key]
    ctx[file_key] = open(path).read() if os.path.exists(path) else ""

@chain_handler
def print_file_info(ctx, file_key, model_key):
    """Print the size of the file in characters and tokens."""
    content = ctx[file_key]
    print(f"[INFO] {file_key} size: {len(content)} characters")
    enc = tiktoken.encoding_for_model(ctx[model_key])
    tokens = len(enc.encode(content))
    print(f"[INFO] {file_key} size: {tokens} tokens")
    ctx[f"{file_key}_tokens"] = tokens

def get_ai_response(prompt, model):
    """Return an OpenAI client response for the given prompt and model."""
    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(model=ctx["model"], messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        print(f"Error from OpenAI API: {e}")
        sys.exit(1)
    return response

@chain_handler
def ai_enrich(ctx, file_type, file_var):
    """Call the OpenAI API to get enrichment suggestions for any file."""
    prompt = get_prompt_template('enrich').format(file_type=file_type, file_var=file_var, diff=ctx["diff"], readme=ctx[file_var])
    response = get_ai_response(prompt, ctx["model"])
    ai_suggestion = response.choices[0].message.content.strip()
    ctx["ai_suggestions"][file_var] = ai_suggestion
    return ctx

def select_wiki_articles(ctx):
    """Ask the AI which wiki articles to extend based on the diff, return a list."""
    wiki_files = ctx["wiki_files"]
    article_list = "\n".join(wiki_files)
    prompt = get_prompt_template('select_wiki_articles').format(diff=ctx["diff"], article_list=article_list)
    response = get_ai_response(prompt, ctx["model"])
    filenames = [fn.strip() for fn in response.choices[0].message.content.split(",") if fn.strip()]
    valid_filenames = [fn for fn in filenames if fn in wiki_files]
    if not valid_filenames:
        print("No valid wiki articles selected. Using Usage.md as fallback.")
        valid_filenames = ["Usage.md"]
    ctx["selected_wiki_articles"] = valid_filenames
    return ctx

def enrich_readme(ctx):
    """Enrich the README file with AI suggestions."""
    return ai_enrich(ctx, file_type="README.md", file_var="readme")

def enrich_selected_wikis(ctx):
    """Enrich the selected wiki articles."""
    for filename in ctx["selected_wiki_articles"]:
        suggestion_ctx = ai_enrich(ctx, file_type=filename, file_var=filename)
        ctx["ai_suggestions"]["wiki"][filename] = suggestion_ctx["ai_suggestions"][filename]
    return ctx

def append_suggestion_and_stage(file_path, ai_suggestion, label):
    """Append AI suggestion to file and stage it with git."""
    if ai_suggestion and ai_suggestion != "NO CHANGES":
        with open(file_path, "a") as f:
            f.write(ai_suggestion)
        print(f"{file_path} enriched and staged with AI suggestions for {label}.")
        subprocess.run(["git", "add", file_path])
    else:
        print(f"No enrichment needed for {file_path}.")

def write_enrichment_outputs(ctx):
    """Write AI suggestions to their corresponding files, and update README with wiki summary and link if needed."""
    file_path = ctx["file_paths"]["readme"]
    ai_suggestion = ctx["ai_suggestions"]["readme"]
    append_suggestion_and_stage(file_path, ai_suggestion, "README")
    for filename, ai_suggestion in ctx["ai_suggestions"].get("wiki", {}).items():
        file_path = ctx["file_paths"]["wiki"][filename]
        append_suggestion_and_stage(file_path, ai_suggestion, filename)

def enrich_wiki_and_readme():
    """Handler chain for enriching wiki and readme (multi-wiki support)"""
    for handler in [
        check_api_key,
        get_diff,
        check_diff_empty,
        print_diff_info,
        fallback_large_diff,
        get_file,
        print_file_info,
        select_wiki_articles,  # plural
        enrich_readme,         # enrich README before wikis
        enrich_selected_wikis,
    ]:
        ctx = handler(ctx)
    write_enrichment_outputs(ctx)

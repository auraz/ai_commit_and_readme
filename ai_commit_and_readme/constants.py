import os

WIKI_DIR = os.getenv("WIKI_DIR", "wiki")
README_PATH = os.path.join(os.getcwd(), "README.md")
WIKI_PATH = os.getenv("WIKI_PATH", WIKI_DIR)
API_KEY = os.getenv("OPENAI_API_KEY", None)
WIKI_URL = os.getenv("WIKI_URL", "https://github.com/auraz/ai_commit_and_readme/wiki/")
WIKI_URL_BASE = os.getenv("WIKI_URL_BASE", None)
MODEL = os.getenv("MODEL", "gpt-4-1106-preview")

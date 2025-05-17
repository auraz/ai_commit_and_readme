import os
from typing import Optional

WIKI_DIR: str = os.getenv("WIKI_DIR", "wiki")
README_PATH: str = os.path.join(os.getcwd(), "README.md")
WIKI_PATH: str = os.getenv("WIKI_PATH", WIKI_DIR)
API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
WIKI_URL: str = os.getenv("WIKI_URL", "https://github.com/auraz/ai_commit_and_readme/wiki/")
WIKI_URL_BASE: Optional[str] = os.getenv("WIKI_URL_BASE", None)
MODEL: str = os.getenv("MODEL", "gpt-4-1106-preview")

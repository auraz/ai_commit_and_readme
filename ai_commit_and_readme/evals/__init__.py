"""Evaluation tools for README and Wiki files."""

from .readme_eval import evaluate as evaluate_readme
from .wiki_eval import evaluate as evaluate_wiki
from .wiki_eval import evaluate_directory as evaluate_wiki_dir

__all__ = ["evaluate_readme", "evaluate_wiki", "evaluate_wiki_dir"]

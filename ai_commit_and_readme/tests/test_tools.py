"""Tests for ai_commit_and_readme.tools utility functions."""

from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

import pytest

import ai_commit_and_readme.tools as tools


class TestChainHandler:
    """Tests for the chain_handler decorator."""

    def test_chain_handler_populates_ctx(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """chain_handler should populate context with defaults and call the wrapped function."""

        @tools.chain_handler
        def dummy(ctx: Dict[str, Any]) -> None:
            """Dummy function for testing chain_handler."""
            ctx["touched"] = True

        ctx: Dict[str, Any] = {}
        monkeypatch.setattr(tools, "get_wiki_files", lambda: (["A.md"], {"A.md": "wiki/A.md"}))
        dummy(ctx)
        assert ctx["touched"] is True
        assert "readme_path" in ctx
        assert "wiki_files" in ctx
        assert ctx["wiki_files"] == ["A.md"]
        assert ctx["wiki_file_paths"] == {"A.md": "wiki/A.md"}
        assert ctx["ai_suggestions"] == {"README.md": None, "wiki": None}
        assert ctx["chain_handler_initialized"] is True
        assert ctx["file_paths"]["wiki"] == {"A.md": "wiki/A.md"}


class TestWikiFiles:
    """Tests for get_wiki_files utility function."""

    def test_get_wiki_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_wiki_files should return all markdown files and their paths."""
        wiki_dir: Path = tmp_path / "wiki"
        wiki_dir.mkdir()
        (wiki_dir / "Home.md").write_text("home")
        (wiki_dir / "Other.md").write_text("other")
        monkeypatch.setattr(tools, "WIKI_PATH", str(wiki_dir))
        files: List[str]
        file_paths: Dict[str, str]
        files, file_paths = tools.get_wiki_files()
        assert set(files) == {"Home.md", "Other.md"}
        assert set(file_paths.keys()) == {"Home.md", "Other.md"}
        assert all(str(wiki_dir) in v for v in file_paths.values())


class TestPromptTemplate:
    """Tests for get_prompt_template and prompt template error handling."""

    def test_get_prompt_template(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_prompt_template should extract correct sections from prompt.md."""
        prompt_path: Path = tmp_path / "prompt.md"
        prompt_path.write_text("""
## enrich
enrich section content
## select_articles
select_articles section content
""")
        monkeypatch.setattr(tools, "PROMPT_PATH", str(prompt_path))
        assert "enrich section content" in tools.get_prompt_template("enrich")
        assert "select_articles section content" in tools.get_prompt_template("select_articles")

    def test_get_prompt_template_missing_section(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_prompt_template should raise ValueError if section is missing."""
        prompt_path: Path = tmp_path / "prompt.md"
        prompt_path.write_text("# ---\nOnly one section\n")
        monkeypatch.setattr(tools, "PROMPT_PATH", str(prompt_path))
        with pytest.raises(ValueError):
            tools.get_prompt_template("not_a_section")

    def test_prompt_template_file_not_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_prompt_template should raise RuntimeError if prompt.md is missing."""
        monkeypatch.setattr(tools, "PROMPT_PATH", "nonexistent_prompt.md")
        with pytest.raises(RuntimeError):
            tools.get_prompt_template("enrich")

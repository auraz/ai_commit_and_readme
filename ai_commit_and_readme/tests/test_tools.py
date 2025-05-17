"""Tests for ai_commit_and_readme.tools utility functions."""

from pathlib import Path
from typing import Any

import pytest
from pipetools import pipe

from ai_commit_and_readme.tools import CtxDict
import ai_commit_and_readme.tools as tools


class TestContextInitialization:
    """Tests for the context initialization functions."""

    def test_initialize_context(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """initialize_context should populate context with defaults."""
        ctx: CtxDict = {}
        monkeypatch.setattr(tools, "get_wiki_files", lambda: (["A.md"], {"A.md": "wiki/A.md"}))
        result = tools.initialize_context(ctx)
        assert result is ctx  # Should return the same context object
        assert "readme_path" in ctx
        assert "wiki_files" in ctx
        assert ctx["wiki_files"] == ["A.md"]
        assert ctx["wiki_file_paths"] == {"A.md": "wiki/A.md"}
        assert ctx["ai_suggestions"] == {"README.md": None, "wiki": None}
        assert ctx["context_initialized"] is True
        assert ctx["file_paths"]["wiki"] == {"A.md": "wiki/A.md"}
    
    def test_ensure_initialized_decorator(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """ensure_initialized decorator should initialize context before calling the function."""

        @tools.ensure_initialized
        def dummy(ctx: CtxDict) -> CtxDict:
            """Dummy function for testing ensure_initialized."""
            ctx["touched"] = True
            return ctx

        ctx: CtxDict = {}
        monkeypatch.setattr(tools, "get_wiki_files", lambda: (["A.md"], {"A.md": "wiki/A.md"}))
        result = dummy(ctx)
        assert result is ctx  # Should return the same context object
        assert ctx["touched"] is True
        assert "readme_path" in ctx
        assert ctx["context_initialized"] is True


class TestWikiFiles:
    """Tests for get_wiki_files utility function."""

    def test_get_wiki_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_wiki_files should return all markdown files and their paths."""
        wiki_dir: Path = tmp_path / "wiki"
        wiki_dir.mkdir()
        (wiki_dir / "Home.md").write_text("home")
        (wiki_dir / "Other.md").write_text("other")
        monkeypatch.setattr(tools, "WIKI_PATH", str(wiki_dir))
        files: list[str]
        file_paths: dict[str, str]
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


class TestPipeline:
    """Tests for pipeline functionality."""
    
    def test_pipeline_integration(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that functions can be combined in a pipeline using the pipe operator."""
        # Define test functions for the pipeline
        def step1(ctx: CtxDict) -> CtxDict:
            ctx["step1"] = True
            return ctx
            
        def step2(ctx: CtxDict) -> CtxDict:
            ctx["step2"] = True
            return ctx
        
        # Set up mocks
        monkeypatch.setattr(tools, "get_wiki_files", lambda: (["A.md"], {"A.md": "wiki/A.md"}))
        
        # Execute pipeline using pipe operator
        empty_ctx: CtxDict = {}
        p = pipe | tools.initialize_context | step1 | step2
        result = p(empty_ctx)
        
        # Verify pipeline processed all steps
        assert result["context_initialized"] is True
        assert result["step1"] is True
        assert result["step2"] is True

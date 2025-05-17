"""Tests for ai_commit_and_readme.main handlers, AI logic, and file operations."""

import sys
import uuid
from pathlib import Path
from typing import Any, ClassVar  # For annotating mutable class attributes in tests
from unittest import mock

import pytest
from pytest import LogCaptureFixture, MonkeyPatch

import ai_commit_and_readme.main as mod
from ai_commit_and_readme.tools import CtxDict


# Shared test OpenAI client for mocking
class FakeClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    class chat:  # noqa: N801
        class completions:  # noqa: N801
            @staticmethod
            def create(*args: Any, **kwargs: Any) -> Any:  # noqa: ARG004
                class R:
                    choices: ClassVar = [type("msg", (), {"message": type("msg", (), {"content": "SUGGESTION"})()})]

                return R()


class FakeClientFail(FakeClient):
    class chat(FakeClient.chat):  # noqa: N801
        class completions(FakeClient.chat.completions):  # noqa: N801
            @staticmethod
            def create(*args: Any, **kwargs: Any) -> Any:  # noqa: ARG004
                raise Exception("fail")


def make_ctx(**kwargs: Any) -> CtxDict:
    """Create a test context dictionary with defaults and overrides."""
    ctx: CtxDict = {
        "readme_path": "README.md",
        "api_key": "test",
        "model": "gpt-4o",
        "file_paths": {"README.md": "README.md", "wiki": "wiki"},
        "ai_suggestions": {"README.md": None, "wiki": {}},
        "wiki_files": ["Usage.md"],
        "wiki_file_paths": {"Usage.md": "wiki/Usage.md"},
        "selected_wiki_articles": ["Usage.md"],
        "README.md": "r",  # Add README.md content for ai_enrich
        "Usage.md": "u",  # Add Usage.md content for ai_enrich
        "diff": "sample diff content",  # Add sample diff content
    }
    ctx.update(kwargs)
    return ctx


class TestHandlers:
    """Tests for handler functions in ai_commit_and_readme.main."""

    @pytest.fixture(autouse=True)
    def setup_ctx(self) -> None:
        """Set up a default context for handler tests."""
        self.ctx: CtxDict = make_ctx()

    def test_check_api_key_present(self, monkeypatch: MonkeyPatch) -> None:
        """Should set API key from environment variable."""
        ctx: CtxDict = make_ctx(api_key=None, context_initialized=True)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "test")
        monkeypatch.setattr("ai_commit_and_readme.tools.API_KEY", "test")
        result = mod.check_api_key(ctx)
        assert result["api_key"] == "test"

    def test_check_api_key_missing(self, monkeypatch: MonkeyPatch) -> None:
        """Should exit if API key is missing."""
        ctx: CtxDict = make_ctx(api_key=None, context_initialized=True)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setattr("ai_commit_and_readme.tools.API_KEY", None)
        monkeypatch.setattr("os.getenv", lambda _key, _default=None: None)
        with pytest.raises(SystemExit):
            mod.check_api_key(ctx)

    def test_check_diff_empty_exits(self) -> None:
        """Should exit if diff is empty."""
        ctx: CtxDict = make_ctx(diff="", context_initialized=True)
        with pytest.raises(SystemExit):
            mod.get_diff(ctx)

    def test_get_diff(self, monkeypatch: MonkeyPatch) -> None:
        """Should set diff from subprocess output."""
        ctx: CtxDict = make_ctx(context_initialized=True)
        monkeypatch.setattr(mod.subprocess, "check_output", lambda *_a, **_k: b"diff")
        # Direct call to get_diff with context
        result = mod.get_diff(ctx)
        assert result["diff"] == "diff"

    def test_fallback_large_diff(self, monkeypatch: MonkeyPatch) -> None:
        """Should fallback to file list if diff is too large."""
        ctx: CtxDict = make_ctx(diff="x" * 100001, context_initialized=True)

        # Test the large diff logic in get_diff
        def mock_check_output(cmd):
            if "--name-only" in cmd:
                return b"file1.py\nfile2.py\n"
            return b"x" * 100001

        monkeypatch.setattr(mod.subprocess, "check_output", mock_check_output)
        result = mod.get_diff(ctx)
        assert "file1.py" in result["diff"]

    def test_get_file_reads_correct_content(self, tmp_path: Path) -> None:
        # Create a unique temp file
        test_file: Path = tmp_path / "some_unique_file.md"
        test_content: str = "hello"
        test_file.write_text(test_content)
        ctx: CtxDict = {"context_initialized": True, "model": "gpt-4"}
        # Pass the file path directly
        result = mod.read_file(ctx, "some_unique_file.md", str(test_file))
        assert result["some_unique_file.md"] == test_content

    def test_get_file_not_exists(self, tmp_path: Path) -> None:
        """Should raise FileNotFoundError if file does not exist (matches current get_file implementation)."""
        # Create a non-existent file path
        nonexistent_path = str(tmp_path / f"nonexistent_{uuid.uuid4().hex}.md")
        # Use a key that matches what we're looking up
        filename = "test_file"
        # Initialize context with initialization flag
        ctx: CtxDict = {"context_initialized": True}
        # This should raise FileNotFoundError when trying to open the non-existent file
        with pytest.raises(FileNotFoundError):
            mod.read_file(ctx, filename, nonexistent_path)

    @pytest.mark.parametrize("filename,content", [("README.md", "abc"), ("Usage.md", "abc")])
    def test_file_info_logging(self, monkeypatch: MonkeyPatch, caplog: LogCaptureFixture, filename: str, content: str, tmp_path: Path) -> None:
        """Should log file info and set token count in context."""
        # Create a temp file
        test_file: Path = tmp_path / filename
        test_file.write_text(content)

        ctx: CtxDict = make_ctx(model="gpt-4", context_initialized=True)
        fake_enc: mock.Mock = mock.Mock()
        fake_enc.encode.return_value = [1, 2, 3]
        monkeypatch.setattr("ai_commit_and_readme.main.count_tokens", lambda _text, _model: 3)

        with caplog.at_level("INFO"):
            result = mod.read_file(ctx, filename, str(test_file))

        assert f"Update to {filename} is currently" in caplog.text
        assert f"That's 3 tokens in update to {filename}!" in caplog.text
        assert result[f"{filename}_tokens"] == 3


class TestAIEnrich:
    """Tests for ai_enrich and related AI logic."""

    @pytest.fixture(autouse=True)
    def setup_ctx(self) -> None:
        """Set up a default context for AI enrich tests."""
        self.ctx: CtxDict = make_ctx(diff="d", readme="r")

    def test_ai_enrich_success(self, monkeypatch: MonkeyPatch) -> None:
        """Should set ai_suggestions from OpenAI response."""
        monkeypatch.setattr(
            "ai_commit_and_readme.main.get_ai_response", lambda _prompt, _ctx: type("obj", (), {"choices": [type("obj", (), {"message": type("obj", (), {"content": "SUGGESTION"})()})]})
        )
        self.ctx["README.md"] = "r"
        self.ctx["context_initialized"] = True
        result = mod.ai_enrich(self.ctx, "README.md")
        assert result["ai_suggestions"]["README.md"] == "SUGGESTION"

    def test_ai_enrich_exception(self, monkeypatch: MonkeyPatch) -> None:
        """Should exit on OpenAI API exception."""

        def mock_get_ai_response(*_args, **_kwargs):
            # Simulate the behavior in get_ai_response that calls sys.exit(1)
            sys.exit(1)

        monkeypatch.setattr("ai_commit_and_readme.main.get_ai_response", mock_get_ai_response)
        self.ctx["README.md"] = "r"
        self.ctx["context_initialized"] = True
        with pytest.raises(SystemExit):
            mod.ai_enrich(self.ctx, "README.md")


class TestFileOps:
    """Tests for file operations like append_suggestion_and_stage."""

    def test_append_suggestion_and_stage(self, tmp_path: Path, monkeypatch: MonkeyPatch, caplog: LogCaptureFixture) -> None:
        """Should append suggestion to file and stage it with git."""
        file_path: Path = tmp_path / "README.md"
        file_path.write_text("start")
        called: dict[str, bool] = {}

        def fake_run(_cmd: list[str]) -> None:
            """Fake subprocess.run for git add."""
            called["ran"] = True

        monkeypatch.setattr(mod.subprocess, "run", fake_run)
        with caplog.at_level("INFO"):
            mod.append_suggestion_and_stage(str(file_path), "SUG", "README")
        content = file_path.read_text()
        assert "SUG" in content
        assert called.get("ran")
        assert "enriched and staged" in caplog.text

    def test_append_suggestion_and_stage_no_changes(self, tmp_path: Path, monkeypatch: MonkeyPatch, caplog: LogCaptureFixture) -> None:
        """Should not append or stage if suggestion is "NO CHANGES"."""
        file_path: Path = tmp_path / "README.md"
        file_path.write_text("start")
        called: dict[str, bool] = {}

        def fake_run(_cmd: list[str]) -> None:
            """Fake subprocess.run for git add."""
            called["ran"] = True

        monkeypatch.setattr(mod.subprocess, "run", fake_run)
        with caplog.at_level("INFO"):
            mod.append_suggestion_and_stage(str(file_path), "NO CHANGES", "README")
        content = file_path.read_text()
        assert "NO CHANGES" not in content
        assert "No enrichment needed" in caplog.text
        assert not called.get("ran", False)

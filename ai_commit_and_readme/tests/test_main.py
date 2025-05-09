"""Tests for ai_commit_and_readme.main handlers, AI logic, and file operations."""

import uuid
from typing import ClassVar  # For annotating mutable class attributes in tests
from unittest import mock

import pytest

import ai_commit_and_readme.main as mod


def make_ctx(**kwargs):
    """Create a test context dictionary with defaults and overrides."""
    ctx = {
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
    }
    ctx.update(kwargs)
    return ctx


class TestHandlers:
    """Tests for handler functions in ai_commit_and_readme.main."""

    @pytest.fixture(autouse=True)
    def setup_ctx(self):
        """Set up a default context for handler tests."""
        self.ctx = make_ctx()

    def test_check_api_key_present(self, monkeypatch):
        """Should set API key from environment variable."""
        ctx = make_ctx(api_key=None)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "test")
        monkeypatch.setattr("ai_commit_and_readme.tools.API_KEY", "test")
        mod.check_api_key(ctx)
        assert ctx["api_key"] == "test"

    def test_check_api_key_missing(self, monkeypatch):
        """Should exit if API key is missing."""
        ctx = make_ctx(api_key=None)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setattr("ai_commit_and_readme.tools.API_KEY", None)
        monkeypatch.setattr("os.getenv", lambda _key, _default=None: None)
        with pytest.raises(SystemExit):
            mod.check_api_key(ctx)

    def test_check_diff_empty_exits(self):
        """Should exit if diff is empty."""
        ctx = make_ctx(diff="")
        with pytest.raises(SystemExit):
            mod.check_diff_empty(ctx)

    def test_get_diff(self, monkeypatch):
        """Should set diff from subprocess output."""
        ctx = make_ctx()
        monkeypatch.setattr(mod.subprocess, "check_output", lambda *_a, **_k: b"diff")
        mod.get_diff(ctx)
        assert ctx["diff"] == "diff"

    def test_fallback_large_diff(self, monkeypatch):
        """Should fallback to file list if diff is too large."""
        ctx = make_ctx(diff="x" * 100001)
        monkeypatch.setattr(mod, "get_diff", lambda ctx, _diff_args=None: ctx.update({"diff": "file1.py\nfile2.py\n"}))
        mod.fallback_large_diff(ctx)
        assert "file1.py" in ctx["diff"]

    def test_get_file_reads_correct_content(self, tmp_path):
        # Create a unique temp file
        test_file = tmp_path / "some_unique_file.md"
        test_content = "hello"
        test_file.write_text(test_content)
        ctx = {}
        # Pass the file path directly
        mod.get_file(ctx, "some_unique_file.md", str(test_file))
        assert ctx["some_unique_file.md"] == test_content

    def test_get_file_not_exists(self, tmp_path):
        """Should return empty string if file does not exist."""
        file_path = tmp_path / f"README_{uuid.uuid4().hex}.md"
        ctx = {"README_{uuid.uuid4().hex}.md_path": str(file_path)}
        filename = f"README_{uuid.uuid4().hex}.md"
        ctx[f"{filename}_path"] = str(file_path)
        mod.get_file(ctx, filename, f"{filename}_path")
        assert ctx[filename] == ""

    @pytest.mark.parametrize("filename,model_key,content", [("README.md", "model", "abc"), ("Usage.md", "model", "abc")])
    def test_print_file_info(self, monkeypatch, caplog, filename, model_key, content):
        """Should log file info and set token count in context."""
        ctx = make_ctx(**{filename: content})
        fake_enc = mock.Mock()
        fake_enc.encode.return_value = [1, 2, 3]
        monkeypatch.setattr(mod.tiktoken, "encoding_for_model", lambda _model: fake_enc)
        with caplog.at_level("INFO"):
            mod.print_file_info(ctx, filename, model_key)
        assert f"Update to {filename} is currently" in caplog.text
        assert f"That's 3 tokens in update to {filename}!" in caplog.text
        assert ctx[f"{filename}_tokens"] == 3


class TestAIEnrich:
    """Tests for ai_enrich and related AI logic."""

    @pytest.fixture(autouse=True)
    def setup_ctx(self):
        """Set up a default context for AI enrich tests."""
        self.ctx = make_ctx(diff="d", readme="r")

    def test_ai_enrich_success(self, monkeypatch):
        """Should set ai_suggestions from OpenAI response."""

        class FakeClient:
            class chat:  # noqa: N801
                class completions:  # noqa: N801
                    @staticmethod
                    def create(*args, **kwargs):  # noqa: ARG004
                        class R:
                            # 'choices' is a mutable class attribute, so we annotate it as ClassVar to satisfy linter RUF012
                            choices: ClassVar = [type("msg", (), {"message": type("msg", (), {"content": "SUGGESTION"})()})]

                        return R()

        monkeypatch.setattr(mod.openai, "OpenAI", lambda *args, **kwargs: FakeClient)  # noqa: ARG005
        self.ctx["README.md"] = "r"
        mod.ai_enrich(self.ctx, "README.md")
        assert self.ctx["ai_suggestions"]["README.md"] == "SUGGESTION"

    def test_ai_enrich_exception(self, monkeypatch):
        """Should exit on OpenAI API exception."""

        class FakeClientFail:
            class Chat:
                class Completions:
                    @staticmethod
                    def create(_model, _messages):
                        raise Exception("fail")

        monkeypatch.setattr(mod.openai, "OpenAI", lambda *args, **kwargs: FakeClientFail)  # noqa: ARG005
        self.ctx["README.md"] = "r"
        with pytest.raises(SystemExit):
            mod.ai_enrich(self.ctx, "README.md")


class TestFileOps:
    """Tests for file operations like append_suggestion_and_stage."""

    def test_append_suggestion_and_stage(self, tmp_path, monkeypatch, caplog):
        """Should append suggestion to file and stage it with git."""
        file_path = tmp_path / "README.md"
        file_path.write_text("start")
        called = {}

        def fake_run(_cmd):
            """Fake subprocess.run for git add."""
            called["ran"] = True

        monkeypatch.setattr(mod.subprocess, "run", fake_run)
        with caplog.at_level("INFO"):
            mod.append_suggestion_and_stage(str(file_path), "SUG", "README")
        content = file_path.read_text()
        assert "SUG" in content
        assert called.get("ran")
        assert "enriched and staged" in caplog.text

    def test_append_suggestion_and_stage_no_changes(self, tmp_path, monkeypatch, caplog):
        """Should not append or stage if suggestion is "NO CHANGES"."""
        file_path = tmp_path / "README.md"
        file_path.write_text("start")
        called = {}

        def fake_run(_cmd):
            """Fake subprocess.run for git add."""
            called["ran"] = True

        monkeypatch.setattr(mod.subprocess, "run", fake_run)
        with caplog.at_level("INFO"):
            mod.append_suggestion_and_stage(str(file_path), "NO CHANGES", "README")
        content = file_path.read_text()
        assert "NO CHANGES" not in content
        assert "No enrichment needed" in caplog.text
        assert not called.get("ran", False)

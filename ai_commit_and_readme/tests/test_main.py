import sys
import pytest
from unittest import mock
import ai_commit_and_readme.main as mod

class TestHandlers:
    """Test handler functions in ai_commit_and_readme.main."""
    default_ctx = {'readme_path': 'README.md', 'api_key': 'test', 'model': 'gpt-4o'}

    def setup_method(self):
        """Set up a fresh context before each test."""
        self.ctx = self.default_ctx.copy()

    def test_check_api_key_present(self, monkeypatch):
        """Test that API key is set from environment."""
        monkeypatch.setenv("OPENAI_API_KEY", "test")
        mod.check_api_key(self.ctx)
        assert self.ctx['api_key'] == "test"

    def test_check_api_key_missing(self, monkeypatch):
        """Test that missing API key causes exit."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        self.ctx.pop('api_key', None)  # Remove api_key from ctx
        with pytest.raises(SystemExit):
            mod.check_api_key(self.ctx)

    def test_check_diff_empty_exits(self):
        """Test that empty diff causes exit."""
        self.ctx['diff'] = ''
        with pytest.raises(SystemExit):
            mod.check_diff_empty(self.ctx)

    def test_get_diff(self, monkeypatch):
        """Test that get_diff sets diff from subprocess output."""
        monkeypatch.setattr(mod.subprocess, "check_output", lambda *a, **k: b"diff")
        mod.get_diff(self.ctx)
        assert self.ctx['diff'] == "diff"

    def test_fallback_large_diff(self, monkeypatch):
        """Test fallback to file list if diff is too large."""
        self.ctx['diff'] = 'x' * 100001
        monkeypatch.setattr(mod, "get_diff", lambda ctx, diff_args=None: ctx.update({'diff': 'file1.py\nfile2.py\n'}))
        mod.fallback_large_diff(self.ctx)
        assert "file1.py" in self.ctx['diff']

    def test_get_readme(self, tmp_path):
        """Test reading README file contents and file not exist case."""
        readme = tmp_path / "README.md"
        readme.write_text("hello")
        self.ctx['readme_path'] = str(readme)
        mod.get_readme(self.ctx)
        assert self.ctx['readme'] == "hello"
        # Now test file not exist
        self.ctx['readme_path'] = str(tmp_path / "README_DOES_NOT_EXIST.md")
        mod.get_readme(self.ctx)
        assert self.ctx['readme'] == ""

    def test_print_diff_info(self, monkeypatch, capsys):
        """Test print_diff_info prints and sets diff_tokens."""
        self.ctx['diff'] = 'abc'
        fake_enc = mock.Mock()
        fake_enc.encode.return_value = [1, 2, 3]
        monkeypatch.setattr(mod.tiktoken, "encoding_for_model", lambda model: fake_enc)
        mod.print_diff_info(self.ctx)
        out = capsys.readouterr().out
        assert "[INFO] Diff size:" in out
        assert self.ctx['diff_tokens'] == 3

    def test_print_readme_info(self, monkeypatch, capsys):
        """Test print_readme_info prints and sets readme_tokens."""
        self.ctx['readme'] = 'abc'
        fake_enc = mock.Mock()
        fake_enc.encode.return_value = [1, 2, 3]
        monkeypatch.setattr(mod.tiktoken, "encoding_for_model", lambda model: fake_enc)
        mod.print_readme_info(self.ctx)
        out = capsys.readouterr().out
        assert "[INFO] README size:" in out
        assert self.ctx['readme_tokens'] == 3

    def test_ai_enrich(self, monkeypatch):
        """Test ai_enrich sets ai_suggestion from OpenAI response and handles exception."""
        self.ctx['diff'] = 'd'
        self.ctx['readme'] = 'r'
        # Normal case
        class FakeClient:
            class chat:
                class completions:
                    @staticmethod
                    def create(model, messages):
                        class R:
                            choices = [type("msg", (), {"message": type("msg", (), {"content": "SUGGESTION"})()})]
                        return R()
        monkeypatch.setattr(mod.openai, "OpenAI", lambda api_key: FakeClient)
        mod.ai_enrich(self.ctx)
        assert self.ctx['ai_suggestion'] == "SUGGESTION"
        # Exception case
        class FakeClientFail:
            class chat:
                class completions:
                    @staticmethod
                    def create(model, messages):
                        raise Exception("fail")
        monkeypatch.setattr(mod.openai, "OpenAI", lambda api_key: FakeClientFail)
        with pytest.raises(SystemExit):
            mod.ai_enrich(self.ctx)

    def test_write_enrichment(self, tmp_path, monkeypatch, capsys):
        """Test write_enrichment appends suggestion, stages README, and handles no changes."""
        readme = tmp_path / "README.md"
        readme.write_text("start")
        self.ctx['ai_suggestion'] = 'SUG'
        self.ctx['readme_path'] = str(readme)
        called = {}
        def fake_run(cmd):
            called['ran'] = True
        monkeypatch.setattr(mod.subprocess, "run", fake_run)
        mod.write_enrichment(self.ctx)
        content = readme.read_text()
        assert "SUG" in content
        out = capsys.readouterr().out
        assert "enriched and staged with AI suggestions" in out
        assert called.get('ran')
        # No changes case
        self.ctx['ai_suggestion'] = 'NO CHANGES'
        mod.write_enrichment(self.ctx)
        out = capsys.readouterr().out
        assert "No enrichment needed" in out

class TestCLI:
    """Test CLI and command dispatch logic in ai_commit_and_readme.main."""
    def test_main_enrich_readme(self, monkeypatch):
        """Test main() calls enrich_readme for default command."""
        called = {}
        monkeypatch.setattr(mod, "enrich_readme", lambda **kwargs: called.setdefault("ran", True))
        monkeypatch.setattr(sys, "argv", ["prog", "enrich-readme"])
        mod.main()
        assert called.get("ran")

    def test_main_with_all_args(self, monkeypatch):
        """Test main() passes all CLI args to enrich_readme."""
        called = {}
        def fake_enrich_readme(readme_path, api_key, model):
            called['args'] = (readme_path, api_key, model)
        monkeypatch.setattr(mod, "enrich_readme", fake_enrich_readme)
        monkeypatch.setattr(sys, "argv", [
            "prog", "enrich-readme",
            "--readme", "SOME_README.md",
            "--api-key", "SOME_KEY",
            "--model", "gpt-3.5-turbo"
        ])
        mod.main()
        assert called['args'] == ("SOME_README.md", "SOME_KEY", "gpt-3.5-turbo")

    def test_enrich_readme_chain(self, monkeypatch):
        """Test enrich_readme calls all handler functions in the chain."""
        called = []
        for name in [
            "check_api_key", "get_diff", "check_diff_empty", "print_diff_info",
            "fallback_large_diff", "get_readme", "print_readme_info", "ai_enrich", "write_enrichment"
        ]:
            monkeypatch.setattr(
                mod, name,
                (lambda n: (lambda ctx, *a, **k: (called.append(n), ctx)[1]))(name)
            )
        mod.enrich_readme()
        assert set(called) == {
            "check_api_key", "get_diff", "check_diff_empty", "print_diff_info",
            "fallback_large_diff", "get_readme", "print_readme_info", "ai_enrich", "write_enrichment"
        }

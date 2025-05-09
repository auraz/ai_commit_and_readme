import sys

import ai_commit_and_readme.cli as cli_mod
import ai_commit_and_readme.main as mod
import ai_commit_and_readme.tools as tools_mod
from ai_commit_and_readme.tests.test_main import FakeClient


class TestCLI:
    """Test CLI and command dispatch logic in ai_commit_and_readme.main."""

    def test_cli_enrich_command(self, monkeypatch, tmp_path):
        """Test cli_enrich_command runs without error and updates files."""
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        api_file = wiki_dir / "API.md"
        usage_file = wiki_dir / "Usage.md"
        api_file.write_text("api content")
        usage_file.write_text("usage content")
        readme_path = tmp_path / "README.md"
        readme_path.write_text("readme content")
        # Patch WIKI_PATH and README_PATH
        monkeypatch.setattr(mod, "WIKI_PATH", str(wiki_dir))
        monkeypatch.setattr(mod, "README_PATH", str(readme_path))
        monkeypatch.setattr(tools_mod, "WIKI_PATH", str(wiki_dir))
        monkeypatch.setattr(tools_mod, "README_PATH", str(readme_path))
        monkeypatch.setattr(
            tools_mod,
            "get_wiki_files",
            lambda: (
                ["API.md", "Usage.md"],
                {
                    "API.md": str(api_file),
                    "Usage.md": str(usage_file),
                },
            ),
        )
        # Patch subprocess.run to avoid actual git commands
        monkeypatch.setattr(mod.subprocess, "run", lambda *_a, **_k: None)
        monkeypatch.setattr(mod.subprocess, "check_output", lambda *_a, **_k: b"diff content")
        monkeypatch.setenv("OPENAI_API_KEY", "test")
        monkeypatch.setattr("openai.OpenAI", lambda *args, **kwargs: FakeClient)  # noqa: ARG005
        sys_argv = sys.argv
        sys.argv = ["prog", "enrich"]
        try:
            cli_mod.main()
        finally:
            sys.argv = sys_argv
        # Assert files exist and are readable
        assert api_file.exists()
        assert usage_file.exists()
        assert readme_path.exists()
        assert "api content" in api_file.read_text()
        assert "usage content" in usage_file.read_text()
        assert "readme content" in readme_path.read_text()

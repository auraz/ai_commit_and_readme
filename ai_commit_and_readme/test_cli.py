"""Test main module functionality."""

from . import constants as constants_mod
from . import main as main_mod
from . import tools as tools_mod
from .test_main import FakeClient


class TestMain:
    """Test main module enrichment functionality."""

    def test_enrich_command(self, monkeypatch, tmp_path):
        """Test enrich command runs without error and updates files."""
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        api_file = wiki_dir / "API.md"
        usage_file = wiki_dir / "Usage.md"
        api_file.write_text("api content")
        usage_file.write_text("usage content")
        readme_path = tmp_path / "README.md"
        readme_path.write_text("readme content")

        # Patch WIKI_PATH and README_PATH
        monkeypatch.setattr(constants_mod, "WIKI_PATH", str(wiki_dir))
        monkeypatch.setattr(constants_mod, "README_PATH", str(readme_path))
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
        monkeypatch.setattr("ai_commit_and_readme.tools.subprocess.run", lambda *_a, **_k: None)
        monkeypatch.setattr("ai_commit_and_readme.tools.subprocess.check_output", lambda *_a, **_k: b"diff content")
        monkeypatch.setenv("OPENAI_API_KEY", "test")
        monkeypatch.setattr("openai.OpenAI", lambda *args, **kwargs: FakeClient)

        # Run enrich
        main_mod.enrich()

        # Assert files exist and are readable
        assert api_file.exists()
        assert usage_file.exists()
        assert readme_path.exists()
        assert "api content" in api_file.read_text()
        assert "usage content" in usage_file.read_text()
        assert "readme content" in readme_path.read_text()

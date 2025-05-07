import os
import sys
import pytest
from unittest import mock
import ai_commit_and_readme.main as main_mod

def make_ctx(**kwargs):
    ctx = {'readme_path': 'README.md', 'api_key': 'test', 'model': 'gpt-4o'}
    ctx.update(kwargs)
    return ctx

def test_check_api_key_present(monkeypatch):
    ctx = {}
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    main_mod.check_api_key(ctx)
    assert ctx['api_key'] == "test"

def test_check_api_key_missing(monkeypatch):
    ctx = {}
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(SystemExit):
        main_mod.check_api_key(ctx)

def test_check_diff_empty_exits():
    ctx = {'diff': ''}
    with pytest.raises(SystemExit):
        main_mod.check_diff_empty(ctx)

def test_get_diff(monkeypatch):
    ctx = {}
    monkeypatch.setattr(main_mod.subprocess, "check_output", lambda *a, **k: b"diff")
    main_mod.get_diff(ctx)
    assert ctx['diff'] == "diff"

def test_fallback_large_diff(monkeypatch):
    ctx = {'diff': 'x' * 100001}
    monkeypatch.setattr(main_mod, "get_diff", lambda ctx, diff_args=None: ctx.update({'diff': 'file1.py\nfile2.py\n'}))
    main_mod.fallback_large_diff(ctx)
    assert "file1.py" in ctx['diff']

def test_get_readme(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("hello")
    ctx = {'readme_path': str(readme)}
    main_mod.get_readme(ctx)
    assert ctx['readme'] == "hello"

def test_print_diff_info(monkeypatch, capsys):
    ctx = {'diff': 'abc', 'model': 'gpt-4o'}
    fake_enc = mock.Mock()
    fake_enc.encode.return_value = [1, 2, 3]
    monkeypatch.setattr(main_mod.tiktoken, "encoding_for_model", lambda model: fake_enc)
    main_mod.print_diff_info(ctx)
    out = capsys.readouterr().out
    assert "[INFO] Diff size:" in out
    assert ctx['diff_tokens'] == 3

def test_print_readme_info(monkeypatch, capsys):
    ctx = {'readme': 'abc', 'model': 'gpt-4o'}
    fake_enc = mock.Mock()
    fake_enc.encode.return_value = [1, 2, 3]
    monkeypatch.setattr(main_mod.tiktoken, "encoding_for_model", lambda model: fake_enc)
    main_mod.print_readme_info(ctx)
    out = capsys.readouterr().out
    assert "[INFO] README size:" in out
    assert ctx['readme_tokens'] == 3

def test_ai_enrich(monkeypatch):
    ctx = {'diff': 'd', 'readme': 'r', 'api_key': 'k', 'model': 'gpt-4o'}
    class FakeClient:
        class chat:
            class completions:
                @staticmethod
                def create(model, messages):
                    class R:
                        choices = [type("msg", (), {"message": type("msg", (), {"content": "SUGGESTION"})()})]
                    return R()
    monkeypatch.setattr(main_mod.openai, "OpenAI", lambda api_key: FakeClient)
    main_mod.ai_enrich(ctx)
    assert ctx['ai_suggestion'] == "SUGGESTION"

def test_write_enrichment(tmp_path, monkeypatch):
    readme = tmp_path / "README.md"
    readme.write_text("start")
    ctx = {'ai_suggestion': 'SUG', 'readme_path': str(readme)}
    monkeypatch.setattr(main_mod.subprocess, "run", lambda *a, **k: None)
    main_mod.write_enrichment(ctx)
    content = readme.read_text()
    assert "SUG" in content

def test_write_enrichment_no_changes(capsys):
    ctx = {'ai_suggestion': 'NO CHANGES', 'readme_path': 'README.md'}
    main_mod.write_enrichment(ctx)
    out = capsys.readouterr().out
    assert "No enrichment needed" in out

def test_main_enrich_readme(monkeypatch):
    # Patch enrich_readme to avoid running the full chain
    called = {}
    monkeypatch.setattr(main_mod, "enrich_readme", lambda **kwargs: called.setdefault("ran", True))
    monkeypatch.setattr(sys, "argv", ["prog", "enrich-readme"])
    main_mod.main()
    assert called.get("ran")

def test_enrich_readme_chain(monkeypatch):
    called = []
    for name in [
        "check_api_key", "get_diff", "check_diff_empty", "print_diff_info",
        "fallback_large_diff", "get_readme", "print_readme_info", "ai_enrich", "write_enrichment"
    ]:
        monkeypatch.setattr(
            main_mod, name,
            (lambda n: (lambda ctx, *a, **k: (called.append(n), ctx)[1]))(name)
        )
    main_mod.enrich_readme()
    assert set(called) == {
        "check_api_key", "get_diff", "check_diff_empty", "print_diff_info",
        "fallback_large_diff", "get_readme", "print_readme_info", "ai_enrich", "write_enrichment"
    }

def test_ai_enrich_exception(monkeypatch):
    ctx = {'diff': 'd', 'readme': 'r', 'api_key': 'k', 'model': 'gpt-4o'}
    class FakeClient:
        class chat:
            class completions:
                @staticmethod
                def create(model, messages):
                    raise Exception("fail")
    monkeypatch.setattr(main_mod.openai, "OpenAI", lambda api_key: FakeClient)
    with pytest.raises(SystemExit):
        main_mod.ai_enrich(ctx)

def test_get_readme_file_not_exist(tmp_path):
    # Use a path that does not exist
    readme = tmp_path / "README_DOES_NOT_EXIST.md"
    ctx = {'readme_path': str(readme)}
    main_mod.get_readme(ctx)
    assert ctx['readme'] == ""

def test_main_with_all_args(monkeypatch):
    called = {}
    def fake_enrich_readme(readme_path, api_key, model):
        called['args'] = (readme_path, api_key, model)
    monkeypatch.setattr(main_mod, "enrich_readme", fake_enrich_readme)
    monkeypatch.setattr(sys, "argv", [
        "prog", "enrich-readme",
        "--readme", "SOME_README.md",
        "--api-key", "SOME_KEY",
        "--model", "gpt-3.5-turbo"
    ])
    main_mod.main()
    assert called['args'] == ("SOME_README.md", "SOME_KEY", "gpt-3.5-turbo")

def test_write_enrichment_prints_and_stages(tmp_path, monkeypatch, capsys):
    readme = tmp_path / "README.md"
    readme.write_text("start")
    ctx = {'ai_suggestion': 'SUG', 'readme_path': str(readme)}
    called = {}
    def fake_run(cmd):
        called['ran'] = True
    monkeypatch.setattr(main_mod.subprocess, "run", fake_run)
    main_mod.write_enrichment(ctx)
    out = capsys.readouterr().out
    assert "enriched and staged with AI suggestions" in out
    assert called.get('ran')

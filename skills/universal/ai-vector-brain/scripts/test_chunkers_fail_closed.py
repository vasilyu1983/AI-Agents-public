"""Malformed corpus text must stop chunking before any JSONL is emitted."""

import subprocess
import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent


def test_markdown_chunker_rejects_invalid_utf8_without_partial_output(tmp_path):
    good = tmp_path / "a.md"
    bad = tmp_path / "b.md"
    good.write_text("# Good\nValid text.\n")
    bad.write_bytes(b"# Bad\nInvalid \xff text.\n")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "chunk_markdown.py"), str(good), str(bad)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert result.stdout == ""


def test_mixed_chunker_rejects_invalid_utf8_without_partial_output(tmp_path):
    (tmp_path / "a.md").write_text("# Good\nValid text.\n")
    (tmp_path / "b.sql").write_bytes(b"SELECT \xff;\n")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "chunk_corpus_files.py"), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert result.stdout == ""

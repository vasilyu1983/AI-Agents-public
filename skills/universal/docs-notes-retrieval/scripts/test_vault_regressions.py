"""Small vault fixtures for scanner and context-pack behavior."""

import json
import subprocess
import sys
from pathlib import Path


SCRIPTS = Path(__file__).parent


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_longer_closing_fence_does_not_hide_real_link(tmp_path: Path) -> None:
    (tmp_path / "Note.md").write_text(
        "# Note\n```md\n[[ExampleOnly]]\n````\n[[MissingRealLink]]\n"
    )
    result = run_script("scan_vault.py", "broken-links", str(tmp_path))
    assert result.returncode == 0
    assert json.loads(result.stdout) == [
        {"source": "Note.md", "target": "MissingRealLink"}
    ]


def test_heading_chunk_uses_h2_and_keeps_note_title(tmp_path: Path) -> None:
    (tmp_path / "Decision.md").write_text(
        "---\nstatus: active\n---\n# Decision\n\n## Scope\napproved path\n"
    )
    result = run_script(
        "build_context_pack.py", str(tmp_path), "--notes", "Decision.md",
        "--chunk-strategy", "heading",
    )
    assert result.returncode == 0
    assert "## Decision _(excerpt)_" in result.stdout
    assert "## Scope\napproved path" in result.stdout


def test_broken_link_command_ignores_code_and_resolves_note(tmp_path: Path) -> None:
    (tmp_path / "Existing.md").write_text("# Existing\n")
    (tmp_path / "Note.md").write_text(
        "# Note\n[[Existing]] [[Missing]] `[[InlineExample]]`\n"
    )
    result = run_script("scan_vault.py", "broken-links", str(tmp_path))
    assert result.returncode == 0
    assert json.loads(result.stdout) == [{"source": "Note.md", "target": "Missing"}]


def test_status_filter_drops_superseded_before_packaging(tmp_path: Path) -> None:
    (tmp_path / "Current.md").write_text("---\nstatus: active\n---\n# Current\nneedle\n")
    (tmp_path / "Old.md").write_text("---\nstatus: superseded\n---\n# Old\nneedle\n")
    result = run_script(
        "build_context_pack.py", str(tmp_path), "--query", "needle",
        "--exclude-status", "superseded", "--order-by", "recency",
    )
    assert result.returncode == 0
    assert "**Source:** `Current.md`" in result.stdout
    assert "**Source:** `Old.md`" not in result.stdout
    assert "1 notes dropped" in result.stdout


def test_conflict_group_keeps_both_notes_with_provenance(tmp_path: Path) -> None:
    (tmp_path / "A.md").write_text("# Decision\nUse A\n")
    (tmp_path / "B.md").write_text("# Decision\nUse B\n")
    result = run_script(
        "build_context_pack.py", str(tmp_path), "--notes", "A.md", "B.md"
    )
    assert result.returncode == 0
    assert "## Conflict: Decision vs Decision" in result.stdout
    assert "**Source:** `A.md`" in result.stdout
    assert "**Source:** `B.md`" in result.stdout


def test_explicit_note_symlink_cannot_escape_vault(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\nsecret material\n")
    (vault / "external.md").symlink_to(outside)
    result = run_script(
        "build_context_pack.py", str(vault), "--notes", "external.md"
    )
    assert result.returncode != 0
    assert "outside the vault" in result.stderr
    assert "secret material" not in result.stdout


def test_scanners_reject_vault_symlink_to_outside(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\nsecret material\n")
    (vault / "external.md").symlink_to(outside)
    for name, args in (
        ("scan_vault.py", ("inventory", str(vault))),
        ("build_context_pack.py", (str(vault), "--query", "external")),
    ):
        result = run_script(name, *args)
        assert result.returncode != 0
        assert "outside the vault" in result.stderr
        assert "secret material" not in result.stdout


def test_oversized_heading_chunk_does_not_count_as_included(tmp_path: Path) -> None:
    (tmp_path / "Large.md").write_text("# Large\n" + "x" * 3000)
    result = run_script(
        "build_context_pack.py", str(tmp_path), "--notes", "Large.md",
        "--chunk-strategy", "heading", "--max-chars", "700",
    )
    assert result.returncode != 0
    assert "no notes included" in result.stderr

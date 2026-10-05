"""Regression tests for the local source-catalog validator."""

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_sources.py")


def _run_catalog(tmp_path: Path, entries: list[dict]) -> subprocess.CompletedProcess[str]:
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps(
            {
                "metadata": {
                    "title": "Test",
                    "description": "Test catalog",
                    "last_updated": "2026-01-01",
                    "last_verified": "2026-01-01",
                    "version": "1.0",
                    "skill": "product-help-center",
                },
                "official_docs": entries,
            }
        )
    )
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--path", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_empty_catalog_fails_closed(tmp_path: Path) -> None:
    result = _run_catalog(tmp_path, [])
    assert result.returncode != 0
    assert "source entry" in result.stderr


def test_blank_url_fails_closed(tmp_path: Path) -> None:
    result = _run_catalog(
        tmp_path,
        [
            {
                "name": "Example",
                "url": " ",
                "description": "Example source",
                "source_type": "official_docs",
                "authority": "primary",
                "volatility": "low",
                "status": "active",
                "add_as_web_search": True,
            }
        ],
    )
    assert result.returncode != 0
    assert "URL" in result.stderr

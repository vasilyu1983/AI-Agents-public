#!/usr/bin/env python3
"""Regression: prepare_documents.py must pass through item metadata, backward-compatibly."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("prepare_documents.py")


def run(rows):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--corpus-type", "docs"],
        input="\n".join(json.dumps(r) for r in rows),
        capture_output=True, text=True, check=True,
    )
    return [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]


def test_absent_metadata_is_backward_compatible():
    out = run([{"source_id": "s", "source_uri": "u", "content_hash": "h", "size_bytes": 5}])
    assert out[0]["metadata"] == {"size_bytes": 5}, out[0]["metadata"]


def test_present_metadata_is_merged_and_size_retained():
    row = {
        "source_id": "s", "source_uri": "u", "content_hash": "h", "size_bytes": 5,
        "metadata": {"source_repo": "r", "source_commit_sha": "abc", "symbol_name": "f"},
    }
    md = run([row])[0]["metadata"]
    assert md["size_bytes"] == 5
    assert md["source_repo"] == "r"
    assert md["source_commit_sha"] == "abc"
    assert md["symbol_name"] == "f"


if __name__ == "__main__":
    test_absent_metadata_is_backward_compatible()
    test_present_metadata_is_merged_and_size_retained()
    print("ok")

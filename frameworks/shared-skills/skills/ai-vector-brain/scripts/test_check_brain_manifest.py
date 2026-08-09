#!/usr/bin/env python3
"""Regression checks for vector-brain manifest validation."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("check_brain_manifest.py")


def run_manifest(data):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "brain-manifest.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)


def valid_manifest():
    return {
        "brain_id": "example",
        "backend": "postgres_pgvector",
        "corpus_type": "docs_hub",
        "embedding_model": "openai/text-embedding-3-small@1024",
        "source_roots": ["docs/"],
        "chunking": {"strategy": "heading", "target_tokens": 600, "overlap_tokens": 80},
        "retrieval": {"mode": "hybrid_rrf", "candidate_k": 50, "return_k": 10, "rrf_k": 60},
        "freshness": {"mode": "scheduled_scan", "max_staleness_hours": 168},
        "eval": {"dataset": "evals/docs-retrieval.jsonl", "primary_metric": "recall@10", "min_value": 0.85},
    }


def test_valid_manifest_reports_dimension():
    proc = run_manifest(valid_manifest())
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["embedding_dimension"] == 1024


def test_rejects_todo_embedding_model():
    data = valid_manifest()
    data["embedding_model"] = "TODO: set provider:model:dim before embed_and_load"
    proc = run_manifest(data)
    assert proc.returncode != 0
    assert "invalid_embedding_model" in proc.stdout


def test_rejects_candidate_pool_smaller_than_return_k():
    data = valid_manifest()
    data["retrieval"]["candidate_k"] = 5
    data["retrieval"]["return_k"] = 10
    proc = run_manifest(data)
    assert proc.returncode != 0
    assert "candidate_k_must_be_at_least_return_k" in proc.stdout


if __name__ == "__main__":
    test_valid_manifest_reports_dimension()
    test_rejects_todo_embedding_model()
    test_rejects_candidate_pool_smaller_than_return_k()
    print("ok")

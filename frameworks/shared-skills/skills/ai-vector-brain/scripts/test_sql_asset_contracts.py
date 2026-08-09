#!/usr/bin/env python3
"""Regression checks for ai-vector-brain SQL asset contracts.

These tests cover the portable contract even when a local Postgres fixture with
pgvector and pg_search is not available.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "sql"
REFERENCES = ROOT / "references"


def read(path: Path) -> str:
    return path.read_text()


def executable_sql(text: str) -> str:
    """Return SQL text with line comments removed for simple contract checks."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        lines.append(line)
    return "\n".join(lines)


def test_quantize_rescore_asset_does_not_execute_down_block():
    text = read(ASSETS / "011_quantize_rescore.sql")
    active = executable_sql(text)

    assert "CREATE INDEX idx_embeddings_bq_hnsw" in active
    assert "DROP INDEX IF EXISTS idx_embeddings_bq_hnsw" not in active
    assert "-- DROP INDEX IF EXISTS idx_embeddings_bq_hnsw;" in text


def test_sparsevec_inner_product_orders_by_ascending_distance():
    files = [
        ASSETS / "010_sparsevec.sql",
        REFERENCES / "learned-sparse-splade-leg.md",
    ]

    for path in files:
        text = read(path)
        assert "query_sparse_vec IS NOT NULL" in text, path
        assert "<#> query_sparse_vec ASC" in text, path
        assert "<#> query_sparse_vec DESC" not in text, path


def test_paradedb_bm25_examples_use_current_api_and_safe_query_binding():
    files = [
        ASSETS / "009_bm25_pg_search.sql",
        REFERENCES / "bm25-when-ts_rank-isnt-enough.md",
    ]

    for path in files:
        text = read(path)
        assert "pdb.score(id)" in text, path
        assert "content ||| query_text" in text, path
        assert "paradedb.score" not in text, path
        assert "paradedb.parse" not in text, path
        assert "' || query_text || '" not in text, path


if __name__ == "__main__":
    test_quantize_rescore_asset_does_not_execute_down_block()
    test_sparsevec_inner_product_orders_by_ascending_distance()
    test_paradedb_bm25_examples_use_current_api_and_safe_query_binding()
    print("ok")

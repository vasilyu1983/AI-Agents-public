#!/usr/bin/env python3
"""Regression checks for ai-vector-brain SQL asset contracts.

These tests cover the portable contract even when a local Postgres fixture with
pgvector and pg_search is not available.
"""
import re
import unittest
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


def uncommented_sql(text: str) -> str:
    """Return SQL text with leading `--` markers stripped.

    Paste-ready query examples live in comment blocks (011's two-pass query,
    010's sparse leg). Stripping the markers lets the contract checks read
    those examples as SQL, so a commented recipe cannot dodge them.
    """
    return "\n".join(re.sub(r"^\s*--", "", line) for line in text.splitlines())


def sql_statements(text: str) -> list[str]:
    return [stmt for stmt in text.split(";") if stmt.strip()]


EMBEDDINGS_READ = re.compile(r"\b(?:FROM|JOIN)\s+embeddings\b", re.IGNORECASE)
# 003's deny-by-default predicate shape: public, or a non-NULL caller scope
# that shares a key with the chunk's acl_scope.
ACL_PREDICATE = re.compile(
    r"is_public\s*=\s*TRUE\s+OR\s+\(\s*:?\w+\s+IS\s+NOT\s+NULL\s+AND\s+\w+\.acl_scope\s*\?\|",
    re.IGNORECASE,
)
MODEL_FILTER = re.compile(r"\bmodel_id\s*=\s*[:\w']", re.IGNORECASE)
CTE_START = re.compile(r"\b(\w+)\s+AS\s*(?:NOT\s+)?(?:MATERIALIZED\s+)?\(", re.IGNORECASE)


def cte_spans(stmt: str) -> dict[str, tuple[int, int, str]]:
    """Map each CTE name to (start, end, body) using balanced parentheses."""
    spans = {}
    for m in CTE_START.finditer(stmt):
        depth, i = 1, m.end()
        while i < len(stmt) and depth:
            depth += {"(": 1, ")": -1}.get(stmt[i], 0)
            i += 1
        spans[m.group(1).lower()] = (m.start(), i, stmt[m.end():i - 1])
    return spans


def acl_reaches_embeddings_read(stmt: str) -> bool:
    """True when the query block that reads `embeddings` applies the ACL
    predicate itself or reads from a CTE that does. A statement that merely
    defines an ACL CTE somewhere, but reads embeddings without joining it,
    is fail-open and returns False."""
    spans = cte_spans(stmt)
    acl_ctes = {n for n, (_, _, body) in spans.items() if ACL_PREDICATE.search(body)}
    holders = [body for _, _, body in spans.values() if EMBEDDINGS_READ.search(body)]
    if holders:
        scope = min(holders, key=len)
    else:  # read sits in the main query: drop every CTE definition first
        scope, cut = stmt, sorted((a, b) for a, b, _ in spans.values())
        for a, b in reversed(cut):
            scope = scope[:a] + scope[b:]
    if ACL_PREDICATE.search(scope):
        return True
    return any(re.search(rf"\b{re.escape(n)}\b", scope, re.IGNORECASE) for n in acl_ctes)


def embeddings_read_violations(assets_dir: Path | None = None) -> list[str]:
    """List every SQL statement (live or in a comment example) that reads
    `embeddings` without the deny-by-default ACL predicate or a model_id
    filter. Returns an empty list when every asset complies."""
    problems = []
    for path in sorted((assets_dir or ASSETS).glob("*.sql")):
        for stmt in sql_statements(uncommented_sql(read(path))):
            if not EMBEDDINGS_READ.search(stmt):
                continue
            head = " ".join(EMBEDDINGS_READ.search(stmt).group(0).split())
            if not acl_reaches_embeddings_read(stmt):
                problems.append(f"{path.name}: reads embeddings without the ACL predicate: {head}")
            if not MODEL_FILTER.search(stmt):
                problems.append(f"{path.name}: reads embeddings without a model_id filter: {head}")
    return problems


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


def test_acl_is_deny_by_default_not_fail_open():
    """001/003 must deny access for an empty or NULL ACL scope, never treat it
    as public. Guards against regressing to the fail-open default the auditor
    found (`acl_scope = '{}'` or `p_acl_scope IS NULL` treated as unfiltered).
    """
    schema = read(ASSETS / "001_schema.sql")
    fn = executable_sql(read(ASSETS / "003_hybrid_search_function.sql"))

    # 001: chunks must carry an explicit public flag, defaulting closed.
    assert "is_public BOOLEAN NOT NULL DEFAULT FALSE" in schema

    # 003: the ACL predicate must gate on is_public / a non-NULL scope match,
    # and must NOT contain the old fail-open shortcuts.
    assert "c.is_public = TRUE" in fn
    assert "p_acl_scope IS NOT NULL" in fn
    assert "c.acl_scope = '{}'::jsonb" not in fn, (
        "regression: empty acl_scope must not be treated as public"
    )
    assert not re.search(r"p_acl_scope\s+IS\s+NULL\s+OR", fn, re.IGNORECASE), (
        "regression: NULL p_acl_scope must not bypass the ACL filter"
    )


def test_existing_chunks_gain_public_flag_before_hybrid_function():
    """Rerunning 001 on an older chunks table must add the closed ACL flag.

    CREATE TABLE IF NOT EXISTS alone leaves old tables unchanged; 003 then
    references a missing column. This checks the documented upgrade ordering,
    not execution against PostgreSQL.
    """
    schema = executable_sql(read(ASSETS / "001_schema.sql"))
    create = schema.index("CREATE TABLE IF NOT EXISTS chunks")
    upgrade = schema.index("ALTER TABLE chunks ADD COLUMN IF NOT EXISTS is_public BOOLEAN NOT NULL DEFAULT FALSE")
    assert create < upgrade


def test_every_embeddings_read_carries_acl_and_model_filters():
    """Every SQL asset that selects from `embeddings` -- including paste-ready
    examples kept in comments -- must apply 003's deny-by-default ACL
    predicate (in the query block that reads embeddings, or in a CTE that
    block reads from) and a model_id filter. 011's two-pass
    query once read `FROM embeddings` with neither, which the 001/003-only
    check above could not see."""
    problems = embeddings_read_violations()
    assert not problems, "\n".join(problems)


def test_vector_dimensions_match_schema():
    """bit(N)/vector(N)/halfvec(N) in the query assets must equal the
    dimension of embeddings.embedding in 001 (011 once used bit(1536)
    against the 1024 default)."""
    schema = read(ASSETS / "001_schema.sql")
    dim = re.search(r"embedding\s+vector\((\d+)\)", schema).group(1)
    for name in ("003_hybrid_search_function.sql", "005_eval_tables.sql", "011_quantize_rescore.sql"):
        text = read(ASSETS / name)
        found = set(re.findall(r"\b(?:bit|vector|halfvec)\((\d+)\)", text))
        assert found <= {dim}, f"{name}: dimensions {sorted(found)} != schema {dim}"


def test_hnsw_indexes_are_partial_per_model():
    """002 and 011 must build one HNSW index per model_id, not one index over
    every model's vectors."""
    for name in ("002_indexes_hnsw.sql", "011_quantize_rescore.sql"):
        for stmt in sql_statements(executable_sql(read(ASSETS / name))):
            if re.search(r"USING\s+hnsw", stmt, re.IGNORECASE):
                assert re.search(r"\bWHERE\s+model_id\s*=", stmt, re.IGNORECASE), (
                    f"{name}: HNSW index is not partial on model_id"
                )


def test_hybrid_function_has_leg_weights_defaulting_to_plain_rrf():
    fn = executable_sql(read(ASSETS / "003_hybrid_search_function.sql"))
    assert re.search(r"lexical_weight\s+DOUBLE PRECISION\s+DEFAULT\s+1\.0", fn)
    assert re.search(r"vector_weight\s+DOUBLE PRECISION\s+DEFAULT\s+1\.0", fn)
    assert "sum(leg_weight / (rrf_k + rank))" in fn
    # The 14-argument signature (before the weights) must be dropped, or
    # positional callers keep the unweighted overload.
    assert re.search(r"TIMESTAMPTZ,\s*TEXT\[\],\s*REGCONFIG\s*\)", fn)


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


class SqlAssetContractTests(unittest.TestCase):
    """unittest entry point so `python3 -m unittest` runs the same checks."""

    def test_quantize_rescore(self):
        test_quantize_rescore_asset_does_not_execute_down_block()

    def test_sparsevec_order(self):
        test_sparsevec_inner_product_orders_by_ascending_distance()

    def test_acl_deny_by_default(self):
        test_acl_is_deny_by_default_not_fail_open()

    def test_existing_chunks_public_flag_upgrade(self):
        test_existing_chunks_gain_public_flag_before_hybrid_function()

    def test_embeddings_reads_filtered(self):
        test_every_embeddings_read_carries_acl_and_model_filters()

    def test_vector_dimensions(self):
        test_vector_dimensions_match_schema()

    def test_hnsw_partial_per_model(self):
        test_hnsw_indexes_are_partial_per_model()

    def test_leg_weights(self):
        test_hybrid_function_has_leg_weights_defaulting_to_plain_rrf()

    def test_paradedb_bm25(self):
        test_paradedb_bm25_examples_use_current_api_and_safe_query_binding()


if __name__ == "__main__":
    unittest.main()

"""Offline CLI regressions; RAG_SCRIPT_ROOT selects saved pre-fix scripts."""

import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT_ROOT = Path(os.environ.get("RAG_SCRIPT_ROOT", Path(__file__).resolve().parent))


def run_cli(tmp_path, script, rows, *options):
    path = tmp_path / "input.jsonl"
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    args = ["--input", str(path)] if script == "late_interaction_eval.py" else [str(path)]
    return subprocess.run([sys.executable, str(SCRIPT_ROOT / script), *args, *options], capture_output=True, text=True)


def retrieval(**updates):
    return {"expected_ids": ["doc-a", "doc-b"], "retrieved_ids": ["doc-a"], **updates}


def late(**updates):
    return {"query_id": "q-a", "query": "Synthetic question", "relevant_doc_ids": ["doc-a", "doc-b"],
            "ranked_results": [{"doc_id": "doc-a", "score": 1.0}], **updates}


def citation(**updates):
    return {"citations": ["doc-a"], "evidence": [{"id": "doc-a"}],
            "claims": [{"citations": ["doc-a"]}], **updates}


def test_late_ndcg_includes_unretrieved_gold(tmp_path):
    result = run_cli(tmp_path, "late_interaction_eval.py", [late()], "--k", "2")
    assert result.returncode == 0, result.stderr
    expected = 1 / (1 + 1 / math.log2(3))
    assert f"{expected:.4f}" in result.stdout
    assert "Recall@2: 0.5000" in result.stdout


@pytest.mark.parametrize("bad", [
    {"expected_ids": ["doc-a"]},
    retrieval(retrieved_ids=["doc-a", "doc-a"]),
    retrieval(expected_ids=["doc-a", "doc-a"]),
    retrieval(retrieved_ids=[None]),
    retrieval(graded_relevance={"doc-a": float("nan"), "doc-b": 1}),
    retrieval(graded_relevance={"doc-a": -1, "doc-b": 1}),
    retrieval(graded_relevance={"doc-a": "3", "doc-b": 1}),
    retrieval(graded_relevance={"doc-a": 1}),
])
def test_retrieval_invalid_row_blocks_whole_batch(tmp_path, bad):
    result = run_cli(tmp_path, "retrieval_eval.py", [retrieval(), bad], "--k", "2")
    assert result.returncode == 2
    assert "ERROR:" in result.stderr
    assert "recall=" not in result.stdout


@pytest.mark.parametrize("script,options", [
    ("retrieval_eval.py", ("--k", "0")),
    ("retrieval_eval.py", ("--k", "-1")),
    ("retrieval_eval.py", ("--k", "")),
    ("late_interaction_eval.py", ("--k", "0")),
    ("late_interaction_eval.py", ("--k", "-1")),
])
def test_invalid_cutoff_fails_closed(tmp_path, script, options):
    row = late() if script.startswith("late") else retrieval()
    result = run_cli(tmp_path, script, [row], *options)
    assert result.returncode == 2
    assert "positive" in result.stderr
    assert not result.stdout


@pytest.mark.parametrize("bad", [
    late(ranked_results=[{"doc_id": "doc-a"}, {"doc_id": "doc-a"}]),
    late(relevant_doc_ids=["doc-a", None]),
    late(ranked_results=[{"doc_id": "doc-a", "score": float("nan")}]),
])
def test_late_invalid_record_blocks_batch(tmp_path, bad):
    result = run_cli(tmp_path, "late_interaction_eval.py", [late(), bad])
    assert result.returncode == 2
    assert "nothing scored" in result.stderr
    assert not result.stdout


def test_claim_citation_target_is_checked(tmp_path):
    result = run_cli(tmp_path, "check_citation_support.py",
                     [citation(claims=[{"citations": ["invented-id"]}])], "--require-claim-citations")
    assert result.returncode == 1
    assert "rows_with_missing_citation_targets=1" in result.stdout


@pytest.mark.parametrize("bad", [
    {}, citation(citations="doc-a"), citation(claims=["malformed"]),
    citation(claims=[{"citations": "doc-a"}]), citation(evidence=[{"id": None}]),
])
def test_citation_invalid_record_blocks_batch(tmp_path, bad):
    result = run_cli(tmp_path, "check_citation_support.py", [citation(), bad], "--require-claim-citations")
    assert result.returncode == 2
    assert "ERROR:" in result.stderr
    assert not result.stdout


def test_valid_controls_and_no_answer_exclusion(tmp_path):
    result = run_cli(tmp_path, "retrieval_eval.py", [retrieval(), retrieval(expected_ids=[], retrieved_ids=[])], "--k", "2")
    assert result.returncode == 0
    assert "scored=1 skipped=1" in result.stdout
    assert "recall=0.5000 mrr=1.0000 ndcg=0.6131" in result.stdout
    result = run_cli(tmp_path, "check_citation_support.py", [citation()], "--require-claim-citations")
    assert result.returncode == 0
    result = run_cli(tmp_path, "check_citation_support.py", [citation(claims=[{"citations": []}])], "--require-claim-citations")
    assert result.returncode == 1
    assert "rows_with_uncited_claims=1" in result.stdout


def test_late_invalid_utf8_is_named_input_error(tmp_path):
    path = tmp_path / "invalid.jsonl"
    path.write_bytes(b"\xff\n")
    result = subprocess.run([sys.executable, str(SCRIPT_ROOT / "late_interaction_eval.py"), "--input", str(path)],
                            capture_output=True, text=True)
    assert result.returncode == 2
    assert str(path) in result.stderr
    assert "Traceback" not in result.stderr


def test_late_unwritable_output_is_named_error(tmp_path):
    result = run_cli(tmp_path, "late_interaction_eval.py", [late()], "--output", str(tmp_path))
    assert result.returncode == 2
    assert str(tmp_path) in result.stderr
    assert "Traceback" not in result.stderr


def test_forbidden_ids_fail_even_on_no_answer_rows(tmp_path):
    leak = retrieval(expected_ids=[], retrieved_ids=["doc-restricted"], forbidden_ids=["doc-restricted"])
    stale = retrieval(retrieved_ids=["doc-a", "doc-old"], forbidden_ids=["doc-old"])
    result = run_cli(tmp_path, "retrieval_eval.py", [leak, stale], "--k", "1,2")
    assert result.returncode == 1
    assert "forbidden_rows=2" in result.stdout
    assert "k=1 recall=0.5000 mrr=1.0000 ndcg=1.0000 forbidden_hit_rows=1" in result.stdout
    assert "k=2 recall=0.5000 mrr=1.0000 ndcg=0.6131 forbidden_hit_rows=2" in result.stdout
    clean = retrieval(forbidden_ids=["doc-old"])
    assert run_cli(tmp_path, "retrieval_eval.py", [clean], "--k", "2").returncode == 0
    both = retrieval(forbidden_ids=["doc-a"])
    assert run_cli(tmp_path, "retrieval_eval.py", [both], "--k", "2").returncode == 2

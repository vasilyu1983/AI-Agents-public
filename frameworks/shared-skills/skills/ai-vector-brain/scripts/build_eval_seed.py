#!/usr/bin/env python3
"""Create a starter eval JSONL from chunk JSONL for human labeling.

Generates corpus-type-aware seed queries so the labeler starts from a
realistic prompt, not a trivial 'Find the section about X' template.

The output is a starter set: every record requires a human pass to set
`expected_evidence_ids`, refine the query, and confirm the metric focus.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

CORPUS_TYPES = ("repo", "docs_hub", "compliance_policy")


def _repo_queries(chunk: dict, idx: int) -> list[dict]:
    """Repo brain: exact-path, symbol, blast-radius, refusal."""
    section = chunk.get("section_path") or ""
    symbol = chunk.get("symbol_name")
    path = chunk.get("source_path") or ""
    out: list[dict] = []
    if symbol:
        out.append({
            "query": f"Where is {symbol} defined?",
            "metric_focus": "symbol_recall@5",
        })
        out.append({
            "query": f"What calls {symbol}?",
            "metric_focus": "blast_radius_recall@10",
        })
    if path:
        out.append({
            "query": f"Show the implementation in {path}",
            "metric_focus": "path_recall@5",
        })
    if section:
        out.append({
            "query": f"How does {section.split('/')[-1]} work?",
            "metric_focus": "module_recall@10",
        })
    out.append({
        "query": f"How is {symbol or section or path or 'this module'} tested?",
        "metric_focus": "test_link_recall@10",
    })
    return out


def _docs_queries(chunk: dict, idx: int) -> list[dict]:
    """Docs hub brain: navigation, paraphrase, freshness, refusal."""
    section = chunk.get("section_path") or chunk.get("source_path") or "this topic"
    short = section.split("/")[-1].split("#")[-1].replace("-", " ").replace("_", " ")
    return [
        {"query": f"Where is the canonical doc on {short}?", "metric_focus": "recall@10"},
        {"query": f"How does {short} work in this system?", "metric_focus": "answer_relevancy"},
        {"query": f"What is the most recent guidance on {short}?", "metric_focus": "freshness_correctness"},
        {"query": f"Are there conflicting docs about {short}?", "metric_focus": "duplicate_detection"},
    ]


def _policy_queries(chunk: dict, idx: int) -> list[dict]:
    """Compliance/policy brain: applicability, effective-time, refusal, conflict."""
    clause = (chunk.get("metadata") or {}).get("clause_id") or chunk.get("citation_anchor") or ""
    section = chunk.get("section_path") or "this obligation"
    short = section.split("/")[-1].split("#")[-1].replace("-", " ").replace("_", " ")
    return [
        {"query": f"What policy covers {short}?", "metric_focus": "citation_precision"},
        {"query": f"Which version of {clause or short} was effective on 2024-06-30?", "metric_focus": "effective_time_correctness"},
        {"query": f"What obligations apply to {short} for an EMI in the UK?", "metric_focus": "applicability_recall"},
        {"query": f"Does anything conflict with {clause or short}?", "metric_focus": "conflict_detection"},
        {"query": f"Show me a regulator letter requiring something not in our policies for {short}.", "metric_focus": "refusal_correctness"},
    ]


def _generate(corpus_type: str, chunk: dict, idx: int) -> list[dict]:
    if corpus_type == "repo":
        return _repo_queries(chunk, idx)
    if corpus_type == "docs_hub":
        return _docs_queries(chunk, idx)
    if corpus_type == "compliance_policy":
        return _policy_queries(chunk, idx)
    raise SystemExit(f"unknown corpus type: {corpus_type!r}; expected one of {CORPUS_TYPES}")


def _emit(corpus_type: str, chunks: Iterable[dict], limit: int) -> int:
    written = 0
    for idx, chunk in enumerate(chunks, start=1):
        if written >= limit:
            break
        for q in _generate(corpus_type, chunk, idx):
            if written >= limit:
                break
            record = {
                "id": f"{corpus_type}-{written + 1:03d}",
                "query": q["query"],
                "metric_focus": q["metric_focus"],
                "expected_evidence_ids": [],
                "candidate_source_path": chunk.get("source_path"),
                "candidate_anchor": chunk.get("anchor") or chunk.get("citation_anchor"),
                "needs_human_label": True,
            }
            print(json.dumps(record, ensure_ascii=False))
            written += 1
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chunks", nargs="?", type=Path, help="JSONL of chunks (stdin if omitted)")
    parser.add_argument("--corpus-type", required=True, choices=CORPUS_TYPES)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    stream = args.chunks.open() if args.chunks else sys.stdin

    def _iter() -> Iterable[dict]:
        with stream:
            for line in stream:
                if not line.strip():
                    continue
                yield json.loads(line)

    n = _emit(args.corpus_type, _iter(), args.limit)
    print(f"# wrote {n} seed queries (corpus_type={args.corpus_type})", file=sys.stderr)


if __name__ == "__main__":
    main()

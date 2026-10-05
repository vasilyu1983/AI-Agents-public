#!/usr/bin/env python3
"""Validate a vector-brain manifest.

The validator is intentionally dependency-free so examples and generated
scaffolds can be checked in CI without a JSON Schema package.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED = {
    "brain_id",
    "backend",
    "corpus_type",
    "embedding_model",
    "source_roots",
    "chunking",
    "retrieval",
    "freshness",
    "eval",
}

BACKENDS = {
    "postgres_pgvector",
    "pgvector",
    "qdrant",
    "weaviate",
    "milvus",
    "vespa",
    "lancedb",
    "chroma",
    "opensearch",
    "elasticsearch",
    "pinecone_serverless",
    "turbopuffer",
    "s3_vectors",
    "azure_ai_search",
    "vertex_ai_vector_search",
    "bedrock_knowledge_bases",
    "openai_file_search",
    "embedded_local",
}

CORPUS_TYPES = {
    "repo",
    "docs",
    "docs_hub",
    "compliance_policy",
    "policy",
    "support_kb",
    "note_vault",
    "dev_context_hub",
}

RETRIEVAL_MODES = {
    "hybrid_rrf",
    "graph_bounded_hybrid",
    "graph_bounded_hybrid_rrf",
    "vector",
    "lexical",
    "bm25_hybrid",
    "sparse_dense_hybrid",
}

FRESHNESS_MODES = {
    "git_diff",
    "scheduled_scan",
    "reviewed_release",
    "git_anchored_incremental",
    "manual",
}

EMBEDDING_RE = re.compile(r"^[A-Za-z0-9_.:/-]+@(?P<dim>[1-9][0-9]{1,4})$")


def error(errors: list[dict], code: str, **fields) -> None:
    errors.append({"error": code, **fields})


def require_object(errors: list[dict], data: dict, key: str) -> dict:
    value = data.get(key)
    if not isinstance(value, dict):
        error(errors, f"{key}_must_be_object")
        return {}
    return value


def require_positive_int(errors: list[dict], obj: dict, key: str, owner: str) -> None:
    value = obj.get(key)
    if not isinstance(value, int) or value <= 0:
        error(errors, "positive_integer_required", field=f"{owner}.{key}", value=value)


def embedding_dimension(value: object) -> int | None:
    if not isinstance(value, str):
        return None
    match = EMBEDDING_RE.match(value)
    if not match:
        return None
    dim = int(match.group("dim"))
    if dim > 4000:
        return None
    return dim


def validate(data: dict) -> list[dict]:
    errors: list[dict] = []
    missing = sorted(REQUIRED - set(data))
    if missing:
        error(errors, "missing_required_fields", fields=missing)

    if data.get("backend") not in BACKENDS:
        error(errors, "unknown_backend", value=data.get("backend"), allowed=sorted(BACKENDS))
    if data.get("corpus_type") not in CORPUS_TYPES:
        error(errors, "unknown_corpus_type", value=data.get("corpus_type"), allowed=sorted(CORPUS_TYPES))

    dim = embedding_dimension(data.get("embedding_model"))
    if dim is None:
        error(
            errors,
            "invalid_embedding_model",
            expected="provider/model@dimension or model@dimension, dimension 10-4000",
            value=data.get("embedding_model"),
        )

    if not isinstance(data.get("source_roots"), list) or not data.get("source_roots"):
        error(errors, "source_roots_must_be_non_empty_list")
    elif not all(isinstance(root, str) and root for root in data["source_roots"]):
        error(errors, "source_roots_must_contain_strings")

    if "source_excludes" in data and (
        not isinstance(data["source_excludes"], list)
        or not all(isinstance(item, str) and item for item in data["source_excludes"])
    ):
        error(errors, "source_excludes_must_be_string_list")

    chunking = require_object(errors, data, "chunking")
    if chunking:
        if not any(key in chunking for key in ("strategy", "unit")):
            error(errors, "chunking_needs_strategy_or_unit")
        for key in ("target_tokens", "max_tokens"):
            if key in chunking:
                require_positive_int(errors, chunking, key, "chunking")
        if "overlap_tokens" in chunking:
            value = chunking["overlap_tokens"]
            if not isinstance(value, int) or value < 0:
                error(errors, "non_negative_integer_required", field="chunking.overlap_tokens", value=value)

    retrieval = require_object(errors, data, "retrieval")
    if retrieval:
        mode = retrieval.get("mode")
        if mode not in RETRIEVAL_MODES:
            error(errors, "unknown_retrieval_mode", value=mode, allowed=sorted(RETRIEVAL_MODES))
        for key in ("candidate_k", "return_k", "top_k", "candidates"):
            if key in retrieval:
                require_positive_int(errors, retrieval, key, "retrieval")
        if "candidate_k" in retrieval and "return_k" in retrieval and retrieval["candidate_k"] < retrieval["return_k"]:
            error(errors, "candidate_k_must_be_at_least_return_k")
        if "candidates" in retrieval and "top_k" in retrieval and retrieval["candidates"] < retrieval["top_k"]:
            error(errors, "candidates_must_be_at_least_top_k")
        if "rrf_k" in retrieval and not isinstance(retrieval["rrf_k"], (int, float)):
            error(errors, "numeric_required", field="retrieval.rrf_k", value=retrieval["rrf_k"])

    freshness = require_object(errors, data, "freshness")
    if freshness:
        mode = freshness.get("mode", freshness.get("strategy"))
        if mode not in FRESHNESS_MODES:
            error(errors, "unknown_freshness_mode", value=mode, allowed=sorted(FRESHNESS_MODES))
        if "max_staleness_hours" in freshness:
            require_positive_int(errors, freshness, "max_staleness_hours", "freshness")

    eval_block = require_object(errors, data, "eval")
    if eval_block:
        if not any(key in eval_block for key in ("dataset", "seed")):
            error(errors, "eval_needs_dataset_or_seed")
        if "min_value" in eval_block:
            value = eval_block["min_value"]
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                error(errors, "eval_min_value_must_be_between_0_and_1", value=value)

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    data = json.loads(args.manifest.read_text())
    errors = validate(data)
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2))
        raise SystemExit(1)
    print(json.dumps({
        "ok": True,
        "brain_id": data["brain_id"],
        "backend": data["backend"],
        "corpus_type": data["corpus_type"],
        "embedding_dimension": embedding_dimension(data["embedding_model"]),
    }, indent=2))


if __name__ == "__main__":
    main()

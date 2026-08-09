#!/usr/bin/env python3
"""Query the vector brain via hybrid_retrieve_context.

Mirrors the agent-tool-contract.md `retrieve_context` shape so the CLI and the
agent tool return the same JSON. Filters map 1:1 to the SQL function's
parameters; NULL on any filter means unfiltered.

Example:
    python retrieve.py --dsn "$DATABASE_URL" \\
        --provider openai --model text-embedding-3-small --dim 1024 \\
        --query "How is the checkout webhook handled?" \\
        --top-k 10 --doc-type repo

    # AWS-native: --provider bedrock --model amazon.nova-2-multimodal-embeddings-v1:0
    # (must match the model + dim used at index time; requires boto3).

The CLI sets `hnsw.ef_search` and `hnsw.iterative_scan` per session -- without
these, filtered queries silently lose recall.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

try:
    import psycopg
    from psycopg.types.json import Jsonb
except ImportError:
    sys.exit("psycopg[binary] is required: pip install 'psycopg[binary]>=3.1'")


def embed_one(provider: str, model: str, dim: int, text: str) -> list[float]:
    if provider == "openai":
        from openai import OpenAI
        r = OpenAI().embeddings.create(model=model, input=[text], dimensions=dim)
        return r.data[0].embedding
    if provider == "voyage":
        import voyageai
        return voyageai.Client().embed([text], model=model, input_type="query").embeddings[0]
    if provider == "cohere":
        import cohere
        r = cohere.ClientV2().embed(model=model, texts=[text],
                                    input_type="search_query", embedding_types=["float"])
        return r.embeddings.float_[0]
    if provider == "gemini":
        # Mirrors _gemini() in scripts/embed_and_load.py.
        # Auth: GOOGLE_API_KEY env var (or Application Default Credentials).
        # Recommended models: gemini-embedding-001 (text-only, 3072 dims with
        # Matryoshka truncation) or gemini-embedding-2 (multimodal, 3072 dims).
        import google.generativeai as genai
        api_key = os.environ.get("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        kwargs: dict = {"model": model, "content": [text]}
        if dim < 3072:
            kwargs["output_dimensionality"] = dim
        result = genai.embed_content(**kwargs)
        emb = result["embedding"]
        # embed_content returns a flat list when input is a single string.
        if isinstance(emb[0], float):
            return emb
        return emb[0]
    if provider == "bedrock":
        # Mirrors _bedrock() in scripts/embed_and_load.py — same model id and
        # dimension MUST be used for query and index vectors. Amazon embedding
        # models take no query/document input_type distinction.
        # Recommended: amazon.nova-2-multimodal-embeddings-v1:0 (legacy:
        # amazon.titan-embed-text-v2:0). Auth: standard AWS credential chain;
        # region via AWS_REGION / AWS_DEFAULT_REGION. Requires: pip install boto3.
        import boto3
        body: dict = {"inputText": text}
        if dim:
            # Body key differs by model family (Titan v2 "dimensions"; Nova may
            # use "embeddingDimension"). Verify against the model card.
            body["dimensions"] = dim
        resp = boto3.client("bedrock-runtime").invoke_model(modelId=model, body=json.dumps(body))
        return json.loads(resp["body"].read())["embedding"]
    raise SystemExit(f"unknown provider: {provider}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dsn", default=os.environ.get("DATABASE_URL"))
    p.add_argument("--query", required=True)
    p.add_argument("--provider", required=True, choices=("openai", "voyage", "cohere", "gemini", "bedrock"))
    p.add_argument("--model", required=True)
    p.add_argument("--dim", type=int, required=True)
    p.add_argument("--top-k", type=int, default=10)
    p.add_argument("--candidates", type=int, default=50)
    p.add_argument("--rrf-k", type=float, default=60.0)
    p.add_argument("--doc-type", action="append")
    p.add_argument("--authority", action="append")
    p.add_argument("--language", default=None)
    p.add_argument("--source-path-prefix", action="append")
    p.add_argument("--acl-scope", default=None, help="JSON object of ACL keys")
    p.add_argument("--as-of", default=None)
    p.add_argument("--unit-type", action="append")
    p.add_argument("--ef-search", type=int, default=100)
    p.add_argument("--iterative-scan", default="relaxed_order",
                   help="pgvector >= 0.8 only; set 'off' to disable")
    args = p.parse_args()

    if not args.dsn:
        sys.exit("--dsn or DATABASE_URL required")

    model_id = f"{args.provider}:{args.model}"
    vec = embed_one(args.provider, args.model, args.dim, args.query)
    acl = json.loads(args.acl_scope) if args.acl_scope else None

    with psycopg.connect(args.dsn) as conn, conn.cursor() as cur:
        cur.execute(f"SET LOCAL hnsw.ef_search = {int(args.ef_search)}")
        if args.iterative_scan and args.iterative_scan != "off":
            try:
                cur.execute(f"SET LOCAL hnsw.iterative_scan = '{args.iterative_scan}'")
            except psycopg.errors.UndefinedObject:
                print("warn: hnsw.iterative_scan unsupported (needs pgvector >= 0.8)", file=sys.stderr)

        cur.execute(
            """
            SELECT chunk_id, evidence_id, content, contextual_summary,
                   source_uri, source_path, section_path, citation_anchor,
                   authority, effective_from, effective_to, rrf_score
            FROM hybrid_retrieve_context(
              %s, %s, %s, %s, %s, %s,
              %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                args.query, vec, model_id, args.top_k, args.candidates, args.rrf_k,
                args.doc_type, args.authority, args.language, args.source_path_prefix,
                Jsonb(acl) if acl is not None else None, args.as_of, args.unit_type,
            ),
        )
        rows = cur.fetchall()

    results = [
        {
            "evidence_id": r[1],
            "content": r[2],
            "contextual_summary": r[3],
            "source_uri": r[4],
            "source_path": r[5],
            "section_path": r[6],
            "citation_anchor": r[7],
            "authority": r[8],
            "score": float(r[11]),
            "retrieval_method": "hybrid_rrf",
        }
        for r in rows
    ]
    print(json.dumps({
        "results": results,
        "no_evidence": len(results) == 0,
    }, indent=2, default=str))


if __name__ == "__main__":
    main()

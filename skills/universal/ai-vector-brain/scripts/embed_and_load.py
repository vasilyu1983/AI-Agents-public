#!/usr/bin/env python3
"""Embed chunk JSONL and load into Postgres + pgvector.

Provider-agnostic: pick an embedder via --provider. The script handles
batching, retries with exponential backoff, idempotent upsert (content_hash),
and refuses to overwrite a live embedding column for an existing (chunk_id,
model_id) pair -- migration must add new rows, not mutate in place.

Inputs: JSONL of chunks from `chunk_markdown.py` (or compatible producer).
Required fields per chunk: source_path, chunk_index, content, content_hash,
section_path, citation_anchor, unit_type, token_count. Optional: anchor,
symbol_name, parent_chunk_ref, metadata.

Document upsert is keyed on (source_uri, content_hash). Pass --source-uri to
override the default (uses source_path).

Example:
    cat chunks.jsonl | python embed_and_load.py \\
        --provider openai --model text-embedding-3-small --dim 1024 \\
        --dsn "$DATABASE_URL" --doc-type docs --authority guideline \\
        --source-id acme-docs

    # AWS-native (Bedrock Nova 2 Multimodal Embeddings):
    cat chunks.jsonl | python embed_and_load.py \\
        --provider bedrock --model amazon.nova-2-multimodal-embeddings-v1:0 --dim 1024 \\
        --dsn "$DATABASE_URL" --doc-type docs --authority guideline --source-id acme-docs

Requires psycopg[binary] >= 3.1 and the provider SDK installed for the chosen
provider (boto3 for --provider bedrock). The provider call is isolated behind `Embedder.embed_batch` so a new
backend is one class.

Provider notes (verify model strings against vendor docs before use):
  openai  -- text-embedding-3-small / text-embedding-3-large
  voyage  -- voyage-4 (current tier), voyage-4-lite, voyage-4-large,
             voyage-4-nano; voyage-3/3.5 are legacy
  cohere  -- embed-v4 (current model string, multimodal text+images,
             1536 dims, 128k context)
  gemini  -- gemini-embedding-001 (#1 MTEB English as of April 2026,
             3072 dims with Matryoshka truncation to 768; requires
             google-generativeai SDK)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Iterable, Sequence

try:
    import psycopg
    from psycopg.types.json import Jsonb
except ImportError:
    sys.exit("psycopg[binary] is required: pip install 'psycopg[binary]>=3.1'")


@dataclass
class Embedder:
    provider: str
    model: str
    dim: int

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        if self.provider == "openai":
            return self._openai(texts)
        if self.provider == "voyage":
            return self._voyage(texts)
        if self.provider == "cohere":
            return self._cohere(texts)
        if self.provider == "gemini":
            return self._gemini(texts)
        if self.provider == "bedrock":
            return self._bedrock(texts)
        raise SystemExit(f"unknown provider: {self.provider}")

    def _openai(self, texts: Sequence[str]) -> list[list[float]]:
        from openai import OpenAI
        client = OpenAI()
        resp = client.embeddings.create(model=self.model, input=list(texts), dimensions=self.dim)
        return [d.embedding for d in resp.data]

    def _voyage(self, texts: Sequence[str]) -> list[list[float]]:
        # Current Voyage tier: voyage-4 (MoE architecture). Also available:
        # voyage-4-large, voyage-4-lite, voyage-4-nano.
        # voyage-3/voyage-3.5 are legacy model strings.
        import voyageai
        client = voyageai.Client()
        result = client.embed(list(texts), model=self.model, input_type="document")
        return result.embeddings

    def _cohere(self, texts: Sequence[str]) -> list[list[float]]:
        # Current model string: embed-v4 (multimodal text+images, 1536 dims,
        # 128k context, Matryoshka + binary quantization).
        import cohere
        client = cohere.ClientV2()
        resp = client.embed(model=self.model, texts=list(texts),
                            input_type="search_document", embedding_types=["float"])
        return resp.embeddings.float_

    def _gemini(self, texts: Sequence[str]) -> list[list[float]]:
        """Google Gemini embeddings via google-generativeai SDK.

        Recommended model: gemini-embedding-001 (#1 MTEB English as of
        April 2026, score 68.32, 3072 dims with Matryoshka truncation to 768).
        Pass --dim 3072 for full precision or --dim 768 for Matryoshka
        truncation (set output_dimensionality accordingly).

        Requires: pip install google-generativeai
        Auth: GOOGLE_API_KEY env var (or Application Default Credentials).
        """
        import google.generativeai as genai
        api_key = os.environ.get("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        # Matryoshka truncation: pass output_dimensionality when dim < 3072.
        kwargs: dict = {"model": self.model, "content": list(texts)}
        if self.dim < 3072:
            kwargs["output_dimensionality"] = self.dim
        result = genai.embed_content(**kwargs)
        return result["embedding"] if isinstance(result["embedding"][0], float) else result["embedding"]

    def _bedrock(self, texts: Sequence[str]) -> list[list[float]]:
        """Amazon Bedrock embeddings (AWS-native default).

        Recommended model: amazon.nova-2-multimodal-embeddings-v1:0 — Nova 2
        Multimodal Embeddings, Matryoshka output dims 3072/1024/384/256,
        8192-token context, 200 languages. Legacy fallback:
        amazon.titan-embed-text-v2:0. Verify the current model id in the
        Bedrock console before pinning a manifest.

        Amazon embedding models embed ONE input per invoke_model call (no
        server-side batching), so this loops over texts.

        Requires: pip install boto3
        Auth: standard AWS credential chain (env vars / shared config / IAM role).
        Region: AWS_REGION or AWS_DEFAULT_REGION.
        """
        import boto3
        client = boto3.client("bedrock-runtime")
        out: list[list[float]] = []
        for text in texts:
            body: dict = {"inputText": text}
            # Matryoshka truncation: the request-body key differs by model
            # family (Titan v2 uses "dimensions"; Nova may use
            # "embeddingDimension"). Verify against the model's card before use.
            if self.dim:
                body["dimensions"] = self.dim
            resp = client.invoke_model(modelId=self.model, body=json.dumps(body))
            payload = json.loads(resp["body"].read())
            out.append(payload["embedding"])
        return out


def retry(fn, *, attempts: int = 5, base: float = 1.0):
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:  # provider-agnostic: catch broadly, log, back off
            if i == attempts - 1:
                raise
            wait = base * (2 ** i)
            print(f"[retry {i+1}/{attempts}] {exc!r} -- sleeping {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)


def iter_chunks(path: str | None) -> Iterable[dict]:
    stream = open(path, encoding="utf-8") if path else sys.stdin
    with stream:
        for line in stream:
            line = line.strip()
            if line:
                yield json.loads(line)


def batched(items: list[dict], n: int) -> Iterable[list[dict]]:
    for i in range(0, len(items), n):
        yield items[i:i + n]


def upsert_document(cur, *, source_id: str, source_uri: str, source_path: str,
                    doc_type: str, authority: str | None, language: str,
                    content_hash: str, metadata: dict) -> int:
    cur.execute(
        """
        INSERT INTO documents
          (source_id, source_uri, source_path, doc_type, language, authority,
           content_hash, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (source_uri, content_hash) DO UPDATE
          SET ingested_at = now()
        RETURNING id
        """,
        (source_id, source_uri, source_path, doc_type, language, authority,
         content_hash, Jsonb(metadata)),
    )
    return cur.fetchone()[0]


def insert_chunk(cur, *, document_id: int, c: dict, doc_type: str,
                 authority: str | None, language: str) -> int:
    cur.execute(
        """
        INSERT INTO chunks
          (document_id, chunk_index, content, token_count, section_path,
           anchor, citation_anchor, symbol_name, unit_type, doc_type,
           language, authority, content_hash, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (document_id, chunk_index) DO UPDATE
          SET content = EXCLUDED.content,
              content_hash = EXCLUDED.content_hash,
              metadata = EXCLUDED.metadata
        RETURNING id
        """,
        (
            document_id, c["chunk_index"], c["content"], c.get("token_count", 0),
            c.get("section_path"), c.get("anchor"), c.get("citation_anchor"),
            c.get("symbol_name"), c.get("unit_type", "chunk"), doc_type,
            language, authority, c["content_hash"], Jsonb(c.get("metadata", {})),
        ),
    )
    return cur.fetchone()[0]


def insert_embedding(cur, *, chunk_id: int, model_id: str, vec: list[float]) -> None:
    # Refuse to overwrite a live (chunk_id, model_id) pair. Migration must add
    # a new model_id row, not mutate in place. See postgres-pgvector-default.md.
    cur.execute(
        "SELECT 1 FROM embeddings WHERE chunk_id = %s AND model_id = %s",
        (chunk_id, model_id),
    )
    if cur.fetchone():
        return
    cur.execute(
        "INSERT INTO embeddings (chunk_id, model_id, embedding) VALUES (%s, %s, %s)",
        (chunk_id, model_id, vec),
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("path", nargs="?", help="JSONL chunks (stdin if omitted)")
    p.add_argument("--dsn", default=os.environ.get("DATABASE_URL"), required=False)
    p.add_argument("--provider", required=True, choices=("openai", "voyage", "cohere", "gemini", "bedrock"))
    p.add_argument("--model", required=True, help="provider model id (also stored in embeddings.model_id)")
    p.add_argument("--dim", type=int, required=True)
    p.add_argument("--source-id", required=True)
    p.add_argument("--doc-type", required=True)
    p.add_argument("--authority", default=None)
    p.add_argument("--language", default="en")
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--source-uri-prefix", default="", help="prepended to source_path to form source_uri")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if not args.dsn:
        sys.exit("--dsn or DATABASE_URL required")

    chunks = list(iter_chunks(args.path))
    if not chunks:
        sys.exit("no chunks on input")

    embedder = Embedder(provider=args.provider, model=args.model, dim=args.dim)
    model_id = f"{args.provider}:{args.model}"

    if args.dry_run:
        print(f"dry-run: would embed {len(chunks)} chunks with {model_id} dim={args.dim}", file=sys.stderr)
        return

    with psycopg.connect(args.dsn) as conn:
        n_docs = n_chunks = n_emb = 0
        for batch in batched(chunks, args.batch_size):
            texts = [c["content"] for c in batch]
            vectors = retry(lambda: embedder.embed_batch(texts))
            if len(vectors) != len(batch) or any(len(v) != args.dim for v in vectors):
                sys.exit(f"embedder returned wrong shape: {len(vectors)} vectors, expected dim {args.dim}")

            with conn.cursor() as cur:
                for c, vec in zip(batch, vectors):
                    source_path = c["source_path"]
                    source_uri = f"{args.source_uri_prefix}{source_path}" if args.source_uri_prefix else source_path
                    doc_hash = hashlib.sha256(source_uri.encode("utf-8")).hexdigest()
                    doc_id = upsert_document(
                        cur, source_id=args.source_id, source_uri=source_uri,
                        source_path=source_path, doc_type=args.doc_type,
                        authority=args.authority, language=args.language,
                        content_hash=doc_hash, metadata={},
                    )
                    chunk_db_id = insert_chunk(
                        cur, document_id=doc_id, c=c, doc_type=args.doc_type,
                        authority=args.authority, language=args.language,
                    )
                    insert_embedding(cur, chunk_id=chunk_db_id, model_id=model_id, vec=vec)
                    n_chunks += 1
                    n_emb += 1
                n_docs += len(batch)
            conn.commit()
            print(f"loaded batch: chunks={n_chunks} embeddings={n_emb}", file=sys.stderr)

        print(f"done: chunks={n_chunks} embeddings={n_emb} model_id={model_id}", file=sys.stderr)


if __name__ == "__main__":
    main()

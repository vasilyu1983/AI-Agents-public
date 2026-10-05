"""Postgres + pgvector RetrievalStore.

Embeds at index time and at query time using the injected EmbeddingClient.
Returns rerankable hits as `RetrievalResult` — never raw scores into the
prompt (A18 blocked at the type level via the contract).

Phase 2 ships cosine-similarity retrieval with a no-op reranker hook. Real
rerankers (Cohere Rerank, BGE, etc.) plug into `_rerank` in Phase 3.
"""

from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from ..contracts import RetrievalResult
from .base import EmbeddingClient


class PostgresRetrievalStore:
    """Satisfies the `RetrievalStore` Protocol."""

    def __init__(self, conn: Any, embedder: EmbeddingClient) -> None:
        self._conn = conn
        self._embedder = embedder

    def index(self, *, source_id: str, chunks: list[dict[str, Any]]) -> None:
        if not chunks:
            return
        owner_scope = chunks[0].get("owner_scope")
        if not owner_scope:
            raise ValueError("chunk.owner_scope is required (A10)")

        snippets = [c["snippet"] for c in chunks]
        embeddings = self._embedder.embed(snippets)

        rows = []
        for i, (c, emb) in enumerate(zip(chunks, embeddings, strict=True)):
            rows.append((
                c.get("id") or f"chunk_{uuid4().hex[:16]}",
                source_id,
                c.get("chunk_index", i),
                c["snippet"],
                _to_embedding_literal(emb),
                json.dumps(c.get("metadata", {})),
                json.dumps(c.get("owner_scope", owner_scope)),
            ))
        with self._conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO knowledge_chunk
                    (id, source_id, chunk_index, snippet, embedding, metadata, owner_scope)
                VALUES (%s, %s, %s, %s, %s::vector, %s::jsonb, %s::jsonb)
                ON CONFLICT (id) DO UPDATE SET
                    snippet = EXCLUDED.snippet,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    indexed_at = now()
                """,
                rows,
            )
        self._conn.commit()

    def retrieve(
        self,
        *,
        query: str,
        owner_scope: dict[str, str],
        top_k: int = 8,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        if not owner_scope:
            raise ValueError("retrieve(owner_scope=...) is required (A10)")

        [embedding] = self._embedder.embed([query])
        sql = """
            SELECT id, source_id, snippet, metadata, chunk_index,
                   1 - (embedding <=> %s::vector) AS cos_sim
            FROM knowledge_chunk
            WHERE owner_scope = %s::jsonb
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        params = [_to_embedding_literal(embedding), json.dumps(owner_scope),
                  _to_embedding_literal(embedding), top_k * 4]  # over-fetch for reranking
        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

        candidates = [
            RetrievalResult(
                evidence_id=row[0],
                source_id=row[1],
                snippet=row[2],
                score=float(row[5]),
                metadata=row[3] or {},
                chunk_index=row[4],
            )
            for row in rows
        ]
        return self._rerank(query, candidates)[:top_k]

    def invalidate(self, source_id: str) -> None:
        with self._conn.cursor() as cur:
            cur.execute("DELETE FROM knowledge_chunk WHERE source_id = %s", (source_id,))
        self._conn.commit()

    def _rerank(self, query: str, candidates: list[RetrievalResult]) -> list[RetrievalResult]:
        """Reranker hook. Phase 2 returns candidates as-is; Phase 3 plugs in a
        cross-encoder. The contract is: input is over-fetched cosine hits,
        output is the same shape but reordered/filtered."""
        return candidates


def _to_embedding_literal(values: list[float]) -> str:
    """Postgres vector parameters accept a string literal '[1.0, 2.0, ...]'."""
    return "[" + ",".join(f"{v:.6f}" for v in values) + "]"

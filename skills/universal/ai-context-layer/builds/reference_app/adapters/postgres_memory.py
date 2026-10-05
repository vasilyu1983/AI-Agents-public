"""Postgres-backed MemoryStore.

Bi-temporal, non-destructive. The adapter is dumb on purpose — business
decisions about *which* contradiction wins live in the runtime, not here.
This file just makes the schema honest:

- `remember` writes a row with full provenance and confidence
- `recall` honors as-of and active-only by default
- `forget` sets `invalidated_at`, never DELETEs (A3, A7 blocked at the API)
- `improve` updates confidence, clipped to [0, 1]
- `find_contradictions` returns conflicting active rows for the runtime to
  categorize (attribution / temporal / stale per `references/anti-patterns-catalog.md` A4)
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from ..contracts import LearnedMemory, MemoryType


class PostgresMemoryStore:
    """Satisfies the `MemoryStore` Protocol."""

    def __init__(self, conn: Any) -> None:
        self._conn = conn

    # ---- remember ----------------------------------------------------------

    def remember(self, fact: LearnedMemory) -> str:
        if not fact.source_episode_id:
            raise ValueError("LearnedMemory.source_episode_id is required (A13)")
        if not fact.owner_scope:
            raise ValueError("LearnedMemory.owner_scope is required (A10)")
        if not 0.0 <= fact.confidence <= 1.0:
            raise ValueError("LearnedMemory.confidence must be in [0, 1] (A14)")

        new_id = fact.id or f"mem_{uuid4().hex[:16]}"
        fact.id = new_id

        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO learned_memory (
                    id, entity_id, entity_type, memory_type, value, source,
                    source_episode_id, confidence, created_at, updated_at,
                    valid_from, valid_to, invalidated_at, expires_at,
                    supersedes_id, owner_scope, inferred, tags
                )
                VALUES (
                    %s, %s, %s, %s, %s::jsonb, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s::jsonb, %s, %s
                )
                """,
                (
                    new_id, fact.entity_id, fact.entity_type, fact.memory_type.value,
                    json.dumps(fact.value), fact.source,
                    fact.source_episode_id, fact.confidence, fact.created_at, fact.updated_at,
                    fact.valid_from, fact.valid_to, fact.invalidated_at, fact.expires_at,
                    fact.supersedes_id, json.dumps(fact.owner_scope), fact.inferred, fact.tags,
                ),
            )
        self._conn.commit()
        return new_id

    # ---- recall ------------------------------------------------------------

    def recall(
        self,
        *,
        entity_id: str,
        owner_scope: dict[str, str],
        memory_types: list[MemoryType] | None = None,
        min_confidence: float = 0.0,
        as_of: datetime | None = None,
        limit: int = 50,
    ) -> list[LearnedMemory]:
        as_of = as_of or datetime.now(UTC)
        types_filter = [t.value for t in memory_types] if memory_types else None

        sql = """
            SELECT id, entity_id, entity_type, memory_type, value, source,
                   source_episode_id, confidence, created_at, updated_at,
                   valid_from, valid_to, invalidated_at, expires_at,
                   supersedes_id, owner_scope, inferred, tags
            FROM learned_memory
            WHERE entity_id = %s
              AND owner_scope = %s::jsonb
              AND confidence >= %s
              AND (invalidated_at IS NULL OR invalidated_at > %s)
              AND (valid_from IS NULL OR valid_from <= %s)
              AND (valid_to IS NULL OR valid_to > %s)
              AND (expires_at IS NULL OR expires_at > %s)
        """
        params: list[Any] = [
            entity_id, json.dumps(owner_scope), min_confidence,
            as_of, as_of, as_of, as_of,
        ]
        if types_filter:
            sql += " AND memory_type = ANY(%s)"
            params.append(types_filter)
        sql += " ORDER BY confidence DESC, updated_at DESC LIMIT %s"
        params.append(limit)

        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return [_row_to_memory(r) for r in rows]

    # ---- forget (non-destructive) ------------------------------------------

    def forget(self, memory_id: str, *, reason: str, actor: str) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                UPDATE learned_memory
                SET invalidated_at = now(),
                    tags = array_append(tags, %s),
                    updated_at = now()
                WHERE id = %s AND invalidated_at IS NULL
                """,
                (f"forgotten_by:{actor}:{reason}", memory_id),
            )
        self._conn.commit()

    # ---- improve -----------------------------------------------------------

    def improve(self, memory_id: str, *, confidence_delta: float, reason: str) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                UPDATE learned_memory
                SET confidence = LEAST(1.0, GREATEST(0.0, confidence + %s)),
                    updated_at = now(),
                    tags = array_append(tags, %s)
                WHERE id = %s
                """,
                (confidence_delta, f"feedback:{reason}", memory_id),
            )
        self._conn.commit()

    # ---- find_contradictions -----------------------------------------------

    def find_contradictions(self, fact: LearnedMemory) -> list[LearnedMemory]:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, entity_id, entity_type, memory_type, value, source,
                       source_episode_id, confidence, created_at, updated_at,
                       valid_from, valid_to, invalidated_at, expires_at,
                       supersedes_id, owner_scope, inferred, tags
                FROM learned_memory
                WHERE entity_id = %s
                  AND memory_type = %s
                  AND owner_scope = %s::jsonb
                  AND value <> %s::jsonb
                  AND invalidated_at IS NULL
                """,
                (
                    fact.entity_id, fact.memory_type.value,
                    json.dumps(fact.owner_scope), json.dumps(fact.value),
                ),
            )
            rows = cur.fetchall()
        return [_row_to_memory(r) for r in rows]


def _row_to_memory(row: tuple) -> LearnedMemory:
    return LearnedMemory(
        id=row[0],
        entity_id=row[1],
        entity_type=row[2],
        memory_type=MemoryType(row[3]),
        value=row[4],
        source=row[5],
        source_episode_id=row[6],
        confidence=row[7],
        created_at=row[8],
        updated_at=row[9],
        valid_from=row[10],
        valid_to=row[11],
        invalidated_at=row[12],
        expires_at=row[13],
        supersedes_id=row[14],
        owner_scope=row[15],
        inferred=row[16],
        tags=list(row[17] or []),
    )

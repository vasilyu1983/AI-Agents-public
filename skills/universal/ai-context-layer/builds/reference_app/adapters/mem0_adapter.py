"""Mem0 / Mem0g adapter — `MemoryStore` Protocol.

Maps the canonical `LearnedMemory` contract onto Mem0's memory operations.
Mem0 is a managed memory layer with built-in extraction, classification, and
vector storage. This adapter demonstrates the *contract translation* — your
production wiring should pin the SDK version and verify method names against
the docs (the API has shifted across minor versions in 2025–2026).

Verified shape against the published `mem0ai` SDK (April 2026). If you upgrade,
rerun the smoke test gated by `MEM0_API_KEY` in `evals/suites/mem0/`.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from ..contracts import LearnedMemory, MemoryType


class Mem0MemoryStore:
    """Satisfies the `MemoryStore` Protocol against a Mem0 client.

    Tenant isolation: Mem0 scopes by `user_id` / `agent_id` / `run_id`. We
    flatten our `owner_scope` dict into a deterministic `user_id` string so
    cross-tenant leakage (A10) is structurally blocked.
    """

    def __init__(self, client: Any) -> None:
        # Lazy import would belong here in a real adapter; keep flexible.
        self._client = client

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

        # Mem0's `add` takes a string and stores extracted memories. We bypass
        # extraction (we already extracted upstream via P5) by passing a tight
        # JSON string that round-trips cleanly through `get`.
        payload = json.dumps({
            "id": new_id,
            "memory_type": fact.memory_type.value,
            "value": fact.value,
            "confidence": fact.confidence,
            "source_episode_id": fact.source_episode_id,
            "inferred": fact.inferred,
            "tags": fact.tags,
        })
        self._client.add(
            messages=[{"role": "user", "content": payload}],
            user_id=_scope_to_user_id(fact.owner_scope, fact.entity_id),
            metadata={
                "memory_type": fact.memory_type.value,
                "source_episode_id": fact.source_episode_id,
                "owner_scope": fact.owner_scope,
                "inferred": fact.inferred,
                "confidence": fact.confidence,
                "supersedes_id": fact.supersedes_id,
            },
        )
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
        # Mem0's `get_all` returns scoped memories; `search` returns ranked.
        # For recall (non-query), use get_all + filter.
        rows = self._client.get_all(
            user_id=_scope_to_user_id(owner_scope, entity_id),
            limit=limit,
        )
        out: list[LearnedMemory] = []
        for row in rows.get("results", []):
            memory = _row_to_memory(row, entity_id=entity_id, owner_scope=owner_scope)
            if memory.confidence < min_confidence:
                continue
            if memory_types and memory.memory_type not in memory_types:
                continue
            if memory.invalidated_at:
                continue
            out.append(memory)
        return out

    # ---- forget (non-destructive emulation) --------------------------------

    def forget(self, memory_id: str, *, reason: str, actor: str) -> None:
        """Mem0's native `delete` is destructive (A7 risk). We emulate
        non-destructive forget by patching metadata with `invalidated_at`
        and a `forgotten_by:*` tag, leaving the row in place for audit.

        If your retention policy requires hard delete, follow this with an
        explicit `client.delete(memory_id=...)` after the audit window.
        """
        current = self._client.get(memory_id=memory_id)
        meta = dict((current or {}).get("metadata", {}) or {})
        meta["invalidated_at"] = datetime.now(UTC).isoformat()
        meta["forgotten_by"] = f"{actor}:{reason}"
        # `metadata=` is the documented update field; writing to the memory
        # text would leave `metadata.invalidated_at` unset and recall would
        # keep returning the "forgotten" row.
        self._client.update(memory_id=memory_id, metadata=meta)

    # ---- improve -----------------------------------------------------------

    def improve(self, memory_id: str, *, confidence_delta: float, reason: str) -> None:
        # Mem0 doesn't expose confidence as a first-class score; we ride
        # the metadata field. Read-modify-write is necessary because the SDK
        # has no atomic increment.
        current = self._client.get(memory_id=memory_id)
        meta = (current or {}).get("metadata", {}) or {}
        new_conf = max(0.0, min(1.0, float(meta.get("confidence", 0.5)) + confidence_delta))
        meta["confidence"] = new_conf
        meta.setdefault("feedback_log", []).append(
            {"reason": reason, "at": datetime.now(UTC).isoformat()}
        )
        self._client.update(memory_id=memory_id, metadata=meta)

    # ---- find_contradictions ----------------------------------------------

    def find_contradictions(self, fact: LearnedMemory) -> list[LearnedMemory]:
        # Mem0's vector search is the natural lookup. Pull semantically
        # similar memories of the same type and let the runtime decide
        # which differ in `value`.
        hits = self._client.search(
            query=json.dumps(fact.value),
            user_id=_scope_to_user_id(fact.owner_scope, fact.entity_id),
            limit=20,
        )
        out: list[LearnedMemory] = []
        for row in hits.get("results", []):
            mem = _row_to_memory(row, entity_id=fact.entity_id, owner_scope=fact.owner_scope)
            if mem.memory_type != fact.memory_type:
                continue
            if mem.value == fact.value:
                continue
            if mem.invalidated_at:
                continue
            out.append(mem)
        return out


def _scope_to_user_id(owner_scope: dict[str, str], entity_id: str) -> str:
    """Stable, collision-free string for Mem0's `user_id`. Format:
    'org=<org>|wsp=<wsp>|ent=<entity>'. Keep keys sorted so identical
    scopes always produce identical user_ids."""
    parts = [f"{k}={v}" for k, v in sorted(owner_scope.items())]
    parts.append(f"ent={entity_id}")
    return "|".join(parts)


def _row_to_memory(
    row: dict[str, Any], *, entity_id: str, owner_scope: dict[str, str]
) -> LearnedMemory:
    meta = row.get("metadata") or {}
    raw_value = row.get("memory") or "{}"
    try:
        decoded = json.loads(raw_value) if isinstance(raw_value, str) else raw_value
    except json.JSONDecodeError:
        decoded = {"text": raw_value}

    invalidated = meta.get("invalidated_at")
    invalidated_at = (
        datetime.fromisoformat(invalidated) if isinstance(invalidated, str) else None
    )

    return LearnedMemory(
        id=row.get("id", ""),
        entity_id=entity_id,
        entity_type=meta.get("entity_type", "user"),
        memory_type=MemoryType(meta.get("memory_type", "fact")),
        value=decoded.get("value", decoded),
        source=meta.get("source", "mem0"),
        source_episode_id=meta.get("source_episode_id", ""),
        confidence=float(meta.get("confidence", 0.5)),
        created_at=_parse_dt(row.get("created_at")) or datetime.now(UTC),
        updated_at=_parse_dt(row.get("updated_at")) or datetime.now(UTC),
        owner_scope=meta.get("owner_scope", owner_scope),
        inferred=bool(meta.get("inferred", True)),
        invalidated_at=invalidated_at,
        supersedes_id=meta.get("supersedes_id"),
        tags=list(meta.get("tags", [])),
    )


def _parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None

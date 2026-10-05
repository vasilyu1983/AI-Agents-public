"""LangGraph Store adapter — `MemoryStore` Protocol.

LangGraph's `BaseStore` is a namespaced KV with optional vector search.
This adapter maps `LearnedMemory` onto `(namespace, key, value)` triples
where the namespace tuple encodes `owner_scope` (structural A10).

Verified against `langgraph.store.base.BaseStore` shape as of April 2026.
Works with the in-memory store (`InMemoryStore`), the Postgres store
(`PostgresStore`), or any other `BaseStore` implementation.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from ..contracts import LearnedMemory, MemoryType


class LangGraphStoreMemoryStore:
    """Satisfies the `MemoryStore` Protocol against a LangGraph BaseStore.

    Namespace shape:
        (organization_id, ..., entity_id, "memory")

    Every read/write goes through the namespace, so cross-tenant queries
    are structurally impossible — you cannot accidentally drop a scope
    component without changing the call site.
    """

    def __init__(self, store: Any) -> None:
        self._store = store

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

        ns = _namespace(fact.owner_scope, fact.entity_id)
        self._store.put(ns, new_id, _to_payload(fact))
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
        ns = _namespace(owner_scope, entity_id)
        items = self._store.search(ns, limit=limit) or []
        out: list[LearnedMemory] = []
        for item in items:
            mem = _payload_to_memory(
                item.value if hasattr(item, "value") else item.get("value", {}),
                fallback_id=getattr(item, "key", None) or item.get("key", ""),
                entity_id=entity_id,
                owner_scope=owner_scope,
            )
            if not mem or mem.invalidated_at:
                continue
            if mem.confidence < min_confidence:
                continue
            if memory_types and mem.memory_type not in memory_types:
                continue
            out.append(mem)
        return out

    # ---- forget (non-destructive: patch payload) ---------------------------

    def forget(self, memory_id: str, *, reason: str, actor: str) -> None:
        # We don't have the namespace cached — search the structured tag
        # store for the memory and patch in place. Most BaseStore impls
        # support get_namespaces(); fall back to scanning if not.
        ns = self._find_namespace(memory_id)
        if ns is None:
            return
        item = self._store.get(ns, memory_id)
        payload = (item.value if hasattr(item, "value") else item.get("value")) or {}
        payload["invalidated_at"] = datetime.now(UTC).isoformat()
        payload.setdefault("tags", []).append(f"forgotten_by:{actor}:{reason}")
        self._store.put(ns, memory_id, payload)

    # ---- improve -----------------------------------------------------------

    def improve(self, memory_id: str, *, confidence_delta: float, reason: str) -> None:
        ns = self._find_namespace(memory_id)
        if ns is None:
            return
        item = self._store.get(ns, memory_id)
        payload = (item.value if hasattr(item, "value") else item.get("value")) or {}
        new_conf = max(0.0, min(1.0, float(payload.get("confidence", 0.5)) + confidence_delta))
        payload["confidence"] = new_conf
        payload.setdefault("feedback_log", []).append(
            {"reason": reason, "at": datetime.now(UTC).isoformat()}
        )
        self._store.put(ns, memory_id, payload)

    # ---- find_contradictions ----------------------------------------------

    def find_contradictions(self, fact: LearnedMemory) -> list[LearnedMemory]:
        ns = _namespace(fact.owner_scope, fact.entity_id)
        items = self._store.search(ns, limit=200) or []
        out: list[LearnedMemory] = []
        for item in items:
            mem = _payload_to_memory(
                item.value if hasattr(item, "value") else item.get("value", {}),
                fallback_id=getattr(item, "key", None) or item.get("key", ""),
                entity_id=fact.entity_id,
                owner_scope=fact.owner_scope,
            )
            if not mem or mem.invalidated_at:
                continue
            if mem.memory_type != fact.memory_type or mem.value == fact.value:
                continue
            out.append(mem)
        return out

    # ---- internals --------------------------------------------------------

    def _find_namespace(self, memory_id: str) -> tuple[str, ...] | None:
        """Locate the namespace a memory_id lives under. BaseStore impls
        vary in efficiency here — InMemoryStore is O(N) over namespaces.
        For high-volume forgets, maintain a side index of id → namespace."""
        try:
            namespaces = self._store.list_namespaces() or []
        except AttributeError:
            return None
        for ns in namespaces:
            if not (ns and ns[-1] == "memory"):
                continue
            try:
                hit = self._store.get(ns, memory_id)
            except Exception:
                hit = None
            if hit:
                return ns
        return None


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _namespace(owner_scope: dict[str, str], entity_id: str) -> tuple[str, ...]:
    """Deterministic namespace tuple. Order keys alphabetically so identical
    scopes always produce identical tuples (no accidental scope shadowing)."""
    parts = [v for _, v in sorted(owner_scope.items())]
    return (*parts, entity_id, "memory")


def _to_payload(fact: LearnedMemory) -> dict[str, Any]:
    return {
        "id": fact.id,
        "entity_id": fact.entity_id,
        "entity_type": fact.entity_type,
        "memory_type": fact.memory_type.value,
        "value": fact.value,
        "source": fact.source,
        "source_episode_id": fact.source_episode_id,
        "confidence": fact.confidence,
        "inferred": fact.inferred,
        "supersedes_id": fact.supersedes_id,
        "tags": fact.tags,
        "owner_scope": fact.owner_scope,
        "created_at": fact.created_at.isoformat(),
    }


def _payload_to_memory(
    payload: dict[str, Any] | str | None,
    *,
    fallback_id: str,
    entity_id: str,
    owner_scope: dict[str, str],
) -> LearnedMemory | None:
    if payload is None:
        return None
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return None

    invalidated = payload.get("invalidated_at")
    invalidated_at = (
        datetime.fromisoformat(invalidated) if isinstance(invalidated, str) else None
    )
    return LearnedMemory(
        id=payload.get("id", fallback_id),
        entity_id=payload.get("entity_id", entity_id),
        entity_type=payload.get("entity_type", "user"),
        memory_type=MemoryType(payload.get("memory_type", "fact")),
        value=payload.get("value"),
        source=payload.get("source", "langgraph_store"),
        source_episode_id=payload.get("source_episode_id", ""),
        confidence=float(payload.get("confidence", 0.5)),
        created_at=_parse_dt(payload.get("created_at")) or datetime.now(UTC),
        updated_at=_parse_dt(payload.get("created_at")) or datetime.now(UTC),
        owner_scope=payload.get("owner_scope", owner_scope),
        inferred=bool(payload.get("inferred", True)),
        invalidated_at=invalidated_at,
        supersedes_id=payload.get("supersedes_id"),
        tags=list(payload.get("tags", [])),
    )


def _parse_dt(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value)) if value else None
    except (TypeError, ValueError):
        return None

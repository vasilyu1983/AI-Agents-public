"""Composition helpers for multi-vendor wiring.

`UnionMemoryStore` lets you combine multiple `MemoryStore` adapters behind
the same Protocol. The supermemory cookbook references this pattern:

    memory = UnionMemoryStore(
        primary=PostgresMemoryStore(conn),    # writes go here
        readers=[SupermemoryMemoryStore(...)], # reads merge from all
    )

Reads merge results from every source, deduping by `LearnedMemory.id`.
Writes go to the primary. Forget/improve route to whichever store owns
the id (best-effort: try each in order). This is good enough for the
common dual-vendor split; for richer routing (e.g. by memory_type or
owner_scope) write a custom Protocol implementation rather than
extending this one.
"""

from __future__ import annotations

from datetime import datetime

from ..adapters import MemoryStore
from ..contracts import LearnedMemory, MemoryType


class UnionMemoryStore:
    """Satisfies the `MemoryStore` Protocol by composing multiple stores."""

    def __init__(self, *, primary: MemoryStore, readers: list[MemoryStore] | None = None) -> None:
        self._primary = primary
        self._readers = list(readers or [])

    # ---- write side: primary only ------------------------------------------

    def remember(self, fact: LearnedMemory) -> str:
        return self._primary.remember(fact)

    # ---- read side: merge + dedupe -----------------------------------------

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
        seen: dict[str, LearnedMemory] = {}
        for store in (self._primary, *self._readers):
            for mem in store.recall(
                entity_id=entity_id,
                owner_scope=owner_scope,
                memory_types=memory_types,
                min_confidence=min_confidence,
                as_of=as_of,
                limit=limit,
            ):
                # Highest-confidence wins on duplicate ids.
                if mem.id not in seen or mem.confidence > seen[mem.id].confidence:
                    seen[mem.id] = mem
        out = sorted(seen.values(), key=lambda m: m.confidence, reverse=True)
        return out[:limit]

    # ---- forget / improve: route by ownership ------------------------------

    def forget(self, memory_id: str, *, reason: str, actor: str) -> None:
        for store in (self._primary, *self._readers):
            try:
                store.forget(memory_id, reason=reason, actor=actor)
            except Exception:  # noqa: BLE001 — adapters raise vendor-specific errors
                continue

    def improve(self, memory_id: str, *, confidence_delta: float, reason: str) -> None:
        for store in (self._primary, *self._readers):
            try:
                store.improve(memory_id, confidence_delta=confidence_delta, reason=reason)
            except Exception:  # noqa: BLE001
                continue

    def find_contradictions(self, fact: LearnedMemory) -> list[LearnedMemory]:
        seen: dict[str, LearnedMemory] = {}
        for store in (self._primary, *self._readers):
            for c in store.find_contradictions(fact):
                seen.setdefault(c.id, c)
        return list(seen.values())

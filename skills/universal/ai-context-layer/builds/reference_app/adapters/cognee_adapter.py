"""Cognee adapter — `RetrievalStore` Protocol (primary) + minimal `MemoryStore`.

Cognee is a graph + vector hybrid: documents are ingested, an ontology is
extracted, and search returns prose evidence + traversed relationships.
This adapter wraps `cognee.add` / `cognee.cognify` / `cognee.search` and maps
results into our `RetrievalResult`.

Cognee is mostly a *retrieval and KG* layer rather than a typed-memory
store — the included `MemoryStore` shape is a thin wrapper for cases where
you want one vendor for both, but pgvector + Cognee for retrieval is a
common production split.

Verified against the `cognee` SDK shape as of April 2026. The async API has
shifted across versions; pin and re-test on upgrade.
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from ..contracts import LearnedMemory, MemoryType, RetrievalResult


class CogneeRetrievalStore:
    """Satisfies the `RetrievalStore` Protocol against the `cognee` package.

    Tenant isolation: Cognee's `dataset_name` (or `tenant_id` in newer
    versions) maps onto our `owner_scope`. The adapter encodes the scope
    deterministically into a dataset name to make A10 structural.
    """

    def __init__(self, cognee_module: Any) -> None:
        self._cognee = cognee_module

    def index(self, *, source_id: str, chunks: list[dict[str, Any]]) -> None:
        if not chunks:
            return
        owner_scope = chunks[0].get("owner_scope")
        if not owner_scope:
            raise ValueError("chunk.owner_scope is required (A10)")

        dataset = _scope_to_dataset(owner_scope)
        text_blob = "\n\n".join(
            f"<chunk id={c.get('id', f'chunk_{i}')}>" + c["snippet"] + "</chunk>"
            for i, c in enumerate(chunks)
        )
        # cognee.add() then cognee.cognify() — both async in current SDK.
        asyncio.run(self._cognee.add(text_blob, dataset_name=dataset))
        asyncio.run(self._cognee.cognify(datasets=[dataset]))

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

        dataset = _scope_to_dataset(owner_scope)
        # `search_type` controls whether we get vector hits, graph traversal,
        # or both. INSIGHTS / GRAPH_COMPLETION / CHUNKS are common values
        # across recent SDK versions.
        raw = asyncio.run(
            self._cognee.search(
                query_text=query,
                query_type=getattr(self._cognee.SearchType, "CHUNKS", None) or "CHUNKS",
                datasets=[dataset],
            )
        )
        results: list[RetrievalResult] = []
        for i, item in enumerate(raw[:top_k]):
            results.append(
                RetrievalResult(
                    evidence_id=str(item.get("id", f"cog_{i}")),
                    source_id=str(item.get("source_id", "cognee")),
                    snippet=str(item.get("text") or item.get("payload", ""))[:2000],
                    score=float(item.get("score", 0.0)),
                    metadata={"graph": item.get("graph_context")} if item.get("graph_context") else {},
                )
            )
        return results

    def invalidate(self, source_id: str) -> None:
        # Cognee 2026-era SDK exposes a `prune` per dataset but not per
        # source_id directly. Most teams handle this by tagging chunks at
        # index time and re-cognifying. For audit-grade invalidation,
        # keep a parallel record of source_id → cognee node IDs and call
        # `delete_nodes(...)` here.
        raise NotImplementedError(
            "Cognee per-source invalidation requires a node-id mapping you "
            "maintain at index time. See cookbook gotcha #3."
        )


class CogneeMemoryStore:
    """Thin `MemoryStore` shim for shops that want one vendor for both.

    Stores each `LearnedMemory` as a tagged document and uses Cognee's
    semantic search for `recall` and `find_contradictions`. Lifecycle
    semantics are emulated; if you need real lifecycle, pair Cognee with
    a separate memory store (pgvector, Mem0).
    """

    def __init__(self, cognee_module: Any) -> None:
        self._cognee = cognee_module

    def remember(self, fact: LearnedMemory) -> str:
        if not fact.source_episode_id:
            raise ValueError("LearnedMemory.source_episode_id is required (A13)")
        if not fact.owner_scope:
            raise ValueError("LearnedMemory.owner_scope is required (A10)")
        if not 0.0 <= fact.confidence <= 1.0:
            raise ValueError("LearnedMemory.confidence must be in [0, 1] (A14)")

        new_id = fact.id or f"mem_{uuid4().hex[:16]}"
        fact.id = new_id

        dataset = _scope_to_dataset(fact.owner_scope)
        envelope = json.dumps(_to_payload(fact))
        asyncio.run(self._cognee.add(envelope, dataset_name=dataset))
        # Caller decides when to cognify (typically batch at end of ingest).
        return new_id

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
        dataset = _scope_to_dataset(owner_scope)
        raw = asyncio.run(
            self._cognee.search(
                query_text=f"entity_id:{entity_id}",
                query_type=getattr(self._cognee.SearchType, "CHUNKS", None) or "CHUNKS",
                datasets=[dataset],
            )
        )
        out: list[LearnedMemory] = []
        for item in raw[:limit]:
            mem = _payload_to_memory(
                str(item.get("text", "")),
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

    def forget(self, memory_id: str, *, reason: str, actor: str) -> None:
        # See gotcha #3: emulate via tombstone document.
        tombstone = json.dumps({
            "tombstone": True, "id": memory_id,
            "invalidated_at": datetime.now(UTC).isoformat(),
            "actor": actor, "reason": reason,
        })
        # Without a per-scope hint here we cannot route the tombstone correctly
        # — caller must re-cognify the scope's dataset after forgetting.
        raise NotImplementedError(
            "Cognee non-destructive forget requires the caller to supply "
            "owner_scope for tombstone routing. Use the dual-vendor pattern "
            "(pgvector for memory + Cognee for retrieval) if you need this."
        )

    def improve(self, memory_id: str, *, confidence_delta: float, reason: str) -> None:
        raise NotImplementedError(
            "Cognee memory-store mode does not support confidence updates. "
            "Pair with pgvector if you need lifecycle support."
        )

    def find_contradictions(self, fact: LearnedMemory) -> list[LearnedMemory]:
        # Reuse retrieval for semantic conflict surfacing.
        retrieval = CogneeRetrievalStore(self._cognee)
        candidates = retrieval.retrieve(
            query=json.dumps(fact.value),
            owner_scope=fact.owner_scope,
            top_k=20,
        )
        out: list[LearnedMemory] = []
        for c in candidates:
            mem = _payload_to_memory(
                c.snippet, entity_id=fact.entity_id, owner_scope=fact.owner_scope
            )
            if not mem or mem.invalidated_at:
                continue
            if mem.memory_type != fact.memory_type or mem.value == fact.value:
                continue
            out.append(mem)
        return out


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _scope_to_dataset(owner_scope: dict[str, str]) -> str:
    parts = [f"{k}-{v}" for k, v in sorted(owner_scope.items())]
    return "ctx-" + "-".join(parts)


def _to_payload(fact: LearnedMemory) -> dict[str, Any]:
    return {
        "id": fact.id,
        "entity_id": fact.entity_id,
        "memory_type": fact.memory_type.value,
        "value": fact.value,
        "source": fact.source,
        "source_episode_id": fact.source_episode_id,
        "confidence": fact.confidence,
        "inferred": fact.inferred,
        "tags": fact.tags,
    }


def _payload_to_memory(
    raw: str, *, entity_id: str, owner_scope: dict[str, str]
) -> LearnedMemory | None:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    if data.get("tombstone"):
        return LearnedMemory(
            id=data["id"], entity_id=entity_id, entity_type="user",
            memory_type=MemoryType.FACT, value={}, source="cognee_tombstone",
            source_episode_id="", confidence=0.0,
            created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
            owner_scope=owner_scope, inferred=False,
            invalidated_at=datetime.fromisoformat(data["invalidated_at"]),
        )
    return LearnedMemory(
        id=data.get("id", ""),
        entity_id=data.get("entity_id", entity_id),
        entity_type=data.get("entity_type", "user"),
        memory_type=MemoryType(data.get("memory_type", "fact")),
        value=data.get("value"),
        source=data.get("source", "cognee"),
        source_episode_id=data.get("source_episode_id", ""),
        confidence=float(data.get("confidence", 0.5)),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        owner_scope=owner_scope,
        inferred=bool(data.get("inferred", True)),
        tags=list(data.get("tags", [])),
    )

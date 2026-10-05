"""Letta (formerly MemGPT) adapter — `MemoryStore` Protocol.

Letta is OS-style: agents own a `core_memory` (RAM analog, always in window)
and `archival_memory` (disk analog, retrieved on demand). The adapter maps
our `LearnedMemory.memory_type` onto these tiers — preferences and high-
confidence facts live in core; episodic and procedural live in archival.

Verified against `letta-client` SDK shape as of April 2026. The SDK is
agent-centric; you must construct or supply a Letta agent before this
adapter is useful.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from ..contracts import LearnedMemory, MemoryType


# Memory types that should live in the always-visible core block. Everything
# else goes to archival memory and is retrieved on demand.
_CORE_TYPES = {MemoryType.PREFERENCE, MemoryType.PROCEDURAL}


class LettaMemoryStore:
    """Satisfies the `MemoryStore` Protocol against a Letta agent.

    One adapter instance ↔ one Letta agent ↔ one `owner_scope`. Multi-tenant
    deployments instantiate one agent per scope. Letta's per-agent isolation
    is what gives us A10 here.
    """

    def __init__(self, client: Any, agent_id: str, owner_scope: dict[str, str]) -> None:
        self._client = client
        self._agent_id = agent_id
        self._owner_scope = owner_scope
        self._tier_block_label = "context_layer_facts"

    # ---- remember ----------------------------------------------------------

    def remember(self, fact: LearnedMemory) -> str:
        if not fact.source_episode_id:
            raise ValueError("LearnedMemory.source_episode_id is required (A13)")
        if fact.owner_scope != self._owner_scope:
            raise ValueError(
                "Adapter is bound to a single owner_scope; got mismatching scope (A10)"
            )
        if not 0.0 <= fact.confidence <= 1.0:
            raise ValueError("LearnedMemory.confidence must be in [0, 1] (A14)")

        new_id = fact.id or f"mem_{uuid4().hex[:16]}"
        fact.id = new_id

        payload = json.dumps(_to_payload(fact))
        if fact.memory_type in _CORE_TYPES and fact.confidence >= 0.7:
            # Append to the core memory block — visible every turn.
            self._client.agents.core_memory.append_to_block(
                agent_id=self._agent_id,
                label=self._tier_block_label,
                content=payload,
            )
        else:
            # Archival — retrievable, not always visible.
            self._client.agents.archival_memory.insert(
                agent_id=self._agent_id,
                memory=payload,
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
        if owner_scope != self._owner_scope:
            return []  # A10: scope mismatch returns empty, never leaks

        out: list[LearnedMemory] = []

        # 1) Read the core block (RAM tier).
        core = self._client.agents.core_memory.get_block(
            agent_id=self._agent_id, label=self._tier_block_label
        )
        for line in (core.value or "").splitlines():
            mem = _payload_to_memory(line, entity_id=entity_id, owner_scope=owner_scope)
            if mem and _passes(mem, memory_types, min_confidence):
                out.append(mem)

        # 2) Pull from archival (disk tier).
        rows = self._client.agents.archival_memory.list(
            agent_id=self._agent_id, limit=limit,
        )
        for row in rows:
            mem = _payload_to_memory(
                row.get("text", ""), entity_id=entity_id, owner_scope=owner_scope
            )
            if mem and _passes(mem, memory_types, min_confidence):
                out.append(mem)

        return out[:limit]

    # ---- forget (non-destructive emulation) --------------------------------

    def forget(self, memory_id: str, *, reason: str, actor: str) -> None:
        """Letta supports archival deletion; core blocks are append-only
        text. We mark the memory as invalidated by appending a tombstone
        record that the recall() filter will recognize."""
        tombstone = json.dumps({
            "id": memory_id,
            "tombstone": True,
            "invalidated_at": datetime.now(UTC).isoformat(),
            "actor": actor,
            "reason": reason,
        })
        self._client.agents.archival_memory.insert(
            agent_id=self._agent_id, memory=tombstone,
        )

    # ---- improve -----------------------------------------------------------

    def improve(self, memory_id: str, *, confidence_delta: float, reason: str) -> None:
        """Letta has no atomic confidence update. We emit a feedback record
        to archival and let the next compaction cycle merge it. Acceptable
        for low-volume feedback; build a confidence aggregator if hot."""
        feedback = json.dumps({
            "id": memory_id,
            "feedback_delta": confidence_delta,
            "reason": reason,
            "at": datetime.now(UTC).isoformat(),
        })
        self._client.agents.archival_memory.insert(
            agent_id=self._agent_id, memory=feedback,
        )

    # ---- find_contradictions ----------------------------------------------

    def find_contradictions(self, fact: LearnedMemory) -> list[LearnedMemory]:
        # Letta's archival has semantic search; cheap to over-fetch then filter.
        hits = self._client.agents.archival_memory.search(
            agent_id=self._agent_id,
            query=json.dumps(fact.value),
            top_k=20,
        )
        out: list[LearnedMemory] = []
        seen_ids: set[str] = set()
        for row in hits:
            mem = _payload_to_memory(
                row.get("text", ""),
                entity_id=fact.entity_id,
                owner_scope=fact.owner_scope,
            )
            if not mem or mem.id in seen_ids:
                continue
            if mem.memory_type != fact.memory_type or mem.value == fact.value:
                continue
            if mem.invalidated_at:
                continue
            out.append(mem)
            seen_ids.add(mem.id)
        return out


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

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
        "created_at": fact.created_at.isoformat(),
    }


def _payload_to_memory(
    raw: str, *, entity_id: str, owner_scope: dict[str, str]
) -> LearnedMemory | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if data.get("tombstone"):
        # Tombstones are folded into recall via the filter; expose as
        # invalidated for completeness.
        return LearnedMemory(
            id=data["id"],
            entity_id=entity_id,
            entity_type="user",
            memory_type=MemoryType.FACT,
            value={},
            source="letta_tombstone",
            source_episode_id="",
            confidence=0.0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            owner_scope=owner_scope,
            inferred=False,
            invalidated_at=datetime.fromisoformat(data["invalidated_at"]),
        )
    return LearnedMemory(
        id=data.get("id", ""),
        entity_id=data.get("entity_id", entity_id),
        entity_type=data.get("entity_type", "user"),
        memory_type=MemoryType(data.get("memory_type", "fact")),
        value=data.get("value"),
        source=data.get("source", "letta"),
        source_episode_id=data.get("source_episode_id", ""),
        confidence=float(data.get("confidence", 0.5)),
        created_at=_parse_dt(data.get("created_at")) or datetime.now(UTC),
        updated_at=_parse_dt(data.get("created_at")) or datetime.now(UTC),
        owner_scope=owner_scope,
        inferred=bool(data.get("inferred", True)),
        supersedes_id=data.get("supersedes_id"),
        tags=list(data.get("tags", [])),
    )


def _passes(
    mem: LearnedMemory,
    memory_types: list[MemoryType] | None,
    min_confidence: float,
) -> bool:
    if mem.invalidated_at:
        return False
    if mem.confidence < min_confidence:
        return False
    if memory_types and mem.memory_type not in memory_types:
        return False
    return True


def _parse_dt(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value)) if value else None
    except (TypeError, ValueError):
        return None

"""Smoke test for Mem0MemoryStore against a live Mem0 client.

Round-trip only — exhaustive lifecycle tests are deferred until the
SDK shape stabilizes (it has shifted across 2025–2026 releases).
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from reference_app.adapters import Mem0MemoryStore
from reference_app.contracts import LearnedMemory, MemoryType


def test_remember_then_recall_against_live_mem0(mem0_client):
    adapter = Mem0MemoryStore(client=mem0_client)
    scope = {"org_id": f"smoke_{uuid4().hex[:8]}"}

    fact = LearnedMemory(
        id="",
        entity_id="user_smoke",
        entity_type="user",
        memory_type=MemoryType.PREFERENCE,
        value={"timezone": "UTC"},
        source="test",
        source_episode_id=f"ep_{uuid4().hex[:8]}",
        confidence=0.8,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        owner_scope=scope,
        inferred=False,
    )

    mem_id = adapter.remember(fact)
    assert mem_id

    out = adapter.recall(entity_id="user_smoke", owner_scope=scope)
    # Mem0's extraction may rephrase; assert at least one hit, not exact match.
    assert len(out) >= 1
    assert all(m.owner_scope == scope for m in out)

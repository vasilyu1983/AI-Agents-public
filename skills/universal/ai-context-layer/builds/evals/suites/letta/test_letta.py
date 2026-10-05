"""Smoke test for LettaMemoryStore against a live Letta agent."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from reference_app.adapters import LettaMemoryStore
from reference_app.contracts import LearnedMemory, MemoryType


def test_remember_then_recall_against_live_letta(letta_client, letta_agent_id):
    scope = {"org_id": f"smoke_{uuid4().hex[:8]}"}
    adapter = LettaMemoryStore(
        client=letta_client, agent_id=letta_agent_id, owner_scope=scope
    )

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
    assert any(m.id == mem_id for m in out)

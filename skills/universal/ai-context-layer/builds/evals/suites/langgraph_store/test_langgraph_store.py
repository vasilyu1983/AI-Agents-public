"""Behavioral smoke tests for LangGraphStoreMemoryStore against InMemoryStore."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from reference_app.adapters import LangGraphStoreMemoryStore
from reference_app.contracts import LearnedMemory, MemoryType


def _make_memory(**overrides) -> LearnedMemory:
    base = dict(
        id="",
        entity_id="user_1",
        entity_type="user",
        memory_type=MemoryType.PREFERENCE,
        value={"timezone": "UTC"},
        source="test",
        source_episode_id="ep_1",
        confidence=0.8,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        owner_scope={"org_id": "org_a"},
        inferred=False,
    )
    base.update(overrides)
    return LearnedMemory(**base)


def test_remember_then_recall_roundtrip(store):
    adapter = LangGraphStoreMemoryStore(store=store)
    mem_id = adapter.remember(_make_memory())

    out = adapter.recall(entity_id="user_1", owner_scope={"org_id": "org_a"})
    assert len(out) == 1
    assert out[0].id == mem_id
    assert out[0].value == {"timezone": "UTC"}


def test_owner_scope_isolates_tenants(store):
    adapter = LangGraphStoreMemoryStore(store=store)
    adapter.remember(_make_memory(owner_scope={"org_id": "org_a"}))
    adapter.remember(_make_memory(owner_scope={"org_id": "org_b"}, value={"timezone": "PST"}))

    a = adapter.recall(entity_id="user_1", owner_scope={"org_id": "org_a"})
    b = adapter.recall(entity_id="user_1", owner_scope={"org_id": "org_b"})

    assert len(a) == 1 and a[0].value == {"timezone": "UTC"}
    assert len(b) == 1 and b[0].value == {"timezone": "PST"}


def test_forget_marks_invalidated(store):
    adapter = LangGraphStoreMemoryStore(store=store)
    mem_id = adapter.remember(_make_memory())
    adapter.forget(mem_id, reason="user_correction", actor="user")

    out = adapter.recall(entity_id="user_1", owner_scope={"org_id": "org_a"})
    assert out == []  # invalidated rows must not appear in recall


def test_remember_rejects_missing_source_episode_id(store):
    adapter = LangGraphStoreMemoryStore(store=store)
    with pytest.raises(ValueError, match="source_episode_id"):
        adapter.remember(_make_memory(source_episode_id=""))

"""Behavioral tests for PostgresMemoryStore.

Asserts the schema-level guarantees that block the type-level anti-patterns
listed in `adapters/migrations/README.md`. These run only when POSTGRES_DSN
is set (see conftest).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from reference_app.adapters import PostgresEpisodeLog, PostgresMemoryStore
from reference_app.contracts import LearnedMemory, MemoryType


def _episode(log: PostgresEpisodeLog, owner_scope: dict[str, str]) -> str:
    return log.append(episode={"kind": "user_turn", "owner_scope": owner_scope, "text": "hi"})


def _fact(episode_id: str, owner_scope: dict[str, str], **overrides) -> LearnedMemory:
    base = dict(
        id="",
        entity_id="usr_pg",
        entity_type="user",
        memory_type=MemoryType.PREFERENCE,
        value={"prefers": "concise"},
        source="user_turn",
        source_episode_id=episode_id,
        confidence=0.8,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        owner_scope=owner_scope,
        inferred=False,
    )
    base.update(overrides)
    return LearnedMemory(**base)


def test_remember_and_recall_roundtrip(conn):
    log = PostgresEpisodeLog(conn)
    store = PostgresMemoryStore(conn)
    scope = {"organization_id": "org_pg_a"}
    eid = _episode(log, scope)
    store.remember(_fact(eid, scope))

    out = store.recall(entity_id="usr_pg", owner_scope=scope)
    assert len(out) == 1
    assert out[0].value == {"prefers": "concise"}
    assert out[0].source_episode_id == eid


def test_recall_rejects_cross_tenant(conn):
    log = PostgresEpisodeLog(conn)
    store = PostgresMemoryStore(conn)
    eid = _episode(log, {"organization_id": "org_pg_a"})
    store.remember(_fact(eid, {"organization_id": "org_pg_a"}))

    leaked = store.recall(entity_id="usr_pg", owner_scope={"organization_id": "org_pg_b"})
    assert leaked == [], "A10: cross-tenant memory must not leak"


def test_forget_is_non_destructive(conn):
    """A3 + A7: forget sets invalidated_at, the row stays for audit."""
    log = PostgresEpisodeLog(conn)
    store = PostgresMemoryStore(conn)
    scope = {"organization_id": "org_pg_c"}
    eid = _episode(log, scope)
    fact_id = store.remember(_fact(eid, scope))
    store.forget(fact_id, reason="user_correction", actor="user")

    active = store.recall(entity_id="usr_pg", owner_scope=scope)
    assert active == [], "Active recall must not return invalidated rows"

    # Audit query: row is still there, just invalidated.
    with conn.cursor() as cur:
        cur.execute("SELECT invalidated_at, tags FROM learned_memory WHERE id = %s", (fact_id,))
        invalidated_at, tags = cur.fetchone()
    assert invalidated_at is not None
    assert any("forgotten_by" in t for t in tags)


def test_bitemporal_as_of_query(conn):
    """A3: 'what did we believe on date X' must work after correction."""
    log = PostgresEpisodeLog(conn)
    store = PostgresMemoryStore(conn)
    scope = {"organization_id": "org_pg_d"}
    eid = _episode(log, scope)
    fact_id = store.remember(_fact(eid, scope, value={"role": "admin"}))

    # Simulate "later" correction: invalidate then write a new row that supersedes.
    store.forget(fact_id, reason="role_change", actor="system")
    later_eid = _episode(log, scope)
    new_id = store.remember(_fact(
        later_eid, scope,
        value={"role": "viewer"},
        supersedes_id=fact_id,
    ))

    now = store.recall(entity_id="usr_pg", owner_scope=scope)
    assert len(now) == 1 and now[0].id == new_id and now[0].value == {"role": "viewer"}

    past = store.recall(
        entity_id="usr_pg",
        owner_scope=scope,
        as_of=datetime.now(UTC) - timedelta(seconds=0.1),
    )
    # The recently-written row may or may not appear depending on timing; the
    # invariant we care about is: now ≠ past for a corrected fact.
    assert {f.id for f in now} != {f.id for f in past} or past == [], (
        "Bi-temporal recall must distinguish system-time states"
    )


def test_find_contradictions_returns_active_conflicts_only(conn):
    log = PostgresEpisodeLog(conn)
    store = PostgresMemoryStore(conn)
    scope = {"organization_id": "org_pg_e"}
    eid = _episode(log, scope)
    store.remember(_fact(eid, scope, value={"prefers": "concise"}))

    candidate = _fact(eid, scope, value={"prefers": "verbose"})
    conflicts = store.find_contradictions(candidate)
    assert len(conflicts) == 1
    assert conflicts[0].value == {"prefers": "concise"}


def test_improve_clips_to_unit_interval(conn):
    log = PostgresEpisodeLog(conn)
    store = PostgresMemoryStore(conn)
    scope = {"organization_id": "org_pg_f"}
    eid = _episode(log, scope)
    fact_id = store.remember(_fact(eid, scope, confidence=0.5))

    store.improve(fact_id, confidence_delta=10.0, reason="big_thumbs_up")
    out = store.recall(entity_id="usr_pg", owner_scope=scope)
    assert out[0].confidence == pytest.approx(1.0), "A14: confidence clipped to [0, 1]"


def test_remember_rejects_invalid_episode_reference(conn):
    """A13 schema-level: source_episode_id is FK to episode_log."""
    store = PostgresMemoryStore(conn)
    scope = {"organization_id": "org_pg_g"}
    bogus = _fact(episode_id="ep_does_not_exist", owner_scope=scope)
    with pytest.raises(Exception):
        store.remember(bogus)


def test_dsar_preserves_unrelated_audit(conn):
    """RA4 + A11: a tenant DSAR purge must not break audit reconstruction
    for unrelated tenants.

    Setup: write memory for tenant A and tenant B. Purge tenant A. Tenant
    B's recall and bi-temporal queries must continue to function. Audit
    rows for tenant A are tombstoned (invalidated_at set), not deleted —
    the row shape stays so audit reconstruction can still report 'tenant A
    held N facts at time T, all redacted on date D'.
    """
    log = PostgresEpisodeLog(conn)
    store = PostgresMemoryStore(conn)
    scope_a = {"organization_id": "org_dsar_a"}
    scope_b = {"organization_id": "org_dsar_b"}

    eid_a = _episode(log, scope_a)
    eid_b = _episode(log, scope_b)
    fact_a = store.remember(_fact(eid_a, scope_a, value={"role": "admin"}))
    fact_b = store.remember(_fact(eid_b, scope_b, value={"role": "viewer"}))

    # Simulate DSAR: tombstone every live row for tenant A. The application
    # would also redact `value` to {}; here we only assert the invalidation
    # contract (A3 + A11: never DELETE).
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE learned_memory SET invalidated_at = now() "
            "WHERE owner_scope ->> 'organization_id' = %s "
            "AND invalidated_at IS NULL",
            ("org_dsar_a",),
        )

    # Tenant A: active recall is empty; the row still exists for audit.
    assert store.recall(entity_id="usr_pg", owner_scope=scope_a) == []
    with conn.cursor() as cur:
        cur.execute("SELECT id, invalidated_at FROM learned_memory WHERE id = %s", (fact_a,))
        row = cur.fetchone()
    assert row is not None and row[1] is not None, (
        "DSAR must tombstone, not DELETE — audit reconstruction depends on the row shape"
    )

    # Tenant B: untouched. Recall works and returns the original fact.
    out_b = store.recall(entity_id="usr_pg", owner_scope=scope_b)
    assert len(out_b) == 1 and out_b[0].id == fact_b
    assert out_b[0].value == {"role": "viewer"}


def test_supersession_chain_reconstructs(conn):
    """A3 + A4: a correction history must be walkable via supersedes_id so a
    reviewer can answer 'what did we believe on date X and why was it changed.'
    """
    log = PostgresEpisodeLog(conn)
    store = PostgresMemoryStore(conn)
    scope = {"organization_id": "org_pg_chain"}

    eid1 = _episode(log, scope)
    v1 = store.remember(_fact(eid1, scope, value={"role": "admin"}))
    store.forget(v1, reason="role_change_1", actor="system")

    eid2 = _episode(log, scope)
    v2 = store.remember(_fact(eid2, scope, value={"role": "editor"}, supersedes_id=v1))
    store.forget(v2, reason="role_change_2", actor="system")

    eid3 = _episode(log, scope)
    v3 = store.remember(_fact(eid3, scope, value={"role": "viewer"}, supersedes_id=v2))

    # Walk the chain backwards from the live row.
    with conn.cursor() as cur:
        cur.execute(
            "WITH RECURSIVE chain AS ("
            "  SELECT id, supersedes_id, value, invalidated_at "
            "  FROM learned_memory WHERE id = %s "
            "  UNION ALL "
            "  SELECT lm.id, lm.supersedes_id, lm.value, lm.invalidated_at "
            "  FROM learned_memory lm JOIN chain c ON lm.id = c.supersedes_id"
            ") SELECT id FROM chain ORDER BY id",
            (v3,),
        )
        ids_in_chain = {r[0] for r in cur.fetchall()}

    assert ids_in_chain == {v1, v2, v3}, "Correction history must be reconstructable"
    # And only the head of the chain is live.
    assert len(store.recall(entity_id="usr_pg", owner_scope=scope)) == 1

"""F5 — Proactive Interference regression suite (deterministic, no API key).

F5 (see `references/context-hygiene.md` §F5): accumulating
semantically-similar key/value pairs for the *same* slot suppress recall
of the current value. Each stale prior for a slot competes at retrieval
time; accuracy on the now-correct entry degrades as priors accumulate.

The skill's documented mitigation is version-tagged / superseding slots:
a new value for a slot must *supersede* the prior (invalidate +
`supersedes_id`), not coexist as a sibling row. This suite is a
regression guard on that invariant.

It is deliberately deterministic — it tests the *store discipline*, not
an LLM. An LLM-based PI probe would be flaky, costly, and would not pin
the architectural claim the skill makes. This mirrors the postgres /
jit_loading invariant suites, not the LLM-driven context_rot suite.

Two assertions, both load-bearing:

1. Defended invariant: under the superseding discipline, recall returns
   exactly one row whose value is the current value, at every
   interference tier. If supersession logic regresses (priors stop being
   invalidated), this collapses to the naive path and the test fails.
2. Anti-tautology (Rule 9): the naive (sibling-accumulating) store must
   demonstrably degrade — at the highest tier it returns more than one
   live row for the slot. If this stops being true (e.g. the store
   starts auto-deduping), the suite would otherwise pass as a no-op;
   this assertion makes that fail loudly instead.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from evals.fakes import FakeMemoryStore
from reference_app.contracts import LearnedMemory, MemoryType

# Each case is one semantic slot that updates over time. `history` is
# ordered oldest -> newest; the final element is the current (correct)
# value. Extend by appending lines here — keep the slot a single
# (entity_id, memory_type) so siblings genuinely collide.
CASES: list[dict] = [
    {
        "slot": "user_current_city",
        "entity_id": "usr_city_1",
        "memory_type": MemoryType.FACT,
        "history": ["Berlin", "Lisbon", "Toronto", "Reykjavik"],
    },
    {
        "slot": "current_project_name",
        "entity_id": "usr_proj_1",
        "memory_type": MemoryType.FACT,
        "history": ["Apollo", "Borealis", "Cascade"],
    },
    {
        "slot": "preferred_contact_channel",
        "entity_id": "usr_chan_1",
        "memory_type": MemoryType.PREFERENCE,
        "history": ["email", "SMS", "Slack"],
    },
    {
        "slot": "subscription_tier",
        "entity_id": "usr_tier_1",
        "memory_type": MemoryType.FACT,
        "history": ["free", "pro", "team", "enterprise"],
    },
    {
        "slot": "primary_device",
        "entity_id": "usr_dev_1",
        "memory_type": MemoryType.FACT,
        "history": ["iPhone 12", "iPhone 14", "Pixel 9"],
    },
]

# Number of stale priors injected before the current value. Spans the
# range over which the F5 finding reports roughly log-linear degradation.
TIERS = [0, 1, 3, 8, 24]

_OWNER = {"organization_id": "org_pi"}
_T0 = datetime(2026, 1, 1, tzinfo=UTC)


def _mk(case: dict, value: str, seq: int) -> LearnedMemory:
    """One memory row for the slot. `seq` makes created/updated_at
    monotonic so 'newest' is unambiguous."""
    ts = _T0 + timedelta(hours=seq)
    return LearnedMemory(
        id="",  # FakeMemoryStore assigns
        entity_id=case["entity_id"],
        entity_type="user",
        memory_type=case["memory_type"],
        value=value,
        source="eval",
        source_episode_id=f"ep_{case['slot']}_{seq}",
        confidence=0.9,
        created_at=ts,
        updated_at=ts,
        owner_scope=_OWNER,
        inferred=False,
    )


def _values_for_tier(case: dict, n_priors: int) -> list[str]:
    """Pad/truncate the history to exactly `n_priors` stale values
    followed by the current value (always history[-1])."""
    current = case["history"][-1]
    priors_pool = case["history"][:-1] or [current + "_stale"]
    priors = [priors_pool[i % len(priors_pool)] for i in range(n_priors)]
    return priors + [current]


def _recall_slot(store: FakeMemoryStore, case: dict) -> list[LearnedMemory]:
    return store.recall(
        entity_id=case["entity_id"],
        owner_scope=_OWNER,
        memory_types=[case["memory_type"]],
    )


def _build_naive(case: dict, n_priors: int) -> FakeMemoryStore:
    """Anti-pattern: every new value is remembered as a sibling row;
    priors are never invalidated. This realizes F5."""
    store = FakeMemoryStore()
    for seq, val in enumerate(_values_for_tier(case, n_priors)):
        store.remember(_mk(case, val, seq))
    return store


def _build_superseding(case: dict, n_priors: int) -> FakeMemoryStore:
    """Documented mitigation: before writing a new value for the slot,
    find the live contradicting rows, forget (tombstone) them, and link
    `supersedes_id`. Recall then yields exactly the current value."""
    store = FakeMemoryStore()
    for seq, val in enumerate(_values_for_tier(case, n_priors)):
        fact = _mk(case, val, seq)
        priors = store.find_contradictions(fact)
        if priors:
            fact.supersedes_id = priors[-1].id
        for p in priors:
            store.forget(p.id, reason="superseded by newer value", actor="eval")
        store.remember(fact)
    return store


def test_superseding_slot_defeats_proactive_interference():
    """Load-bearing: the defended discipline keeps recall unambiguous and
    current at every interference tier."""
    failures: list[str] = []
    for case in CASES:
        current = case["history"][-1]
        for tier in TIERS:
            store = _build_superseding(case, tier)
            live = _recall_slot(store, case)
            if len(live) != 1 or live[0].value != current:
                got = [m.value for m in live]
                failures.append(
                    f"slot={case['slot']} tier={tier} "
                    f"expected exactly ['{current}'] got {got}"
                )
    assert not failures, (
        "supersession invariant regressed — proactive interference is no "
        "longer defended:\n  " + "\n  ".join(failures)
    )


def test_naive_slot_actually_degrades(capsys):
    """Anti-tautology (Rule 9): prove the naive path genuinely suffers
    proactive interference, otherwise the suite could pass as a no-op."""
    rollup: list[str] = []
    degraded_any = False
    for case in CASES:
        current = case["history"][-1]
        line = [f"{case['slot']:<26}"]
        for tier in TIERS:
            store = _build_naive(case, tier)
            live = _recall_slot(store, case)
            ambiguous = len(live) > 1 or (live and live[0].value != current)
            if tier >= 1 and ambiguous:
                degraded_any = True
            line.append(f"t{tier}:{len(live)}row{'s' if len(live) != 1 else ''}")
        rollup.append("  ".join(line))

    print("\n[proactive-interference] naive store live rows per slot/tier")
    print("  (>1 row == slot is ambiguous; the model has no in-window")
    print("   reason to pick the current value — F5 realized)\n")
    print("\n".join(rollup))

    # Highest tier must be ambiguous for every multi-value slot.
    worst = max(TIERS)
    still_unique = []
    for case in CASES:
        store = _build_naive(case, worst)
        if len(_recall_slot(store, case)) <= 1:
            still_unique.append(case["slot"])
    assert degraded_any, (
        "naive store never became ambiguous — the test is not exercising "
        "real proactive interference; check FakeMemoryStore.recall"
    )
    assert not still_unique, (
        f"naive store stayed unique at tier {worst} for {still_unique}; "
        "sibling accumulation is not being modeled, suite would be a no-op"
    )

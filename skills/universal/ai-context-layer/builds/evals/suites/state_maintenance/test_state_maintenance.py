"""State-maintenance regression suite (deterministic, no API key).

Guards the P22 / A38 / A39 discipline from `references/patterns-catalog.md`
and `references/anti-patterns-catalog.md`: current state is derived from a
deduplicated event log ordered by effective time, filtered by source
authority, and stored as bi-temporal `LearnedMemory` rows.

Four invariants, using the INC-42 running example from
`references/evals-and-operations.md` §State-Maintenance Eval:

1. Replay invariance: shuffling arrival order and redelivering events never
   changes the current value, the history, or any as-of answer (A39).
2. Stale secondary signals (index refresh, summary, chat topic) never
   override the system-of-record value; they surface as candidates (A38).
3. As-of answers follow `valid_from <= t < valid_to`.
4. Anti-tautology: the naive arrival-order, last-writer-wins reducer gets
   this stream wrong, so the suite cannot pass as a no-op.

Like the proactive-interference suite, the defended reducer lives here: the
suite pins the discipline and the contract fields it needs, not a model.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import UTC, datetime

from evals.fakes import FakeMemoryStore
from reference_app.contracts import LearnedMemory, MemoryType

_OWNER = {"organization_id": "org_state"}
ENTITY = "INC-42"

# Source precedence: higher wins regardless of arrival time or effective time.
AUTHORITY = {"system_of_record": 3, "index_refresh": 1, "summary": 1, "chat_topic": 1}


def _t(hh: int, mm: int) -> datetime:
    return datetime(2026, 3, 2, hh, mm, tzinfo=UTC)


@dataclass(frozen=True)
class Event:
    event_id: str
    value: str
    valid_from: datetime
    source: str


# Arrival order as a consumer would see it. The true change is Alice -> Bob
# at 09:10; everything after it is noise the reducer must survive.
STREAM: list[Event] = [
    Event("ev-1", "Alice", _t(8, 0), "system_of_record"),
    Event("ev-2", "Bob", _t(9, 10), "system_of_record"),
    Event("ev-2", "Bob", _t(9, 10), "system_of_record"),   # redelivered
    Event("ev-3", "Alice", _t(9, 11), "index_refresh"),    # stale index row
    Event("ev-4", "Alice", _t(9, 15), "summary"),          # misleading summary
    Event("ev-5", "Alice", _t(9, 0), "system_of_record"),  # late backfill of a 09:00 snapshot
    Event("ev-6", "Alice", _t(9, 20), "chat_topic"),       # stale secondary source
]

EXPECTED_CURRENT = "Bob"
EXPECTED_HISTORY = [("Alice", _t(8, 0), _t(9, 10)), ("Bob", _t(9, 10), None)]
EXPECTED_AS_OF = {_t(7, 0): None, _t(9, 5): "Alice", _t(9, 10): "Bob", _t(12, 0): "Bob"}
EXPECTED_CANDIDATES = {"ev-3", "ev-4", "ev-6"}


def _row(value: str, start: datetime, end: datetime | None, ev: Event) -> LearnedMemory:
    return LearnedMemory(
        id="",
        entity_id=ENTITY,
        entity_type="incident",
        memory_type=MemoryType.FACT,
        value=value,
        source=ev.source,
        source_episode_id=ev.event_id,
        confidence=1.0,
        created_at=start,
        updated_at=start,
        owner_scope=_OWNER,
        inferred=False,
        valid_from=start,
        valid_to=end,
    )


def defended_reducer(stream: list[Event]) -> tuple[FakeMemoryStore, set[str]]:
    """Dedupe on event_id, keep only top-authority events, order by effective
    time, merge repeated values, and write closed intervals linked by
    supersedes_id. Lower-authority events become review candidates."""
    unique = {ev.event_id: ev for ev in stream}.values()
    top = max(AUTHORITY[ev.source] for ev in unique)
    applied = sorted((ev for ev in unique if AUTHORITY[ev.source] == top),
                     key=lambda ev: (ev.valid_from, ev.event_id))
    candidates = {ev.event_id for ev in unique if AUTHORITY[ev.source] < top}

    intervals: list[tuple[str, datetime, Event]] = []
    for ev in applied:
        if intervals and intervals[-1][0] == ev.value:
            continue  # a snapshot that confirms the running value is not a transition
        intervals.append((ev.value, ev.valid_from, ev))

    store = FakeMemoryStore()
    prior_id = None
    for i, (value, start, ev) in enumerate(intervals):
        end = intervals[i + 1][1] if i + 1 < len(intervals) else None
        row = _row(value, start, end, ev)
        row.supersedes_id = prior_id
        prior_id = store.remember(row)
    return store, candidates


def naive_reducer(stream: list[Event]) -> FakeMemoryStore:
    """Anti-pattern A38 + A39: apply in arrival order, last writer wins, no
    idempotency, no authority check."""
    store = FakeMemoryStore()
    for ev in stream:
        for live in _rows(store):
            if live.valid_to is None:
                live.valid_to = ev.valid_from
        store.remember(_row(ev.value, ev.valid_from, None, ev))
    return store


def _rows(store: FakeMemoryStore) -> list[LearnedMemory]:
    return store.recall(entity_id=ENTITY, owner_scope=_OWNER, memory_types=[MemoryType.FACT])


def current(store: FakeMemoryStore) -> str | None:
    live = [r for r in _rows(store) if r.valid_to is None]
    return live[-1].value if live else None


def as_of(store: FakeMemoryStore, t: datetime) -> str | None:
    hits = [r for r in _rows(store)
            if r.valid_from <= t and (r.valid_to is None or t < r.valid_to)]
    return hits[-1].value if hits else None


def history(store: FakeMemoryStore) -> list[tuple]:
    return sorted(((r.value, r.valid_from, r.valid_to) for r in _rows(store)),
                  key=lambda h: h[1])


def test_replay_order_and_duplicates_do_not_change_state():
    rng = random.Random(42)
    failures = []
    for trial in range(50):
        stream = STREAM + rng.sample(STREAM, 3)  # extra redeliveries
        rng.shuffle(stream)
        store, candidates = defended_reducer(stream)
        got = (current(store), history(store), {t: as_of(store, t) for t in EXPECTED_AS_OF})
        want = (EXPECTED_CURRENT, EXPECTED_HISTORY, EXPECTED_AS_OF)
        if got != want or candidates != EXPECTED_CANDIDATES:
            failures.append(f"trial={trial} order={[e.event_id for e in stream]} got={got}")
    assert not failures, "replay changed state (A39):\n  " + "\n  ".join(failures[:5])


def test_stale_secondary_source_never_overrides_record():
    store, candidates = defended_reducer(STREAM)
    assert current(store) == EXPECTED_CURRENT, "a secondary source overrode the record (A38)"
    assert candidates == EXPECTED_CANDIDATES, f"secondary events not surfaced as candidates: {candidates}"
    sources = {r.source for r in _rows(store)}
    assert sources == {"system_of_record"}, f"state rows written from secondary sources: {sources}"


def test_as_of_queries_follow_validity_windows():
    store, _ = defended_reducer(STREAM)
    for t, want in EXPECTED_AS_OF.items():
        assert as_of(store, t) == want, f"as_of({t:%H:%M}) expected {want}, got {as_of(store, t)}"
    rows = sorted(_rows(store), key=lambda r: r.valid_from)
    assert rows[1].supersedes_id == rows[0].id, "transition rows are not linked by supersedes_id"


def test_naive_reducer_actually_fails_this_stream():
    """Anti-tautology: if the naive path passes, the stream is not testing anything."""
    store = naive_reducer(STREAM)
    wrong_current = current(store) != EXPECTED_CURRENT
    wrong_history = history(store) != EXPECTED_HISTORY
    assert wrong_current and wrong_history, (
        f"naive reducer matched the defended result (current={current(store)}); "
        "the stream no longer exercises A38/A39"
    )

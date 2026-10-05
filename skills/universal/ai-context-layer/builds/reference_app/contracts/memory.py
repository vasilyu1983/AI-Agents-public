from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class MemoryType(str, Enum):
    """The four memory types from the references. Add domain types only when
    a new lifecycle truly differs — most domain "memory" is just a `value`
    payload under one of these."""

    PREFERENCE = "preference"          # user-stated or model-inferred (track separately!)
    FACT = "fact"                      # durable claim about the entity or world
    EPISODIC = "episodic"              # time-stamped event reference
    PROCEDURAL = "procedural"          # learned how-to / playbook step


@dataclass(slots=True)
class LearnedMemory:
    """A typed, durable fact derived from an episode.

    Bi-temporal by design: `valid_from`/`valid_to` are *fact time* (when the
    claim was true in the world), `created_at`/`invalidated_at` are *system
    time* (when the system learned or corrected it). Preserve both — it's the
    only honest answer to "what did we know on date X" vs "what was true on
    date X". Storing only one collapses A3 (destructive overwrite) into your
    schema by accident.
    """

    id: str
    entity_id: str
    entity_type: str
    memory_type: MemoryType
    value: Any
    """The typed payload. Keep it small and structured; raw prose belongs in
    KnowledgeSource, not memory."""

    source: str
    """Human-readable origin: 'user_turn', 'support_ticket_42', 'crm_sync'."""

    source_episode_id: str
    """Stable pointer to the raw input the fact was derived from (A13). Without
    this, you cannot reverify, audit, or roll back. Required, not optional."""

    confidence: float
    """[0.0, 1.0]. Used by select() to filter noise and by the feedback loop
    to decay unreinforced inferences (A14, A26)."""

    created_at: datetime
    updated_at: datetime
    owner_scope: dict[str, str]
    """ACL/tenant scope. Memory leaks across tenants are A10 and a
    multi-tenant security incident waiting to happen."""

    inferred: bool
    """True if extracted from model output or implicit signal. False only if
    user-stated or system-of-record-derived. Critical for A26 mode-collapse
    defense — never extract from assistant turns and mark inferred=False."""

    valid_from: datetime | None = None
    valid_to: datetime | None = None
    invalidated_at: datetime | None = None
    """Set when the fact is *superseded by newer evidence* (non-destructive).
    Distinct from expires_at, which is TTL-based."""

    expires_at: datetime | None = None
    supersedes_id: str | None = None
    """Points at the prior memory row this one replaces. Lets you reconstruct
    'when did we first believe X' and roll back wrong corrections."""

    tags: list[str] = field(default_factory=list)

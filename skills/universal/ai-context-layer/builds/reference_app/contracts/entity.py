from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class EntityProfile:
    """A canonical pointer to an entity backed by operational truth (P1).

    `EntityProfile` is the *handle*, not the source of truth. Live values
    (billing state, plan, role, current usage) live in the operational store
    and are fetched through tools. The profile carries identity, ownership,
    and ACL scope so the assembly layer can scope memory and retrieval
    correctly without re-querying the system of record on every turn.
    """

    id: str
    entity_type: str
    """e.g. 'user', 'org', 'project'. Add domain types here, never invent
    parallel hierarchies in app code."""

    owner_scope: dict[str, str]
    """e.g. {"organization_id": "org_123"}. Used for ACL and tenant isolation."""

    source_of_truth: str
    """URI or service name where the live record lives. Memory lookups must
    cite this when conflicts arise (A2 blocked)."""

    updated_at: datetime
    acl_tags: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    """Domain-specific extension point. Avoid stuffing live state here —
    that belongs behind a tool. Use for stable descriptors (locale, timezone)
    that don't move per request."""

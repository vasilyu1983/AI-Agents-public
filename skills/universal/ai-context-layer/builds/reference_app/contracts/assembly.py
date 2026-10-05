from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from .knowledge import RetrievalResult
from .memory import LearnedMemory
from .runtime_refs import ArtifactRef, ContextRef, LoadedArtifact


@dataclass(slots=True)
class Projection:
    """How a bundle should be shaped before going to the model.

    `priority_order` is load-bearing for the `order` runtime verb — it sets
    the deterministic layout that keeps the KV cache warm. Do not randomize
    it across turns."""

    allowed_fields: list[str] = field(default_factory=list)
    max_tokens: int = 8000
    max_artifacts: int = 6
    max_inline_artifact_chars: int = 1200
    compression_strategy: str = "progressive_disclosure"
    """One of: 'progressive_disclosure' | 'summarize' | 'none'."""

    modality_budgets: dict[str, int] = field(
        default_factory=lambda: {
            "text_tokens": 8000,
            "artifacts": 6,
            "artifact_chars": 1200,
        }
    )

    priority_order: list[str] = field(
        default_factory=lambda: [
            "guardrails",
            "live_facts",
            "memory",
            "domain_evidence",
            "loaded_artifacts",
            "relationship_context",
        ]
    )


@dataclass(slots=True)
class ContextAssemblyRequest:
    """Input to the assembly layer. The assembly layer is the product-critical
    layer (stance #5) — different surfaces need different bundles,
    budgets, and trust levels, all driven from this request."""

    surface: str
    """e.g. 'chat', 'dashboard', 'email', 'ask'. Drives tool allowlist and
    bundle shape."""

    actor: dict[str, str]
    """e.g. {"entity_type": "user", "entity_id": "usr_123"}."""

    owner_scope: dict[str, str]
    intent: str
    """One-line description of what the user is trying to do on this surface.
    Drives select() relevance."""

    projection: Projection = field(default_factory=Projection)
    context_refs: list[ContextRef] = field(default_factory=list)
    artifact_refs: list[ArtifactRef] = field(default_factory=list)
    requested_at: datetime | None = None
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Guardrails:
    entitlements: list[str] = field(default_factory=list)
    privacy_constraints: list[str] = field(default_factory=list)
    freshness_requirements: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ContextBundle:
    """The output of the assembly layer. This is what goes into the prompt.

    Every bundle gets a stable `id` so feedback (`InlineReactionFeedback`)
    can correlate the user's reaction back to the exact assembly that
    produced the response."""

    id: str = field(default_factory=lambda: f"bndl_{uuid4().hex[:16]}")
    surface: str = ""
    actor: dict[str, str] = field(default_factory=dict)
    owner_scope: dict[str, str] = field(default_factory=dict)
    live_facts: list[dict[str, Any]] = field(default_factory=list)
    """From P1 tools. Always fetched at assembly time, never cached past the
    request — that's the whole point of operational truth."""

    memory: list[LearnedMemory] = field(default_factory=list)
    domain_evidence: list[RetrievalResult] = field(default_factory=list)
    context_refs: list[ContextRef] = field(default_factory=list)
    loaded_artifacts: list[LoadedArtifact] = field(default_factory=list)
    relationship_context: list[dict[str, Any]] = field(default_factory=list)
    """From P4 graph traversal, only when the surface needs it (A9)."""

    guardrails: Guardrails = field(default_factory=Guardrails)
    projection: Projection = field(default_factory=Projection)
    assembled_at: datetime | None = None
    token_count_estimate: int = 0
    """Used by eval harness to enforce budgets and detect F2 distraction risk."""

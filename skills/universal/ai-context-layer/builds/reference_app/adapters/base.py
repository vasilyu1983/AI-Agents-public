"""Adapter Protocols.

Each Protocol is the minimum surface the runtime verbs need. Concrete
implementations may expose more, but the runtime only depends on these.
Keep this file boring — adding a method here forces every adapter to update.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol, runtime_checkable

from ..contracts import (
    ArtifactRef,
    ContextAssemblyRequest,
    ContextRef,
    EntityProfile,
    LearnedMemory,
    LoadedArtifact,
    MemoryType,
    RetrievalResult,
)


@runtime_checkable
class MemoryStore(Protocol):
    """Storage for `LearnedMemory`. Backs P2/P5/P6.

    Lifecycle verbs (`remember`/`recall`/`forget`/`improve`) are exposed
    explicitly — A11 (no lifecycle verbs) is blocked at the type level.
    `forget` is non-destructive: it sets `invalidated_at` and (optionally)
    inserts a tombstone, never `DELETE`.
    """

    def remember(self, fact: LearnedMemory) -> str: ...
    """Insert a new memory. Returns the assigned id. Must reject inserts
    missing source_episode_id, owner_scope, or confidence (A13/A10/A14)."""

    def recall(
        self,
        *,
        entity_id: str,
        owner_scope: dict[str, str],
        memory_types: list[MemoryType] | None = None,
        min_confidence: float = 0.0,
        as_of: datetime | None = None,
        limit: int = 50,
    ) -> list[LearnedMemory]: ...
    """Bi-temporal read. `as_of` defaults to now; pass an earlier timestamp
    to ask 'what did we believe on date X'. ACL scope is mandatory."""

    def forget(self, memory_id: str, *, reason: str, actor: str) -> None: ...
    """Non-destructive invalidation. Records the reason for audit."""

    def improve(self, memory_id: str, *, confidence_delta: float, reason: str) -> None: ...
    """Confidence update from feedback (A14, A26). Clipped to [0, 1] at the
    adapter boundary."""

    def find_contradictions(self, fact: LearnedMemory) -> list[LearnedMemory]: ...
    """Ingest-time contradiction detection (A4 blocked). Returns memories
    that conflict with `fact` so the runtime can categorize and route to
    P4 invalidation."""


@runtime_checkable
class RetrievalStore(Protocol):
    """Storage for KnowledgeSource and the embedding index. Backs P8.

    Returns `RetrievalResult` already reranked and projected — never raw
    embedding hits (A18 blocked at the type level)."""

    def index(self, *, source_id: str, chunks: list[dict[str, Any]]) -> None: ...

    def retrieve(
        self,
        *,
        query: str,
        owner_scope: dict[str, str],
        top_k: int = 8,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]: ...

    def invalidate(self, source_id: str) -> None: ...
    """Mark all chunks for a source as stale. Re-index pulls fresh content."""


@runtime_checkable
class EpisodeLog(Protocol):
    """Append-only log of raw inputs (turns, events, tool calls).

    Every LearnedMemory.source_episode_id points here. This is the audit
    spine — never truncate or rewrite."""

    def append(self, *, episode: dict[str, Any]) -> str: ...
    def get(self, episode_id: str) -> dict[str, Any] | None: ...


@runtime_checkable
class OperationalToolkit(Protocol):
    """The P1 surface: tools that read live state from the system of record.

    Adapters here are app-specific — billing, profile, project state. The
    runtime verb `select` calls these via `fetch_live_facts` to populate
    `ContextBundle.live_facts`. Cache only within a single request."""

    def fetch_live_facts(
        self,
        *,
        entity: EntityProfile,
        request: ContextAssemblyRequest,
    ) -> list[dict[str, Any]]: ...

    def list_tools_for_surface(self, surface: str) -> list[str]: ...
    """Per-surface tool allowlist. F4 confusion mitigation — never expose
    every tool on every surface."""


@runtime_checkable
class EmbeddingClient(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...
    @property
    def model_id(self) -> str: ...
    """Pinned model id. Re-embedding on model change is the responsibility
    of the caller; the adapter must surface what it used."""


@runtime_checkable
class LLMClient(Protocol):
    """Minimal LLM surface. Anything richer (streaming, tool use) is
    framework-specific and lives in your orchestrator, not here."""

    def complete(
        self,
        *,
        system: str,
        messages: list[dict[str, str]],
        max_tokens: int,
    ) -> str: ...

    def count_tokens(self, text: str) -> int: ...
    """Used by the `compress` verb to enforce projection.max_tokens."""


@runtime_checkable
class ArtifactLoader(Protocol):
    """Loads referenced artifacts just in time.

    This is the main P12 guardrail against A29: the bundle carries pointers,
    not raw files, until the runtime explicitly resolves them.
    """

    def load(
        self,
        *,
        refs: list[ArtifactRef],
        request: ContextAssemblyRequest,
    ) -> list[LoadedArtifact]: ...


@runtime_checkable
class ReferenceResolver(Protocol):
    """Resolves small runtime pointers into typed projections.

    The return shape is intentionally plain dicts/lists so app code can decide
    which layers each reference can populate. Supported keys:
    `live_facts`, `memory`, `evidence`, `relationship_context`, `artifact_refs`.
    """

    def resolve(
        self,
        *,
        refs: list[ContextRef],
        request: ContextAssemblyRequest,
    ) -> dict[str, Any]: ...

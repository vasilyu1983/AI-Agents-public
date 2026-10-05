from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class KnowledgeSource:
    """A document, page, or other corpus item registered for retrieval.

    The knowledge layer holds prose and derived summaries; entity facts live
    in LearnedMemory and operational truth lives behind tools. Mixing these
    is anti-pattern A8 (monolithic personalization store)."""

    id: str
    uri: str
    title: str
    content_hash: str
    """Used for change detection and freshness checks. Re-embed only when
    this changes; do not re-embed every nightly job."""

    owner_scope: dict[str, str]
    """ACL/tenant scope. Retrieval must filter by this — never trust the
    application layer to scope post-hoc (A10)."""

    indexed_at: datetime
    last_seen_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
    """Free-form: author, version, locale, classification. Used for filters
    and reranking signals."""


@dataclass(slots=True)
class RetrievalResult:
    """Evidence-bearing retrieval hit.

    Never inject raw embedding scores into the prompt (A18). Always carry
    `evidence_id` so the model can cite and the user can audit."""

    evidence_id: str
    """Stable across retrieval runs for the same chunk. Powers citation and
    feedback correlation."""

    source_id: str
    """Points back at KnowledgeSource.id."""

    snippet: str
    """The actual text the model will see. Already chunked and projected."""

    score: float
    """Reranker score (post-rerank), not raw cosine similarity."""

    metadata: dict[str, Any] = field(default_factory=dict)
    chunk_index: int | None = None
    page: int | None = None

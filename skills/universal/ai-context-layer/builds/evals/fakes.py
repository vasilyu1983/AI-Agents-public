"""In-memory adapter fakes for the eval harness.

These satisfy the Protocols in `reference_app/adapters/base.py` structurally —
no inheritance. Use them in tests; do not ship them to production.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from reference_app.contracts import (
    ArtifactRef,
    ContextAssemblyRequest,
    ContextRef,
    EntityProfile,
    LearnedMemory,
    LoadedArtifact,
    MemoryType,
    Projection,
    RetrievalResult,
)


class FakeMemoryStore:
    def __init__(self) -> None:
        self._rows: dict[str, LearnedMemory] = {}
        self._next = 0

    def remember(self, fact: LearnedMemory) -> str:
        self._next += 1
        new_id = fact.id or f"mem_{self._next}"
        fact.id = new_id
        self._rows[new_id] = fact
        return new_id

    def recall(
        self,
        *,
        entity_id: str,
        owner_scope: dict[str, str],
        memory_types: list[MemoryType] | None = None,
        min_confidence: float = 0.0,
        as_of: datetime | None = None,
        limit: int = 50,
    ) -> list[LearnedMemory]:
        out = [
            m
            for m in self._rows.values()
            if m.entity_id == entity_id
            and m.owner_scope == owner_scope
            and m.confidence >= min_confidence
            and m.invalidated_at is None
        ]
        return out[:limit]

    def forget(self, memory_id: str, *, reason: str, actor: str) -> None:
        if memory_id in self._rows:
            self._rows[memory_id].invalidated_at = datetime.now(UTC)

    def improve(self, memory_id: str, *, confidence_delta: float, reason: str) -> None:
        if memory_id in self._rows:
            new = max(0.0, min(1.0, self._rows[memory_id].confidence + confidence_delta))
            self._rows[memory_id].confidence = new

    def find_contradictions(self, fact: LearnedMemory) -> list[LearnedMemory]:
        return [
            m
            for m in self._rows.values()
            if m.entity_id == fact.entity_id
            and m.memory_type == fact.memory_type
            and m.value != fact.value
            and m.invalidated_at is None
        ]


class FakeRetrievalStore:
    def __init__(self) -> None:
        self._chunks: list[dict[str, Any]] = []

    def index(self, *, source_id: str, chunks: list[dict[str, Any]]) -> None:
        for c in chunks:
            self._chunks.append({**c, "source_id": source_id})

    def retrieve(
        self,
        *,
        query: str,
        owner_scope: dict[str, str],
        top_k: int = 8,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        # naive: return first top_k chunks matching scope, score by token overlap
        q_tokens = set(query.lower().split())
        scored = []
        for c in self._chunks:
            if c.get("owner_scope") != owner_scope:
                continue
            text = c.get("snippet", "")
            score = len(q_tokens & set(text.lower().split())) / max(len(q_tokens), 1)
            scored.append((score, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            RetrievalResult(
                evidence_id=c.get("id", f"ev_{i}"),
                source_id=c["source_id"],
                snippet=c.get("snippet", ""),
                score=score,
            )
            for i, (score, c) in enumerate(scored[:top_k])
        ]

    def invalidate(self, source_id: str) -> None:
        self._chunks = [c for c in self._chunks if c["source_id"] != source_id]


class FakeEpisodeLog:
    def __init__(self) -> None:
        self._rows: dict[str, dict[str, Any]] = {}
        self._next = 0

    def append(self, *, episode: dict[str, Any]) -> str:
        self._next += 1
        eid = f"ep_{self._next}"
        self._rows[eid] = {**episode, "id": eid}
        return eid

    def get(self, episode_id: str) -> dict[str, Any] | None:
        return self._rows.get(episode_id)


class FakeToolkit:
    def __init__(self, live_facts: list[dict[str, Any]] | None = None,
                 surface_tools: dict[str, list[str]] | None = None) -> None:
        self._live = live_facts or []
        self._tools = surface_tools or {}

    def fetch_live_facts(self, *, entity: EntityProfile, request: ContextAssemblyRequest):
        return list(self._live)

    def list_tools_for_surface(self, surface: str) -> list[str]:
        return list(self._tools.get(surface, []))


class FakeLLM:
    def complete(self, *, system: str, messages: list[dict[str, str]], max_tokens: int) -> str:
        return f"[fake-llm] sys={len(system)}c msgs={len(messages)}"

    def count_tokens(self, text: str) -> int:
        # rough heuristic: ~4 chars per token
        return max(1, len(text) // 4)


class FakeArtifactLoader:
    def __init__(self, payloads: dict[str, dict[str, Any]] | None = None) -> None:
        self._payloads = payloads or {}
        self.loaded_ids: list[str] = []

    def load(self, *, refs: list[ArtifactRef], request: ContextAssemblyRequest) -> list[LoadedArtifact]:
        out: list[LoadedArtifact] = []
        for ref in refs:
            if ref.owner_scope != request.owner_scope:
                raise ValueError(f"artifact {ref.artifact_id} requested outside owner_scope")
            payload = self._payloads.get(ref.artifact_id, {})
            self.loaded_ids.append(ref.artifact_id)
            out.append(
                LoadedArtifact(
                    artifact_id=ref.artifact_id,
                    artifact_type=ref.artifact_type,
                    owner_scope=ref.owner_scope,
                    text_content=str(payload.get("text_content", ref.title or ref.locator)),
                    structured_content=dict(payload.get("structured_content", {})),
                    mime_type=payload.get("mime_type", ref.mime_type),
                    source_ref_id=payload.get("source_ref_id"),
                    evidence_id=payload.get("evidence_id"),
                    metadata=dict(payload.get("metadata", {})),
                )
            )
        return out


class FakeReferenceResolver:
    def __init__(self, resolutions: dict[str, dict[str, Any]] | None = None) -> None:
        self._resolutions = resolutions or {}
        self.resolved_ids: list[str] = []

    def resolve(
        self,
        *,
        refs: list[ContextRef],
        request: ContextAssemblyRequest,
    ) -> dict[str, Any]:
        out: dict[str, Any] = {
            "live_facts": [],
            "memory": [],
            "evidence": [],
            "relationship_context": [],
            "artifact_refs": [],
        }
        for ref in refs:
            if ref.owner_scope != request.owner_scope:
                raise ValueError(f"context ref {ref.ref_id} requested outside owner_scope")
            payload = self._resolutions.get(ref.ref_id, {})
            self.resolved_ids.append(ref.ref_id)
            for key in out:
                out[key].extend(payload.get(key, []))
        return out

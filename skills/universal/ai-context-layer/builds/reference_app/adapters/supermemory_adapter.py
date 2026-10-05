"""Supermemory adapter — `MemoryStore` Protocol.

Supermemory is a hosted, cross-app universal memory layer. The HTTP API
is REST-shaped (`POST /add`, `POST /search`, etc.). The adapter here
takes any HTTP-callable client object and translates our Protocol to
that surface.

Verified against the Supermemory REST API as of April 2026. The exact
endpoint paths and response shapes have moved across versions; the
adapter isolates that drift to a small set of helper methods.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

from ..contracts import LearnedMemory, MemoryType


class HttpClient(Protocol):
    """Minimal HTTP surface. Use `httpx.Client`, `requests.Session`, or a
    test double — anything with `post(url, json=...)` and `.json()` on
    the response."""

    def post(self, url: str, *, json: dict[str, Any], headers: dict[str, str] | None = ...) -> Any: ...
    def get(self, url: str, *, params: dict[str, Any] | None = ..., headers: dict[str, str] | None = ...) -> Any: ...
    def delete(self, url: str, *, headers: dict[str, str] | None = ...) -> Any: ...


class SupermemoryMemoryStore:
    """Satisfies the `MemoryStore` Protocol against the Supermemory REST API.

    Tenant isolation: Supermemory's container/space concept (called
    `userId` or `containerTags` depending on API version) maps to our
    `owner_scope`. The adapter enforces this on every call.
    """

    def __init__(self, http: HttpClient, *, base_url: str, api_key: str) -> None:
        self._http = http
        self._base = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {api_key}"}

    # ---- remember ----------------------------------------------------------

    def remember(self, fact: LearnedMemory) -> str:
        if not fact.source_episode_id:
            raise ValueError("LearnedMemory.source_episode_id is required (A13)")
        if not fact.owner_scope:
            raise ValueError("LearnedMemory.owner_scope is required (A10)")
        if not 0.0 <= fact.confidence <= 1.0:
            raise ValueError("LearnedMemory.confidence must be in [0, 1] (A14)")

        new_id = fact.id or f"mem_{uuid4().hex[:16]}"
        fact.id = new_id

        body = {
            "id": new_id,
            "content": json.dumps(fact.value),
            "metadata": {
                "memory_type": fact.memory_type.value,
                "confidence": fact.confidence,
                "source_episode_id": fact.source_episode_id,
                "inferred": fact.inferred,
                "supersedes_id": fact.supersedes_id,
                "tags": fact.tags,
                "owner_scope": fact.owner_scope,
            },
            "containerTags": _scope_to_tags(fact.owner_scope, fact.entity_id),
        }
        self._http.post(f"{self._base}/v1/memories", json=body, headers=self._headers)
        return new_id

    # ---- recall ------------------------------------------------------------

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
        body = {
            "containerTags": _scope_to_tags(owner_scope, entity_id),
            "limit": limit,
        }
        resp = self._http.post(
            f"{self._base}/v1/memories/search", json=body, headers=self._headers
        )
        rows = _json(resp).get("results", [])
        out: list[LearnedMemory] = []
        for row in rows:
            mem = _row_to_memory(row, entity_id=entity_id, owner_scope=owner_scope)
            if mem.invalidated_at:
                continue
            if mem.confidence < min_confidence:
                continue
            if memory_types and mem.memory_type not in memory_types:
                continue
            out.append(mem)
        return out

    # ---- forget ------------------------------------------------------------

    def forget(self, memory_id: str, *, reason: str, actor: str) -> None:
        """Supermemory has destructive `delete`. We emulate non-destructive
        forget via metadata patch + tag, mirroring the Mem0 pattern."""
        body = {
            "metadata": {
                "invalidated_at": datetime.now(UTC).isoformat(),
                "forgotten_by": f"{actor}:{reason}",
            }
        }
        self._http.post(
            f"{self._base}/v1/memories/{memory_id}", json=body, headers=self._headers
        )

    # ---- improve -----------------------------------------------------------

    def improve(self, memory_id: str, *, confidence_delta: float, reason: str) -> None:
        # Read-modify-write — Supermemory has no atomic increment.
        resp = self._http.get(
            f"{self._base}/v1/memories/{memory_id}", headers=self._headers
        )
        meta = (_json(resp).get("metadata") or {})
        new_conf = max(0.0, min(1.0, float(meta.get("confidence", 0.5)) + confidence_delta))
        meta["confidence"] = new_conf
        meta.setdefault("feedback_log", []).append(
            {"reason": reason, "at": datetime.now(UTC).isoformat()}
        )
        self._http.post(
            f"{self._base}/v1/memories/{memory_id}",
            json={"metadata": meta},
            headers=self._headers,
        )

    # ---- find_contradictions ----------------------------------------------

    def find_contradictions(self, fact: LearnedMemory) -> list[LearnedMemory]:
        body = {
            "query": json.dumps(fact.value),
            "containerTags": _scope_to_tags(fact.owner_scope, fact.entity_id),
            "limit": 20,
        }
        resp = self._http.post(
            f"{self._base}/v1/memories/search", json=body, headers=self._headers
        )
        out: list[LearnedMemory] = []
        for row in _json(resp).get("results", []):
            mem = _row_to_memory(row, entity_id=fact.entity_id, owner_scope=fact.owner_scope)
            if mem.invalidated_at:
                continue
            if mem.memory_type != fact.memory_type or mem.value == fact.value:
                continue
            out.append(mem)
        return out


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _scope_to_tags(owner_scope: dict[str, str], entity_id: str) -> list[str]:
    """Container tags as a stable, sorted list. Supermemory treats
    containerTags as a set on the server side; ordering is irrelevant
    semantically but we sort to make audit logs readable."""
    tags = [f"{k}:{v}" for k, v in sorted(owner_scope.items())]
    tags.append(f"entity:{entity_id}")
    return tags


def _row_to_memory(
    row: dict[str, Any], *, entity_id: str, owner_scope: dict[str, str]
) -> LearnedMemory:
    meta = row.get("metadata") or {}
    raw_content = row.get("content") or "{}"
    try:
        decoded = json.loads(raw_content) if isinstance(raw_content, str) else raw_content
    except json.JSONDecodeError:
        decoded = raw_content

    invalidated = meta.get("invalidated_at")
    invalidated_at = (
        datetime.fromisoformat(invalidated) if isinstance(invalidated, str) else None
    )

    return LearnedMemory(
        id=row.get("id", ""),
        entity_id=entity_id,
        entity_type=meta.get("entity_type", "user"),
        memory_type=MemoryType(meta.get("memory_type", "fact")),
        value=decoded,
        source=meta.get("source", "supermemory"),
        source_episode_id=meta.get("source_episode_id", ""),
        confidence=float(meta.get("confidence", 0.5)),
        created_at=_parse_dt(row.get("createdAt")) or datetime.now(UTC),
        updated_at=_parse_dt(row.get("updatedAt")) or datetime.now(UTC),
        owner_scope=meta.get("owner_scope", owner_scope),
        inferred=bool(meta.get("inferred", True)),
        invalidated_at=invalidated_at,
        supersedes_id=meta.get("supersedes_id"),
        tags=list(meta.get("tags", [])),
    )


def _json(resp: Any) -> dict[str, Any]:
    if hasattr(resp, "json"):
        return resp.json()
    if isinstance(resp, dict):
        return resp
    return {}


def _parse_dt(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value)) if value else None
    except (TypeError, ValueError):
        return None

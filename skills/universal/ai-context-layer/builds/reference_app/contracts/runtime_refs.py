from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class ContextRef:
    """A pointer to context that should be resolved just in time.

    P12's core rule is pointer-first assembly: carry small, stable handles in
    the request, then load only what the surface actually needs.
    """

    ref_id: str
    ref_type: str
    pointer: str
    owner_scope: dict[str, str]
    source: str = "runtime"
    freshness_ts: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ArtifactRef:
    """A pointer to a large or multimodal artifact.

    The runtime should prefer these over stuffing raw files or tool payloads
    directly into the bundle (A29).
    """

    artifact_id: str
    artifact_type: str
    locator: str
    owner_scope: dict[str, str]
    mime_type: str = ""
    title: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LoadedArtifact:
    """Typed artifact payload after the loader resolves an `ArtifactRef`."""

    artifact_id: str
    artifact_type: str
    owner_scope: dict[str, str]
    text_content: str = ""
    structured_content: dict[str, Any] = field(default_factory=dict)
    mime_type: str = ""
    source_ref_id: str | None = None
    evidence_id: str | None = None
    freshness_ts: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

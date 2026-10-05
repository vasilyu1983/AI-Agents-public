"""Canonical context-layer contracts.

Mirrors the markdown templates in ../../assets/contracts/. The dataclasses here
are the executable source of truth; the markdown is the human-readable spec.
Keep them in sync — if a field is added in code, add it to the markdown in the
same commit, and vice versa.
"""

from .assembly import ContextAssemblyRequest, ContextBundle, Guardrails, Projection
from .entity import EntityProfile
from .feedback import FeedbackOutcome, InlineReactionFeedback
from .knowledge import KnowledgeSource, RetrievalResult
from .memory import LearnedMemory, MemoryType
from .runtime_refs import ArtifactRef, ContextRef, LoadedArtifact

__all__ = [
    "ArtifactRef",
    "ContextAssemblyRequest",
    "ContextBundle",
    "ContextRef",
    "EntityProfile",
    "FeedbackOutcome",
    "Guardrails",
    "InlineReactionFeedback",
    "KnowledgeSource",
    "LearnedMemory",
    "LoadedArtifact",
    "MemoryType",
    "Projection",
    "RetrievalResult",
]

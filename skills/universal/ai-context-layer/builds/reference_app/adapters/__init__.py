"""Adapter Protocols for the context layer.

Concrete adapters live alongside this module (Phase 2 ships postgres_*) or in
../cookbooks/ for vendor-backed implementations (Mem0, Letta, Cognee, etc.).

The contract here is structural: any class whose methods match a Protocol
satisfies it, no inheritance required. This is what lets the eval harness
swap a fake in-memory adapter for the real Postgres one without changing
assembly code.
"""

from .base import (
    ArtifactLoader,
    EmbeddingClient,
    EpisodeLog,
    LLMClient,
    MemoryStore,
    OperationalToolkit,
    ReferenceResolver,
    RetrievalStore,
)

# Vendor adapters are imported lazily — their SDKs are optional deps.
_LAZY: dict[str, tuple[str, str]] = {
    "PostgresEpisodeLog":        (".postgres_episodes",        "PostgresEpisodeLog"),
    "PostgresMemoryStore":       (".postgres_memory",          "PostgresMemoryStore"),
    "PostgresRetrievalStore":    (".postgres_retrieval",       "PostgresRetrievalStore"),
    "Mem0MemoryStore":           (".mem0_adapter",             "Mem0MemoryStore"),
    "LettaMemoryStore":          (".letta_adapter",            "LettaMemoryStore"),
    "CogneeRetrievalStore":      (".cognee_adapter",           "CogneeRetrievalStore"),
    "CogneeMemoryStore":         (".cognee_adapter",           "CogneeMemoryStore"),
    "LangGraphStoreMemoryStore": (".langgraph_store_adapter",  "LangGraphStoreMemoryStore"),
    "SupermemoryMemoryStore":    (".supermemory_adapter",      "SupermemoryMemoryStore"),
    "AnthropicLLM":              (".anthropic_llm",            "AnthropicLLM"),
}


def __getattr__(name: str):
    if name in _LAZY:
        from importlib import import_module
        module_path, attr = _LAZY[name]
        mod = import_module(module_path, package=__name__)
        return getattr(mod, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AnthropicLLM",
    "ArtifactLoader",
    "CogneeMemoryStore",
    "CogneeRetrievalStore",
    "EmbeddingClient",
    "EpisodeLog",
    "LLMClient",
    "LangGraphStoreMemoryStore",
    "LettaMemoryStore",
    "MemoryStore",
    "Mem0MemoryStore",
    "OperationalToolkit",
    "PostgresEpisodeLog",
    "PostgresMemoryStore",
    "PostgresRetrievalStore",
    "ReferenceResolver",
    "RetrievalStore",
    "SupermemoryMemoryStore",
]

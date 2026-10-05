"""End-to-end demo: ingest → recall → assemble → respond.

Runs against the in-memory fakes by default so it works with no infra. Set
USE_POSTGRES=1 (and POSTGRES_DSN) to swap in the Postgres adapters; set
USE_ANTHROPIC=1 (and ANTHROPIC_API_KEY) to swap in the real LLM.

The whole point of the kit is that swapping infra does not change the
runtime verbs or the assembly logic — only the adapter wiring at the top.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

# Make the kit importable when run from the repo root or from this dir.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
sys.path.insert(0, str(_HERE.parent / "reference_app"))

from reference_app.contracts import (  # noqa: E402
    ContextAssemblyRequest,
    EntityProfile,
    LearnedMemory,
    MemoryType,
    Projection,
)
from reference_app.runtime import assemble, isolate, write  # noqa: E402

from evals.fakes import (  # noqa: E402
    FakeEpisodeLog,
    FakeLLM,
    FakeMemoryStore,
    FakeRetrievalStore,
    FakeToolkit,
)


class _DemoEmbedder:
    """Deterministic 1536-dim hashing pseudo-embedder.

    Demo-only. It produces stable vectors so the Postgres path runs end-to-end
    with no external embedding provider, but the vectors are not semantically
    meaningful — recall against this will hit on near-duplicate strings only.
    Swap for `OpenAIEmbeddingClient`, `VoyageEmbeddingClient`, or a local
    BGE/Nomic model in production.
    """

    DIM = 1536

    def embed(self, texts: list[str]) -> list[list[float]]:
        import hashlib

        vectors: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha512(text.encode("utf-8")).digest()
            # Repeat the 64-byte digest to fill 1536 dims, then normalize to [-1, 1].
            raw = (digest * ((self.DIM // len(digest)) + 1))[: self.DIM]
            vectors.append([(b / 127.5) - 1.0 for b in raw])
        return vectors


def _build_llm():
    """Pick an LLM adapter. USE_ANTHROPIC=1 (with ANTHROPIC_API_KEY) swaps in
    the real client; otherwise fall back to FakeLLM so the demo always runs."""
    if os.getenv("USE_ANTHROPIC") == "1":
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise SystemExit("USE_ANTHROPIC=1 but ANTHROPIC_API_KEY is unset; refusing to fall back to FakeLLM silently")
        from reference_app.adapters import AnthropicLLM
        return AnthropicLLM()
    return FakeLLM()


def build_stack():
    """Pick adapters based on env vars. Default is fully in-memory."""
    llm = _build_llm()
    toolkit = FakeToolkit(
        live_facts=[{"plan": "pro", "seats_used": 4}],
        surface_tools={"chat": ["read_profile"]},
    )

    if os.getenv("USE_POSTGRES") == "1":
        # Real-Postgres path. Requires `pip install psycopg[binary] pgvector`
        # and `POSTGRES_DSN` set, plus the schema from
        # reference_app/adapters/migrations/0001_initial.sql applied.
        import psycopg
        from reference_app.adapters import (
            PostgresEpisodeLog,
            PostgresMemoryStore,
            PostgresRetrievalStore,
        )

        conn = psycopg.connect(os.environ["POSTGRES_DSN"])
        return {
            "episodes": PostgresEpisodeLog(conn),
            "memory": PostgresMemoryStore(conn),
            "retrieval": PostgresRetrievalStore(conn, _DemoEmbedder()),
            "toolkit": toolkit,
            "llm": llm,
        }
    return {
        "episodes": FakeEpisodeLog(),
        "memory": FakeMemoryStore(),
        "retrieval": FakeRetrievalStore(),
        "toolkit": toolkit,
        "llm": llm,
    }


def main() -> int:
    stack = build_stack()
    owner_scope = {"organization_id": "org_demo"}

    # 1. Append an episode (the audit spine)
    episode_id = stack["episodes"].append(
        episode={
            "kind": "user_turn",
            "owner_scope": owner_scope,
            "text": "I prefer concise responses.",
        }
    )

    # 2. Extract a typed memory from that episode and write it
    fact = LearnedMemory(
        id="",
        entity_id="usr_demo",
        entity_type="user",
        memory_type=MemoryType.PREFERENCE,
        value={"prefers": "concise"},
        source="user_turn",
        source_episode_id=episode_id,
        confidence=0.9,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        owner_scope=owner_scope,
        inferred=False,  # user-stated, not model-inferred (A26 defense)
    )
    write(fact=fact, memory_store=stack["memory"])

    # 3. Index a knowledge chunk
    stack["retrieval"].index(
        source_id="src_handbook",
        chunks=[
            {
                "id": "chunk_handbook_1",
                "snippet": "Concise responses (under 100 words) work best for chat.",
                "owner_scope": owner_scope,
            }
        ],
    )

    # 4. Build a per-surface assembly request
    entity = EntityProfile(
        id="usr_demo",
        entity_type="user",
        owner_scope=owner_scope,
        source_of_truth="users://usr_demo",
        updated_at=datetime.now(UTC),
    )
    request = ContextAssemblyRequest(
        surface="chat",
        actor={"entity_type": "user", "entity_id": "usr_demo"},
        owner_scope=owner_scope,
        intent="give a concise update",
        projection=Projection(max_tokens=2000),
    )

    # 5. Assemble the bundle
    bundle = assemble(
        request=request,
        entity=entity,
        memory_store=stack["memory"],
        retrieval_store=stack["retrieval"],
        toolkit=stack["toolkit"],
        llm=stack["llm"],
    )

    # 6. Demonstrate sub-agent isolation
    sub = isolate(
        sub_task_intent="restate the user's preference using cited evidence only",
        parent_bundle=bundle,
        llm=stack["llm"],
    )

    # 7. Print what shipped
    print(json.dumps({
        "bundle_id": bundle.id,
        "surface": bundle.surface,
        "owner_scope": bundle.owner_scope,
        "memory_count": len(bundle.memory),
        "evidence_count": len(bundle.domain_evidence),
        "live_fact_count": len(bundle.live_facts),
        "token_estimate": bundle.token_count_estimate,
        "sub_agent": sub,
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

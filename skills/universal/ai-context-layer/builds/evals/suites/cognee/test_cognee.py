"""Smoke test for CogneeRetrievalStore against the live `cognee` package.

Index + retrieve round-trip. The graph extraction step (`cognify`) can
take 10–60s depending on chunk count and provider latency.
"""

from __future__ import annotations

from uuid import uuid4

from reference_app.adapters import CogneeRetrievalStore


def test_index_then_retrieve_against_live_cognee(cognee_module):
    adapter = CogneeRetrievalStore(cognee_module=cognee_module)
    scope = {"org_id": f"smoke_{uuid4().hex[:8]}"}

    chunks = [
        {
            "id": "chunk_1",
            "snippet": "The customer's preferred timezone is UTC for all support tickets.",
            "owner_scope": scope,
        }
    ]
    adapter.index(source_id="src_1", chunks=chunks)

    hits = adapter.retrieve(query="timezone preference", owner_scope=scope, top_k=3)
    # Cognee may rephrase / shard. Just assert we got something cited.
    assert hits
    assert all(h.evidence_id for h in hits)

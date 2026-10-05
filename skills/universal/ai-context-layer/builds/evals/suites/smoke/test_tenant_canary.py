"""Cross-tenant canary: tenant A's data must never reach tenant B's bundle.

Seeds a unique canary string into tenant A's memory and retrieval index, then
assembles a bundle for tenant B with the same entity id and intent. The canary
must be absent from B's bundle. A negative control (a store that ignores
owner_scope) proves the check can fail.

Runs without pytest:
    cd builds && PYTHONDONTWRITEBYTECODE=1 python3 -m evals.suites.smoke.test_tenant_canary
"""

from __future__ import annotations

import dataclasses
import uuid
from datetime import UTC, datetime

from reference_app.contracts import (
    ContextAssemblyRequest,
    EntityProfile,
    LearnedMemory,
    MemoryType,
    Projection,
)
from reference_app.runtime import assemble, write

from evals.fakes import FakeLLM, FakeMemoryStore, FakeRetrievalStore, FakeToolkit

TENANT_A = {"organization_id": "org_a"}
TENANT_B = {"organization_id": "org_b"}
INTENT = "what is the renewal date on the contract"


class LeakyRetrievalStore(FakeRetrievalStore):
    """Negative control: retrieves across tenants (scope filter missing)."""

    def retrieve(self, *, query, owner_scope, top_k=8, filters=None):
        results = []
        for scope in {tuple(sorted(c["owner_scope"].items())) for c in self._chunks}:
            results += super().retrieve(
                query=query, owner_scope=dict(scope), top_k=top_k, filters=filters
            )
        return results[:top_k]


def _seed(canary: str, memory: FakeMemoryStore, retrieval: FakeRetrievalStore) -> None:
    now = datetime.now(UTC)
    write(
        fact=LearnedMemory(
            id="",
            entity_id="usr_1",
            entity_type="user",
            memory_type=MemoryType.PREFERENCE,
            value={"note": canary},
            source="user_turn",
            source_episode_id="ep_a",
            confidence=0.9,
            created_at=now,
            updated_at=now,
            owner_scope=TENANT_A,
            inferred=False,
        ),
        memory_store=memory,
    )
    retrieval.index(
        source_id="src_a",
        chunks=[
            {
                "id": "ev_a",
                "snippet": f"the renewal date on the contract is {canary}",
                "owner_scope": TENANT_A,
            }
        ],
    )


def _bundle_text_for_tenant_b(memory, retrieval) -> str:
    bundle = assemble(
        request=ContextAssemblyRequest(
            surface="chat",
            actor={"entity_type": "user", "entity_id": "usr_1"},
            owner_scope=TENANT_B,
            intent=INTENT,
            projection=Projection(max_tokens=2000),
        ),
        entity=EntityProfile(
            id="usr_1",
            entity_type="user",
            owner_scope=TENANT_B,
            source_of_truth="users://usr_1",
            updated_at=datetime.now(UTC),
        ),
        memory_store=memory,
        retrieval_store=retrieval,
        toolkit=FakeToolkit(live_facts=[], surface_tools={"chat": []}),
        llm=FakeLLM(),
    )
    return repr(dataclasses.asdict(bundle))


def canary_leaks(retrieval_store_cls=FakeRetrievalStore) -> bool:
    canary = f"CANARY-{uuid.uuid4().hex}"
    memory, retrieval = FakeMemoryStore(), retrieval_store_cls()
    _seed(canary, memory, retrieval)
    return canary in _bundle_text_for_tenant_b(memory, retrieval)


def test_canary_absent_from_other_tenant_bundle():
    assert not canary_leaks(), "Tenant A canary reached tenant B's bundle"


def test_negative_control_detects_leak():
    assert canary_leaks(LeakyRetrievalStore), (
        "Canary check is blind: a store that ignores owner_scope went undetected"
    )


if __name__ == "__main__":
    failed = 0
    for fn in (test_canary_absent_from_other_tenant_bundle, test_negative_control_detects_leak):
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
    raise SystemExit(1 if failed else 0)

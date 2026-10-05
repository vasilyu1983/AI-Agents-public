from __future__ import annotations

from datetime import UTC, datetime

import pytest

from reference_app.contracts import ContextAssemblyRequest, ContextRef, EntityProfile, LearnedMemory, MemoryType, Projection
from reference_app.runtime import assemble

from evals.fakes import (
    FakeArtifactLoader,
    FakeLLM,
    FakeMemoryStore,
    FakeReferenceResolver,
    FakeRetrievalStore,
    FakeToolkit,
)


def test_operational_truth_stays_separate_from_managed_memory():
    toolkit = FakeToolkit(live_facts=[{"plan": "pro", "seats_used": 4}])
    resolver = FakeReferenceResolver(
        {
            "ctx_managed": {
                "memory": [
                    LearnedMemory(
                        id="mem_managed",
                        entity_id="usr_1",
                        entity_type="user",
                        memory_type=MemoryType.FACT,
                        value={"plan_guess": "starter"},
                        source="managed_store",
                        source_episode_id="ep_managed",
                        confidence=0.6,
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                        owner_scope={"organization_id": "org_1"},
                        inferred=True,
                    )
                ]
            }
        }
    )

    bundle = assemble(
        request=ContextAssemblyRequest(
            surface="chat",
            actor={"entity_type": "user", "entity_id": "usr_1"},
            owner_scope={"organization_id": "org_1"},
            intent="answer using live account context",
            context_refs=[
                ContextRef(
                    ref_id="ctx_managed",
                    ref_type="managed_memory",
                    pointer="managed://usr_1",
                    owner_scope={"organization_id": "org_1"},
                )
            ],
            projection=Projection(max_tokens=1200),
        ),
        entity=EntityProfile(
            id="usr_1",
            entity_type="user",
            owner_scope={"organization_id": "org_1"},
            source_of_truth="users://usr_1",
            updated_at=datetime.now(UTC),
        ),
        memory_store=FakeMemoryStore(),
        retrieval_store=FakeRetrievalStore(),
        toolkit=toolkit,
        llm=FakeLLM(),
        resolver=resolver,
        artifact_loader=FakeArtifactLoader(),
    )

    assert bundle.live_facts == [{"plan": "pro", "seats_used": 4}]
    assert bundle.memory[0].value == {"plan_guess": "starter"}


def test_managed_boundary_rejects_scope_free_resolution():
    resolver = FakeReferenceResolver()
    request = ContextAssemblyRequest(
        surface="chat",
        actor={"entity_type": "user", "entity_id": "usr_1"},
        owner_scope={"organization_id": "org_1"},
        intent="fetch memory",
        context_refs=[
            ContextRef(
                ref_id="ctx_wrong",
                ref_type="managed_memory",
                pointer="managed://usr_1",
                owner_scope={"organization_id": "org_2"},
            )
        ],
    )

    with pytest.raises(ValueError, match="owner_scope"):
        resolver.resolve(refs=request.context_refs, request=request)

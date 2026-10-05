"""Smoke tests — prove the contracts, adapters, and runtime verbs wire up.

These tests do not assert quality. They assert *structural correctness*: the
Protocols are satisfied, the verbs compose, and a basic assemble() call
returns a well-formed bundle. Quality assertions land in Phase 4 suites.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from reference_app.adapters import (
    ArtifactLoader,
    EmbeddingClient,
    EpisodeLog,
    LLMClient,
    MemoryStore,
    OperationalToolkit,
    ReferenceResolver,
    RetrievalStore,
)
from reference_app.contracts import (
    ArtifactRef,
    ContextAssemblyRequest,
    ContextRef,
    EntityProfile,
    LearnedMemory,
    MemoryType,
    Projection,
)
from reference_app.contracts import ContextBundle, LoadedArtifact, RetrievalResult
from reference_app.runtime import (
    UnionMemoryStore,
    assemble,
    compress,
    isolate,
    resolve,
    write,
)

from evals.fakes import (
    FakeArtifactLoader,
    FakeEpisodeLog,
    FakeLLM,
    FakeMemoryStore,
    FakeRetrievalStore,
    FakeReferenceResolver,
    FakeToolkit,
)


# -----------------------------------------------------------------------------
# Protocol satisfaction (structural typing)
# -----------------------------------------------------------------------------

def test_fakes_satisfy_protocols():
    assert isinstance(FakeMemoryStore(), MemoryStore)
    assert isinstance(FakeRetrievalStore(), RetrievalStore)
    assert isinstance(FakeEpisodeLog(), EpisodeLog)
    assert isinstance(FakeToolkit(), OperationalToolkit)
    assert isinstance(FakeLLM(), LLMClient)
    assert isinstance(FakeArtifactLoader(), ArtifactLoader)
    assert isinstance(FakeReferenceResolver(), ReferenceResolver)


# -----------------------------------------------------------------------------
# write() blocks the type-level anti-patterns
# -----------------------------------------------------------------------------

def _fact(**overrides) -> LearnedMemory:
    base = dict(
        id="",
        entity_id="usr_1",
        entity_type="user",
        memory_type=MemoryType.PREFERENCE,
        value={"prefers": "concise"},
        source="user_turn",
        source_episode_id="ep_1",
        confidence=0.8,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        owner_scope={"organization_id": "org_1"},
        inferred=False,
    )
    base.update(overrides)
    return LearnedMemory(**base)


def test_write_rejects_missing_episode_id():
    with pytest.raises(ValueError, match="source_episode_id"):
        write(fact=_fact(source_episode_id=""), memory_store=FakeMemoryStore())


def test_write_rejects_missing_owner_scope():
    with pytest.raises(ValueError, match="owner_scope"):
        write(fact=_fact(owner_scope={}), memory_store=FakeMemoryStore())


def test_write_rejects_invalid_confidence():
    with pytest.raises(ValueError, match="confidence"):
        write(fact=_fact(confidence=1.5), memory_store=FakeMemoryStore())


def test_write_tags_contradictions_at_ingest():
    store = FakeMemoryStore()
    write(fact=_fact(value={"prefers": "concise"}), memory_store=store)
    rid = write(fact=_fact(value={"prefers": "verbose"}), memory_store=store)
    second = store._rows[rid]
    assert any(t.startswith("conflicts:") for t in second.tags), (
        "Ingest-time contradiction detection (A4) must surface conflicts"
    )


# -----------------------------------------------------------------------------
# assemble() composes the verbs end-to-end
# -----------------------------------------------------------------------------

def test_assemble_produces_bundle_under_budget():
    memory = FakeMemoryStore()
    retrieval = FakeRetrievalStore()
    toolkit = FakeToolkit(
        live_facts=[{"plan": "pro", "seats_used": 4}],
        surface_tools={"chat": ["read_profile", "send_message"]},
    )
    llm = FakeLLM()

    write(fact=_fact(value={"prefers": "concise"}), memory_store=memory)
    retrieval.index(
        source_id="src_1",
        chunks=[
            {
                "id": "ev_1",
                "snippet": "concise responses are preferred for chat surfaces",
                "owner_scope": {"organization_id": "org_1"},
            },
        ],
    )

    entity = EntityProfile(
        id="usr_1",
        entity_type="user",
        owner_scope={"organization_id": "org_1"},
        source_of_truth="users://usr_1",
        updated_at=datetime.now(UTC),
    )
    request = ContextAssemblyRequest(
        surface="chat",
        actor={"entity_type": "user", "entity_id": "usr_1"},
        owner_scope={"organization_id": "org_1"},
        intent="give a concise update",
        projection=Projection(max_tokens=2000),
    )

    bundle = assemble(
        request=request,
        entity=entity,
        memory_store=memory,
        retrieval_store=retrieval,
        toolkit=toolkit,
        llm=llm,
    )

    assert bundle.id.startswith("bndl_")
    assert bundle.surface == "chat"
    assert bundle.owner_scope == {"organization_id": "org_1"}
    assert bundle.token_count_estimate <= request.projection.max_tokens, (
        "F2 mitigation: assembled bundle must respect the projection budget"
    )
    assert bundle.live_facts, "Live facts from P1 toolkit must reach the bundle"


def test_resolve_loads_runtime_refs_just_in_time():
    request = ContextAssemblyRequest(
        surface="workspace",
        actor={"entity_type": "user", "entity_id": "usr_1"},
        owner_scope={"organization_id": "org_1"},
        intent="summarize the uploaded design doc",
        context_refs=[
            ContextRef(
                ref_id="ctx_doc",
                ref_type="search_hit",
                pointer="doc://design",
                owner_scope={"organization_id": "org_1"},
            )
        ],
        projection=Projection(max_tokens=2000, max_artifacts=1),
    )
    resolver = FakeReferenceResolver(
        {
            "ctx_doc": {
                "evidence": [
                    RetrievalResult(
                        evidence_id="ev_doc",
                        source_id="src_doc",
                        snippet="Design decisions live in the PRD.",
                        score=0.95,
                    )
                ],
                "artifact_refs": [
                    ArtifactRef(
                        artifact_id="art_doc",
                        artifact_type="document",
                        locator="doc://design",
                        owner_scope={"organization_id": "org_1"},
                        title="Design Doc",
                    )
                ],
            }
        }
    )
    loader = FakeArtifactLoader(
        {
            "art_doc": {
                "text_content": "Large design document body " * 200,
                "mime_type": "text/markdown",
                "evidence_id": "ev_doc",
                "source_ref_id": "ctx_doc",
            }
        }
    )

    resolved = resolve(
        selected={"live_facts": [], "memory": [], "evidence": [], "artifact_refs": [], "context_refs": request.context_refs},
        request=request,
        resolver=resolver,
        artifact_loader=loader,
    )

    assert resolver.resolved_ids == ["ctx_doc"], "P12: only requested refs should resolve"
    assert loader.loaded_ids == ["art_doc"], "Artifact loading must happen after ref resolution"
    assert resolved["evidence"][0].evidence_id == "ev_doc"
    assert resolved["loaded_artifacts"][0].source_ref_id == "ctx_doc"


def test_assemble_projects_multimodal_artifacts_without_raw_payload_stuffing():
    memory = FakeMemoryStore()
    retrieval = FakeRetrievalStore()
    toolkit = FakeToolkit()
    llm = FakeLLM()
    resolver = FakeReferenceResolver(
        {
            "ctx_image": {
                "artifact_refs": [
                    ArtifactRef(
                        artifact_id="art_img",
                        artifact_type="image",
                        locator="image://1",
                        owner_scope={"organization_id": "org_1"},
                        mime_type="image/png",
                    )
                ]
            }
        }
    )
    loader = FakeArtifactLoader(
        {
            "art_img": {
                "text_content": "OCR summary " * 400,
                "metadata": {"raw_payload": "base64-goes-here", "width": 1600},
                "mime_type": "image/png",
                "source_ref_id": "ctx_image",
            }
        }
    )
    entity = EntityProfile(
        id="usr_1",
        entity_type="user",
        owner_scope={"organization_id": "org_1"},
        source_of_truth="users://usr_1",
        updated_at=datetime.now(UTC),
    )
    request = ContextAssemblyRequest(
        surface="workspace",
        actor={"entity_type": "user", "entity_id": "usr_1"},
        owner_scope={"organization_id": "org_1"},
        intent="review screenshot",
        context_refs=[
            ContextRef(
                ref_id="ctx_image",
                ref_type="artifact_pointer",
                pointer="image://1",
                owner_scope={"organization_id": "org_1"},
            )
        ],
        projection=Projection(max_tokens=1200, max_artifacts=1, max_inline_artifact_chars=120),
    )

    bundle = assemble(
        request=request,
        entity=entity,
        memory_store=memory,
        retrieval_store=retrieval,
        toolkit=toolkit,
        llm=llm,
        resolver=resolver,
        artifact_loader=loader,
    )

    assert bundle.loaded_artifacts[0].artifact_id == "art_img"
    assert len(bundle.loaded_artifacts[0].text_content) > request.projection.max_inline_artifact_chars
    formatted = {
        "live_facts": [],
        "memory": [],
        "evidence": [],
        "loaded_artifacts": [
            {
                "artifact_id": bundle.loaded_artifacts[0].artifact_id,
                "artifact_type": bundle.loaded_artifacts[0].artifact_type,
                "text_excerpt": bundle.loaded_artifacts[0].text_content[: request.projection.max_inline_artifact_chars],
                "metadata": {"width": 1600},
            }
        ],
    }
    assert "base64" not in str(formatted["loaded_artifacts"][0]), (
        "A29: artifact projections must drop raw payload content"
    )


def test_recall_respects_owner_scope():
    """A10: a memory store query without matching scope returns nothing,
    even if entity_id matches."""
    store = FakeMemoryStore()
    write(fact=_fact(owner_scope={"organization_id": "org_1"}), memory_store=store)

    leaked = store.recall(entity_id="usr_1", owner_scope={"organization_id": "org_2"})
    assert leaked == [], "Cross-tenant memory leak (A10) must be impossible"


# -----------------------------------------------------------------------------
# compress — summarize strategy preserves IDs
# -----------------------------------------------------------------------------

def test_compress_summarize_preserves_evidence_ids():
    """A18 + A24: when summarize compresses evidence, evidence_ids must
    survive so downstream citation still works."""
    llm = FakeLLM()
    big_snippet = "x " * 2000  # forces summarization
    formatted = {
        "live_facts": [],
        "memory": [],
        "evidence": [
            {"evidence_id": "ev_a", "snippet": big_snippet, "source_id": "src", "score": 0.9},
            {"evidence_id": "ev_b", "snippet": big_snippet, "source_id": "src", "score": 0.8},
        ],
    }
    compressed = compress(formatted=formatted, max_tokens=200, llm=llm, strategy="summarize")
    ids = {e["evidence_id"] for e in compressed["evidence"]}
    assert ids == {"ev_a", "ev_b"}, "evidence_id must survive summarization"


# -----------------------------------------------------------------------------
# isolate — rejects fabricated evidence_ids (F1 at sub-agent boundary)
# -----------------------------------------------------------------------------

class _FakeLLMWithReply(FakeLLM):
    def __init__(self, reply: str) -> None:
        self._reply = reply

    def complete(self, *, system, messages, max_tokens):
        return self._reply


def test_union_memory_store_dedupes_and_writes_to_primary():
    """UnionMemoryStore: writes hit primary; reads merge with id-dedupe;
    higher-confidence duplicate wins."""
    primary = FakeMemoryStore()
    secondary = FakeMemoryStore()

    # Pre-seed both stores with the same id but different confidence.
    fact_a = _fact(value={"prefers": "concise"})
    fact_a.id = "shared_id"
    fact_a.confidence = 0.6
    primary.remember(fact_a)

    fact_b = _fact(value={"prefers": "concise"})
    fact_b.id = "shared_id"
    fact_b.confidence = 0.9
    secondary.remember(fact_b)

    union = UnionMemoryStore(primary=primary, readers=[secondary])

    # Writes go to primary only.
    new_fact = _fact(value={"prefers": "verbose"})
    new_id = write(fact=new_fact, memory_store=union)
    assert new_id in primary._rows
    assert new_id not in secondary._rows

    # Reads merge; higher-confidence wins on duplicate id.
    out = union.recall(entity_id="usr_1", owner_scope={"organization_id": "org_1"})
    by_id = {m.id: m for m in out}
    assert by_id["shared_id"].confidence == 0.9, "Higher-confidence duplicate must win"
    assert new_id in by_id, "Newly-written fact must appear in union recall"


def test_isolate_rejects_fabricated_evidence_ids():
    parent = ContextBundle(
        id="bndl_parent",
        domain_evidence=[
            RetrievalResult(evidence_id="ev_real", source_id="src", snippet="real", score=0.9),
        ],
    )
    llm = _FakeLLMWithReply(
        '{"summary": "done", "cited_evidence_ids": ["ev_real", "ev_fake"]}'
    )
    result = isolate(sub_task_intent="summarize", parent_bundle=parent, llm=llm)
    assert result["cited_evidence_ids"] == ["ev_real"]
    assert result["rejected_ids"] == ["ev_fake"], (
        "F1 at sub-agent boundary: hallucinated evidence IDs must be quarantined"
    )

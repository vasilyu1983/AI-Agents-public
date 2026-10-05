from __future__ import annotations

from reference_app.contracts import ArtifactRef, ContextAssemblyRequest, ContextRef, Projection
from reference_app.runtime import resolve

from evals.fakes import FakeArtifactLoader, FakeReferenceResolver


def test_jit_loading_resolves_only_requested_refs():
    request = ContextAssemblyRequest(
        surface="workspace",
        actor={"entity_type": "user", "entity_id": "usr_1"},
        owner_scope={"organization_id": "org_1"},
        intent="open the relevant design file",
        context_refs=[
            ContextRef(
                ref_id="ctx_doc",
                ref_type="search_hit",
                pointer="doc://design",
                owner_scope={"organization_id": "org_1"},
            )
        ],
        projection=Projection(max_artifacts=1),
    )
    resolver = FakeReferenceResolver(
        {
            "ctx_doc": {
                "artifact_refs": [
                    ArtifactRef(
                        artifact_id="art_doc",
                        artifact_type="document",
                        locator="doc://design",
                        owner_scope={"organization_id": "org_1"},
                    )
                ]
            }
        }
    )
    loader = FakeArtifactLoader({"art_doc": {"text_content": "doc body", "source_ref_id": "ctx_doc"}})

    resolved = resolve(
        selected={"live_facts": [], "memory": [], "evidence": [], "context_refs": request.context_refs, "artifact_refs": []},
        request=request,
        resolver=resolver,
        artifact_loader=loader,
    )

    assert resolver.resolved_ids == ["ctx_doc"]
    assert loader.loaded_ids == ["art_doc"]
    assert resolved["loaded_artifacts"][0].source_ref_id == "ctx_doc"


def test_jit_loading_caps_artifacts_to_projection_budget():
    request = ContextAssemblyRequest(
        surface="workspace",
        actor={"entity_type": "user", "entity_id": "usr_1"},
        owner_scope={"organization_id": "org_1"},
        intent="review the latest pack",
        context_refs=[
            ContextRef(
                ref_id="ctx_pack",
                ref_type="artifact_group",
                pointer="pack://latest",
                owner_scope={"organization_id": "org_1"},
            )
        ],
        projection=Projection(max_artifacts=1),
    )
    resolver = FakeReferenceResolver(
        {
            "ctx_pack": {
                "artifact_refs": [
                    ArtifactRef(
                        artifact_id="art_a",
                        artifact_type="document",
                        locator="doc://a",
                        owner_scope={"organization_id": "org_1"},
                    ),
                    ArtifactRef(
                        artifact_id="art_b",
                        artifact_type="image",
                        locator="image://b",
                        owner_scope={"organization_id": "org_1"},
                    ),
                ]
            }
        }
    )
    loader = FakeArtifactLoader(
        {
            "art_a": {"text_content": "doc a"},
            "art_b": {"text_content": "doc b"},
        }
    )

    resolved = resolve(
        selected={"live_facts": [], "memory": [], "evidence": [], "context_refs": request.context_refs, "artifact_refs": []},
        request=request,
        resolver=resolver,
        artifact_loader=loader,
    )

    assert len(resolved["loaded_artifacts"]) == 1
    assert loader.loaded_ids == ["art_a"]

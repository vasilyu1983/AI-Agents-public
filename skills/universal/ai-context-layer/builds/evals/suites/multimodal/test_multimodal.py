from __future__ import annotations

from datetime import UTC, datetime

from reference_app.contracts import ArtifactRef, ContextAssemblyRequest, ContextRef, EntityProfile, Projection
from reference_app.runtime import assemble

from evals.fakes import (
    FakeArtifactLoader,
    FakeLLM,
    FakeMemoryStore,
    FakeReferenceResolver,
    FakeRetrievalStore,
    FakeToolkit,
)


def test_multimodal_bundle_carries_typed_artifacts_not_raw_payloads():
    resolver = FakeReferenceResolver(
        {
            "ctx_assets": {
                "artifact_refs": [
                    ArtifactRef(
                        artifact_id="art_pdf",
                        artifact_type="document",
                        locator="doc://spec",
                        owner_scope={"organization_id": "org_1"},
                        mime_type="application/pdf",
                    ),
                    ArtifactRef(
                        artifact_id="art_img",
                        artifact_type="image",
                        locator="image://shot",
                        owner_scope={"organization_id": "org_1"},
                        mime_type="image/png",
                    ),
                ]
            }
        }
    )
    loader = FakeArtifactLoader(
        {
            "art_pdf": {
                "text_content": "PDF summary " * 150,
                "metadata": {"raw_payload": "do-not-inline", "pages": 12},
                "mime_type": "application/pdf",
                "source_ref_id": "ctx_assets",
            },
            "art_img": {
                "text_content": "OCR screenshot summary",
                "metadata": {"raw_payload": "do-not-inline", "width": 1440},
                "mime_type": "image/png",
                "source_ref_id": "ctx_assets",
            },
        }
    )

    bundle = assemble(
        request=ContextAssemblyRequest(
            surface="workspace",
            actor={"entity_type": "user", "entity_id": "usr_1"},
            owner_scope={"organization_id": "org_1"},
            intent="review the uploaded pack",
            context_refs=[
                ContextRef(
                    ref_id="ctx_assets",
                    ref_type="artifact_group",
                    pointer="pack://latest",
                    owner_scope={"organization_id": "org_1"},
                )
            ],
            projection=Projection(max_tokens=1300, max_artifacts=2, max_inline_artifact_chars=80),
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
        toolkit=FakeToolkit(),
        llm=FakeLLM(),
        resolver=resolver,
        artifact_loader=loader,
    )

    assert {artifact.artifact_type for artifact in bundle.loaded_artifacts} == {"document", "image"}
    assert all("do-not-inline" not in artifact.text_content for artifact in bundle.loaded_artifacts)
    assert bundle.token_count_estimate <= bundle.projection.max_tokens

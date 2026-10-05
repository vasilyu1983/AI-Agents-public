"""Demo: pointer-first just-in-time multimodal context assembly.

Shows the P12/P13-style flow:
1. carry small refs in the request
2. resolve refs into typed evidence / artifact pointers
3. load only the artifacts needed for this surface
4. format them into compact projections instead of raw payload stuffing
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
sys.path.insert(0, str(_HERE.parent / "reference_app"))

from reference_app.contracts import (  # noqa: E402
    ArtifactRef,
    ContextAssemblyRequest,
    ContextRef,
    EntityProfile,
    Projection,
)
from reference_app.runtime import assemble  # noqa: E402

from evals.fakes import (  # noqa: E402
    FakeArtifactLoader,
    FakeLLM,
    FakeMemoryStore,
    FakeReferenceResolver,
    FakeRetrievalStore,
    FakeToolkit,
)


def main() -> int:
    owner_scope = {"organization_id": "org_demo"}
    resolver = FakeReferenceResolver(
        {
            "ctx_design": {
                "live_facts": [{"workspace_mode": "review"}],
                "artifact_refs": [
                    ArtifactRef(
                        artifact_id="art_doc",
                        artifact_type="document",
                        locator="doc://design",
                        owner_scope=owner_scope,
                        mime_type="text/markdown",
                        title="Design Spec",
                    ),
                    ArtifactRef(
                        artifact_id="art_shot",
                        artifact_type="image",
                        locator="image://homepage",
                        owner_scope=owner_scope,
                        mime_type="image/png",
                        title="Homepage Screenshot",
                    ),
                ],
            }
        }
    )
    loader = FakeArtifactLoader(
        {
            "art_doc": {
                "text_content": "The design doc says the assistant should prefer concise summaries. " * 20,
                "source_ref_id": "ctx_design",
                "metadata": {"title": "Design Spec"},
            },
            "art_shot": {
                "text_content": "OCR: hero headline, CTA, pricing table, and comparison rows.",
                "source_ref_id": "ctx_design",
                "metadata": {"width": 1440, "height": 2200},
            },
        }
    )

    bundle = assemble(
        request=ContextAssemblyRequest(
            surface="workspace",
            actor={"entity_type": "user", "entity_id": "usr_demo"},
            owner_scope=owner_scope,
            intent="review the latest design pack",
            context_refs=[
                ContextRef(
                    ref_id="ctx_design",
                    ref_type="search_hit",
                    pointer="design-pack://latest",
                    owner_scope=owner_scope,
                )
            ],
            projection=Projection(max_tokens=1400, max_artifacts=2, max_inline_artifact_chars=160),
        ),
        entity=EntityProfile(
            id="usr_demo",
            entity_type="user",
            owner_scope=owner_scope,
            source_of_truth="users://usr_demo",
            updated_at=datetime.now(UTC),
        ),
        memory_store=FakeMemoryStore(),
        retrieval_store=FakeRetrievalStore(),
        toolkit=FakeToolkit(),
        llm=FakeLLM(),
        resolver=resolver,
        artifact_loader=loader,
    )

    print(
        json.dumps(
            {
                "bundle_id": bundle.id,
                "surface": bundle.surface,
                "context_ref_ids": [ref.ref_id for ref in bundle.context_refs],
                "loaded_artifacts": [
                    {
                        "artifact_id": artifact.artifact_id,
                        "artifact_type": artifact.artifact_type,
                        "mime_type": artifact.mime_type,
                        "source_ref_id": artifact.source_ref_id,
                        "excerpt": artifact.text_content[:120],
                    }
                    for artifact in bundle.loaded_artifacts
                ],
                "live_fact_count": len(bundle.live_facts),
                "token_estimate": bundle.token_count_estimate,
            },
            indent=2,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

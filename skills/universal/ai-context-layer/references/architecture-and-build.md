# Context-Layer Architecture, Build, and Admission Detail

This reference contains detail moved out of the skill root. Load it after the root router selects the relevant workflow; do not preload it for unrelated work.

## Contents

- [Architecture, contracts, and workflow](#architecture-contracts-and-workflow)
- [ASCII flow](#ascii-flow)
- [Build kit](#build-kit)
- [Templates](#templates)
- [Context admission gate](#context-admission-gate)

## Architecture, Contracts, and Workflow

## ASCII Flow

```text
Context-layer design request
  -> Classify profile, memory, retrieval, grounding, or assembly need
  -> Select the smallest architecture pattern that fits tenancy and freshness
  -> Define contracts, lifecycle verbs, and source boundaries
  -> Check hygiene, contradiction, isolation, and threat-model risks
  -> Return architecture decisions with validation gates
```

Full depth — 7-layer architecture model, pattern-picker (P1–P13 Default Choice Framework), canonical contracts (`EntityProfile`, `LearnedMemory`, `KnowledgeSource`, `RetrievalResult`, `ContextAssemblyRequest`, `ContextBundle`, `FeedbackOutcome`, `ContextRef`, `ArtifactRef`, `LoadedArtifact`), memory lifecycle verbs (`remember`/`recall`/`forget`/`improve`), 16-step Review Workflow (includes F1–F5 context-hygiene, contradiction handling, sub-agent isolation, anti-pattern sweep, security threat model), Operational Defaults (do/avoid), Known Traps, and Top-7 Anti-Patterns — lives in [references/context-layer-detail.md](context-layer-detail.md).

Quick entry points for specific concerns:

- Patterns P1–P25: [references/patterns-catalog.md](patterns-catalog.md)
- Reference architectures RA1–RA13: [references/reference-architectures.md](reference-architectures.md)
- Anti-patterns A1–A49: [references/anti-patterns-catalog.md](anti-patterns-catalog.md)
- Context hygiene (F1–F5 failure modes; F1–F4 = Breunig canonical, F5 = proactive interference): [references/context-hygiene.md](context-hygiene.md)
- Inspection & review surfaces: [references/inspection-and-review-surfaces.md](inspection-and-review-surfaces.md)
- Security threat model: [references/security-threat-model.md](security-threat-model.md)
- Scorecard: [assets/eval/context-layer-scorecard.md](../assets/eval/context-layer-scorecard.md)

## Build Kit

For build-grade work — shipping the layer rather than designing it — see
[`builds/`](../builds/README.md):

- [`builds/reference_app/`](../builds/reference_app/README.md) — RA1 reference implementation plus P12/P13-ready runtime refs: contracts as Python dataclasses, adapter `Protocol`s for memory/retrieval/episodes/tools/LLM plus resolver/loader helpers, six runtime verbs, vendor-neutral core, Postgres + 5 vendor adapters
- [`builds/evals/`](../builds/evals/README.md) — runnable eval harness: smoke + Postgres + context-rot + mode-collapse + 5 vendor smoke suites + `jit_loading` + `managed_boundary` + `multimodal`
- [`builds/cookbooks/`](../builds/cookbooks/README.md) — vendor adapter recipes (Mem0, Letta, Cognee, LangGraph, pgvector, Supermemory), managed-runtime guides (OpenAI Retrieval, Vertex Memory Bank), latency/cost cookbook, ops runbook, 2026 traps appendix
- [`builds/TUTORIAL.md`](../builds/TUTORIAL.md) — zero-to-shipped 11-step walkthrough

All six phases shipped. Phase status and per-directory ownership are tracked in `builds/README.md`.

## Templates

- [Context Layer System Design](../assets/design/context-layer-system-design.md)
- [Context Layer Review Template](../assets/design/context-layer-review-template.md)
- [Context Bundle Template](../assets/contracts/context-bundle-template.md)
- [Entity + Memory Contract](../assets/contracts/entity-memory-contract.md)
- [Feedback Outcome Contract](../assets/contracts/feedback-outcome-contract.md)
- [Context Layer Scorecard](../assets/eval/context-layer-scorecard.md)

## Context Admission Gate

The assembler must attach the available envelope metadata for every candidate item: source class (`operational`, `retrieved`, `derived`, or `user-supplied`), owner scope, observed or effective time, provenance ID, and token cost. For a direct user turn, default provenance to the session and turn ID and time to receipt; do not require the user to supply system metadata. Admit an item only when the requesting surface is authorized, its freshness is adequate for the decision, and it fits the surface budget after higher-authority items. Exclude it for missing metadata only when the missing field is material to authority, isolation, or freshness. Record the item ID and class plus the exclusion reason, never the rejected raw content unless retention is explicitly authorized.



# Build Kit — `ai-context-layer`

Build-grade companion to the architect-grade skill. Where the references answer
*what should this layer look like*, this kit answers *how do I ship it*.

## What's in here

| Directory | Purpose | Phase |
|-----------|---------|-------|
| `reference_app/` | Working RA1 implementation plus P12/P13-ready runtime refs: P1 (operational tools) + P2 (typed memory) + P5 (lifecycle verbs) + P8 (evidence-bearing retrieval). Vendor-neutral core with adapter interfaces. | 1 scaffold, 2 impl |
| `reference_app/contracts/` | Canonical contracts as Python dataclasses. Mirrors `assets/contracts/*.md`. | ✅ Phase 1 |
| `reference_app/adapters/` | Adapter `Protocol`s for memory, retrieval, episode log, embedding, LLM, plus optional `ReferenceResolver` / `ArtifactLoader` for pointer-first loading. | ✅ Phase 1 (interfaces), 3 (vendors), 6 (runtime refs) |
| `reference_app/runtime/` | The six runtime verbs (`write`, `select`, `compress`, `isolate`, `order`, `format`) plus the P12 helper step for resolving runtime refs before projection. | ✅ Phase 1 (signatures), 2 (impl), 6 (runtime refs) |
| `evals/` | Runnable harness for F1–F5 (incl. proactive-interference), context rot, mode collapse, pointer-first loading, managed-memory boundaries, and multimodal regressions. | ✅ Phase 1 (smoke), 4 (suites), 6 (runtime refs) |
| `cookbooks/` | Vendor adapter cookbooks, managed-runtime guides, latency/cost worked examples, and ops runbooks. | 5 + 6 |
| `TUTORIAL.md` | Zero-to-shipped walkthrough following the reference app. | ✅ Phase 6 |

## Decisions locked in

| Decision | Choice | Why |
|----------|--------|-----|
| Language | Python 3.11+ | Matches `ai-rag` / `ai-agents` / Anthropic & OpenAI SDKs; broadest LLM ecosystem |
| Vendor stance | Neutral core + adapters | Lets the same app swap Mem0 → pgvector → Letta without touching assembly logic |
| Reference architecture | RA1 only (most common SaaS shape) | RA3/RA5 added in later phases if useful |
| Eval depth (v1) | Smoke + 1 substantive (context rot) | Proves the harness catches a real failure mode before scaling to all six |
| Location | Inside the skill at `builds/` | Matches `huggingface-*` skills that ship runnable code |

## Phase status

- [x] Phase 1 — scaffold, contracts, adapter interfaces, runtime signatures, smoke eval
- [x] Phase 2 — RA1 reference impl end-to-end (Postgres + pgvector adapters, real `compress`/`isolate`, env-gated behavioral tests, demo, pgvector cookbook)
- [x] Phase 3 — Adapter cookbooks for 5 more vendors (Mem0, Letta, Cognee, LangGraph Store, Supermemory) — adapters compile import-clean, behavioral tests gated by credentials
- [x] Phase 4 — Context-rot suite (16-case needle-in-haystack at 5 token tiers) + mode-collapse suite (12-prompt cross-prompt variance) + Anthropic LLM adapter + metrics module + rollup reports — all gated on `ANTHROPIC_API_KEY` with a token-spend cost guard
- [x] Phase 5 — Latency/cost cookbook (5 levers, per-surface budgets, KV-cache layout) + ops runbook (pre-launch checklist, zero-downtime migrations, backfill, A/B, kill switch, observability, 2 incident playbooks) + traps appendix (10 production traps) + `UnionMemoryStore` composition helper
- [x] Phase 6 — Pointer-first runtime refs (`ContextRef`, `ArtifactRef`, `LoadedArtifact`), optional `ReferenceResolver` / `ArtifactLoader`, JIT multimodal demo, new eval suites (`jit_loading`, `managed_boundary`, `multimodal`), and managed-runtime cookbooks

**Build kit complete.** All six phases shipped: contracts as code, vendor-neutral adapters with 10 cookbooks, runtime verbs plus pointer-first ref resolution, eval harness with smoke + Postgres + context-rot + mode-collapse + runtime-ref suites, and full operational guidance.

## How to use this kit

1. Read `TUTORIAL.md` for the end-to-end mental model.
2. Copy `reference_app/` into your project (or vendor it as a package).
3. Implement adapters for your chosen vendors using `adapters/base.py` as the contract.
4. Add `ReferenceResolver` / `ArtifactLoader` only if the surface needs P12-style pointer-first loading.
5. Run the eval harness against your assembled bundles before each release.
6. Apply the anti-pattern sweep (`../references/anti-patterns-catalog.md`) on every meaningful change.

## What this kit does NOT replace

- The architect-grade references — pattern selection, anti-pattern sweep, scorecard, security threat model, vendor landscape. Those still own the *design* decisions; this kit owns the *build* mechanics.
- A real eval dataset for your domain. The harness ships smoke fixtures only; substantive evaluation requires your own labeled cases.
- Production ops. The ops runbook (Phase 5) is starter material — your platform team owns rollout, observability, and SLOs.

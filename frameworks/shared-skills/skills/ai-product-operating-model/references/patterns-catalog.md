# AI Product Operating Model — Patterns Catalog

**Purpose.** Named, numbered catalog of the durable May 2026 patterns for AI product operating models. Every operating-model design this skill produces should cite one or more pattern IDs. Pair with `anti-patterns-catalog.md` for the anti-pattern sweep.

## Table of Contents

- [Pattern Index](#pattern-index)
- [P1 — Central-platform-first](#p1--central-platform-first)
- [P2 — External-APIs-first](#p2--external-apis-first)
- [P3 — Three-data-planes](#p3--three-data-planes)
- [P4 — Workflow-shape-classification](#p4--workflow-shape-classification)
- [P5 — Risk-tier-before-provider](#p5--risk-tier-before-provider)
- [P6 — Shared-platform-contracts](#p6--shared-platform-contracts)
- [P7 — Rollout-gates](#p7--rollout-gates)
- [P8 — Provider-abstraction-layer](#p8--provider-abstraction-layer)
- [P9 — Sensitive-data-minimization](#p9--sensitive-data-minimization)
- [P10 — Cost-and-latency-telemetry](#p10--cost-and-latency-telemetry)
- [P11 — Model-lifecycle-governance](#p11--model-lifecycle-governance)
- [P12 — Multi-model-ops](#p12--multi-model-ops)
- [Composition Rules of Thumb](#composition-rules-of-thumb)

## Pattern Index

| ID | Name | Primary role |
|----|------|--------------|
| P1 | Central-platform-first | Shared standards, contracts, and policy before federated sprawl |
| P2 | External-APIs-first | Provider abstraction before self-hosting |
| P3 | Three-data-planes | Operational truth / AI context / analytics separated |
| P4 | Workflow-shape-classification | LLM feature vs tool workflow vs agent system |
| P5 | Risk-tier-before-provider | Data and action sensitivity determines deployment posture |
| P6 | Shared-platform-contracts | Typed contracts before scale |
| P7 | Rollout-gates | Eval suite, telemetry, canary, rollback before broad launch |
| P8 | Provider-abstraction-layer | Model routing through a gateway, not direct per-feature calls |
| P9 | Sensitive-data-minimization | PI and sensitive fields minimized or redacted before model submission |
| P10 | Cost-and-latency-telemetry | Per-feature cost, latency, refusal, and fallback metrics from day one |
| P11 | Model-lifecycle-governance | Provider model deprecations treated as planned product events |
| P12 | Multi-model-ops | Multi-provider routing, fallback, eval parity, and cost attribution as platform concerns |

---

## P1 — Central-platform-first

- **Problem shape**: product teams independently choose providers, build incompatible wrappers, and own inconsistent safety postures, making governance impossible at scale.
- **Non-negotiables**: a central AI platform function owns provider policy, model routing, prompt versioning, eval standards, telemetry, and approval patterns before product teams ship production AI features.
- **When to use**: any organization shipping more than one AI-powered feature.
- **Blocks**: A1 (federated-before-contracts), A5 (per-team auth sprawl)

---

## P2 — External-APIs-first

- **Problem shape**: teams default to self-hosting models as a sign of AI maturity, incurring infrastructure cost before value is proven.
- **Non-negotiables**: external provider APIs are the default; self-hosting is reserved for cases where risk-tier requirements, latency SLAs, or data-residency constraints cannot be met via managed options.
- **When to use**: greenfield planning, provider selection discussions, cost reviews.
- **Blocks**: A2 (self-hosting-as-default)

---

## P3 — Three-data-planes

- **Problem shape**: operational truth, AI context, and analytics are collapsed into one warehouse, one vector DB, or one prompt log — creating freshness failures, tenancy violations, and provenance loss.
- **Non-negotiables**: three distinct planes — `operational truth` (users, orgs, billing, product state), `AI context layer` (retrieved evidence, derived memory, context bundles), `analytics layer` (event taxonomy, semantic metrics, marts) — each with independent ownership, freshness SLAs, and access controls.
- **When to use**: any data architecture review for AI-enabled products.
- **Blocks**: A3 (collapsed-planes), A6 (analytics-as-context)

---

## P4 — Workflow-shape-classification

- **Problem shape**: teams default to "agent" for all AI features, adding unnecessary autonomy, latency, and approval complexity to features that should be simple request/response.
- **Non-negotiables**: classify every AI surface before building — `LLM feature` (request/response or streaming generation), `tool workflow` (bounded tool use with explicit control flow), `agent system` (longer-running or ambiguous work with measurable autonomy value); default to the simplest shape that works.
- **When to use**: feature scoping, architectural design reviews.
- **Blocks**: A10 (agent-as-default)

---

## P5 — Risk-tier-before-provider

- **Problem shape**: teams select model providers based on benchmark rankings, not on the actual data and action sensitivity of the feature being built.
- **Non-negotiables**: define risk tiers and minimum controls before provider selection; provider choice follows data sensitivity and action reversibility, not the other way around.
- **When to use**: before any provider selection or deployment posture decision.
- **Reference**: `references/data-boundaries-and-risk-tiers.md`
- **Blocks**: A7 (provider-first-tier-second), A9 (marketing-language-safety)

---

## P6 — Shared-platform-contracts

- **Problem shape**: teams build incompatible local wrappers for model calls, context assembly, safety decisions, tool invocations, and audit events — impossible to govern at scale.
- **Non-negotiables**: standardize before scale — `ModelRequest`, `ModelResponse`, `ContextBundle`, `SafetyDecision`, `ToolInvocation`, `EvalRun`, `AuditEvent`.
- **When to use**: any platform that has shipped or is about to ship more than two AI features.
- **Blocks**: A1

---

## P7 — Rollout-gates

- **Problem shape**: AI features ship to all users before evals, telemetry, canary testing, and rollback procedures exist.
- **Non-negotiables**: every production feature has an eval suite, cost/latency/refusal telemetry, a canary rollout path, a rollback plan, and a human-escalation path before broad launch.
- **Eval function split (required)**: the eval function must be split into two distinct roles with different owners and cadences:
  - **Capability evals**: does the new model, prompt, or config meet the quality bar? Owner: platform/ML team. Cadence: per model or prompt change.
  - **Regression evals**: did we break anything already shipped? Owner: feature team. Cadence: every deployment.
  Collapsing both into one "eval run" hides regressions behind capability gains and vice versa.
- **When to use**: any production feature with AI-generated or AI-influenced output.
- **Blocks**: A8 (shipping-before-evals), A11 (model-deprecation-surprise)

---

## P8 — Provider-abstraction-layer

- **Problem shape**: provider-specific prompts, JSON schemas, and tool semantics leak directly into every product surface — switching providers requires rewriting feature code.
- **Non-negotiables**: all model calls go through an abstraction layer that enforces policy, logs decisions, and isolates provider semantics from product logic.
- **When to use**: any platform with two or more providers, or anticipating provider changes.
- **Blocks**: A4 (abstraction-that-leaks)

---

## P9 — Sensitive-data-minimization

- **Problem shape**: sensitive fields (PII, financial data, health data) are sent to public-cloud model APIs in raw form without verification of the actual request path, logging path, and retention settings.
- **Non-negotiables**: sensitive fields are minimized or redacted before model submission; logs and traces mask raw PI by default; provider's actual data handling is verified against primary docs, not marketing language.
- **When to use**: any feature that processes PI or regulated data.
- **Blocks**: A9

---

## P10 — Cost-and-latency-telemetry

- **Problem shape**: teams measure only model output quality; cost per conversation, latency percentiles, refusal rates, and fallback behavior are invisible until they cause incidents.
- **Non-negotiables**: every production feature has per-call cost tracking, latency percentiles (p50/p95/p99), refusal rate, fallback trigger rate, and cost-per-resolved-outcome from day one.
- **When to use**: always — instrument before first production traffic.
- **Blocks**: A6 (quality-only-metrics)

---

## P11 — Model-lifecycle-governance

- **Problem shape**: a provider retires a model ID and the platform team discovers this from a 4xx error in production, not from a managed migration process.
- **Non-negotiables**: (1) track all production model IDs and their provider retirement dates, (2) when a deprecation is announced trigger a migration runbook — identify affected features, select candidate replacement, run capability eval parity gate, run regression evals, canary behind a flag, communicate cutover to dependent teams, document rollback plan. Cutover is blocked until the replacement clears the capability eval threshold on your task-specific suite (not public benchmarks).
- **When to use**: any platform with hardcoded model IDs in production config; whenever a provider issues a deprecation notice.
- **Blocks**: A11 (model-deprecation-surprise)

---

## P12 — Multi-model-ops

- **Problem shape**: teams add a second or third frontier provider reactively (fallback to an outage, cost optimization, capability gap) without a routing policy, eval-parity gate, or per-provider cost attribution — making the multi-provider state ungovernable.
- **Non-negotiables**: define at the platform level — (1) routing policy per feature or risk tier (which model, why), (2) explicit fallback chain with trigger condition (error rate, latency threshold) and fallback target, (3) eval-parity gate before routing any feature to a new provider on your task-specific suite, (4) cost telemetry tagged by provider and model ID, (5) DPA review and data-handling verification for each provider in the allowlist.
- **When to use**: any platform routing production traffic to more than one frontier provider or model, or planning to add a second provider.
- **Blocks**: A12 (single-provider-dependency)

---

## Composition Rules of Thumb

- Every AI platform needs P1 (central platform) + P3 (three data planes) + P6 (shared contracts) as the foundation before any feature work begins.
- Every feature needs P4 (workflow shape) + P5 (risk tier) before provider selection.
- Every production launch needs P7 (rollout gates) + P10 (telemetry).
- Sensitive-data features always add P9.
- Multi-provider platforms always add P8 + P12.
- Any platform with hardcoded model IDs in production config needs P11.
- P7 eval split (capability vs regression) applies to every platform — not optional.
